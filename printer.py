# coding=utf-8
import win32print

# app
from qt_core import QMessageBox



class Printer:

    def __init__(self, main):
        self.main = main
        self.linhas_por_pagina = 60


    def start_printer(self, endereco_arquivo, nome_arquivo, nome_impressora=None):
        self.endereco_arquivo = endereco_arquivo
        self.nome_impressora = nome_impressora
        self.nome_arquivo = nome_arquivo

        self.print_file()


    def get_name_printers(self):
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
        printer_names = [printer[2] for printer in printers]
        return printer_names        


    def print_file(self):

        # Se nenhuma impressora for especificada, usa a impressora padrão
        if self.nome_impressora is None:
            self.nome_impressora = win32print.GetDefaultPrinter()

        # Abre o arquivo .txt
        with open(self.endereco_arquivo, 'r', encoding='utf-8-sig') as file:
            arquivo = file.read()

        # Adiciona quebras de página manualmente (exemplo: a cada 60 linhas)
        linhas = arquivo.split('\n')
        arquivo_com_paginas = ""
        for i, line in enumerate(linhas):
            arquivo_com_paginas += line + '\n'
            if (i + 1) % self.linhas_por_pagina == 0:
                arquivo_com_paginas += '\f'  # Adiciona uma quebra de página

        # Abre a impressora
        hPrinter = win32print.OpenPrinter(self.nome_impressora)
        infoPrinter = win32print.GetPrinter(hPrinter, 2)['Status']

        if infoPrinter != 0:
            QMessageBox(self.main, 'Aviso', 'Impressora parece desligada?')
            return None

        try:
            # Inicia um trabalho de impressão
            hJob = win32print.StartDocPrinter(hPrinter, 1, (self.nome_arquivo, None, "RAW"))
            try:
                # Inicia uma página
                win32print.StartPagePrinter(hPrinter)

                # Escreve o conteúdo na impressora
                win32print.WritePrinter(hPrinter,  arquivo_com_paginas.encode('utf-8'))

                # Finaliza a página
                win32print.EndPagePrinter(hPrinter)

            finally:
                # Finaliza o trabalho de impressão
                win32print.EndDocPrinter(hPrinter)
        finally:
            # Fecha a impressora
            win32print.ClosePrinter(hPrinter)
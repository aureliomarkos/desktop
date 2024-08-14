# coding: utf-8
from datetime import datetime

# app
from models import Produto, getSessionDB


class Relatorio:

    def __init__(self, titulo, cabecalho, nome_arquivo):
        self.titulo = titulo
        self.cabecalho = cabecalho

        self.pagina = 1
        self.count_linhas = 0
        self.linhas_por_pagina = 60

        self.prnFile = open('./relatorio/' + nome_arquivo, 'w', encoding='utf-8')

        self.set_header()


    def set_header(self):
        largura_total = 80

        data = datetime.now().strftime('%d/%m/%Y')
        hora = datetime.now().strftime('%H:%M:%S')

        texto_data = 'Data:' + data
        texto_pagina = f'Pág.: {self.pagina}'

        # centralizar o título
        largura_fixa = len(texto_data) + len(texto_pagina)
        largura_titulo = largura_total - largura_fixa
        espacos_esquerda = (largura_titulo - len(self.titulo)) // 2
        linha_cabecalho = f"{texto_data}{' ' * espacos_esquerda}{self.titulo}{' ' * (largura_titulo - espacos_esquerda - len(self.titulo))}{texto_pagina}"

        self.prnFile.write("-" * 80 + '\n')
        self.prnFile.write(linha_cabecalho + '\n')
        self.prnFile.write(hora + '\n')
        self.prnFile.write("-" * 80 + '\n')
        self.prnFile.write(self.cabecalho + '\n')
        self.prnFile.write("-" * 80 + '\n')


    def printer_row(self, row):

        self.prnFile.write(row)
        self.prnFile.write('\n')

        self.count_linhas += 1
        if self.count_linhas >= self.linhas_por_pagina:
            self.pagina += 1
            self.count_linhas = 0
            self.set_header()
    
    
    def set_footer(self, value):

        if self.count_linhas >= self.linhas_por_pagina:
            self.pagina += 1
            self.count_linhas = 0
            self.set_header()

        self.prnFile.write("-" * 80 + '\n')
        self.prnFile.write(value)

    
    def get_file(self):
        return self.prnFile


    def close_file(self):
        self.prnFile.close()
# coding=utf-8
from qt_core import QMessageBox, QFont

# app
from printer import Printer
from report import Relatorio
from models import ContaPagar, Fornecedor, getSessionDB


class AccountPayableReport:

    def __init__(self, main):
        self.main = main

        self.main.btn_imprimir_relatorio_conta_pagar.clicked.connect(self.on_click_button_imprimir_relatorio)
                  
        self.main.btn_gerar_relatorio_conta_pagar.clicked.connect(self.on_click_button_gerar_relatorio)

        self.main.btn_goback_relatorio_conta_pagar.clicked.connect(self.on_click_button_goback_data_table_conta_pagar)
        
    
    def on_click_button_imprimir_relatorio(self):
        printer = Printer(self.main)

        printer.start_printer('./relatorio/conta_pagar.txt', 'Relatório de Contas à Pagar')


    def on_click_button_goback_data_table_conta_pagar(self, e):
        self.main.forms.setCurrentWidget(self.main.formDataTableContaPagar)


    def on_click_button_gerar_relatorio(self):

        session = getSessionDB()
        data_inicial = self.main.relatorio_conta_pagar_data_inicial.date().toPython()
        data_final = self.main.relatorio_conta_pagar_data_final.date().toPython()

        status = 'Pago'
        if self.main.chk_relatorio_conta_pagar_status.isChecked():
            status = 'Aberto'

        contapag = session.query(ContaPagar).join(Fornecedor).filter(
                                                Fornecedor.nome.like(f'%{self.main.search_cliente_relatorio_conta_pagar.text()}%'),
                                                ContaPagar.data_vcto >= data_inicial,
                                                ContaPagar.data_vcto <= data_final,
                                                ContaPagar.status == status).order_by(ContaPagar.data_vcto.desc()).all()

        # button imprimir relatório
        if contapag:
            self.main.btn_imprimir_relatorio_conta_pagar.setDisabled(False)
        else:
            self.main.btn_imprimir_relatorio_conta_pagar.setDisabled(True)

        cabecalho = f'{'FORNECEDOR':<15} {'REFERÊNCIA':<24} {'DESCRIÇÃO':<18} {'DATA VCTO':<10} {'VALOR':>9}'

        relContaPagar = Relatorio(f'Relatório de Contas à Pagar ({status})', cabecalho, 'conta_pagar.txt')

        total = 0.00
        for conta in contapag:

            relContaPagar.printer_row(f'{conta.fornecedor.nome:<15.15} {conta.referencia:<24.24} {conta.descricao:<18.18} {conta.data_vcto.strftime('%d/%m/%Y')} {str(conta.valor_parcela).replace('.', ','):>9}')
            total += float(conta.valor_parcela)

        total = round(total, 2)
        footer = f'{str(total).replace('.', ','):>80}'

        relContaPagar.set_footer(footer)
        relContaPagar.close_file()
        
        with open('./relatorio/conta_pagar.txt',  'r', encoding='utf-8') as file:
            relatorio_texto = file.read()

        # Define a fonte monoespaçada
        font = QFont("Courier New")
        font.setPointSize(11)

        self.main.te_relatorio_conta_pagar.setFont(font)
        self.main.te_relatorio_conta_pagar.setPlainText(relatorio_texto) 
        self.main.te_relatorio_conta_pagar.setReadOnly(True)


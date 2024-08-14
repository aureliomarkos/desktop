# coding=utf-8
from qt_core import QMessageBox, QFont

# app
from printer import Printer
from report import Relatorio
from models import ContaReceber, Cliente, getSessionDB


class AccountReceivableReport:

    def __init__(self, main):
        self.main = main

        self.main.btn_imprimir_relatorio_conta_receber.clicked.connect(self.on_click_button_imprimir_relatorio)
                  
        self.main.btn_gerar_relatorio_conta_receber.clicked.connect(self.on_click_button_gerar_relatorio)

        self.main.btn_goback_relatorio_conta_receber.clicked.connect(self.on_click_button_goback_data_table_conta_receber)
        
    
    def on_click_button_imprimir_relatorio(self):
        printer = Printer(self.main)

        printer.start_printer('./relatorio/conta_receber.txt', 'Relatório de Contas à Receber')


    def on_click_button_goback_data_table_conta_receber(self, e):
        self.main.forms.setCurrentWidget(self.main.formDataTableContaReceber)


    def on_click_button_gerar_relatorio(self):

        session = getSessionDB()
        data_inicial = self.main.relatorio_conta_receber_data_inicial.date().toPython()
        data_final = self.main.relatorio_conta_receber_data_final.date().toPython()

        status = 'Pago'
        if self.main.chk_relatorio_conta_receber_status.isChecked():
            status = 'Aberto'

        contarec = session.query(ContaReceber).join(Cliente).filter(
                                                Cliente.nome.like(f'%{self.main.search_cliente_relatorio_conta_receber.text()}%'),
                                                ContaReceber.data_vcto >= data_inicial,
                                                ContaReceber.data_vcto <= data_final,
                                                ContaReceber.status == status).order_by(ContaReceber.data_vcto.desc()).all()

        # button imprimir relatório
        if contarec:
            self.main.btn_imprimir_relatorio_conta_receber.setDisabled(False)
        else:
            self.main.btn_imprimir_relatorio_conta_receber.setDisabled(True)

        cabecalho = f'{'CLIENTE':<15} {'REFERÊNCIA':<24} {'DESCRIÇÃO':<18} {'DATA VCTO':<10} {'VALOR':>9}'

        relContaReceber = Relatorio(f'Relatório de Contas à Receber ({status})', cabecalho, 'conta_receber.txt')

        total = 0.00
        for conta in contarec:

            relContaReceber.printer_row(f'{conta.cliente.nome:<15.15} {conta.referencia:<24.24} {conta.descricao:<18.18} {conta.data_vcto.strftime('%d/%m/%Y')} {str(conta.valor_parcela).replace('.', ','):>9}')
            total += float(conta.valor_parcela)

        total = round(total, 2)
        footer = f'{str(total).replace('.', ','):>80}'

        relContaReceber.set_footer(footer)
        relContaReceber.close_file()
        
        with open('./relatorio/conta_receber.txt',  'r', encoding='utf-8') as file:
            relatorio_texto = file.read()

        # Define a fonte monoespaçada
        font = QFont("Courier New")
        font.setPointSize(11)

        self.main.te_relatorio_conta_receber.setFont(font)
        self.main.te_relatorio_conta_receber.setPlainText(relatorio_texto) 
        self.main.te_relatorio_conta_receber.setReadOnly(True)


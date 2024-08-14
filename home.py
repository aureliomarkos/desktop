# coding=utf-8
from qt_core import QDate

# app
from models import Venda, Compra, ContaReceber, ContaPagar, getSessionDB, func



# Home
class Home:

    def __init__(self, main):
        self.main = main

        self.main.home_data_inicial.setDate(QDate.currentDate())
        self.main.home_data_final.setDate(QDate.currentDate())

        # button home
        self.main.btn_home.clicked.connect(self.on_click_button_home)

        # button home filtrar
        self.main.btn_home_filtrar.clicked.connect(self.on_click_button_home_filtrar)
    
        
    # on click button home
    def on_click_button_home(self, e):

        self.main.home_data_inicial.setFocus()

        self.main.forms.setCurrentWidget(self.main.formHome)       

    
    # on click button home filtrar
    def on_click_button_home_filtrar(self, e):

        receita = 0.00
        despesa = 0.00
        saldo = 0.00

        data_inicial = self.main.home_data_inicial.date().toPython()
        data_final = self.main.home_data_final.date().toPython()

        self.main.lbl_home_venda_value.setText('Vendas R$:')
        self.main.lbl_home_conta_receber_value.setText('Conta à Receber R$:')
        self.main.lbl_home_compra_value.setText('Compras R$:')
        self.main.lbl_home_conta_pagar_value.setText('Conta à Pagar R$:')

        session = getSessionDB()

        total_vendas = session.query(func.sum(Venda.total)).filter(Venda.data_emissao >= data_inicial, Venda.data_emissao <= data_final, Venda.status == 'À Vista').first()[0]
        total_cta_receber = session.query(func.sum(ContaReceber.valor_pago)).filter(ContaReceber.data_pagto >= data_inicial, ContaReceber.data_pagto <= data_final, ContaReceber.status == 'Pago').first()[0]
        
        total_compras = session.query(func.sum(Compra.total)).filter(Compra.data_emissao >= data_inicial, Compra.data_emissao <= data_final, Compra.status == 'À Vista').first()[0]
        total_cta_pagar = session.query(func.sum(ContaPagar.valor_pago)).filter(ContaPagar.data_pagto >= data_inicial, ContaPagar.data_pagto <= data_final, ContaPagar.status == 'Pago').first()[0]

        session.close()
        
        if total_vendas:
            receita += float(total_vendas)
            self.main.lbl_home_venda_value.setText(f'Vendas R$: {str(total_vendas).replace('.', ',')}')

        if total_cta_receber:
            receita += float(total_cta_receber)
            self.main.lbl_home_conta_receber_value.setText(f'Conta à Receber R$: {str(total_cta_receber).replace('.', ',')}')

        if total_compras:
            despesa += float(total_compras)
            self.main.lbl_home_compra_value.setText(f'Compras R$: {str(total_compras).replace('.', ',')}')

        if total_cta_pagar:
            despesa += float(total_cta_pagar)
            self.main.lbl_home_conta_pagar_value.setText(f'Conta à Pagar R$: {str(total_cta_pagar).replace('.', ',')}')

        saldo = receita - despesa
        self.main.lbl_home_saldo_value.setText(f'R$ {str(saldo).replace('.', ',')}')
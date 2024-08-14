# coding=utf-8
from qt_core import QTableWidgetItem, QMessageBox, QPushButton, QIcon, QDate, Qt

# app
from utils import set_table_row_color, proximo_mes, get_mes_ano_referencia
from models import Fornecedor, ContaPagar, CentroCusto, getSessionDB, SQLAlchemyError



class AccountPayable:

    def __init__(self, main):
        self.main = main

        # on click button conta pagar
        self.main.btn_form_conta_pagar.clicked.connect(self.on_click_button_conta_pagar)

        # on click button goback
        self.main.btn_goback_data_table_conta_pagar.clicked.connect(self.on_click_button_goback_data_table_conta_pagar)

        # on click button add conta pagar
        self.main.btn_add_conta_pagar.clicked.connect(self.on_click_button_add_conta_pagar)

        # on click button gerar conta pagar
        self.main.btn_gerar_conta_pagar.clicked.connect(self.on_click_button_gerar_conta_pagar)

        # on click button refresh data table conta pagar
        self.main.btn_refresh_table_conta_pagar.clicked.connect(self.on_click_button_refresh_data_table_conta_pagar)

        # on click butto search cliente conta pagar
        self.main.btn_search_fornecedor_conta_pagar.clicked.connect(self.on_click_button_search_fornecedor_conta_pagar)

        # on click button relatorio de conta pagar
        self.main.btn_relatorio_conta_pagar.clicked.connect(self.on_click_button_relatorio_conta_pagar)


    # on click conta button conta pagar
    def on_click_button_conta_pagar(self, e):

        self.main.conta_pagar_data_inicial.setDate(QDate.currentDate())
        self.main.conta_pagar_data_final.setDate(QDate.currentDate())

        self.populate_data_table_conta_pagar()

        self.main.search_fornecedor_conta_pagar.setFocus()

        self.main.forms.setCurrentWidget(self.main.formDataTableContaPagar)


    # on click button relatorio conta pagar
    def on_click_button_relatorio_conta_pagar(self, e):

        self.main.relatorio_conta_pagar_data_inicial.setDate(QDate.currentDate())
        self.main.relatorio_conta_pagar_data_final.setDate(QDate.currentDate())

        self.main.search_cliente_relatorio_conta_pagar.setText('')
        self.main.search_cliente_relatorio_conta_pagar.setFocus()

        self.main.te_relatorio_conta_pagar.clear()

        self.main.forms.setCurrentWidget(self.main.formRelatorioContaPagar)


    # on click button goback data table conta pagar
    def on_click_button_goback_data_table_conta_pagar(self, e):
        self.main.forms.setCurrentWidget(self.main.formDataTableContaPagar)

    
    # on click button add conta pagar
    def on_click_button_add_conta_pagar(self, e):

        self.flagDataSet = 'Insert'

        self.main.supplier.populate_combo_box_fornecedor()
        self.main.cost_center.populate_combo_box_centro_custo()

        self.clear_fields_form_conta_pagar()

        self.main.conta_pagar_doc_numero.setFocus()

        self.main.forms.setCurrentWidget(self.main.formCadastroContaPagar)

    
    # on click button refresh data table conta pagar
    def on_click_button_refresh_data_table_conta_pagar(self, e):
        self.populate_data_table_conta_pagar()

    
    # on click button search cliente conta pagar
    def on_click_button_search_fornecedor_conta_pagar(self):
        self.populate_data_table_conta_pagar(flagQueryByUser=True)


    # clear fields form conta pagar
    def clear_fields_form_conta_pagar(self):

        self.main.conta_pagar_doc_numero.setText('')
        self.main.conta_pagar_descricao.setText('')

        self.main.sb_conta_pagar_valor_titulo.setValue(0.00)
        self.main.sb_conta_pagar_nro_parcelas.setValue(1)

        self.main.conta_pagar_data_vcto.setDate(QDate.currentDate())

        self.main.cb_conta_pagar_centro_custo.setCurrentIndex(-1)
        self.main.cb_conta_pagar_fornecedor.setCurrentIndex(-1)


    # populate data table conta pagar
    def populate_data_table_conta_pagar(self, flagQueryByUser=None):

        total_contas = 0
        data_inicial = self.main.conta_pagar_data_inicial.date().toPython()
        data_final = self.main.conta_pagar_data_final.date().toPython()
        
        status = 'Pago'
        if self.main.chk_conta_pagar_status.isChecked():
            status = 'Aberto'

        session = getSessionDB()

        if flagQueryByUser:
            contapag = session.query(ContaPagar).join(Fornecedor).filter(
                                                                Fornecedor.nome.like(f'%{self.main.search_fornecedor_conta_pagar.text()}%'),
                                                                ContaPagar.data_vcto >= data_inicial,
                                                                ContaPagar.data_vcto <= data_final,
                                                                ContaPagar.status == status).order_by(ContaPagar.data_vcto.desc()).all()
        else:
            contapag = session.query(ContaPagar).order_by(ContaPagar.data_vcto.desc()).all()

        self.main.dt_Conta_Pagar.setRowCount(len(contapag))
        self.main.dt_Conta_Pagar.setColumnCount(15)
        self.main.dt_Conta_Pagar.setColumnWidth(0, 80)
        self.main.dt_Conta_Pagar.setColumnWidth(1, 80)
        self.main.dt_Conta_Pagar.setColumnWidth(4, 180)
        self.main.dt_Conta_Pagar.setColumnWidth(5, 140)
        self.main.dt_Conta_Pagar.setColumnWidth(6, 180)

        # insert data
        for row, conta in enumerate(contapag):

            baixar_conta_button = QPushButton(QIcon("./icons/iconBaixarCtaReceber.png"), "")
            baixar_conta_button.setToolTip("Baixar Contas a Pagar")
            baixar_conta_button.clicked.connect(self.on_click_button_baixar_conta)
            self.main.dt_Conta_Pagar.setCellWidget(row, 0, baixar_conta_button)

            delete_button = QPushButton(QIcon("./icons/iconTrash.png"), "")
            delete_button.setToolTip("Excluir Conta a Pagar")
            delete_button.clicked.connect(self.on_click_button_delete_conta_pagar)
            self.main.dt_Conta_Pagar.setCellWidget(row, 1, delete_button)

            # id - 1
            id_conta = QTableWidgetItem(str(conta.id))
            self.main.dt_Conta_Pagar.setItem(row, 2, id_conta)
            id_conta.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.main.dt_Conta_Pagar.setItem(row, 3, QTableWidgetItem(conta.doc_numero))
            self.main.dt_Conta_Pagar.setItem(row, 4, QTableWidgetItem(conta.descricao))
            self.main.dt_Conta_Pagar.setItem(row, 5, QTableWidgetItem(conta.referencia))
            self.main.dt_Conta_Pagar.setItem(row, 6, QTableWidgetItem(conta.fornecedor.nome))
            self.main.dt_Conta_Pagar.setItem(row, 7, QTableWidgetItem(conta.status))
            self.main.dt_Conta_Pagar.setItem(row, 8, QTableWidgetItem(str(conta.data_vcto.strftime('%d/%m/%Y'))))

            if not conta.data_pagto:
                self.main.dt_Conta_Pagar.setItem(row, 9, QTableWidgetItem(''))
            else:
                self.main.dt_Conta_Pagar.setItem(row, 9, QTableWidgetItem(str(conta.data_pagto.strftime('%d/%m/%Y'))))

            # valor parcela - 10
            valor_parcela = QTableWidgetItem(f'{conta.valor_parcela:>9.2f}'.replace('.', ','))
            self.main.dt_Conta_Pagar.setItem(row, 10, valor_parcela)
            valor_parcela.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # valor pago - 11
            valor_pago = QTableWidgetItem(f'{conta.valor_pago:>9.2f}'.replace('.', ','))
            self.main.dt_Conta_Pagar.setItem(row, 11, valor_pago)
            valor_pago.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # valor título - 12
            valor_titulo = QTableWidgetItem(f'{conta.valor_titulo:>9.2f}'.replace('.', ','))
            self.main.dt_Conta_Pagar.setItem(row, 12, valor_titulo)
            valor_titulo.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            if not conta.forma_pagto:
                self.main.dt_Conta_Pagar.setItem(row, 13, QTableWidgetItem(""))
            else:
                self.main.dt_Conta_Pagar.setItem(row, 13, QTableWidgetItem(conta.forma_pagto.descricao))
               
            self.main.dt_Conta_Pagar.setItem(row, 14, QTableWidgetItem(conta.centro_custo.descricao))

            set_table_row_color(row, self.main.dt_Conta_Pagar)

            total_contas += conta.valor_parcela
        
        self.main.lbl_conta_pagar_total_value.setText(f'TOTAL R$ {str(total_contas).replace('.', ',')}')


        # close session
        session.close()


    # on click button baixar conta
    def on_click_button_baixar_conta(self, e):
        idConta = self.main.dt_Conta_Pagar.item(self.main.dt_Conta_Pagar.currentRow(), 2).text()
        self.main.down_account_pay.set_id_conta_pagar(idConta)
        self.main.baixar_conta_pagar_data_pagto.setFocus()
        self.main.forms.setCurrentWidget(self.main.formBaixarContaPagar)


    # on click button delete conta pagar
    def on_click_button_delete_conta_pagar(self, e):
       
        idConta = self.main.dt_Conta_Pagar.item(self.main.dt_Conta_Pagar.currentRow(), 2).text()

        if QMessageBox.question(self.main, 'Excluir Conta Pagar', f'Tem certeza que deseja excluir Conta Pagar: "{idConta}"?',
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
        
            session = getSessionDB()
            contapag = session.query(ContaPagar).filter_by(id=idConta).first()

            try:
                session.delete(contapag)
                session.commit()
                session.close()

            except SQLAlchemyError as err:
                error_message = str(err).split('\n')[0]
                QMessageBox.warning(self.main, 'Erro', f'Conta Pagar: "{idConta}" não pode ser excluído\n{error_message}.')
                session.close()
                return None

            self.main.dt_Conta_Pagar.removeRow(self.main.dt_Conta_Pagar.currentRow())
    

    # on click button save conta pagar
    def on_click_button_gerar_conta_pagar(self, e):

        session = getSessionDB()

        if not self.main.conta_pagar_doc_numero.text():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "DOC NÚMERO" deve ser informado.')
            return None

        if not self.main.sb_conta_pagar_nro_parcelas.value():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "NRO PARCELAS" deve ser informado.')
            return None

        if not self.main.cb_conta_pagar_fornecedor.currentText():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "FORNECEDOR" deve ser informado.')
            return None
        
        if not session.query(Fornecedor).filter_by(nome=self.main.cb_conta_pagar_fornecedor.currentText()).first():
            QMessageBox.warning(self.main,  "Aviso", f'"FORNECEDOR" {self.main.cb_conta_pagar_fornecedor.currentText()} não cadastrado.')
            session.close()
            return None

        if not self.main.conta_pagar_descricao.text():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "DESCRIÇÃO" deve ser informado.')
            return None

        if not self.main.cb_conta_pagar_centro_custo.currentText():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "CENTRO DE CUSTO" deve ser informado.')
            return None

        if not session.query(CentroCusto).filter_by(descricao=self.main.cb_conta_pagar_centro_custo.currentText()).first():
            QMessageBox.warning(self.main, "Aviso", f'Centro de Custo: "{self.main.cb_conta_pagar_centro_custo.currentText()}" não cadastrado.')
            self.main.cb_conta_pagar_centro_custo.setFocus()
            session.close()
            return None
       
        if not self.main.sb_conta_pagar_valor_titulo.value():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "VALOR TÍTULO" deve ser informado.')
            return None

        nroParcelas = 1
        if self.main.sb_conta_pagar_nro_parcelas.value():
            nroParcelas = self.main.sb_conta_pagar_nro_parcelas.value()

        data_inicial = self.main.conta_pagar_data_vcto.date().toPython()

        for parcela in range(nroParcelas):

            mes, ano = get_mes_ano_referencia(data_inicial)

            contapag = ContaPagar(

                        descricao = self.main.conta_pagar_descricao.text(),
                        referencia =  f'{mes}/{ano} Parcela {parcela+1} de {self.main.sb_conta_pagar_nro_parcelas.value()}.',
                        doc_numero = self.main.conta_pagar_doc_numero.text(),

                        data_vcto = data_inicial,

                        valor_titulo = self.main.sb_conta_pagar_valor_titulo.value(),
                        valor_parcela = round(self.main.sb_conta_pagar_valor_titulo.value() / self.main.sb_conta_pagar_nro_parcelas.value(), 2),

                        fornecedor_id = session.query(Fornecedor.id).filter_by(nome=self.main.cb_conta_pagar_fornecedor.currentText()).first()[0],
                        centro_custo_id = session.query(CentroCusto.id).filter_by(descricao=self.main.cb_conta_pagar_centro_custo.currentText()).first()[0])
                
            data_inicial = proximo_mes(data_inicial.day, data_inicial)

            try:
                session.add(contapag)
                session.commit()

            except SQLAlchemyError as err:
                error_message = str(err).split('\n')[0]
                QMessageBox.warning(self.main,  "Erro", f'Não foi possível gerar Conta a Pagar.\n{error_message}')
                session.close()
                return None

        session.close()
        self.clear_fields_form_conta_pagar()
        self.populate_data_table_conta_pagar()
        self.main.forms.setCurrentWidget(self.main.formDataTableContaPagar)
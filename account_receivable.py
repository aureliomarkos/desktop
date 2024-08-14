# coding=utf-8
from qt_core import QTableWidgetItem, QMessageBox, QPushButton, QIcon, QDate, Qt

# app
from utils import set_table_row_color, proximo_mes, get_mes_ano_referencia
from models import Cliente, ContaReceber, CentroCusto, getSessionDB, SQLAlchemyError


class AccountReceivable:

    def __init__(self, main):
        self.main = main

        # on click button contas a receber
        self.main.btn_form_conta_receber.clicked.connect(self.on_click_button_conta_receber)

        # on click button goback
        self.main.btn_goback_data_table_conta_receber.clicked.connect(self.on_click_button_goback_data_table_conta_receber)

        # on click button add contas a receber
        self.main.btn_add_conta_receber.clicked.connect(self.on_click_button_add_conta_receber)

        # on click button gerar conta receber
        self.main.btn_gerar_conta_receber.clicked.connect(self.on_click_button_gerar_conta_receber)

        # on click button refresh data table conta receber
        self.main.btn_refresh_table_conta_receber.clicked.connect(self.on_click_button_refresh_data_table_conta_receber)

        # on click butto search cliente conta receber
        self.main.btn_search_cliente_conta_receber.clicked.connect(self.on_click_button_search_cliente_conta_receber)

        # on click button relatorio de conta receber
        self.main.btn_relatorio_conta_receber.clicked.connect(self.on_click_button_relatorio_conta_receber)


    # on click conta button conta receber
    def on_click_button_conta_receber(self, e):

        self.main.conta_receber_data_inicial.setDate(QDate.currentDate())
        self.main.conta_receber_data_final.setDate(QDate.currentDate())

        self.populate_data_table_conta_receber()

        self.main.search_cliente_conta_receber.setFocus()

        self.main.forms.setCurrentWidget(self.main.formDataTableContaReceber)

    
    # on click button relatorio conta receber
    def on_click_button_relatorio_conta_receber(self, e):

        self.main.relatorio_conta_receber_data_inicial.setDate(QDate.currentDate())
        self.main.relatorio_conta_receber_data_final.setDate(QDate.currentDate())

        self.main.search_cliente_relatorio_conta_receber.setText('')
        self.main.search_cliente_relatorio_conta_receber.setFocus()

        self.main.te_relatorio_conta_receber.clear()

        self.main.forms.setCurrentWidget(self.main.formRelatorioContaReceber)


    # on click button goback data table conta receber
    def on_click_button_goback_data_table_conta_receber(self, e):
        self.main.forms.setCurrentWidget(self.main.formDataTableContaReceber)

    
    # on click button add conta receber
    def on_click_button_add_conta_receber(self, e):

        self.flagDataSet = 'Insert'

        self.main.client.populate_combo_box_cliente()
        self.main.cost_center.populate_combo_box_centro_custo()

        self.clear_fields_form_conta_receber()

        self.main.conta_receber_doc_numero.setFocus()

        self.main.forms.setCurrentWidget(self.main.formCadastroContaReceber)

    
    # on click button refresh data table conta receber
    def on_click_button_refresh_data_table_conta_receber(self, e):
        self.populate_data_table_conta_receber()

    
    # on click button search cliente conta receber
    def on_click_button_search_cliente_conta_receber(self):
        self.populate_data_table_conta_receber(flagQueryByUser=True)


    # clear fields form conta receber
    def clear_fields_form_conta_receber(self):

        self.main.conta_receber_doc_numero.setText('')
        self.main.conta_receber_descricao.setText('')

        self.main.sb_conta_receber_valor_titulo.setValue(0.00)
        self.main.sb_conta_receber_nro_parcelas.setValue(1)

        self.main.conta_receber_data_vcto.setDate(QDate.currentDate())

        self.main.cb_conta_receber_centro_custo.setCurrentIndex(-1)
        self.main.cb_conta_receber_cliente.setCurrentIndex(-1)


    # populate data table conta receber
    def populate_data_table_conta_receber(self, flagQueryByUser=None):

        total_contas = 0
        data_inicial = self.main.conta_receber_data_inicial.date().toPython()
        data_final = self.main.conta_receber_data_final.date().toPython()

        status = 'Pago'
        if self.main.chk_conta_receber_status.isChecked():
            status = 'Aberto'

        session = getSessionDB()

        if flagQueryByUser:
            contarec = session.query(ContaReceber).join(Cliente).filter(
                                                                    Cliente.nome.like(f'%{self.main.search_cliente_conta_receber.text()}%'),
                                                                    ContaReceber.data_vcto >= data_inicial,
                                                                    ContaReceber.data_vcto <= data_final,
                                                                    ContaReceber.status == status).order_by(ContaReceber.data_vcto.desc()).all()
        else:
            contarec = session.query(ContaReceber).order_by(ContaReceber.data_vcto.desc()).all()

        self.main.dt_Conta_Receber.setRowCount(len(contarec))
        self.main.dt_Conta_Receber.setColumnCount(15)
        self.main.dt_Conta_Receber.setColumnWidth(0, 80)
        self.main.dt_Conta_Receber.setColumnWidth(1, 80)
        self.main.dt_Conta_Receber.setColumnWidth(4, 180)
        self.main.dt_Conta_Receber.setColumnWidth(5, 140)
        self.main.dt_Conta_Receber.setColumnWidth(6, 180)


        # insert data
        for row, conta in enumerate(contarec):

            baixar_conta_button = QPushButton(QIcon("./icons/iconBaixarCtaReceber.png"), "")
            baixar_conta_button.setToolTip("Baixar Contas a Receber")
            baixar_conta_button.clicked.connect(self.on_click_button_baixar_conta)
            self.main.dt_Conta_Receber.setCellWidget(row, 0, baixar_conta_button)

            delete_button = QPushButton(QIcon("./icons/iconTrash.png"), "")
            delete_button.setToolTip("Excluir Conta a Receber")
            delete_button.clicked.connect(self.on_click_button_delete_conta_receber)
            self.main.dt_Conta_Receber.setCellWidget(row, 1, delete_button)

            # id - 1
            id_conta = QTableWidgetItem(str(conta.id))
            self.main.dt_Conta_Receber.setItem(row, 2, id_conta)
            id_conta.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.main.dt_Conta_Receber.setItem(row, 3, QTableWidgetItem(conta.doc_numero))
            self.main.dt_Conta_Receber.setItem(row, 4, QTableWidgetItem(conta.descricao))
            self.main.dt_Conta_Receber.setItem(row, 5, QTableWidgetItem(conta.referencia))
            self.main.dt_Conta_Receber.setItem(row, 6, QTableWidgetItem(conta.cliente.nome))
            self.main.dt_Conta_Receber.setItem(row, 7, QTableWidgetItem(conta.status))
            self.main.dt_Conta_Receber.setItem(row, 8, QTableWidgetItem(str(conta.data_vcto.strftime('%d/%m/%Y'))))

            if not conta.data_pagto:
                self.main.dt_Conta_Receber.setItem(row, 9, QTableWidgetItem(''))
            else:
                self.main.dt_Conta_Receber.setItem(row, 9, QTableWidgetItem(str(conta.data_pagto.strftime('%d/%m/%Y'))))

            # valor parcela - 10
            valor_parcela = QTableWidgetItem(f'{conta.valor_parcela:>9.2f}'.replace('.', ','))
            self.main.dt_Conta_Receber.setItem(row, 10, valor_parcela)
            valor_parcela.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # valor pago - 11
            valor_pago = QTableWidgetItem(f'{conta.valor_pago:>9.2f}'.replace('.', ','))
            self.main.dt_Conta_Receber.setItem(row, 11, valor_pago)
            valor_pago.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # valor título - 12
            valor_titulo = QTableWidgetItem(f'{conta.valor_titulo:>9.2f}'.replace('.', ','))
            self.main.dt_Conta_Receber.setItem(row, 12, valor_titulo)
            valor_titulo.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            if not conta.forma_pagto:
                self.main.dt_Conta_Receber.setItem(row, 13, QTableWidgetItem(""))
            else:
                self.main.dt_Conta_Receber.setItem(row, 13, QTableWidgetItem(conta.forma_pagto.descricao))
               
            self.main.dt_Conta_Receber.setItem(row, 14, QTableWidgetItem(conta.centro_custo.descricao))

            set_table_row_color(row, self.main.dt_Conta_Receber)

            total_contas += conta.valor_parcela
        
        self.main.lbl_conta_receber_total_value.setText(f'TOTAL R$ {str(total_contas).replace('.', ',')}')


        # close session
        session.close()


    # on click button baixar conta
    def on_click_button_baixar_conta(self, e):
        idConta = self.main.dt_Conta_Receber.item(self.main.dt_Conta_Receber.currentRow(), 2).text()
        self.main.down_account_rec.set_id_conta_receber(idConta)
        self.main.baixar_conta_receber_data_pagto.setFocus()
        self.main.forms.setCurrentWidget(self.main.formBaixarContaReceber)


    # on click button delete conta receber
    def on_click_button_delete_conta_receber(self, e):
       
        idConta = self.main.dt_Conta_Receber.item(self.main.dt_Conta_Receber.currentRow(), 2).text()

        if QMessageBox.question(self.main, 'Excluir Conta Receber', f'Tem certeza que deseja excluir Conta Receber: "{idConta}"?',
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
        
            session = getSessionDB()
            contarec = session.query(ContaReceber).filter_by(id=idConta).first()

            try:
                session.delete(contarec)
                session.commit()
                session.close()
            except SQLAlchemyError as err:
                error_message = str(err).split('\n')[0]
                QMessageBox.warning(self.main, 'Erro', f'Conta Receber: "{idConta}" não pode ser excluído\n{error_message}.')
                session.close()
                return None

            self.main.dt_Conta_Receber.removeRow(self.main.dt_Conta_Receber.currentRow())
    

    # on click button save conta receber
    def on_click_button_gerar_conta_receber(self, e):

        session = getSessionDB()

        if not self.main.conta_receber_doc_numero.text():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "DOC NÚMERO" deve ser informado.')
            return None

        if not self.main.sb_conta_receber_nro_parcelas.value():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "NRO PARCELAS" deve ser informado.')
            return None

        if not self.main.cb_conta_receber_cliente.currentText():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "CLIENTE" deve ser informado.')
            return None
        
        if not session.query(Cliente).filter_by(nome=self.main.cb_conta_receber_cliente.currentText()).first():
            QMessageBox.warning(self.main,  "Aviso", f'"CLIENTE" {self.main.cb_conta_receber_cliente.currentText()} não cadastrado.')
            session.close()
            return None

        if not self.main.conta_receber_descricao.text():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "DESCRIÇÃO" deve ser informado.')
            return None

        if not self.main.cb_conta_receber_centro_custo.currentText():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "CENTRO DE CUSTO" deve ser informado.')
            return None

        if not session.query(CentroCusto).filter_by(descricao=self.main.cb_conta_receber_centro_custo.currentText()).first():
            QMessageBox.warning(self.main, "Aviso", f'Centro de Custo: "{self.main.cb_conta_receber_centro_custo.currentText()}" não cadastrado.')
            self.main.cb_conta_receber_centro_custo.setFocus()
            session.close()
            return None
       
        if not self.main.sb_conta_receber_valor_titulo.value():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "VALOR TÍTULO" deve ser informado.')
            return None

        nroParcelas = 1
        if self.main.sb_conta_receber_nro_parcelas.value():
            nroParcelas = self.main.sb_conta_receber_nro_parcelas.value()

        data_inicial = self.main.conta_receber_data_vcto.date().toPython()

        for parcela in range(nroParcelas):

            mes, ano = get_mes_ano_referencia(data_inicial)

            contarec = ContaReceber(

                        descricao = self.main.conta_receber_descricao.text(),
                        referencia =  f'{mes}/{ano} Parcela {parcela+1} de {self.main.sb_conta_receber_nro_parcelas.value()}.',
                        doc_numero = self.main.conta_receber_doc_numero.text(),

                        data_vcto = data_inicial,

                        valor_titulo = self.main.sb_conta_receber_valor_titulo.value(),
                        valor_parcela = round(self.main.sb_conta_receber_valor_titulo.value() / self.main.sb_conta_receber_nro_parcelas.value(), 2),

                        cliente_id = session.query(Cliente.id).filter_by(nome=self.main.cb_conta_receber_cliente.currentText()).first()[0],
                        centro_custo_id = session.query(CentroCusto.id).filter_by(descricao=self.main.cb_conta_receber_centro_custo.currentText()).first()[0])
                
            data_inicial = proximo_mes(data_inicial.day, data_inicial)

            try:
                session.add(contarec)
                session.commit()
            except SQLAlchemyError as err:
                error_message = str(err).split('\n')[0]
                QMessageBox.warning(self.main,  "Erro", f'Não foi possível gerar Contas a Receber.\n{error_message}')
                session.close()
                return None

        session.close()
        self.clear_fields_form_conta_receber()
        self.populate_data_table_conta_receber()
        self.main.forms.setCurrentWidget(self.main.formDataTableContaReceber)
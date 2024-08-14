# coding=utf-8
from qt_core import QMessageBox, QDate

# app
from models import FormaPagto, ContaReceber, getSessionDB, SQLAlchemyError


class DownAccountReceivable:

    def __init__(self, main):
        self.main = main

        # on click button goback
        self.main.btn_goback_conta_receber.clicked.connect(self.on_click_button_goback_conta_receber)

        # on click button save baixar conta receber
        self.main.btn_save_baixar_conta_receber.clicked.connect(self.on_click_button_baixar_conta_receber)


    # on click button goback data table conta receber
    def on_click_button_goback_conta_receber(self, e):
        self.main.forms.setCurrentWidget(self.main.formDataTableContaReceber)


    # set id conta receber
    def set_id_conta_receber(self, idConta):
        self.idConta = idConta

        self.clear_fields_form_baixar_conta_receber()
        self.main.payt_meth.populate_combo_box_forma_pagto()

        session = getSessionDB()
        contarec = session.query(ContaReceber).filter_by(id=idConta).first()

        self.main.lbl_baixar_conta_receber_doc_numero_value.setText(contarec.doc_numero)
        self.main.lbl_baixar_conta_receber_referencia_value.setText(contarec.referencia)
        self.main.lbl_baixar_conta_receber_descricao_value.setText(contarec.descricao)
        self.main.lbl_baixar_conta_receber_cliente_value.setText(contarec.cliente.nome + ' Tel: '  + contarec.cliente.telefone)
        self.main.sb_baixar_conta_receber_valor_pago.setValue(contarec.valor_pago)
        self.main.sb_baixar_conta_receber_valor_parcela.setValue(contarec.valor_parcela)

        self.main.sb_baixar_conta_receber_valor_pago.setFocus()


    # clear fields form conta receber
    def clear_fields_form_baixar_conta_receber(self):
        self.main.lbl_baixar_conta_receber_doc_numero_value.setText('')
        self.main.lbl_baixar_conta_receber_referencia_value.setText('')
        self.main.lbl_baixar_conta_receber_descricao_value.setText('')
        self.main.lbl_baixar_conta_receber_cliente_value.setText('')
        self.main.baixar_conta_receber_data_pagto.setDate(QDate.currentDate())
        self.main.sb_baixar_conta_receber_valor_pago.setValue(0.00)
        self.main.sb_baixar_conta_receber_valor_parcela.setValue(0.00)

  
    # on click button save conta receber
    def on_click_button_baixar_conta_receber(self, e):

        session = getSessionDB()

        if not self.main.cb_baixar_conta_receber_forma_pagto.currentText():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "FORMA PAGAMENTO" deve ser informado.')
            return None

        if not session.query(FormaPagto).filter_by(descricao=self.main.cb_baixar_conta_receber_forma_pagto.currentText()).first():
            QMessageBox.warning(self.main, "Aviso", f'Forma Pagamento: "{self.main.cb_baixar_conta_receber_forma_pagto.currentText()}" não cadastrado.')
            self.main.cb_conta_receber_forma_pagto.setFocus()
            session.close()
            return None
        
        if not self.main.sb_baixar_conta_receber_valor_pago.value():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "VALOR PAGO" deve ser informado.')
            self.main.sb_baixar_conta_receber_valor_pago.setFocus()
            return None

        statusRec = 'Aberto'
        if self.main.sb_baixar_conta_receber_valor_pago.value() >= self.main.sb_baixar_conta_receber_valor_parcela.value():
            statusRec = 'Pago'

        # update conta receber
        contarec = session.query(ContaReceber).filter_by(id=self.idConta).first()
        contarec.status = statusRec
        contarec.data_pagto = self.main.baixar_conta_receber_data_pagto.date().toPython()
        contarec.valor_pago = self.main.sb_baixar_conta_receber_valor_pago.value()
        contarec.forma_pagto_id = session.query(FormaPagto.id).filter_by(descricao=self.main.cb_baixar_conta_receber_forma_pagto.currentText()).first()[0]

        try:
            session.add(contarec)
            session.commit()
        except SQLAlchemyError as err:
            error_message = str(err).split('\n')[0]
            QMessageBox.warning(self.main,  "Erro", f'Não foi baixar Contas a Receber.\n{error_message}')
            session.close()
            return None

        session.close()
        self.clear_fields_form_baixar_conta_receber()
        self.main.account_rec.populate_data_table_conta_receber()
        self.main.forms.setCurrentWidget(self.main.formDataTableContaReceber)
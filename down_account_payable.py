# coding=utf-8
from qt_core import QMessageBox, QDate

# app
from models import FormaPagto, ContaPagar, getSessionDB, SQLAlchemyError


class DownAccountPayable:

    def __init__(self, main):
        self.main = main

        # on click button goback
        self.main.btn_goback_conta_pagar.clicked.connect(self.on_click_button_goback_conta_pagar)

        # on click button save baixar conta pagar
        self.main.btn_save_baixar_conta_pagar.clicked.connect(self.on_click_button_baixar_conta_pagar)


    # on click button goback data table conta pagar
    def on_click_button_goback_conta_pagar(self, e):
        self.main.forms.setCurrentWidget(self.main.formDataTableContaPagar)


    # set id conta pagar
    def set_id_conta_pagar(self, idConta):
        self.idConta = idConta

        self.clear_fields_form_baixar_conta_pagar()
        self.main.payt_meth.populate_combo_box_forma_pagto()

        session = getSessionDB()
        contapag = session.query(ContaPagar).filter_by(id=idConta).first()

        self.main.lbl_baixar_conta_pagar_doc_numero_value.setText(contapag.doc_numero)
        self.main.lbl_baixar_conta_pagar_referencia_value.setText(contapag.referencia)
        self.main.lbl_baixar_conta_pagar_descricao_value.setText(contapag.descricao)
        self.main.lbl_baixar_conta_pagar_fornecedor_value.setText(contapag.fornecedor.nome + ' Tel: '  + contapag.fornecedor.telefone)
        self.main.sb_baixar_conta_pagar_valor_pago.setValue(contapag.valor_pago)
        self.main.sb_baixar_conta_pagar_valor_parcela.setValue(contapag.valor_parcela)

        self.main.sb_baixar_conta_pagar_valor_pago.setFocus()


    # clear fields form conta pagar
    def clear_fields_form_baixar_conta_pagar(self):
        self.main.lbl_baixar_conta_pagar_doc_numero_value.setText('')
        self.main.lbl_baixar_conta_pagar_referencia_value.setText('')
        self.main.lbl_baixar_conta_pagar_descricao_value.setText('')
        self.main.lbl_baixar_conta_pagar_fornecedor_value.setText('')
        self.main.baixar_conta_pagar_data_pagto.setDate(QDate.currentDate())
        self.main.sb_baixar_conta_pagar_valor_pago.setValue(0.00)
        self.main.sb_baixar_conta_pagar_valor_parcela.setValue(0.00)

  
    # on click button save conta pagar
    def on_click_button_baixar_conta_pagar(self, e):

        session = getSessionDB()

        if not self.main.cb_baixar_conta_pagar_forma_pagto.currentText():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "FORMA PAGAMENTO" deve ser informado.')
            return None

        if not session.query(FormaPagto).filter_by(descricao=self.main.cb_baixar_conta_pagar_forma_pagto.currentText()).first():
            QMessageBox.warning(self.main, "Aviso", f'Forma Pagamento: "{self.main.cb_baixar_conta_pagar_forma_pagto.currentText()}" não cadastrado.')
            self.main.cb_baixar_conta_pagar_forma_pagto.setFocus()
            session.close()
            return None
        
        if not self.main.sb_baixar_conta_pagar_valor_pago.value():
            QMessageBox.warning(self.main,  "Aviso", 'O campo: "VALOR PAGO" deve ser informado.')
            self.main.sb_baixar_conta_pagar_valor_pago.setFocus()
            return None

        statusRec = 'Aberto'
        if self.main.sb_baixar_conta_pagar_valor_pago.value() >= self.main.sb_baixar_conta_pagar_valor_parcela.value():
            statusRec = 'Pago'

        # update conta pagar
        contapag = session.query(ContaPagar).filter_by(id=self.idConta).first()
        contapag.status = statusRec
        contapag.data_pagto = self.main.baixar_conta_pagar_data_pagto.date().toPython()
        contapag.valor_pago = self.main.sb_baixar_conta_pagar_valor_pago.value()
        contapag.forma_pagto_id = session.query(FormaPagto.id).filter_by(descricao=self.main.cb_baixar_conta_pagar_forma_pagto.currentText()).first()[0]

        try:
            session.add(contapag)
            session.commit()

        except SQLAlchemyError as err:
            error_message = str(err).split('\n')[0]
            QMessageBox.warning(self.main,  "Erro", f'Não foi baixar Contas a Receber.\n{error_message}')
            session.close()
            return None

        session.close()
        self.clear_fields_form_baixar_conta_pagar()
        self.main.account_pay.populate_data_table_conta_pagar()
        self.main.forms.setCurrentWidget(self.main.formDataTableContaPagar)
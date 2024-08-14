# coding=utf-8
import copy
from qt_core import QMessageBox, QTableWidgetItem, QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QIcon, QWidget, Qt, QCheckBox

# app
from utils import set_table_row_color
from models import FormaPagto, getSessionDB, SQLAlchemyError



class FormFormaPagto(QDialog):
    def __init__(self, main, parent, forma_pagto_id=None):
        super().__init__()
        self.main = main
        self.parent = parent
        self.forma_pagto_id = forma_pagto_id
        
        if self.forma_pagto_id is None:
            self.flagDataSet = 'Insert'
            self.setWindowTitle("Incluir Forma de Pagamento")
        else:
            self.flagDataSet = 'Edit'
            self.setWindowTitle("Alterar Forma de Pagamento")

        colMaster = QVBoxLayout()
        col = QVBoxLayout()
        row = QHBoxLayout()

        self.label = QLabel('DESCRIÇÃO FORMA PAGAMENTO')
        self.label.setStyleSheet(
                                """
                                    font: 700 10pt "Arial";
                                """)

        self.descricao = QLineEdit()
        self.descricao.setMinimumWidth(350)
        self.descricao.setMinimumHeight(25)
        self.descricao.setStyleSheet(
                                    """
                                    background-color: #4fc2f7;
                                    font: 12pt "Arial";
                                    color: rgb(255, 255, 255);
                                    border:none;
                                    border-radius: 2px;
                                    """)

        col.addWidget(self.label)
        col.addWidget(self.descricao)

        self.checkAtivo = QCheckBox('Ativo', checked=True)
        self.checkAtivo.setMinimumHeight(25)
        self.checkAtivo.setStyleSheet(""" font: 12pt "Arial"; """)
      
        self.btn_save_forma_pagto = QPushButton(QIcon("./icons/iconSave.png"), "Salvar")
        self.btn_save_forma_pagto.setMinimumHeight(30)
        self.btn_save_forma_pagto.setStyleSheet(
                                    """
                                    QPushButton {
                                        font: 10pt "Arial";
                                        background-color: #7AB32E;
                                        color: #FFF;
                                    }
                                    QPushButton:hover{
                                        background-color: rgb(0, 170, 0);
                                    }
                                    """
                                    )

        row.addWidget(self.btn_save_forma_pagto)
        self.btn_save_forma_pagto.clicked.connect(self.on_click_button_save_forma_pagto)

        self.btn_close_form = QPushButton(QIcon("./icons/iconExit.png"), "Fechar")
        self.btn_close_form.setMinimumHeight(30)
        self.btn_close_form.setStyleSheet(
                                    """
                                    QPushButton {
                                        font: 10pt "Arial";
                                        background-color: rgb(253, 115, 163);
                                        color: #FFF;
                                    }
                                    QPushButton:hover{
                                        background-color: rgb(255, 0, 0);    
                                    }
                                    """
                                    )

        row.addWidget(self.btn_close_form)
        self.btn_close_form.clicked.connect(self.on_click_button_close_form_forma_pagto)

        colMaster.addLayout(col)
        colMaster.addWidget(self.checkAtivo)
        colMaster.addLayout(row)
        self.setLayout(colMaster)

        if self.flagDataSet == 'Edit':
            session = getSessionDB()
            formap = session.query(FormaPagto).filter_by(id=self.forma_pagto_id).first()
            self.descricao.setText(formap.descricao)
            self.checkAtivo.setChecked(formap.ativo)
            session.close()


    # on click button save forma_pagto
    def on_click_button_save_forma_pagto(self, e):
        
        if not self.descricao.text():
            QMessageBox.warning(self.main, "Aviso", "Descrição da Forma de Pagamento deve ser informada.")
            self.descricao.setFocus()
            return None

        session = getSessionDB()

        if self.flagDataSet == 'Edit':
            formap = session.query(FormaPagto).filter_by(id=self.forma_pagto_id).first()
            oldFormaPgto = copy.deepcopy(formap.descricao)
            formap.descricao = self.descricao.text()
            formap.ativo = self.checkAtivo.isChecked()
        else:
            formap = FormaPagto(
                descricao = self.descricao.text(),
                ativo = self.checkAtivo.isChecked()
                )

        try:
            session.add(formap)
            session.commit()

            if self.flagDataSet == 'Edit':
                QMessageBox.information(self.main, "Sucesso", f'Forma de Pagamento: "{oldFormaPgto}" alterada com sucesso.')
                self.parent.populate_combo_box_forma_pagto()
                self.parent.populate_table_forma_pagto()

            else:
                QMessageBox.information(self.main, "Sucesso", f'Forma de Pagamento: "{self.descricao.text()}" cadastrada com sucesso.')
                self.parent.populate_combo_box_forma_pagto()
                self.parent.populate_table_forma_pagto()

                self.main.cb_baixar_conta_receber_forma_pagto.setCurrentText(self.descricao.text())
                self.main.cb_baixar_conta_pagar_forma_pagto.setCurrentText(self.descricao.text())
                self.main.cb_compra_forma_pagto.setCurrentText(self.descricao.text())
                self.main.cb_venda_forma_pagto.setCurrentText(self.descricao.text())


        except SQLAlchemyError as err:
            error_message = str(err).split('\n')[0]

            if self.flagDataSet == 'Edit':
                QMessageBox.warning(self.main, "Erro", f'Não foi possível fazer a alteração da Forma de Pagamento: "{oldFormaPgto}"\n{error_message}.')
            else:
                QMessageBox.warning(self.main, "Erro", f'Não foi possível fazer a inclusão da Forma de Pagamento: "{self.descricao.text()}"\n{error_message}.')
            session.close()
            return None

        session.close()
        self.close()


    # on click button close form
    def on_click_button_close_form_forma_pagto(self, e):
        self.close()


   
class PaymentMethod:

    def __init__(self, main):
        self.main = main

        # button form forma_pagto (baixar conta receber)
        self.main.btn_form_forma_pagto_baixar_conta_receber.clicked.connect(self.on_click_button_form_forma_pagto_conta_receber)

        # button form forma_pagto (baixar conta pagar)
        self.main.btn_form_forma_pagto_baixar_conta_pagar.clicked.connect(self.on_click_button_form_forma_pagto_conta_pagar)

        # button form forma_pagto (compra)
        self.main.btn_form_forma_pagto_compra.clicked.connect(self.on_click_button_form_forma_pagto_compra)
        
        # button form forma_pagto (venda)
        self.main.btn_form_forma_pagto_venda.clicked.connect(self.on_click_button_form_forma_pagto_venda)

        # button search forma_pagto
        self.main.btn_search_forma_pagto.clicked.connect(self.on_click_button_search_forma_pagto)

        # button refresh table forma_pagto
        self.main.btn_refresh_table_forma_pagto.clicked.connect(self.on_click_button_refresh_table_forma_pagto)
        
        # button add forma_pagto
        self.main.btn_add_forma_pagto.clicked.connect(self.on_click_button_add_forma_pagto)

        # button goback form
        self.main.btn_forma_pagto_goback_form.clicked.connect(self.on_click_button_goback_form)


    # on click button form forma_pagto (conta receber)
    def on_click_button_form_forma_pagto_conta_receber(self, e):

        self.goback_form ='ContaReceber'

        self.populate_table_forma_pagto()

        self.main.forma_pagto_descricao.setFocus()

        self.main.forms.setCurrentWidget(self.main.formDataTableFormaPagto)


    # on click button form forma_pagto (conta pagar)
    def on_click_button_form_forma_pagto_conta_pagar(self, e):

        self.goback_form ='ContaPagar'

        self.populate_table_forma_pagto()

        self.main.forma_pagto_descricao.setFocus()

        self.main.forms.setCurrentWidget(self.main.formDataTableFormaPagto)


    # on click button form forma_pagto (compra)
    def on_click_button_form_forma_pagto_compra(self, e):

        self.goback_form ='Compra'

        self.populate_table_forma_pagto()

        self.main.forma_pagto_descricao.setFocus()

        self.main.forms.setCurrentWidget(self.main.formDataTableFormaPagto)


    # on click button form forma_pagto (venda)
    def on_click_button_form_forma_pagto_venda(self, e):

        self.goback_form ='Venda'

        self.populate_table_forma_pagto()

        self.main.forma_pagto_descricao.setFocus()

        self.main.forms.setCurrentWidget(self.main.formDataTableFormaPagto)


    # on click button search forma_pagto
    def on_click_button_search_forma_pagto(self, e):
        if not self.main.forma_pagto_descricao.text():
            QMessageBox.warning(self.main, "Erro", 'Campo "DESCRIÇÃO FORMA DE PAGAMENTO" deve ser informado.')
            self.main.forma_pagto_descricao.setFocus()
            return None
        self.populate_table_forma_pagto(flagQueryByUser=True)


    # on click button add forma_pagto
    def on_click_button_add_forma_pagto(self, e):
        formPagto = FormFormaPagto(self.main, self)
        formPagto.exec()


    # on click button refresh table forma_pagto
    def on_click_button_refresh_table_forma_pagto(self, e):
        self.populate_table_forma_pagto()


    # on click button goback form
    def on_click_button_goback_form(self, e):
        
        # form compra
        if self.goback_form == 'Compra':
            self.main.forms.setCurrentWidget(self.main.formCadastroCompra)

        # form venda
        elif self.goback_form == 'Venda':
            self.main.forms.setCurrentWidget(self.main.formCadastroVenda)

        # form conta receber
        elif self.goback_form == 'ContaReceber':
            self.main.forms.setCurrentWidget(self.main.formBaixarContaReceber)

        # form conta pagar
        elif self.goback_form == 'ContaPagar':
            self.main.forms.setCurrentWidget(self.main.formBaixarContaPagar)


    # populate combo box forma pagto
    def populate_combo_box_forma_pagto(self):
        session = getSessionDB()
        formPagto = session.query(FormaPagto).filter_by(ativo=True).order_by(FormaPagto.descricao.asc()).all()
        
        self.main.cb_baixar_conta_receber_forma_pagto.clear()
        self.main.cb_baixar_conta_pagar_forma_pagto.clear()
        self.main.cb_compra_forma_pagto.clear()
        self.main.cb_venda_forma_pagto.clear()

        for frm_pgto in formPagto:
            self.main.cb_baixar_conta_receber_forma_pagto.addItem(frm_pgto.descricao)
            self.main.cb_baixar_conta_pagar_forma_pagto.addItem(frm_pgto.descricao)
            self.main.cb_compra_forma_pagto.addItem(frm_pgto.descricao)
            self.main.cb_venda_forma_pagto.addItem(frm_pgto.descricao)

        self.main.cb_baixar_conta_receber_forma_pagto.setCurrentIndex(-1)
        self.main.cb_baixar_conta_pagar_forma_pagto.setCurrentIndex(-1)
        self.main.cb_compra_forma_pagto.setCurrentIndex(-1)
        self.main.cb_venda_forma_pagto.setCurrentIndex(-1)

        session.close()


    # populate table forma_pagto
    def populate_table_forma_pagto(self, flagQueryByUser=False):

        session = getSessionDB()
        if not flagQueryByUser:
            form_pgto = session.query(FormaPagto).order_by(FormaPagto.descricao.asc()).all()
        else:
            form_pgto = session.query(FormaPagto).filter(FormaPagto.descricao.like(f'%{self.main.forma_pagto_descricao.text()}%')).order_by(FormaPagto.descricao.asc()).all()

        # config data table
        self.main.dt_Forma_Pagto.setRowCount(len(form_pgto))
        self.main.dt_Forma_Pagto.setColumnCount(4)
        self.main.dt_Forma_Pagto.setColumnWidth(2, 300)
        
        # insert data
        for row, frm_pgto in enumerate(form_pgto):

            buttonContainer = QWidget()
            rowButtons = QHBoxLayout(buttonContainer)

            # button edit
            edit_button = QPushButton(QIcon("./icons/iconEdit.png"), "")
            edit_button.setToolTip("Editar Categoria")
            edit_button.setMinimumWidth(25)
            edit_button.setMinimumHeight(25)
            edit_button.clicked.connect(lambda checked, row=row: self.on_click_button_edit_forma_pagto(row))

            rowButtons.addWidget(edit_button)

            # button delete
            delete_button = QPushButton(QIcon("./icons/iconTrash.png"), "")
            delete_button.setToolTip("Excluir Categoria")
            delete_button.setMinimumWidth(25)
            delete_button.setMinimumHeight(25)
            delete_button.clicked.connect(lambda checked, row=row: self.on_click_button_delete_forma_pagto(row))

            rowButtons.addWidget(delete_button)
            rowButtons.setContentsMargins(0, 0, 0, 0)
            
            # buttons edit delete
            self.main.dt_Forma_Pagto.setCellWidget(row, 0, buttonContainer)

            # ID
            itemId = QTableWidgetItem(str(frm_pgto.id))
            self.main.dt_Forma_Pagto.setItem(row, 1, itemId)
            itemId.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # descrição forma_pagto
            self.main.dt_Forma_Pagto.setItem(row, 2, QTableWidgetItem(str(frm_pgto.descricao)))

            # ativo
            lblAtivo = 'Não'
            if frm_pgto.ativo:
                lblAtivo = 'Sim'
            self.main.dt_Forma_Pagto.setItem(row, 3, QTableWidgetItem(lblAtivo))

            # color table row
            set_table_row_color(row, self.main.dt_Forma_Pagto, ativo=frm_pgto.ativo)

        # close session
        session.close()


    # on click button edit forma_pagto
    def on_click_button_edit_forma_pagto(self, row):
                                    
        frm_pgto_id = int(self.main.dt_Forma_Pagto.item(row, 1).text())
        formPagto = FormFormaPagto(self.main, self, frm_pgto_id)
        formPagto.exec()
       

    # on click button delete forma_pagto
    def on_click_button_delete_forma_pagto(self, row):
        idForma = int(self.main.dt_Forma_Pagto.item(row, 1).text())
        session = getSessionDB()
        frm_pgto = session.query(FormaPagto).filter_by(id=idForma).first()
        
        if QMessageBox.question(self.main, 'Excluir Forma de Pagamento', f'Tem certeza que deseja excluir a Forma de Pagamento: "{frm_pgto.descricao}"?',
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            try:
                frm_pgto.ativo=False
                session.add(frm_pgto)
                session.commit()
                QMessageBox.information(self.main, 'Sucesso', f'Forma de Pagamento: "{frm_pgto.descricao}" excluída com sucesso.')

            except SQLAlchemyError as err:
                error_message = str(err).split('\n')[0]

                QMessageBox.warning(self.main, 'Erro', f'Forma de Pagamento: "{frm_pgto.descricao}" não pode ser excluída\n{error_message}.')

        session.close()
        self.populate_table_forma_pagto()
        self.populate_combo_box_forma_pagto()

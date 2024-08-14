# coding=utf-8
import copy
from pycpfcnpj import cpfcnpj
import brazilcep
from qt_core import QTableWidgetItem, QMessageBox, QPushButton, QIcon, QComboBox

# app
from utils import set_table_row_color, validate_cep, validate_email
from models import Fornecedor, getSessionDB, SQLAlchemyError


# Fornecedor
class Supplier:

    def __init__(self, main):
        self.main = main

        # flag dataSet
        self.flagDataSet=None

        # on click button fornecedor menu
        self.main.btn_form_fornecedor.clicked.connect(self.on_click_button_form_data_table_fornecedor)

        # on click button search fornecedor
        self.main.btn_search_fornecedor.clicked.connect(self.on_click_button_search_fornecedor)

        # button add fornecedor
        self.main.btn_add_fornecedor.clicked.connect(self.on_click_button_add_fornecedor)

        # button save fornecedor
        self.main.btn_save_fornecedor.clicked.connect(self.on_click_button_save_fornecedor)

        # button refresh data table fornecedor
        self.main.btn_refresh_data_table_fornecedor.clicked.connect(self.on_click_button_refresh_data_table_fornecedor)

        # button goback fornecedor
        self.main.btn_goback_fornecedor.clicked.connect(self.on_click_button_goback_form_data_table_fornecedor)

        # button search cep
        self.main.btn_search_cep_fornecedor.clicked.connect(self.on_click_button_search_fornecedor_cep)



    # clear fields form fornecedor
    def clear_form_fornecedor(self):
        self.main.id_fornecedor.setText('')
        self.main.fornecedor_nome.setText('')
        self.main.razao_social.setText('')
        self.main.cnpj.setText('')
        self.main.inscricao_estadual.setText('')
        self.main.fornecedor_telefone.setText('')
        self.main.fornecedor_email.setText('')
        self.main.fornecedor_site.setText('')
        self.main.fornecedor_observacao.setText('')
        self.main.fornecedor_cep.setText('')
        self.main.fornecedor_rua.setText('')
        self.main.fornecedor_nro.setText('')
        self.main.fornecedor_bairro.setText('')
        self.main.fornecedor_cidade.setText('')
        self.main.fornecedor_estado.setText('')
        self.main.fornecedor_complemento.setText('')
        self.main.chk_fornecedor_ativo.setChecked(True)


    # on click button refresh data table fornecedor
    def on_click_button_refresh_data_table_fornecedor(self, e):
        self.populate_table_fornecedor()


    # on click button search fornecedor
    def on_click_button_search_fornecedor(self, e):

        if not self.main.search_fornecedor.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "NOME FORNECEDOR" deve ser informado.')
            self.main.search_fornecedor.setFocus()
            return None

        self.populate_table_fornecedor(flagQueryByUser=True)


    # on change stacked form
    def on_click_button_add_fornecedor(self, e):

        self.flagDataSet = 'Insert'

        self.main.lbl_title_cadastro_fornecedor.setText('Cadastro de Fornecedor')

        self.clear_form_fornecedor()

        self.main.fornecedor_nome.setFocus()

        self.main.forms.setCurrentWidget(self.main.formCadastroFornecedor)


    # on click button form data table fornecedor
    def on_click_button_form_data_table_fornecedor(self, e):
        
        self.populate_table_fornecedor()

        self.main.search_fornecedor.setFocus()

        self.main.forms.setCurrentWidget(self.main.formDataTableFornecedor)


    # on click button goback form data table fornecedor
    def on_click_button_goback_form_data_table_fornecedor(self, e):

        self.main.forms.setCurrentWidget(self.main.formDataTableFornecedor)


    # on click button search fornecedor cep
    def on_click_button_search_fornecedor_cep(self, e):
        if not validate_cep(self.main.fornecedor_cep.text()):
            QMessageBox.warning(self.main, "Aviso", 'Campo: "CEP" no formato inválido.')
            self.main.fornecedor_cep.setFocus()
            return None
        
        try:
            cep = brazilcep.get_address_from_cep(self.main.fornecedor_cep.text())
        except:
            QMessageBox.warning(self.main, "Aviso", 'CEP não localizado.')
            self.main.fornecedor_cep.setFocus()
            return None

        self.main.fornecedor_rua.setText(cep['street'])
        self.main.fornecedor_bairro.setText(cep['district'])
        self.main.fornecedor_cidade.setText(cep['city'])
        self.main.fornecedor_estado.setText(cep['uf'])
        self.main.fornecedor_complemento.setText(cep['complement'])
        self.main.fornecedor_nro.setFocus()


    # populate combo box fornecedor
    def populate_combo_box_fornecedor(self):
        session = getSessionDB()
        fornec = session.query(Fornecedor).filter_by(ativo=True).order_by(Fornecedor.nome.asc()).all()
        
        self.main.cb_compra_fornecedor.clear()
        self.main.cb_conta_pagar_fornecedor.clear()

        for forn in fornec:
            self.main.cb_compra_fornecedor.addItem(forn.nome)
            self.main.cb_conta_pagar_fornecedor.addItem(forn.nome)

        self.main.cb_compra_fornecedor.setCurrentIndex(-1)
        self.main.cb_conta_pagar_fornecedor.setCurrentIndex(-1)
        session.close()


    # populate table fornecedor
    def populate_table_fornecedor(self, flagQueryByUser=None):
        session = getSessionDB()

        if flagQueryByUser:
            fornecedor = session.query(Fornecedor).filter(Fornecedor.nome.like(f'%{self.main.search_fornecedor.text()}%'), Fornecedor.id != 1).order_by(Fornecedor.nome.asc()).all()
        else:
            fornecedor = session.query(Fornecedor).filter(Fornecedor.id != 1).order_by(Fornecedor.nome.asc()).all()

        # config data table
        self.main.dt_Fornecedor.setRowCount(len(fornecedor))
        self.main.dt_Fornecedor.setColumnCount(19)
        self.main.dt_Fornecedor.setColumnWidth(0, 70)
        self.main.dt_Fornecedor.setColumnWidth(1, 70)
        self.main.dt_Fornecedor.setColumnWidth(2, 40)
        self.main.dt_Fornecedor.setColumnWidth(3, 250)
        self.main.dt_Fornecedor.setColumnWidth(4, 450)

        # insert data
        for row, fornec in enumerate(fornecedor):

            # button edit
            edit_button = QPushButton(QIcon("./icons/iconEdit.png"), "")
            edit_button.setToolTip("Editar Fornecedor")
            edit_button.setMinimumWidth(25)
            edit_button.setMinimumHeight(25)
            edit_button.clicked.connect(lambda checked, row=row: self.on_click_button_edit_fornecedor(row))

            # button delete
            delete_button = QPushButton(QIcon("./icons/iconTrash.png"), "")
            delete_button.setToolTip("Excluir Fornecedor")
            delete_button.setMinimumWidth(25)
            delete_button.setMinimumHeight(25)
            delete_button.clicked.connect(lambda checked, row=row: self.on_click_button_delete_fornecedor(row))

            # buttons edit delete
            self.main.dt_Fornecedor.setCellWidget(row, 0, edit_button)
            self.main.dt_Fornecedor.setCellWidget(row, 1, delete_button)

            self.main.dt_Fornecedor.setItem(row, 2, QTableWidgetItem(str(fornec.id)))
            self.main.dt_Fornecedor.setItem(row, 3, QTableWidgetItem(str(fornec.nome)))

            if fornec.conta_pagar:
                combo_box_conta_pagar = QComboBox()
                for contapag in fornec.conta_pagar:
                    if 'Status: Aberto' in str(contapag):
                        combo_box_conta_pagar.addItem(str(contapag))
                self.main.dt_Fornecedor.setCellWidget(row, 4, combo_box_conta_pagar)
            
            else:
                self.main.dt_Fornecedor.setItem(row, 4, QTableWidgetItem(''))

            self.main.dt_Fornecedor.setItem(row, 5, QTableWidgetItem(str(fornec.telefone)))
            self.main.dt_Fornecedor.setItem(row, 6, QTableWidgetItem(str(fornec.cnpj)))
            self.main.dt_Fornecedor.setItem(row, 7, QTableWidgetItem(str(fornec.inscricao_estadual)))
            self.main.dt_Fornecedor.setItem(row, 8, QTableWidgetItem(str(fornec.email)))
            self.main.dt_Fornecedor.setItem(row, 9, QTableWidgetItem(str(fornec.site)))
            self.main.dt_Fornecedor.setItem(row, 10, QTableWidgetItem(str(fornec.cep)))
            self.main.dt_Fornecedor.setItem(row, 11, QTableWidgetItem(str(fornec.rua)))
            self.main.dt_Fornecedor.setItem(row, 12, QTableWidgetItem(str(fornec.numero)))
            self.main.dt_Fornecedor.setItem(row, 13, QTableWidgetItem(str(fornec.bairro)))
            self.main.dt_Fornecedor.setItem(row, 14, QTableWidgetItem(str(fornec.cidade)))
            self.main.dt_Fornecedor.setItem(row, 15, QTableWidgetItem(str(fornec.estado)))
            self.main.dt_Fornecedor.setItem(row, 16, QTableWidgetItem(str(fornec.complemento)))
            self.main.dt_Fornecedor.setItem(row, 17, QTableWidgetItem(str(fornec.observacao)))

            lblAtivo = 'Sim'
            if not fornec.ativo:
                lblAtivo = 'Não'
                delete_button.setDisabled(True)
            self.main.dt_Fornecedor.setItem(row, 18, QTableWidgetItem(lblAtivo))

            set_table_row_color(row, self.main.dt_Fornecedor, ativo=fornec.ativo)

        # close session
        session.close()


    # on click button edit fornecedor
    def on_click_button_edit_fornecedor(self, row):

        self.flagDataSet = 'Edit'

        self.main.lbl_title_cadastro_fornecedor.setText('Alterar Fornecedor')

        idFornec = int(self.main.dt_Fornecedor.item(row, 2).text())
        session = getSessionDB()
        fornec = session.query(Fornecedor).filter_by(id=idFornec).first()

        self.main.id_fornecedor.setText(str(fornec.id))
        self.oldFornecedorNome = copy.deepcopy(fornec.nome)
        self.main.fornecedor_nome.setText(fornec.nome)
        self.main.razao_social.setText(fornec.razao_social)
        self.main.cnpj.setText(fornec.cnpj)
        self.main.inscricao_estadual.setText(fornec.inscricao_estadual)
        self.main.fornecedor_telefone.setText(fornec.telefone)
        self.main.fornecedor_email.setText(fornec.email)
        self.main.fornecedor_site.setText(fornec.site)
        self.main.fornecedor_observacao.setText(fornec.observacao)
        self.main.fornecedor_cep.setText(fornec.cep)
        self.main.fornecedor_rua.setText(fornec.rua)
        self.main.fornecedor_nro.setText(fornec.numero)
        self.main.fornecedor_bairro.setText(fornec.bairro)
        self.main.fornecedor_cidade.setText(fornec.cidade)
        self.main.fornecedor_estado.setText(fornec.estado)
        self.main.fornecedor_complemento.setText(fornec.complemento)
        self.main.chk_fornecedor_ativo.setChecked(fornec.ativo)

        session.close()

        # change stack
        self.main.forms.setCurrentWidget(self.main.formCadastroFornecedor)


    # on click button delete fornecedor
    def on_click_button_delete_fornecedor(self, row):
        idFornec = int(self.main.dt_Fornecedor.item(row, 2).text())
        session = getSessionDB()
        fornec = session.query(Fornecedor).filter_by(id=idFornec).first()
        
        if QMessageBox.question(self.main, 'Excluir Fornecedor', f'Tem certeza que deseja excluir o Fornecedor: "{fornec.nome}"?',
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            try:
                fornec.ativo=False
                session.add(fornec)
                session.commit()
                QMessageBox.information(self.main, 'Sucesso', f'Fornecedor: "{fornec.nome}" excluído com sucesso.')

            except BaseException:
                QMessageBox.warning(self.main, 'Erro', f'Fornecedor: "{fornec.nome}" não pode ser excluído.')

        session.close()
        self.populate_combo_box_fornecedor()
        self.populate_table_fornecedor()


    # on click button save fornecedor
    def on_click_button_save_fornecedor(self, e):

        # verify required fields
        if not self.main.fornecedor_nome.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "NOME" deve ser informado.')
            self.main.fornecedor_nome.setFocus()
            return None

        if not self.main.razao_social.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "RAZÃO SOCIAL" deve ser informado.')
            self.main.razao_social.setFocus()
            return None
        
        if not self.main.cnpj.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "CNPJ" deve ser informado.')
            self.main.cnpj.setFocus()
            return None
        
        if not cpfcnpj.validate(self.main.cnpj.text()):
            QMessageBox.warning(self.main, "Aviso", '"CNPJ" inválido.')
            self.main.cnpj.setFocus()
            return None


        if not self.main.inscricao_estadual.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "INSCRIÇÃO ESTADUAL" deve ser informado.')
            self.main.inscricao_estadual.setFocus()
            return None

        if not self.main.fornecedor_telefone.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "TELEFONE" deve ser informado.')
            self.main.fornecedor_telefone.setFocus()
            return None

        if not self.main.fornecedor_email.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "EMAIL" deve ser informado.')
            self.main.fornecedor_email.setFocus()
            return None

        if not validate_email(self.main.fornecedor_email.text()):
            QMessageBox.warning(self.main, "Aviso", '"EMAIL" inválido.')
            self.main.fornecedor_email.setFocus()
            return None

        if not validate_cep(self.main.fornecedor_cep.text()):
            QMessageBox.warning(self.main, "Aviso", '"CEP" inválido.')
            self.main.fornecedor_cep.setFocus()
            return None

        if not self.main.fornecedor_rua.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "RUA" deve ser informado.')
            self.main.fornecedor_rua.setFocus()
            return None

        if not self.main.fornecedor_nro.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "NÚMERO" deve ser informado.')
            self.main.fornecedor_nro.setFocus()
            return None

        if not self.main.fornecedor_bairro.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "BAIRRO" deve ser informado.')
            self.main.fornecedor_bairro.setFocus()
            return None

        if not self.main.fornecedor_cidade.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "CIDADE" deve ser informado.')
            self.main.fornecedor_cidade.setFocus()
            return None

        if not self.main.fornecedor_estado.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "ESTADO" deve ser informado.')
            self.main.fornecedor_estado.setFocus()
            return None

        session = getSessionDB()

        if self.flagDataSet == 'Insert':

            fornecedor = Fornecedor(
                        nome = self.main.fornecedor_nome.text(),
                        razao_social = self.main.razao_social.text(),
                        cnpj = self.main.cnpj.text(),
                        inscricao_estadual = self.main.inscricao_estadual.text(),
                        telefone = self.main.fornecedor_telefone.text(),
                        email = self.main.fornecedor_email.text(),
                        site = self.main.fornecedor_site.text(),
                        observacao = self.main.fornecedor_observacao.text(),
                        cep = self.main.fornecedor_cep.text(),
                        rua = self.main.fornecedor_rua.text(),
                        numero = self.main.fornecedor_nro.text(),
                        bairro = self.main.fornecedor_bairro.text(),
                        cidade = self.main.fornecedor_cidade.text(),
                        estado = self.main.fornecedor_estado.text(),
                        complemento = self.main.fornecedor_complemento.text(),
                        ativo = self.main.chk_fornecedor_ativo.isChecked(),
                        )

        # Save Edit
        else:

            fornecedor = session.query(Fornecedor).filter_by(id=self.main.id_fornecedor.text()).first()

            fornecedor.nome = self.main.fornecedor_nome.text()
            fornecedor.razao_social = self.main.razao_social.text()
            fornecedor.cnpj = self.main.cnpj.text()
            fornecedor.inscricao_estadual = self.main.inscricao_estadual.text()
            fornecedor.telefone = self.main.fornecedor_telefone.text()
            fornecedor.email = self.main.fornecedor_email.text()
            fornecedor.site = self.main.fornecedor_site.text()
            fornecedor.observacao = self.main.fornecedor_observacao.text()
            fornecedor.cep = self.main.fornecedor_cep.text()
            fornecedor.rua = self.main.fornecedor_rua.text()
            fornecedor.numero = self.main.fornecedor_nro.text()
            fornecedor.bairro = self.main.fornecedor_bairro.text()
            fornecedor.cidade = self.main.fornecedor_cidade.text()
            fornecedor.estado = self.main.fornecedor_estado.text()
            fornecedor.complemento = self.main.fornecedor_complemento.text()
            fornecedor.ativo = self.main.chk_fornecedor_ativo.isChecked()

        try:
            session.add(fornecedor)
            session.commit()

            if self.flagDataSet == 'Insert':
                QMessageBox.information(self.main, "Sucesso", f'Fornecedor: "{self.main.fornecedor_nome.text()}" cadastrado com sucesso.')
            else:
                QMessageBox.information(self.main, "Sucesso", f'Fornecedor: "{self.oldFornecedorNome}" alterado com sucesso.')

        except SQLAlchemyError as err:
            error_message = str(err).split('\n')[0]
        
            if self.flagDataSet == 'Insert':
                QMessageBox.warning(self.main, "Erro", f'Não foi possível fazer inclusão do Fornecedor: "{self.main.fornecedor_nome.text()}"\n{error_message}.')
            else:
                QMessageBox.warning(self.main, "Erro", f'Não foi possível fazer alteração do Fornecedor: "{self.oldFornecedorNome}"\n{error_message}.')
            
            session.close()
            return None

        session.close()
        self.flagDataSet = None
        self.clear_form_fornecedor()
        self.populate_table_fornecedor()
        self.populate_combo_box_fornecedor()
        self.main.forms.setCurrentWidget(self.main.formDataTableFornecedor)

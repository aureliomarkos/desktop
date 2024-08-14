# coding=utf-8
import copy
from pycpfcnpj import cpfcnpj
import brazilcep
from qt_core import QTableWidgetItem, QMessageBox, QPushButton, QIcon, QComboBox

# app
from utils import set_table_row_color, validate_cep, validate_email
from models import Cliente, getSessionDB, SQLAlchemyError


# Cliente
class Client:

    def __init__(self, main):
        self.main = main

        # flag dataSet
        self.flagDataSet=None

        # on click button cliente menu
        self.main.btn_form_cliente.clicked.connect(self.on_click_button_form_data_table_cliente)

        # on click button search cliente
        self.main.btn_search_cliente.clicked.connect(self.on_click_button_search_cliente)

        # button add cliente
        self.main.btn_add_cliente.clicked.connect(self.on_click_button_add_cliente)

        # button save cliente
        self.main.btn_save_cliente.clicked.connect(self.on_click_button_save_cliente)

        # button refresh data table cliente
        self.main.btn_refresh_data_table_cliente.clicked.connect(self.on_click_button_refresh_data_table_cliente)

        # button goback cliente
        self.main.btn_goback_cliente.clicked.connect(self.on_click_button_goback_form_data_table_cliente)

        # button search cep
        self.main.btn_search_cep_cliente.clicked.connect(self.on_click_button_search_cliente_cep)



    # clear fields form cliente
    def clear_form_cliente(self):
        self.main.id_cliente.setText('')
        self.main.cliente_nome.setText('')
        self.main.rg.setText('')
        self.main.cpf.setText('')
        self.main.cliente_telefone.setText('')
        self.main.cliente_email.setText('')
        self.main.cliente_observacao.setText('')
        self.main.cliente_cep.setText('')
        self.main.cliente_rua.setText('')
        self.main.cliente_nro.setText('')
        self.main.cliente_bairro.setText('')
        self.main.cliente_cidade.setText('')
        self.main.cliente_estado.setText('')
        self.main.cliente_complemento.setText('')
        self.main.chk_cliente_ativo.setChecked(True)


    # on click button refresh data table cliente
    def on_click_button_refresh_data_table_cliente(self, e):
        self.populate_table_cliente()


    # on click button search cliente
    def on_click_button_search_cliente(self, e):

        if not self.main.search_cliente.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "NOME" deve ser informado.')
            self.main.search_cliente.setFocus()
            return None

        self.populate_table_cliente(flagQueryByUser=True)


    # on change stacked form
    def on_click_button_add_cliente(self, e):

        self.flagDataSet = 'Insert'

        self.main.lbl_title_cadastro_cliente.setText('Cadastro de Cliente')

        self.clear_form_cliente()

        self.main.cliente_nome.setFocus()

        self.main.forms.setCurrentWidget(self.main.formCadastroCliente)


    # on click button form data table cliente
    def on_click_button_form_data_table_cliente(self, e):
        
        self.main.search_cliente.setFocus()

        self.main.forms.setCurrentWidget(self.main.formDataTableCliente)

        self.populate_table_cliente()


    # on click button goback form data table cliente
    def on_click_button_goback_form_data_table_cliente(self, e):

        self.main.forms.setCurrentWidget(self.main.formDataTableCliente)


    # on click button search cliente cep
    def on_click_button_search_cliente_cep(self, e):
        if not validate_cep(self.main.cliente_cep.text()):
            QMessageBox.warning(self.main, "Aviso", 'Campo: "CEP" no formato inválido.')
            self.main.cliente_cep.setFocus()
            return None
        
        try:
            cep = brazilcep.get_address_from_cep(self.main.cliente_cep.text())
        except:
            QMessageBox.warning(self.main, "Aviso", 'CEP não localizado.')
            self.main.cliente_cep.setFocus()
            return None

        self.main.cliente_rua.setText(cep['street'])
        self.main.cliente_bairro.setText(cep['district'])
        self.main.cliente_cidade.setText(cep['city'])
        self.main.cliente_estado.setText(cep['uf'])
        self.main.cliente_complemento.setText(cep['complement'])
        self.main.cliente_nro.setFocus()


    # populate combo box cliente
    def populate_combo_box_cliente(self):
        session = getSessionDB()
        cliente = session.query(Cliente).filter_by(ativo=True).order_by(Cliente.nome.asc()).all()
        
        self.main.cb_conta_receber_cliente.clear()
        self.main.cb_venda_cliente.clear()

        for cli in cliente:
            self.main.cb_conta_receber_cliente.addItem(cli.nome)
            self.main.cb_venda_cliente.addItem(cli.nome)

        self.main.cb_conta_receber_cliente.setCurrentIndex(-1)
        self.main.cb_venda_cliente.setCurrentIndex(-1)
        session.commit()



    # populate table cliente
    def populate_table_cliente(self, flagQueryByUser=None):
        session = getSessionDB()

        if flagQueryByUser:
            cliente = session.query(Cliente).filter(Cliente.nome.like(f'%{self.main.search_cliente.text()}%'), Cliente.id != 1).order_by(Cliente.nome.asc()).all()
        else:
            cliente = session.query(Cliente).filter(Cliente.id != 1).order_by(Cliente.nome.asc()).all()

        # config data table
        self.main.dt_Cliente.setRowCount(len(cliente))
        self.main.dt_Cliente.setColumnCount(18)
        self.main.dt_Cliente.setColumnWidth(0, 70)
        self.main.dt_Cliente.setColumnWidth(1, 70)
        self.main.dt_Cliente.setColumnWidth(2, 40)
        self.main.dt_Cliente.setColumnWidth(3, 250)
        self.main.dt_Cliente.setColumnWidth(4, 450)

        # insert data
        for row, cli in enumerate(cliente):

            # button edit
            edit_button = QPushButton(QIcon("./icons/iconEdit.png"), "")
            edit_button.setToolTip("Editar Cliente")
            edit_button.setMinimumWidth(25)
            edit_button.setMinimumHeight(25)
            edit_button.clicked.connect(lambda checked, row=row: self.on_click_button_edit_cliente(row))

            # button delete
            delete_button = QPushButton(QIcon("./icons/iconTrash.png"), "")
            delete_button.setToolTip("Excluir Cliente")
            delete_button.setMinimumWidth(25)
            delete_button.setMinimumHeight(25)
            delete_button.clicked.connect(lambda checked, row=row: self.on_click_button_delete_cliente(row))

            # buttons edit delete
            self.main.dt_Cliente.setCellWidget(row, 0, edit_button)
            self.main.dt_Cliente.setCellWidget(row, 1, delete_button)

            self.main.dt_Cliente.setItem(row, 2, QTableWidgetItem(str(cli.id)))
            self.main.dt_Cliente.setItem(row, 3, QTableWidgetItem(str(cli.nome)))

            if cli.conta_receber:
                combo_box_conta_receber = QComboBox()
                for contarec in cli.conta_receber:
                    if 'Status: Aberto' in str(contarec):
                        combo_box_conta_receber.addItem(str(contarec))
                self.main.dt_Cliente.setCellWidget(row, 4, combo_box_conta_receber)
            
            else:
                self.main.dt_Cliente.setItem(row, 4, QTableWidgetItem(''))

            self.main.dt_Cliente.setItem(row, 5, QTableWidgetItem(str(cli.telefone)))
            self.main.dt_Cliente.setItem(row, 6, QTableWidgetItem(str(cli.cpf)))
            self.main.dt_Cliente.setItem(row, 7, QTableWidgetItem(str(cli.rg)))
            self.main.dt_Cliente.setItem(row, 8, QTableWidgetItem(str(cli.email)))
            self.main.dt_Cliente.setItem(row, 9, QTableWidgetItem(str(cli.cep)))
            self.main.dt_Cliente.setItem(row, 10, QTableWidgetItem(str(cli.rua)))
            self.main.dt_Cliente.setItem(row, 11, QTableWidgetItem(str(cli.numero)))
            self.main.dt_Cliente.setItem(row, 12, QTableWidgetItem(str(cli.bairro)))
            self.main.dt_Cliente.setItem(row, 13, QTableWidgetItem(str(cli.cidade)))
            self.main.dt_Cliente.setItem(row, 14, QTableWidgetItem(str(cli.estado)))
            self.main.dt_Cliente.setItem(row, 15, QTableWidgetItem(str(cli.complemento)))
            self.main.dt_Cliente.setItem(row, 16, QTableWidgetItem(str(cli.observacao)))

            lblAtivo = 'Sim'
            if not cli.ativo:
                lblAtivo = 'Não'
                delete_button.setDisabled(True)
            self.main.dt_Cliente.setItem(row, 17, QTableWidgetItem(lblAtivo))

            set_table_row_color(row, self.main.dt_Cliente, ativo=cli.ativo)

        # close session
        session.close()


    # on click button edit cliente
    def on_click_button_edit_cliente(self, row):

        self.flagDataSet = 'Edit'

        self.main.lbl_title_cadastro_cliente.setText('Alterar Cliente')

        idCli = int(self.main.dt_Cliente.item(row, 2).text())
        session = getSessionDB()
        cli = session.query(Cliente).filter_by(id=idCli).first()

        self.main.id_cliente.setText(str(cli.id))
        self.oldClienteNome = copy.deepcopy(cli.nome)
        self.main.cliente_nome.setText(cli.nome)
        self.main.rg.setText(cli.rg)
        self.main.cpf.setText(cli.cpf)
        self.main.cliente_telefone.setText(cli.telefone)
        self.main.cliente_email.setText(cli.email)
        self.main.cliente_observacao.setText(cli.observacao)
        self.main.cliente_cep.setText(cli.cep)
        self.main.cliente_rua.setText(cli.rua)
        self.main.cliente_nro.setText(cli.numero)
        self.main.cliente_bairro.setText(cli.bairro)
        self.main.cliente_cidade.setText(cli.cidade)
        self.main.cliente_estado.setText(cli.estado)
        self.main.cliente_complemento.setText(cli.complemento)
        self.main.chk_cliente_ativo.setChecked(cli.ativo)

        session.close()

        # change stack
        self.main.forms.setCurrentWidget(self.main.formCadastroCliente)


    # on click button delete cliente
    def on_click_button_delete_cliente(self, row):
        idCli = int(self.main.dt_Cliente.item(row, 2).text())
        session = getSessionDB()
        cli = session.query(Cliente).filter_by(id=idCli).first()
        
        if QMessageBox.question(self.main, 'Excluir Cliente', f'Tem certeza que deseja excluir o Cliente: "{cli.nome}"?',
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            try:
                cli.ativo=False
                session.add(cli)
                session.commit()
                QMessageBox.information(self.main, 'Sucesso', f'Cliente: "{cli.nome}" excluído com sucesso.')

            except SQLAlchemyError as err:
                error_message = str(err).split('\n')[0]

                QMessageBox.warning(self.main, 'Erro', f'Cliente: "{cli.nome}" não pode ser excluído\n{error_message}.')

        session.close()
        self.populate_table_cliente()
        self.populate_combo_box_cliente()


    # on click button save cliente
    def on_click_button_save_cliente(self, e):

        # verify required fields
        if not self.main.cliente_nome.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "NOME" deve ser informado.')
            self.main.cliente_nome.setFocus()
            return None

        if not self.main.cpf.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "CPF" deve ser informado.')
            self.main.cpf.setFocus()
            return None
        
        if not cpfcnpj.validate(self.main.cpf.text()):
            QMessageBox.warning(self.main, "Aviso", '"CPF" inválido.')
            self.main.cpf.setFocus()
            return None

        if not self.main.cliente_telefone.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "TELEFONE" deve ser informado.')
            self.main.cliente_telefone.setFocus()
            return None

        if not self.main.cliente_email.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "EMAIL" deve ser informado.')
            self.main.cliente_email.setFocus()
            return None

        if not validate_email(self.main.cliente_email.text()):
            QMessageBox.warning(self.main, "Aviso", '"EMAIL" inválido.')
            self.main.cliente_email.setFocus()
            return None

        if not validate_cep(self.main.cliente_cep.text()):
            QMessageBox.warning(self.main, "Aviso", '"CEP" inválido.')
            self.main.cliente_cep.setFocus()
            return None

        if not self.main.cliente_rua.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "RUA" deve ser informado.')
            self.main.cliente_rua.setFocus()
            return None

        if not self.main.cliente_nro.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "NÚMERO" deve ser informado.')
            self.main.cliente_nro.setFocus()
            return None

        if not self.main.cliente_bairro.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "BAIRRO" deve ser informado.')
            self.main.cliente_bairro.setFocus()
            return None

        if not self.main.cliente_cidade.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "CIDADE" deve ser informado.')
            self.main.cliente_cidade.setFocus()
            return None

        if not self.main.cliente_estado.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "ESTADO" deve ser informado.')
            self.main.cliente_estado.setFocus()
            return None

        session = getSessionDB()

        if self.flagDataSet == 'Insert':

            cliente = Cliente(
                        nome = self.main.cliente_nome.text(),
                        cpf = self.main.cpf.text(),
                        rg = self.main.rg.text(),
                        telefone = self.main.cliente_telefone.text(),
                        email = self.main.cliente_email.text(),
                        observacao = self.main.cliente_observacao.text(),
                        cep = self.main.cliente_cep.text(),
                        rua = self.main.cliente_rua.text(),
                        numero = self.main.cliente_nro.text(),
                        bairro = self.main.cliente_bairro.text(),
                        cidade = self.main.cliente_cidade.text(),
                        estado = self.main.cliente_estado.text(),
                        complemento = self.main.cliente_complemento.text(),
                        ativo = self.main.chk_cliente_ativo.isChecked()
                        )

        # Save Edit
        else:

            cliente = session.query(Cliente).filter_by(id=self.main.id_cliente.text()).first()

            cliente.nome = self.main.cliente_nome.text()
            cliente.rg = self.main.rg.text()
            cliente.cpf = self.main.cpf.text()
            cliente.telefone = self.main.cliente_telefone.text()
            cliente.email = self.main.cliente_email.text()
            cliente.observacao = self.main.cliente_observacao.text()
            cliente.cep = self.main.cliente_cep.text()
            cliente.rua = self.main.cliente_rua.text()
            cliente.numero = self.main.cliente_nro.text()
            cliente.bairro = self.main.cliente_bairro.text()
            cliente.cidade = self.main.cliente_cidade.text()
            cliente.estado = self.main.cliente_estado.text()
            cliente.complemento = self.main.cliente_complemento.text()
            cliente.ativo = self.main.chk_cliente_ativo.isChecked()

        try:
            session.add(cliente)
            session.commit()

            if self.flagDataSet == 'Insert':
                QMessageBox.information(self.main, "Sucesso", f'Cliente: "{self.main.cliente_nome.text()}" cadastrado com sucesso.')
            else:
                QMessageBox.information(self.main, "Sucesso", f'Cliente: "{self.oldClienteNome}" alterado com sucesso.')

        except SQLAlchemyError as err:
            error_message = str(err).split('\n')[0]
        
            if self.flagDataSet == 'Insert':
                QMessageBox.warning(self.main, "Erro", f'Não foi possível fazer inclusão do Cliente: "{self.main.cliente_nome.text()}"\n{error_message}.')
            else:
                QMessageBox.warning(self.main, "Erro", f'Não foi possível fazer alteração do Cliente: "{self.oldClienteNome}"\n{error_message}.')
            
            session.close()
            return None

        session.close()
        self.flagDataSet = None
        self.clear_form_cliente()
        self.populate_table_cliente()
        self.populate_combo_box_cliente()
        self.main.forms.setCurrentWidget(self.main.formDataTableCliente)

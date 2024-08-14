# coding=utf-8
import copy
from qt_core import QMessageBox, QTableWidgetItem, QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QIcon, QWidget, Qt, QCheckBox

# app
from utils import set_table_row_color
from models import Marca, getSessionDB, SQLAlchemyError



class FormMarca(QDialog):
    def __init__(self, main, parent, marca_id=None):
        super().__init__()
        self.main = main
        self.parent = parent
        self.marca_id = marca_id
        
        if self.marca_id is None:
            self.flagDataSet = 'Insert'
            self.setWindowTitle("Incluir Marca")
        else:
            self.flagDataSet = 'Edit'
            self.setWindowTitle("Alterar Marca")

        colMaster = QVBoxLayout()
        colDescricao = QVBoxLayout()
        rowButtons = QHBoxLayout()

        self.label = QLabel('DESCRIÇÃO MARCA')
        self.label.setStyleSheet(""" font: 700 10pt "Arial"; """)

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

        colDescricao.addWidget(self.label)
        colDescricao.addWidget(self.descricao)

        # ativo
        self.checkAtivo = QCheckBox('Ativo', checked=True)
        self.checkAtivo.setMinimumHeight(25)
        self.checkAtivo.setStyleSheet(""" font:12pt "Arial"; """)

        self.btn_save_marca = QPushButton(QIcon("./icons/iconSave.png"), "Salvar")
        self.btn_save_marca.setMinimumHeight(30)
        self.btn_save_marca.setStyleSheet(
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

        rowButtons.addWidget(self.btn_save_marca)
        self.btn_save_marca.clicked.connect(self.on_click_button_save_marca)

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

        rowButtons.addWidget(self.btn_close_form)
        self.btn_close_form.clicked.connect(self.on_click_button_close_form_marca)

        colMaster.addLayout(colDescricao)
        colMaster.addWidget(self.checkAtivo)
        colMaster.addLayout(rowButtons)
        self.setLayout(colMaster)

        if self.flagDataSet == 'Edit':
            session = getSessionDB()
            marca = session.query(Marca).filter_by(id=self.marca_id).first()
            self.descricao.setText(marca.descricao)
            self.checkAtivo.setChecked(marca.ativo)
            session.close()


    # on click button save marca
    def on_click_button_save_marca(self, e):
        
        if not self.descricao.text():
            QMessageBox.warning(self.main, "Aviso", "Descrição da Marca deve ser informada.")
            self.descricao.setFocus()
            return None

        session = getSessionDB()

        if self.flagDataSet == 'Edit':
            marca = session.query(Marca).filter_by(id=self.marca_id).first()
            oldMarca = copy.deepcopy(marca.descricao)
            marca.descricao = self.descricao.text()
            marca.ativo = self.checkAtivo.isChecked()
        else:
            marca = Marca(
                descricao = self.descricao.text(),
                ativo = self.checkAtivo.isChecked()
                )

        try:
            session.add(marca)
            session.commit()

            if self.flagDataSet == 'Edit':
                QMessageBox.information(self.main, "Sucesso", f'Marca: "{oldMarca}" alterada com sucesso.')
                self.parent.populate_combo_box_marca()
                self.parent.populate_table_marca()

            else:
                QMessageBox.information(self.main, "Sucesso", f'Marca: "{self.descricao.text()}" cadastrada com sucesso.')
                self.parent.populate_combo_box_marca()
                self.parent.populate_table_marca()
                self.main.cb_marca.setCurrentText(self.descricao.text())

        except SQLAlchemyError as err:
            error_message = str(err).split('\n')[0]
            
            if self.flagDataSet == 'Edit':
                QMessageBox.warning(self.main, "Erro", f'Não foi possível fazer a alteração da Marca: "{oldMarca}"\n{error_message}.')
            else:
                QMessageBox.warning(self.main, "Erro", f'Não foi possível fazer a inclusão da Marca: "{self.descricao.text()}"\n{error_message}.')

            session.close()
            return None

        session.close()
        self.close()


    # on click button close form
    def on_click_button_close_form_marca(self, e):
        self.close()


   
class Brand:

    def __init__(self, main):
        self.main = main

        # button form marca
        self.main.btn_form_marca.clicked.connect(self.on_click_button_form_marca)
        
        # button search marca
        self.main.btn_search_marca.clicked.connect(self.on_click_button_search_marca)

        # button refresh table marca
        self.main.btn_refresh_table_marca.clicked.connect(self.on_click_button_refresh_table_marca)
        
        # button add marca
        self.main.btn_add_marca.clicked.connect(self.on_click_button_add_marca)

        # button goback form produto
        self.main.btn_marca_goback_form_produto.clicked.connect(self.on_click_button_goback_form_produto)
        

    # on click button form marca
    def on_click_button_form_marca(self, e):
       
        self.populate_table_marca()

        self.main.marca_descricao.setFocus()

        self.main.forms.setCurrentWidget(self.main.formDataTableMarca)


    # on click button search marca
    def on_click_button_search_marca(self, e):
        if not self.main.marca_descricao.text():
            QMessageBox.warning(self.main, "Erro", 'Campo "DESCRIÇÃO MARCA" deve ser informado.')
            self.main.marca_descricao.setFocus()
            return None
        self.populate_table_marca(flagQueryByUser=True)


    # on click button add marca
    def on_click_button_add_marca(self, e):
        self.formMarca = FormMarca(self.main, self)
        self.formMarca.exec()


    # on click button refresh table marca
    def on_click_button_refresh_table_marca(self, e):
        self.populate_table_marca()


    # on click button goback form produto
    def on_click_button_goback_form_produto(self, e):
        self.main.forms.setCurrentWidget(self.main.formCadastroProduto)


    # populate combo box marca
    def populate_combo_box_marca(self):

        self.main.cb_marca_relatorio_produto.clear()
        self.main.cb_marca.clear()
        
        session = getSessionDB()
        marcas = session.query(Marca).filter(Marca.ativo==True).order_by(Marca.descricao.asc()).all()

        for marca in marcas:
            self.main.cb_marca_relatorio_produto.addItem(marca.descricao)
            self.main.cb_marca.addItem(marca.descricao)
        
        self.main.cb_marca_relatorio_produto.setCurrentIndex(-1)
        self.main.cb_marca.setCurrentIndex(-1)
        session.close()


    # populate table marca
    def populate_table_marca(self, flagQueryByUser=False):

        session = getSessionDB()
        if not flagQueryByUser:
            marcas = session.query(Marca).order_by(Marca.descricao.asc()).all()
        else:
            marcas = session.query(Marca).filter(Marca.descricao.like(f'%{self.main.marca_descricao.text()}%')).order_by(Marca.descricao.asc()).all()

        # config data table
        self.main.dt_Marca.setRowCount(len(marcas))
        self.main.dt_Marca.setColumnCount(4)
        self.main.dt_Marca.setColumnWidth(2, 300)

        # insert data
        for row, marca in enumerate(marcas):

            buttonContainer = QWidget()
            rowButtons = QHBoxLayout(buttonContainer)

            # button edit
            edit_button = QPushButton(QIcon("./icons/iconEdit.png"), "")
            edit_button.setToolTip("Editar Marca")
            edit_button.setMinimumWidth(25)
            edit_button.setMinimumHeight(25)
            edit_button.clicked.connect(lambda checked, row=row: self.on_click_button_edit_marca(row))

            rowButtons.addWidget(edit_button)

            # button delete
            delete_button = QPushButton(QIcon("./icons/iconTrash.png"), "")
            delete_button.setToolTip("Excluir Marca")
            delete_button.setMinimumWidth(25)
            delete_button.setMinimumHeight(25)
            delete_button.clicked.connect(lambda checked, row=row: self.on_click_button_delete_marca(row))

            rowButtons.addWidget(delete_button)
            rowButtons.setContentsMargins(0, 0, 0, 0)

            # buttons edit delete
            self.main.dt_Marca.setCellWidget(row, 0, buttonContainer)

            # ID
            itemId = QTableWidgetItem(str(marca.id))
            self.main.dt_Marca.setItem(row, 1, itemId)
            itemId.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # descrição marca
            self.main.dt_Marca.setItem(row, 2, QTableWidgetItem(str(marca.descricao)))

            # ativo
            lblAtivo = 'Não'
            if marca.ativo:
                lblAtivo = 'Sim'
            self.main.dt_Marca.setItem(row, 3, QTableWidgetItem(lblAtivo))

            # color table row
            set_table_row_color(row, self.main.dt_Marca, ativo=marca.ativo)

        # close session
        session.close()


    # on click button edit marca
    def on_click_button_edit_marca(self, row):
        marca_id = int(self.main.dt_Marca.item(row, 1).text())
        formMarca = FormMarca(self.main, self, marca_id)
        formMarca.exec()
       

    # on click button delete marca
    def on_click_button_delete_marca(self, row):
        idMarca = int(self.main.dt_Marca.item(row, 1).text())
        session = getSessionDB()
        marca = session.query(Marca).filter_by(id=idMarca).first()
        
        if QMessageBox.question(self.main, 'Excluir Marca', f'Tem certeza que deseja excluir a marca: "{marca.descricao}"?',
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            try:
                marca.ativo=False
                session.add(marca)
                session.commit()
                QMessageBox.information(self.main, 'Sucesso', f'Marca: "{marca.descricao}" excluída com sucesso.')

            except SQLAlchemyError as err:
                error_message = str(err).split('\n')[0]

                QMessageBox.warning(self.main, 'Erro', f'Marca: "{marca.descricao}" não pode ser excluída\n{error_message}.')

        session.close()
        self.populate_table_marca()
        self.populate_combo_box_marca()
            
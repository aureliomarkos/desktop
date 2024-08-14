# coding=utf-8
import copy
from qt_core import QMessageBox, QTableWidgetItem, QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QIcon, QWidget, Qt, QCheckBox


# app
from utils import set_table_row_color
from models import Categoria, getSessionDB, SQLAlchemyError



class FormCategoria(QDialog):
    def __init__(self, main, parent, categoria_id=None):
        super().__init__()
        self.main = main
        self.parent = parent
        self.categoria_id = categoria_id
        
        if self.categoria_id is None:
            self.flagDataSet = 'Insert'
            self.setWindowTitle("Incluir Categoria")
        else:
            self.flagDataSet = 'Edit'
            self.setWindowTitle("Alterar Categoria")

        colMaster = QVBoxLayout()
        col = QVBoxLayout()
        row = QHBoxLayout()

        self.label = QLabel('DESCRIÇÃO CATEGORIA')
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
      
        self.btn_save_categoria = QPushButton(QIcon("./icons/iconSave.png"), "Salvar")
        self.btn_save_categoria.setMinimumHeight(30)
        self.btn_save_categoria.setStyleSheet(
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

        row.addWidget(self.btn_save_categoria)
        self.btn_save_categoria.clicked.connect(self.on_click_button_save_categoria)

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
        self.btn_close_form.clicked.connect(self.on_click_button_close_form_categoria)

        colMaster.addLayout(col)
        colMaster.addWidget(self.checkAtivo)
        colMaster.addLayout(row)
        self.setLayout(colMaster)

        if self.flagDataSet == 'Edit':
            session = getSessionDB()
            categ = session.query(Categoria).filter_by(id=self.categoria_id).first()
            self.descricao.setText(categ.descricao)
            self.checkAtivo.setChecked(categ.ativo)
            session.close()


    # on click button save categoria
    def on_click_button_save_categoria(self, e):
        
        if not self.descricao.text():
            QMessageBox.warning(self.main, "Aviso", "Descrição da Categoria deve ser informada.")
            self.descricao.setFocus()
            return None

        session = getSessionDB()

        if self.flagDataSet == 'Edit':
            categ = session.query(Categoria).filter_by(id=self.categoria_id).first()
            oldCateg = copy.deepcopy(categ.descricao)
            categ.descricao = self.descricao.text()
            categ.ativo = self.checkAtivo.isChecked()
        else:
            categ = Categoria(
                descricao = self.descricao.text(),
                ativo = self.checkAtivo.isChecked()
                )

        try:
            session.add(categ)
            session.commit()

            if self.flagDataSet == 'Edit':
                QMessageBox.information(self.main, "Sucesso", f'Categoria: "{oldCateg}" alterada com sucesso.')
                self.parent.populate_combo_box_categoria()
                self.parent.populate_table_categoria()

            else:
                QMessageBox.information(self.main, "Sucesso", f'Categoria: "{self.descricao.text()}" cadastrada com sucesso.')
                self.parent.populate_combo_box_categoria()
                self.parent.populate_table_categoria()
                self.main.cb_categoria.setCurrentText(self.descricao.text())


        except SQLAlchemyError as err:
            error_message = str(err).split('\n')[0]

            if self.flagDataSet == 'Edit':
                QMessageBox.warning(self.main, "Erro", f'Não foi possível fazer a alteração da Categoria: "{oldCateg}"\n{error_message}.')
            else:
                QMessageBox.warning(self.main, "Erro", f'Não foi possível fazer a inclusão da Categoria: "{self.descricao.text()}"\n{error_message}.')
            session.close()
            return None

        session.close()
        self.close()


    # on click button close form
    def on_click_button_close_form_categoria(self, e):
        self.close()


   
class Category:

    def __init__(self, main):
        self.main = main

        # button form categoria
        self.main.btn_form_categoria.clicked.connect(self.on_click_button_form_categoria)
        
        # button search categoria
        self.main.btn_search_categoria.clicked.connect(self.on_click_button_search_categoria)

        # button refresh table categoria
        self.main.btn_refresh_table_categoria.clicked.connect(self.on_click_button_refresh_table_categoria)
        
        # button add categoria
        self.main.btn_add_categoria.clicked.connect(self.on_click_button_add_categoria)

        # button goback form produto
        self.main.btn_categoria_goback_form_produto.clicked.connect(self.on_click_button_goback_form_produto)
        

    # on click button form categoria
    def on_click_button_form_categoria(self, e):
        
        self.main.categoria_descricao.setFocus()

        self.main.forms.setCurrentWidget(self.main.formDataTableCategoria)

        self.populate_table_categoria()
    

    # on click button search categoria
    def on_click_button_search_categoria(self, e):
        if not self.main.categoria_descricao.text():
            QMessageBox.warning(self.main, "Erro", 'Campo "DESCRIÇÃO CATEGORIA" deve ser informado.')
            self.main.categoria_descricao.setFocus()
            return None
        self.populate_table_categoria(flagQueryByUser=True)


    # on click button add categoria
    def on_click_button_add_categoria(self, e):
        formCateg = FormCategoria(self.main, self)
        formCateg.exec()


    # on click button refresh table categoria
    def on_click_button_refresh_table_categoria(self, e):
        self.populate_table_categoria()


    # on click button goback form produto
    def on_click_button_goback_form_produto(self, e):
        self.main.forms.setCurrentWidget(self.main.formCadastroProduto)


    # populate combo box categoria
    def populate_combo_box_categoria(self):

        self.main.cb_categoria_relatorio_produto.clear()
        self.main.cb_categoria.clear()

        session = getSessionDB()
        categorias = session.query(Categoria).filter(Categoria.ativo==True).order_by(Categoria.descricao.asc()).all()

        for categ in categorias:
            self.main.cb_categoria_relatorio_produto.addItem(categ.descricao)
            self.main.cb_categoria.addItem(categ.descricao)

        self.main.cb_categoria_relatorio_produto.setCurrentIndex(-1)
        self.main.cb_categoria.setCurrentIndex(-1)
        session.close()


    # populate table categoria
    def populate_table_categoria(self, flagQueryByUser=False):

        session = getSessionDB()
        if not flagQueryByUser:
            categ = session.query(Categoria).order_by(Categoria.descricao.asc()).all()
        else:
            categ = session.query(Categoria).filter(Categoria.descricao.like(f'%{self.main.categoria_descricao.text()}%')).order_by(Categoria.descricao.asc()).all()

        # config data table
        self.main.dt_Categoria.setRowCount(len(categ))
        self.main.dt_Categoria.setColumnCount(4)
        self.main.dt_Categoria.setColumnWidth(2, 300)
        
        # insert data
        for row, categ in enumerate(categ):

            buttonContainer = QWidget()
            rowButtons = QHBoxLayout(buttonContainer)

            # button edit
            edit_button = QPushButton(QIcon("./icons/iconEdit.png"), "")
            edit_button.setToolTip("Editar Categoria")
            edit_button.setMinimumWidth(25)
            edit_button.setMinimumHeight(25)
            edit_button.clicked.connect(lambda checked, row=row: self.on_click_button_edit_categoria(row))

            rowButtons.addWidget(edit_button)

            # button delete
            delete_button = QPushButton(QIcon("./icons/iconTrash.png"), "")
            delete_button.setToolTip("Excluir Categoria")
            delete_button.setMinimumWidth(25)
            delete_button.setMinimumHeight(25)
            delete_button.clicked.connect(lambda checked, row=row: self.on_click_button_delete_categoria(row))

            rowButtons.addWidget(delete_button)
            rowButtons.setContentsMargins(0, 0, 0, 0)
            
            # buttons edit delete
            self.main.dt_Categoria.setCellWidget(row, 0, buttonContainer)

            # ID
            itemId = QTableWidgetItem(str(categ.id))
            self.main.dt_Categoria.setItem(row, 1, itemId)
            itemId.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # descrição categoria
            self.main.dt_Categoria.setItem(row, 2, QTableWidgetItem(str(categ.descricao)))

            # ativo
            lblAtivo = 'Não'
            if categ.ativo:
                lblAtivo = 'Sim'
            self.main.dt_Categoria.setItem(row, 3, QTableWidgetItem(lblAtivo))

            # color table row
            set_table_row_color(row, self.main.dt_Categoria, ativo=categ.ativo)

        # close session
        session.close()


    # on click button edit categoria
    def on_click_button_edit_categoria(self, row):
        categ_id = int(self.main.dt_Categoria.item(row, 1).text())
        formCateg = FormCategoria(self.main, self, categ_id)
        formCateg.exec()
       

    # on click button delete categoria
    def on_click_button_delete_categoria(self, row):
        idCateg = int(self.main.dt_Categoria.item(row, 1).text())
        session = getSessionDB()
        categ = session.query(Categoria).filter_by(id=idCateg).first()
        
        if QMessageBox.question(self.main, 'Excluir Categoria', f'Tem certeza que deseja excluir a categoria: "{categ.descricao}"?',
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            try:
                categ.ativo=False
                session.add(categ)
                session.commit()
                QMessageBox.information(self.main, 'Sucesso', f'Categoria: "{categ.descricao}" excluída com sucesso.')

            except SQLAlchemyError as err:
                error_message = str(err).split('\n')[0]

                QMessageBox.warning(self.main, 'Erro', f'Categoria: "{categ.descricao}" não pode ser excluída\n{error_message}.')

        session.close()
        self.populate_table_categoria()
        self.populate_combo_box_categoria()

            
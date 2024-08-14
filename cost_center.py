# coding=utf-8
import copy
from qt_core import QMessageBox, QTableWidgetItem, QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QIcon, QWidget, Qt, QCheckBox

# app
from utils import set_table_row_color
from models import CentroCusto, getSessionDB, SQLAlchemyError



class FormCentroCusto(QDialog):
    def __init__(self, main, parent, centro_custo_id=None):
        super().__init__()
        self.main = main
        self.parent = parent
        self.centro_custo_id = centro_custo_id
        
        if self.centro_custo_id is None:
            self.flagDataSet = 'Insert'
            self.setWindowTitle("Incluir Centro de Custo")
        else:
            self.flagDataSet = 'Edit'
            self.setWindowTitle("Alterar Centro de Custo")

        colMaster = QVBoxLayout()
        col = QVBoxLayout()
        row = QHBoxLayout()

        self.label = QLabel('DESCRIÇÃO CENTRO DE CUSTO')
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
      
        self.btn_save_centro_custo = QPushButton(QIcon("./icons/iconSave.png"), "Salvar")
        self.btn_save_centro_custo.setMinimumHeight(30)
        self.btn_save_centro_custo.setStyleSheet(
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

        row.addWidget(self.btn_save_centro_custo)
        self.btn_save_centro_custo.clicked.connect(self.on_click_button_save_centro_custo)

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
        self.btn_close_form.clicked.connect(self.on_click_button_close_form_centro_custo)

        colMaster.addLayout(col)
        colMaster.addWidget(self.checkAtivo)
        colMaster.addLayout(row)
        self.setLayout(colMaster)

        if self.flagDataSet == 'Edit':
            session = getSessionDB()
            centroc = session.query(CentroCusto).filter_by(id=self.centro_custo_id).first()
            self.descricao.setText(centroc.descricao)
            self.checkAtivo.setChecked(centroc.ativo)
            session.close()


    # on click button save centro custo
    def on_click_button_save_centro_custo(self, e):
        
        if not self.descricao.text():
            QMessageBox.warning(self.main, "Aviso", "Descrição do Centro de Custo deve ser informada.")
            self.descricao.setFocus()
            return None

        session = getSessionDB()

        centroTipo = 'Débito'
        if self.parent.goback_form == 'ContaReceber':
            centroTipo = 'Crédito'

        if self.flagDataSet == 'Edit':
            centroc = session.query(CentroCusto).filter_by(id=self.centro_custo_id).first()
            oldCentroCusto = copy.deepcopy(centroc.descricao)
            centroc.descricao = self.descricao.text()
            centroc.ativo = self.checkAtivo.isChecked()
        else:
            centroc = CentroCusto(
                descricao = self.descricao.text(),
                tipo = centroTipo,
                ativo = self.checkAtivo.isChecked()
                )

        try:
            session.add(centroc)
            session.commit()

            if self.flagDataSet == 'Edit':
                QMessageBox.information(self.main, "Sucesso", f'Centro de Custo: "{oldCentroCusto}" alterado com sucesso.')
                self.parent.populate_table_centro_custo()
                self.parent.populate_combo_box_centro_custo()

            else:
                QMessageBox.information(self.main, "Sucesso", f'Centro de Custo: "{self.descricao.text()}" cadastrado com sucesso.')
                self.parent.populate_combo_box_centro_custo()
                self.main.cb_conta_receber_centro_custo.setCurrentText(self.descricao.text())
                self.main.cb_conta_pagar_centro_custo.setCurrentText(self.descricao.text())

        except SQLAlchemyError as err:
            error_message = str(err).split('\n')[0]

            if self.flagDataSet == 'Edit':
                QMessageBox.warning(self.main, "Erro", f'Não foi possível fazer a alteração do Centro de Custo: "{oldCentroCusto}"\n{error_message}.')
            else:
                QMessageBox.warning(self.main, "Erro", f'Não foi possível fazer a inclusão do Centro de Custo: "{self.descricao.text()}"\n{error_message}.')
            session.close()
            return None

        session.close()
        self.close()


    # on click button close form
    def on_click_button_close_form_centro_custo(self, e):
        self.close()


   
class CostCenter:

    def __init__(self, main):
        self.main = main

        # button form centro de custo (conta receber)
        self.main.btn_form_centro_custo_conta_receber.clicked.connect(self.on_click_button_form_centro_custo_conta_receber)

        # button form centro de custo (conta pagar)
        self.main.btn_form_centro_custo_conta_pagar.clicked.connect(self.on_click_button_form_centro_custo_conta_pagar)

        # button search centro de custo
        self.main.btn_search_centro_custo.clicked.connect(self.on_click_button_search_centro_custo)

        # button refresh table centro de custo
        self.main.btn_refresh_table_centro_custo.clicked.connect(self.on_click_button_refresh_table_centro_custo)
        
        # button add centro de custo
        self.main.btn_add_centro_custo.clicked.connect(self.on_click_button_add_centro_custo)

        # button goback form
        self.main.btn_centro_custo_goback_form.clicked.connect(self.on_click_button_goback_form)


    # on click button form centro de custo (conta receber)
    def on_click_button_form_centro_custo_conta_receber(self, e):

        self.goback_form ='ContaReceber'

        self.main.centro_custo_descricao.setFocus()

        self.main.forms.setCurrentWidget(self.main.formDataTableCentroCusto)

        self.populate_table_centro_custo()


    # on click button form centro de custo (conta pagar)
    def on_click_button_form_centro_custo_conta_pagar(self, e):

        self.goback_form ='ContaPagar'

        self.main.centro_custo_descricao.setFocus()

        self.main.forms.setCurrentWidget(self.main.formDataTableCentroCusto)

        self.populate_table_centro_custo()


    # on click button search centro de custo
    def on_click_button_search_centro_custo(self, e):
        if not self.main.centro_custo_descricao.text():
            QMessageBox.warning(self.main, "Erro", 'Campo "CENTRO DE CUSTO" deve ser informado.')
            self.main.centro_custo_descricao.setFocus()
            return None
        self.populate_table_centro_custo(flagQueryByUser=True)


    # on click button add centro de custo
    def on_click_button_add_centro_custo(self, e):
        formCentro = FormCentroCusto(self.main, self)
        formCentro.exec()


    # on click button refresh table centro de custo
    def on_click_button_refresh_table_centro_custo(self, e):
        self.populate_table_centro_custo()


    # on click button goback form
    def on_click_button_goback_form(self, e):

        # form conta receber
        if self.goback_form == 'ContaReceber':
            self.main.forms.setCurrentWidget(self.main.formCadastroContaReceber)


        # form conta receber
        elif self.goback_form == 'ContaPagar':
            self.main.forms.setCurrentWidget(self.main.formCadastroContaPagar)


    # populate combo box centro de custo
    def populate_combo_box_centro_custo(self):
        session = getSessionDB()
        centroCustoC = session.query(CentroCusto).filter_by(ativo=True, tipo='Crédito').order_by(CentroCusto.descricao.asc()).all()
        centroCustoD = session.query(CentroCusto).filter_by(ativo=True, tipo='Débito').order_by(CentroCusto.descricao.asc()).all()

        self.main.cb_conta_receber_centro_custo.clear()
        self.main.cb_conta_pagar_centro_custo.clear()

        for centroc in centroCustoC:
            self.main.cb_conta_receber_centro_custo.addItem(centroc.descricao)

        for centroc in centroCustoD:
            self.main.cb_conta_pagar_centro_custo.addItem(centroc.descricao)
        
        self.main.cb_conta_receber_centro_custo.setCurrentIndex(-1)
        self.main.cb_conta_pagar_centro_custo.setCurrentIndex(-1)
        session.close()


    # populate table centro de custo
    def populate_table_centro_custo(self, flagQueryByUser=False):

        session = getSessionDB()
        if not flagQueryByUser:
            centro_custo = session.query(CentroCusto).order_by(CentroCusto.descricao.asc()).all()
        else:
            centro_custo = session.query(CentroCusto).filter(CentroCusto.descricao.like(f'%{self.main.centro_custo_descricao.text()}%')).order_by(CentroCusto.descricao.asc()).all()

        # config data table
        self.main.dt_Centro_Custo.setRowCount(len(centro_custo))
        self.main.dt_Centro_Custo.setColumnCount(5)
        self.main.dt_Centro_Custo.setColumnWidth(2, 300)
        
        # insert data
        for row, centro_cto in enumerate(centro_custo):

            buttonContainer = QWidget()
            rowButtons = QHBoxLayout(buttonContainer)

            # button edit
            edit_button = QPushButton(QIcon("./icons/iconEdit.png"), "")
            edit_button.setToolTip("Editar Centro de Custo")
            edit_button.setMinimumWidth(25)
            edit_button.setMinimumHeight(25)
            edit_button.clicked.connect(lambda checked, row=row: self.on_click_button_edit_centro_custo(row))

            rowButtons.addWidget(edit_button)

            # button delete
            delete_button = QPushButton(QIcon("./icons/iconTrash.png"), "")
            delete_button.setToolTip("Excluir Centro de Custo")
            delete_button.setMinimumWidth(25)
            delete_button.setMinimumHeight(25)
            delete_button.clicked.connect(lambda checked, row=row: self.on_click_button_delete_centro_custo(row))

            rowButtons.addWidget(delete_button)
            rowButtons.setContentsMargins(0, 0, 0, 0)
            
            # buttons edit delete
            self.main.dt_Centro_Custo.setCellWidget(row, 0, buttonContainer)

            # ID
            itemId = QTableWidgetItem(str(centro_cto.id))
            self.main.dt_Centro_Custo.setItem(row, 1, itemId)
            itemId.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # descrição centro de custo
            self.main.dt_Centro_Custo.setItem(row, 2, QTableWidgetItem(str(centro_cto.descricao)))

            # ativo
            lblAtivo = 'Não'
            if centro_cto.ativo:
                lblAtivo = 'Sim'
            self.main.dt_Centro_Custo.setItem(row, 3, QTableWidgetItem(lblAtivo))

            self.main.dt_Centro_Custo.setItem(row, 4, QTableWidgetItem(centro_cto.tipo))

            # color table row
            set_table_row_color(row, self.main.dt_Centro_Custo, ativo=centro_cto.ativo)

        # close session
        session.close()


    # on click button edit centro de custo
    def on_click_button_edit_centro_custo(self, row):
                                    
        centro_cto_id = int(self.main.dt_Centro_Custo.item(row, 1).text())
        centroCusto = FormCentroCusto(self.main, self, centro_cto_id)
        centroCusto.exec()
       

    # on click button delete centro de custo
    def on_click_button_delete_centro_custo(self, row):
        idCentro = int(self.main.dt_Centro_Custo.item(row, 1).text())
        session = getSessionDB()
        centro_cto = session.query(CentroCusto).filter_by(id=idCentro).first()
        
        if QMessageBox.question(self.main, 'Excluir Centro de Custo', f'Tem certeza que deseja excluir o Centro de Custo: "{centro_cto.descricao}"?',
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            try:
                centro_cto.ativo=False
                session.add(centro_cto)
                session.commit()
                QMessageBox.information(self.main, 'Sucesso', f'Centro de Custo: "{centro_cto.descricao}" excluído com sucesso.')

            except SQLAlchemyError as err:
                error_message = str(err).split('\n')[0]

                QMessageBox.warning(self.main, 'Erro', f'Centro de Custo: "{centro_cto.descricao}" não pode ser excluído\n{error_message}.')

        session.close()
        self.populate_table_centro_custo()
        self.populate_combo_box_centro_custo()

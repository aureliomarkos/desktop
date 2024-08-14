# coding=utf-8
import copy
from qt_core import QTableWidgetItem, QPixmap, QFileDialog, QByteArray, QBuffer, QIODevice, QMessageBox, QPushButton, QComboBox, QIcon, Qt

# app
from utils import set_table_row_color
from models import Produto, Categoria, Marca, getSessionDB, SQLAlchemyError


# Product
class Product:

    def __init__(self, main):
        self.main = main

        # flag dataSet
        self.flagDataSet=None

        # on click button product menu
        self.main.btn_form_produto.clicked.connect(self.on_click_button_form_data_table_produto)

        # on click button search produto
        self.main.btn_search_produto.clicked.connect(self.on_click_button_search_produto)

        # button add product
        self.main.btn_add_produto.clicked.connect(self.on_click_button_add_produto)

        # button add image
        self.main.btn_add_imagem.clicked.connect(self.on_click_button_add_imagem)

        # button remove imagem
        self.main.btn_remove_imagem.hide()
        self.main.btn_remove_imagem.clicked.connect(self.on_click_button_remove_imagem)

        # button save product
        self.main.btn_save_produto.clicked.connect(self.on_click_button_save_produto)

        # button refresh data table produto
        self.main.btn_refresh_data_table_produto.clicked.connect(self.on_click_button_refresh_data_table_produto)

        # button goback product
        self.main.btn_goback_produto.clicked.connect(self.on_click_button_goback_form_data_table_produto)

        # button relatorio
        self.main.btn_relatorio_produto.clicked.connect(self.on_click_button_relatorio_produto)


    # clear fields form produto
    def clear_form_produto(self):
        pixmap = QPixmap()
        self.main.label_imagem_produto.setPixmap(pixmap)
        self.main.id_produto.setText('')
        self.main.produto_descricao.setText('')
        self.main.sb_produto_qtde.setValue(0)
        self.main.sb_estoque_minimo.setValue(5)
        self.main.sb_estoque_maximo.setValue(100)
        self.main.sb_qtde_atacado.setValue(10)
        self.main.sb_preco_custo.setValue(0)
        self.main.sb_preco_varejo.setValue(0)
        self.main.sb_preco_atacado.setValue(0)
        self.main.observacao.setText('')
        self.main.chk_produto_ativo.setChecked(True)


    # on click button relatorio produto
    def on_click_button_relatorio_produto(self, e):

        self.main.categ.populate_combo_box_categoria()
        self.main.brand.populate_combo_box_marca()
        
        self.main.cb_categoria_relatorio_produto.setFocus()

        self.main.btn_imprimir_relatorio_produto.setDisabled(True)

        self.main.te_relatorio_produto.clear()

        self.main.forms.setCurrentWidget(self.main.formRelatorioProduto)


    # on click button refresh data table produto
    def on_click_button_refresh_data_table_produto(self, e):
        self.populate_table_produto()


    # on click button search produto
    def on_click_button_search_produto(self, e):

        if not self.main.search_produto_descricao.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "DESCRIÇÃO PRODUTO" deve ser informado.')
            self.main.search_produto_descricao.setFocus()
            return None

        self.populate_table_produto(flagQueryByUser=True)


    # on change stacked form
    def on_click_button_add_produto(self, e):

        self.flagDataSet = 'Insert'

        self.main.categ.populate_combo_box_categoria()
        self.main.brand.populate_combo_box_marca()

        self.clear_form_produto()

        self.main.lbl_title_cadastro_produto.setText('Cadastro de Produto')

        self.main.produto_descricao.setFocus()

        self.main.forms.setCurrentWidget(self.main.formCadastroProduto)


    # on click button form data table produto
    def on_click_button_form_data_table_produto(self, e):
        
        self.populate_table_produto()

        self.main.search_produto_descricao.setFocus()

        self.main.forms.setCurrentWidget(self.main.formDataTableProduto)


    # on click button add imagem
    def on_click_button_add_imagem(self, e):
        filename, _ = QFileDialog.getOpenFileName(self.main, caption="Abrir Imagem", filter="Imagens (*.png *.jpg *.bmp)")
        if filename:
            pixmap = QPixmap(filename)
            self.main.label_imagem_produto.setPixmap(pixmap)
            self.main.label_imagem_produto.setScaledContents(True)
        
        self.main.btn_add_imagem.hide()
        self.main.btn_remove_imagem.show()


    # on click button remove imagem
    def on_click_button_remove_imagem(self, e):
        pixmap = QPixmap()
        self.main.label_imagem_produto.setPixmap(pixmap)
        self.main.btn_add_imagem.show()
        self.main.btn_remove_imagem.hide()


    # on click button goback form data table produto
    def on_click_button_goback_form_data_table_produto(self, e):

        self.main.forms.setCurrentWidget(self.main.formDataTableProduto)


    # populate table product
    def populate_table_produto(self, flagQueryByUser=None):
        session = getSessionDB()

        if flagQueryByUser:
            produto = session.query(Produto).filter(Produto.descricao.like(f'%{self.main.search_produto_descricao.text()}%')).order_by(Produto.descricao.asc()).all()
        else:
            produto = session.query(Produto).order_by(Produto.descricao.asc()).all()

        # config data table
        self.main.dt_Produto.setRowCount(len(produto))
        self.main.dt_Produto.setColumnCount(17)
        self.main.dt_Produto.setColumnWidth(0, 70)
        self.main.dt_Produto.setColumnWidth(1, 70)
        self.main.dt_Produto.setColumnWidth(2, 40)
        self.main.dt_Produto.setColumnWidth(3, 300)
        self.main.dt_Produto.setColumnWidth(8, 400)

        # insert data
        for row, prod in enumerate(produto):

            # button edit
            edit_button = QPushButton(QIcon("./icons/iconEdit.png"), "")
            edit_button.setToolTip("Editar Produto")
            edit_button.setMinimumWidth(25)
            edit_button.setMinimumHeight(25)
            edit_button.clicked.connect(lambda checked, row=row: self.on_click_button_edit_produto(row))

            # button delete
            delete_button = QPushButton(QIcon("./icons/iconTrash.png"), "")
            delete_button.setToolTip("Excluir Produto")
            delete_button.setMinimumWidth(25)
            delete_button.setMinimumHeight(25)
            delete_button.clicked.connect(lambda checked, row=row: self.on_click_button_delete_produto(row))

            # buttons edit delete
            self.main.dt_Produto.setCellWidget(row, 0, edit_button)
            self.main.dt_Produto.setCellWidget(row, 1, delete_button)

            self.main.dt_Produto.setItem(row, 2, QTableWidgetItem(str(prod.id)))
            self.main.dt_Produto.setItem(row, 3, QTableWidgetItem(str(prod.descricao)))
            self.main.dt_Produto.setItem(row, 4, QTableWidgetItem(str(prod.qtde)))
            self.main.dt_Produto.setItem(row, 5, QTableWidgetItem(str(prod.unidade)))
            self.main.dt_Produto.setItem(row, 6, QTableWidgetItem(str(prod.categoria.descricao)))
            self.main.dt_Produto.setItem(row, 7, QTableWidgetItem(str(prod.marca.descricao)))

            if prod.compra_item:
                combo_box_ultimas_compras = QComboBox()
                for cnt, itens in enumerate(prod.compra_item):
                    combo_box_ultimas_compras.addItem(str(itens))
                    
                    # última 10 compras
                    if cnt == 9:
                        break

                self.main.dt_Produto.setCellWidget(row, 8, combo_box_ultimas_compras)
            else:
                self.main.dt_Produto.setItem(row, 8, QTableWidgetItem(''))

            # preco custo - 9
            itemPrecoCusto = QTableWidgetItem(f'{prod.preco_custo:>9.2f}'.replace('.', ','))
            self.main.dt_Produto.setItem(row, 9, itemPrecoCusto)
            itemPrecoCusto.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # preco varejo - 10
            itemPrecoVarejo = QTableWidgetItem(f'{prod.preco_varejo:>9.2f}'.replace('.', ','))
            self.main.dt_Produto.setItem(row, 10, itemPrecoVarejo)
            itemPrecoVarejo.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # preco atacado - 11
            itemPrecoAtacado = QTableWidgetItem(f'{prod.preco_atacado:>9.2f}'.replace('.', ','))
            self.main.dt_Produto.setItem(row, 11, itemPrecoAtacado)
            itemPrecoAtacado.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.main.dt_Produto.setItem(row, 12, QTableWidgetItem(str(prod.estoque_minimo)))
            self.main.dt_Produto.setItem(row, 13, QTableWidgetItem(str(prod.estoque_maximo)))
            self.main.dt_Produto.setItem(row, 14, QTableWidgetItem(str(prod.qtde_atacado)))
            self.main.dt_Produto.setItem(row, 15, QTableWidgetItem(str(prod.observacao)))

            lblAtivo = 'Sim'
            if not prod.ativo:
                lblAtivo = 'Não'
                delete_button.setDisabled(True)
            self.main.dt_Produto.setItem(row, 16, QTableWidgetItem(lblAtivo))

            set_table_row_color(row, self.main.dt_Produto, ativo=prod.ativo)

        # close session
        session.close()


    # on click button edit produto
    def on_click_button_edit_produto(self, row):

        self.flagDataSet = 'Edit'

        self.main.lbl_title_cadastro_produto.setText('Alterar Produto')

        self.main.categ.populate_combo_box_categoria()
        self.main.brand.populate_combo_box_marca()

        idProd = int(self.main.dt_Produto.item(row, 2).text())
        session = getSessionDB()
        prod = session.query(Produto).filter_by(id=idProd).first()

        if prod.imagem:
            self.main.btn_add_imagem.hide()
            self.main.btn_remove_imagem.show()
        else:
            self.main.btn_add_imagem.show()
            self.main.btn_remove_imagem.hide()

        pixmap = QPixmap()
        pixmap.loadFromData(prod.imagem)
        self.main.label_imagem_produto.setPixmap(pixmap)
        self.main.label_imagem_produto.setScaledContents(True)

        self.main.id_produto.setText(str(prod.id))
        self.oldProdutoDescricao = copy.deepcopy(prod.descricao)
        self.main.produto_descricao.setText(prod.descricao)

        self.main.cb_unidade.setCurrentText(prod.unidade)
        self.main.cb_categoria.setCurrentText(prod.categoria.descricao)
        self.main.cb_marca.setCurrentText(prod.marca.descricao)

        self.main.sb_produto_qtde.setValue(prod.qtde)
        self.main.sb_estoque_minimo.setValue(prod.estoque_minimo)
        self.main.sb_estoque_maximo.setValue(prod.estoque_maximo)
        self.main.sb_qtde_atacado.setValue(prod.qtde_atacado)

        self.main.sb_preco_custo.setValue(prod.preco_custo)
        self.main.sb_preco_varejo.setValue(prod.preco_varejo)
        self.main.sb_preco_atacado.setValue(prod.preco_atacado)

        self.main.observacao.setText(prod.observacao)
        self.main.chk_produto_ativo.setChecked(prod.ativo)

        session.close()

        # change stack
        self.main.forms.setCurrentWidget(self.main.formCadastroProduto)


    # on click button delete produto
    def on_click_button_delete_produto(self, row):
        idProd = int(self.main.dt_Produto.item(row, 2).text())
        session = getSessionDB()
        prod = session.query(Produto).filter_by(id=idProd).first()
        
        if QMessageBox.question(self.main, 'Excluir Produto', f'Tem certeza que deseja excluir o Produto: "{prod.descricao}"?',
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            try:
                prod.ativo=False
                session.add(prod)
                session.commit()
                QMessageBox.information(self.main, 'Sucesso', f'Produto: "{prod.descricao}" excluído com sucesso.')

            except SQLAlchemyError as err:
                error_message = str(err).split('\n')[0]

                QMessageBox.warning(self.main, 'Erro', f'Produto: "{prod.descricao}" não pode ser excluído\n{error_message}.')

        session.close()
        self.populate_table_produto()


    # on click button save produto
    def on_click_button_save_produto(self, e):

        session = getSessionDB()
        
        # verify required fields
        if not self.main.produto_descricao.text():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "DESCRIÇÃO" deve ser informado.')
            self.main.produto_descricao.setFocus()
            return None

        if not self.main.cb_categoria.currentText():
            QMessageBox.warning(self.main, "Aviso", 'Categoria deve ser selecionada.')
            return None
        
        # combo box categoria
        if not session.query(Categoria.id).filter_by(descricao=self.main.cb_categoria.currentText()).first():
            QMessageBox.warning(self.main, "Aviso", f'CATEGORIA: "{self.main.cb_categoria.currentText()}" não existe.')
            session.close()
            return None

        if not self.main.cb_marca.currentText():
            QMessageBox.warning(self.main, "Aviso", 'Marca deve ser selecionada.')
            return None
        
        # combo box marca
        if not session.query(Marca.id).filter_by(descricao=self.main.cb_marca.currentText()).first():
            QMessageBox.warning(self.main, "Aviso", f'MARCA: "{self.main.cb_marca.currentText()}" não existe.')
            session.close()
            return None

        if not self.main.sb_estoque_minimo.value():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "MÍNIMO" deve ser informado.')
            self.main.sb_estoque_minimo.setFocus()
            return None

        if not self.main.sb_estoque_maximo.value():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "MÁXIMO" deve ser informado.')
            self.main.sb_estoque_maximo.setFocus()
            return None

        if not self.main.sb_qtde_atacado.value():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "QUANTIDADE" deve ser informado.')
            self.main.sb_qtde_atacado.setFocus()
            return None

        if not self.main.sb_preco_custo.value():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "PREÇO DE CUSTO" deve ser informado.')
            self.main.sb_preco_custo.setFocus()
            return None

        if not self.main.sb_preco_varejo.value():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "PREÇO VAREJO" deve ser informado.')
            self.main.sb_preco_varejo.setFocus()
            return None

        if not self.main.sb_preco_atacado.value():
            QMessageBox.warning(self.main, "Aviso", 'Campo: "PREÇO ATACADO" deve ser informado.')
            self.main.sb_preco_atacado.setFocus()
            return None

        if self.flagDataSet == 'Insert':

            # convertendo a image para salvar
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            self.main.label_imagem_produto.pixmap().save(buffer, "PNG")

            produto = Produto(
                        descricao = self.main.produto_descricao.text(),
                        unidade = self.main.cb_unidade.currentText(),
                        imagem = byte_array,
                        categoria_id = session.query(Categoria.id).filter_by(descricao=self.main.cb_categoria.currentText()).first()[0],
                        marca_id = session.query(Marca.id).filter_by(descricao=self.main.cb_marca.currentText()).first()[0],
                        qtde = self.main.sb_produto_qtde.value(),
                        estoque_minimo = self.main.sb_estoque_minimo.value(),
                        estoque_maximo = self.main.sb_estoque_maximo.value(),
                        qtde_atacado = self.main.sb_qtde_atacado.value(),
                        preco_custo = self.main.sb_preco_custo.value(),
                        preco_varejo = self.main.sb_preco_varejo.value(),
                        preco_atacado = self.main.sb_preco_atacado.value(),
                        observacao = self.main.observacao.text(),
                        ativo = self.main.chk_produto_ativo.isChecked()
                        )

        # Save Edit
        else:

            # convertendo a image para salvar
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            self.main.label_imagem_produto.pixmap().save(buffer, "PNG")

            produto = session.query(Produto).filter_by(id=self.main.id_produto.text()).first()

            produto.descricao = self.main.produto_descricao.text()
            produto.unidade = self.main.cb_unidade.currentText()
            produto.imagem = byte_array
            produto.categoria_id = session.query(Categoria.id).filter_by(descricao=self.main.cb_categoria.currentText()).first()[0]
            produto.marca_id = session.query(Marca.id).filter_by(descricao=self.main.cb_marca.currentText()).first()[0]
            produto.qtde = self.main.sb_produto_qtde.value()
            produto.estoque_minimo = self.main.sb_estoque_minimo.value()
            produto.estoque_maximo = self.main.sb_estoque_maximo.value()
            produto.qtde_atacado = self.main.sb_qtde_atacado.value()
            produto.preco_custo = self.main.sb_preco_custo.value()
            produto.preco_varejo = self.main.sb_preco_varejo.value()
            produto.preco_atacado = self.main.sb_preco_atacado.value()
            produto.observacao = self.main.observacao.text()
            produto.ativo = self.main.chk_produto_ativo.isChecked()

        try:
            session.add(produto)
            session.commit()

            if self.flagDataSet == 'Insert':
                QMessageBox.information(self.main, "Sucesso", f'Produto: "{self.main.produto_descricao.text()}" cadastrado com sucesso.')
            else:
                QMessageBox.information(self.main, "Sucesso", f'Produto: "{self.oldProdutoDescricao}" alterado com sucesso.')

        except SQLAlchemyError as err:
            error_message = str(err).split('\n')[0]
            
            if self.flagDataSet == 'Insert':
                QMessageBox.warning(self.main, "Erro", f'Não foi possível fazer inclusão do Produto: "{self.main.produto_descricao.text()}"\n{error_message}.')
            else:
                QMessageBox.warning(self.main, "Erro", f'Não foi possível fazer alteração do Produto: "{self.oldProdutoDescricao}"\n{error_message}.')
            
            session.close()
            return None

        session.close()
        self.flagDataSet = None
        self.clear_form_produto()
        self.populate_table_produto()
        self.main.forms.setCurrentWidget(self.main.formDataTableProduto)

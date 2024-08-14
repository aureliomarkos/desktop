# coding=utf-8
from qt_core import QMessageBox, QFont

# app
from printer import Printer
from report import Relatorio
from models import Produto, Categoria, Marca, getSessionDB


class ProductReport:

    def __init__(self, main):
        self.main = main

        self.main.btn_imprimir_relatorio_produto.clicked.connect(self.on_click_button_imprimir_relatorio)

        self.main.btn_gerar_relatorio_produto.clicked.connect(self.on_click_button_gerar_relatorio)

        self.main.btn_goback_relatorio_produto.clicked.connect(self.on_click_button_goback_data_table_produto)
        
    
    def on_click_button_imprimir_relatorio(self):
        printer = Printer(self.main)

        printer.start_printer('./relatorio/produto.txt', 'Relatório de Produtos')


    def on_click_button_goback_data_table_produto(self, e):
        self.main.forms.setCurrentWidget(self.main.formDataTableProduto)


    def on_click_button_gerar_relatorio(self):

        session = getSessionDB()

        # combo box categoria
        if self.main.cb_categoria_relatorio_produto.currentText():
            if not session.query(Categoria.id).filter_by(descricao=self.main.cb_categoria_relatorio_produto.currentText()).first():
                QMessageBox.warning(self.main, "Aviso", f'CATEGORIA: "{self.main.cb_categoria_relatorio_produto.currentText()}" não existe.')
                session.close()
                return None

        # combo box marca
        if self.main.cb_marca_relatorio_produto.currentText():
            if not session.query(Marca.id).filter_by(descricao=self.main.cb_marca_relatorio_produto.currentText()).first():
                QMessageBox.warning(self.main, "Aviso", f'MARCA: "{self.main.cb_marca_relatorio_produto.currentText()}" não existe.')
                session.close()
                return None
        
        produtos = session.query(Produto).filter(Produto.ativo == 1).all()
        
        if self.main.cb_categoria_relatorio_produto.currentText():
            categoria_id = session.query(Categoria.id).filter_by(descricao=self.main.cb_categoria_relatorio_produto.currentText()).first()[0]
            produtos = session.query(Produto).filter(Produto.categoria_id == categoria_id, Produto.ativo == 1).all()

        if self.main.cb_marca_relatorio_produto.currentText():
            marca_id = session.query(Marca.id).filter_by(descricao=self.main.cb_marca_relatorio_produto.currentText()).first()[0]
            produtos = session.query(Produto).filter(Produto.marca_id == marca_id, Produto.ativo == 1).all()

        if self.main.chk_produto_qtde_minima_relatorio.isChecked():
            produtos = session.query(Produto).filter(Produto.qtde < Produto.estoque_minimo, Produto.ativo == 1).all()

        if self.main.cb_categoria_relatorio_produto.currentText() and self.main.chk_produto_qtde_minima_relatorio.isChecked():
            categoria_id = session.query(Categoria.id).filter_by(descricao=self.main.cb_categoria_relatorio_produto.currentText()).first()[0]
            produtos = session.query(Produto).filter(Produto.categoria_id == categoria_id, Produto.qtde < Produto.estoque_minimo, Produto.ativo == 1).all()

        if self.main.cb_categoria_relatorio_produto.currentText() and self.main.cb_marca_relatorio_produto.currentText():
            categoria_id = session.query(Categoria.id).filter_by(descricao=self.main.cb_categoria_relatorio_produto.currentText()).first()[0]
            marca_id = session.query(Marca.id).filter_by(descricao=self.main.cb_marca_relatorio_produto.currentText()).first()[0]
            produtos = session.query(Produto).filter(Produto.categoria_id == categoria_id, Produto.marca_id == marca_id, Produto.ativo == 1).all()

        if self.main.cb_marca_relatorio_produto.currentText() and self.main.chk_produto_qtde_minima_relatorio.isChecked():
            marca_id = session.query(Marca.id).filter_by(descricao=self.main.cb_marca_relatorio_produto.currentText()).first()[0]
            produtos = session.query(Produto).filter(Produto.marca_id == marca_id, Produto.qtde < Produto.estoque_minimo, Produto.ativo == 1).all()

        if self.main.cb_categoria_relatorio_produto.currentText() and self.main.cb_marca_relatorio_produto.currentText() and self.main.chk_produto_qtde_minima_relatorio.isChecked():
            categoria_id = session.query(Categoria.id).filter_by(descricao=self.main.cb_categoria_relatorio_produto.currentText()).first()[0]
            marca_id = session.query(Marca.id).filter_by(descricao=self.main.cb_marca_relatorio_produto.currentText()).first()[0]
            produtos = session.query(Produto).filter(Produto.categoria_id == categoria_id,
                                                     Produto.marca_id == marca_id,
                                                     Produto.qtde < Produto.estoque_minimo,
                                                     Produto.ativo == 1).all()

        # button imprimir relatório
        if produtos:
            self.main.btn_imprimir_relatorio_produto.setDisabled(False)
        else:
            self.main.btn_imprimir_relatorio_produto.setDisabled(True)

        cabecalho = f'{'ID':>6} {'DESCRIÇÃO':<29} {'QTDE':>4} {'PREÇO CUSTO':>11} {'PREÇO VAREJO':>12} {'PREÇO ATACADO':>13}'

        relProduto = Relatorio('Relatório de Produtos', cabecalho, 'produto.txt')

        for produto in produtos:
            relProduto.printer_row(f'{produto.id:>6d} {produto.descricao:<29.29} {produto.qtde:>4d} {str(produto.preco_custo).replace('.', ','):>11} {str(produto.preco_varejo).replace('.', ','):>12} {str(produto.preco_atacado).replace('.', ','):>13}')

        relProduto.close_file()
        
        with open('./relatorio/produto.txt',  'r', encoding='utf-8') as file:
            relatorio_texto = file.read()

        # Define a fonte monoespaçada
        font = QFont("Courier New")
        font.setPointSize(11)

        self.main.te_relatorio_produto.setFont(font)
        self.main.te_relatorio_produto.setPlainText(relatorio_texto) 
        self.main.te_relatorio_produto.setReadOnly(True)


# coding=utf-8
from qt_core import QTableWidgetItem, QMessageBox, QPushButton, QComboBox, QIcon, QDate, Qt

# app
from utils import set_table_row_color, get_values_data_table, proximo_mes, get_mes_ano_referencia
from models import Produto, Compra, CompraItem, Fornecedor, FormaPagto, ContaPagar, getSessionDB, SQLAlchemyError


# Purchase
class Purchase:

    def __init__(self, main):
        self.main = main

        # button Purchase
        self.main.btn_form_compra.clicked.connect(self.on_click_button_form_compra)

        # button add compra
        self.main.btn_add_compra.clicked.connect(self.on_click_button_add_compra)

        # button save compra
        self.main.btn_save_compra.clicked.connect(self.on_click_button_save_compra)

        # button goback data table compra
        self.main.btn_goback_compra.clicked.connect(self.on_click_button_goback_form_data_table_compra)

        # button search nota
        self.main.btn_search_nota_fornecedor.clicked.connect(self.on_click_button_search_nota_fornecedor)
        
        # btn refresh data table compra
        self.main.btn_refresh_data_table_compra.clicked.connect(self.on_click_button_refresh_data_table_compra)

        # on_change search_produto_descricao_compra
        self.main.search_produto_descricao_compra.textChanged.connect(self.populate_table_produto)


    # on click button form compra
    def on_click_button_form_compra(self, e):

        self.main.compra_data_inicial.setDate(QDate.currentDate())
        self.main.compra_data_final.setDate(QDate.currentDate())

        self.populate_data_table_compra()

        self.main.search_compra_fornecedor_nome.setFocus()

        self.main.forms.setCurrentWidget(self.main.formDataTableCompra)


    # on click button goback form data table compra
    def on_click_button_goback_form_data_table_compra(self, e):
        self.main.forms.setCurrentWidget(self.main.formDataTableCompra)

    
    # on click button search nota fornecedor
    def on_click_button_search_nota_fornecedor(self, e):
        self.populate_data_table_compra(flagQueryByUser=True)


    # on click button refresh data table compra
    def on_click_button_refresh_data_table_compra(self, e):
        self.populate_data_table_compra()


    # on click button save Purchase
    def on_click_button_save_compra(self, e):

        session = getSessionDB()

        # combo box fornecedor
        if not self.main.cb_compra_fornecedor.currentText():
            QMessageBox.warning(self.main, "Aviso", 'Fornecedor: deve ser selecionado.')
            self.main.cb_compra_fornecedor.setFocus()
            return None

        if not session.query(Fornecedor.id).filter_by(nome=self.main.cb_compra_fornecedor.currentText()).first():
            QMessageBox.warning(self.main, "Aviso", f'Fornecedor: "{self.main.cb_compra_fornecedor.currentText()}" não cadastrado.')
            self.main.cb_compra_fornecedor.setFocus()
            session.close()
            return None
        
        if not self.main.chk_gerar_conta_pagar.isChecked():
            if not self.main.cb_compra_forma_pagto.currentText():
                QMessageBox.warning(self.main, "Aviso", f'Forma de pagamento deve ser selecionada.')
                self.main.cb_compra_forma_pagto.setFocus()
                return None

            # combo box forma de pagto
            if not session.query(FormaPagto.id).filter_by(descricao=self.main.cb_compra_forma_pagto.currentText()).first():
                QMessageBox.warning(self.main, "Aviso", f'Forma de pagamento: "{self.main.cb_compra_forma_pagto.currentText()}" não cadastrada.')
                self.main.cb_compra_forma_pagto.setFocus()
                session.close()
                return None

        # nro nota
        if not self.main.nro_nota.text():
            QMessageBox.warning(self.main, "Aviso", f'"DOCUMENTO NRO" deve ser informado.')
            self.main.nro_nota.setFocus()
            return None

        # total nota
        if not self.main.sb_total_compra.value():
            QMessageBox.warning(self.main, "Aviso", 'Campo "TOTAL" deve ser informado.')
            self.main.sb_total_compra.setFocus()
            return None

        # items na nota
        if not self.main.dt_Compra_Item.rowCount():
            QMessageBox.warning(self.main, "Aviso", f'Deve ser informado um "PRODUTO" na nota pelo menos.')
            return None
        
        # validar valores da nota de compra
        if not (
            self.main.sb_compra_desconto.value() +
            self.main.sb_compra_frete.value() +
            self.total_itens) == self.main.sb_total_compra.value():

            QMessageBox.warning(self.main, "Aviso",
                f'Valores informados na Nota estão divergentes.\nDesconto: R$ {self.main.sb_compra_desconto.value()} + Frete: R$ {self.main.sb_compra_frete.value()} + Total Itens: R$ {self.total_itens}\ndevem ser igual ao Total: R$ :{self.main.sb_total_compra.value()}')
            return None

        # check button contas a pagar
        statusCompra = 'À Vista'
        if self.main.chk_gerar_conta_pagar.isChecked():
            statusCompra = 'À Prazo'
            forma_pagto_id = ''
            if not self.main.sb_nro_parcelas_compra.value():
                QMessageBox.warning(self.main, "Aviso", f'Para gerar Contas a Pagar "NRO PARCELAS" deve ser informado.')
                return None
        else:
            forma_pagto_id = session.query(FormaPagto.id).filter_by(descricao=self.main.cb_compra_forma_pagto.currentText()).first()[0]

        # verifica se nota de compra já foi cadastrada para o fornecedor
        idFornec = session.query(Fornecedor.id).filter_by(nome=self.main.cb_compra_fornecedor.currentText()).first()[0]
        fornec = session.query(Compra).filter(Compra.fornecedor_id == idFornec, Compra.nro_nota == self.main.nro_nota.text()).first()

        if fornec:
            QMessageBox.warning(self.main, "Aviso", f'"DOCUMENTO NRO: {self.main.nro_nota.text()}", já cadastrado para este fornecedor.')
            session.close()
            return None


        compra = Compra(
                nro_nota = self.main.nro_nota.text(),
                status = statusCompra,
                data_emissao = self.main.data_emissao.date().toPython(),
                data_entrega = self.main.data_entrega.date().toPython(),
                data_vencimento = self.main.data_vencimento.date().toPython(),
                
                desconto = self.main.sb_compra_desconto.value(),
                frete = self.main.sb_compra_frete.value(),
                total = self.main.sb_total_compra.value(),

                fornecedor_id = session.query(Fornecedor.id).filter_by(nome=self.main.cb_compra_fornecedor.currentText()).first()[0],
                forma_pagto_id = forma_pagto_id,

                observacao = self.main.compra_observacao.text()
            )

        # Nota de Compra
        try:
            session.add(compra)
            session.commit()

        except SQLAlchemyError as err:
            error_message = str(err).split('\n')[0]
            QMessageBox.warning(self.main,  "Erro", f'Não foi possível salvar a Nota de Compra.\n{error_message}')
            return None

        # get all itens da Nota de Compra
        for row in get_values_data_table(self.main.dt_Compra_Item):

            compraItem = CompraItem(
                    compra_id = compra.id,
                    produto_id = row[1],
                    qtde = row[3],
                    preco = row[4].replace(',', '.'))

            session.add(compraItem)

            # Atualiza Preço custo
            if row[6] == 'Sim':
                prod = session.query(Produto).filter_by(id=row[1]).first()
                prod.preco_custo = row[4].replace(',', '.')

        try:
            session.commit()
        except SQLAlchemyError as err:
            error_message = str(err).split('\n')[0]
            QMessageBox.warning(self.main,  "Erro", f'Não foi possível Inserir os Ítens na Nota de Compra.\n{error_message}')
            session.close()
            return None

        # contas a pagar
        if self.main.chk_gerar_conta_pagar.isChecked():
                
            data_inicial = self.main.data_vencimento.date().toPython()

            for parcela in range(self.main.sb_nro_parcelas_compra.value()):

                mes, ano = get_mes_ano_referencia(data_inicial)
    
                nova_conta = ContaPagar(
                        descricao = f'Pagto Fornec: {self.main.cb_compra_fornecedor.currentText()[:20]}',
                        referencia = f'"{mes}/{ano}" Parcela {parcela+1} de {self.main.sb_nro_parcelas_compra.value()}.',
                        data_vcto = data_inicial,
                        data_pagto = data_inicial,
                        valor_titulo = self.main.sb_total_compra.value(),
                        valor_parcela = round(self.main.sb_total_compra.value() / self.main.sb_nro_parcelas_compra.value(), 2),
                        compra_id = compra.id,
                        doc_numero = compra.nro_nota,
                        fornecedor_id = compra.fornecedor_id)

                session.add(nova_conta)
                data_inicial = proximo_mes(data_inicial.day, data_inicial)

            try:
                session.commit()
            except SQLAlchemyError as err:
                error_message = str(err).split('\n')[0]
                QMessageBox.warning(self.main,  "Erro", f'Não foi possível Gerar Contas a Pagar.\n{error_message}')
                session.close()
                return None

        self.clear_fields_form_compra()
        self.populate_data_table_compra()
        self.main.forms.setCurrentWidget(self.main.formDataTableCompra)
        session.close()


    # clear fields form compra
    def clear_fields_form_compra(self):
        self.main.nro_nota.setText('')
        self.main.sb_compra_desconto.setValue(0.00)
        self.main.sb_compra_frete.setValue(0.00)
        self.main.sb_compra_qtde.setValue(0)
        self.main.sb_compra_preco_custo.setValue(0.00)
        self.main.sb_total_compra.setValue(0.00)
        self.main.sb_nro_parcelas_compra.setValue(0)
        self.main.chk_gerar_conta_pagar.setChecked(False)
        self.main.chk_compra_atualiza_preco_custo.setChecked(False)
        self.main.search_produto_descricao_compra.setText('')
        self.main.compra_observacao.setText('')
        self.main.lbl_total_itens.setText('Total Ítens R$')

        self.main.data_emissao.setDate(QDate.currentDate())
        self.main.data_entrega.setDate(QDate.currentDate())
        self.main.data_vencimento.setDate(QDate.currentDate())

        self.row = 0
        self.rowCount = 1
        self.total_itens = 0.00

        self.main.cb_compra_fornecedor.setCurrentIndex(-1)
        self.main.cb_compra_forma_pagto.setCurrentIndex(-1)        

        self.main.dt_Produto_Compra.setRowCount(0)
        self.main.dt_Compra_Item.setRowCount(0)


    # populate table product
    def populate_table_produto(self):
        session = getSessionDB()
        produto = session.query(Produto).filter(Produto.descricao.like(f'%{self.main.search_produto_descricao_compra.text()}%')).order_by(Produto.descricao.asc()).all()

        # config data table
        self.main.dt_Produto_Compra.setRowCount(len(produto))
        self.main.dt_Produto_Compra.setColumnCount(5)
        self.main.dt_Produto_Compra.setColumnWidth(0, 30)
        self.main.dt_Produto_Compra.setColumnWidth(1, 50)
        self.main.dt_Produto_Compra.setColumnWidth(2, 470)
        self.main.dt_Produto_Compra.setColumnWidth(3, 50)


        # insert data
        for row, prod in enumerate(produto):

            # button add produto
            add_button = QPushButton(QIcon("./icons/iconAdd.png"), "")
            add_button.setToolTip("Incluir Produto")
            add_button.clicked.connect(lambda checked, row=row: self.on_click_button_add_produto(row))
           
            self.main.dt_Produto_Compra.setCellWidget(row, 0, add_button)
            self.main.dt_Produto_Compra.setItem(row, 1, QTableWidgetItem(str(prod.id)))
            self.main.dt_Produto_Compra.setItem(row, 2, QTableWidgetItem(str(prod.descricao)))
            self.main.dt_Produto_Compra.setItem(row, 3, QTableWidgetItem(str(prod.qtde)))
            self.main.dt_Produto_Compra.setItem(row, 4, QTableWidgetItem(str(prod.preco_custo).replace('.', ',')))

            set_table_row_color(row, self.main.dt_Produto_Compra)

        # close session
        session.close()


    # populate data table compra
    def populate_data_table_compra(self, flagQueryByUser=None):

        total_compras = 0
        data_inicial = self.main.compra_data_inicial.date().toPython()
        data_final = self.main.compra_data_final.date().toPython()

        session = getSessionDB()

        if flagQueryByUser:
            compras = session.query(Compra).join(Fornecedor).filter(
                                                            Fornecedor.nome.like(f'%{self.main.search_compra_fornecedor_nome.text()}%'),
                                                            Compra.data_emissao >= data_inicial,
                                                            Compra.data_emissao <= data_final).order_by(Compra.data_emissao.desc()).all()
        else:
            compras = session.query(Compra).order_by(Compra.data_emissao.desc()).all()

        self.main.dt_Compra.setRowCount(len(compras))
        self.main.dt_Compra.setColumnCount(14)
        self.main.dt_Compra.setColumnWidth(0, 50)
        self.main.dt_Compra.setColumnWidth(1, 50)
        self.main.dt_Compra.setColumnWidth(2, 120)
        self.main.dt_Compra.setColumnWidth(3, 250)
        self.main.dt_Compra.setColumnWidth(4, 300)
        self.main.dt_Compra.setColumnWidth(6, 550)
        self.main.dt_Compra.setColumnWidth(11, 120)
        self.main.dt_Compra.setColumnWidth(13, 250)

        # insert data
        for row, compra in enumerate(compras):

            # button remove nota de compra
            delete_button = QPushButton(QIcon("./icons/iconTrash.png"), "")
            delete_button.setToolTip("Excluir Nota de Compra")
            delete_button.clicked.connect(self.on_click_button_delete_compra)
           
            self.main.dt_Compra.setCellWidget(row, 0, delete_button)

            # id - 1
            id_nota = QTableWidgetItem(str(compra.id))
            self.main.dt_Compra.setItem(row, 1, id_nota)
            id_nota.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # nota nro - 2
            nota_nro = QTableWidgetItem(compra.nro_nota)
            self.main.dt_Compra.setItem(row, 2, nota_nro)
            nota_nro.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.main.dt_Compra.setItem(row, 3, QTableWidgetItem(str(compra.fornecedor.nome)))

            # Ítens na Nota - 4
            combo_box_itens = QComboBox()
            for itens in compra.compra_item:
                combo_box_itens.addItem(str(itens))
            self.main.dt_Compra.setCellWidget(row, 4, combo_box_itens)

            # total - 5
            total = QTableWidgetItem(f'{compra.total:>9.2f}'.replace('.', ','))
            self.main.dt_Compra.setItem(row, 5, total)
            total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # contas a pagar - 6
            if compra.conta_pagar:
                combo_box_conta_pagar = QComboBox()
                for conta in compra.conta_pagar:
                    combo_box_conta_pagar.addItem(str(conta))
                self.main.dt_Compra.setCellWidget(row, 6, combo_box_conta_pagar)
            else:
                self.main.dt_Compra.setItem(row, 6, QTableWidgetItem('À Vista'))

            # frete - 7
            frete = QTableWidgetItem(f'{compra.frete:>9.2f}'.replace('.', ','))
            self.main.dt_Compra.setItem(row, 7, frete)
            frete.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # desconto - 8
            desconto = QTableWidgetItem(f'{compra.desconto:>9.2f}'.replace('.', ','))
            self.main.dt_Compra.setItem(row, 8, desconto)
            desconto.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.main.dt_Compra.setItem(row, 9, QTableWidgetItem(str(compra.data_emissao.strftime('%d/%m/%Y'))))
            self.main.dt_Compra.setItem(row,10, QTableWidgetItem(str(compra.data_entrega.strftime('%d/%m/%Y'))))
            self.main.dt_Compra.setItem(row,11, QTableWidgetItem(str(compra.data_vencimento.strftime('%d/%m/%Y'))))

            if compra.forma_pagto:
                self.main.dt_Compra.setItem(row,12, QTableWidgetItem(compra.forma_pagto.descricao))
            else:
                self.main.dt_Compra.setItem(row,12, QTableWidgetItem(''))

            self.main.dt_Compra.setItem(row,13, QTableWidgetItem(compra.observacao))

            set_table_row_color(row, self.main.dt_Compra)

            total_compras += compra.total
        
        self.main.lbl_compra_total_value.setText(f'TOTAL COMPRAS R$ {str(total_compras).replace('.', ',')}')

        # close session
        session.close()


    # on click button delete compra
    def on_click_button_delete_compra(self, e):
        idCompra = self.main.dt_Compra.item(self.main.dt_Compra.currentRow(), 1).text()
        nroNota = self.main.dt_Compra.item(self.main.dt_Compra.currentRow(), 2).text()

        if QMessageBox.question(self.main, 'Excluir Nota de Compra', f'Tem certeza que deseja excluir Nota de Compra: "{nroNota}"?',
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
        
            session = getSessionDB()
            compra = session.query(Compra).filter_by(id=idCompra).first()

            try:
                session.delete(compra)
                session.commit()
                session.close()
            except SQLAlchemyError as err:
                error_message = str(err).split('\n')[0]
                QMessageBox.warning(self.main, 'Erro', f'Nota de Compra: "{nroNota}" não pode ser excluído\n{error_message}.')
                session.close()
                return None

        self.main.dt_Compra.removeRow(self.main.dt_Compra.currentRow())


    # on click button add compra
    def on_click_button_add_compra(self, e):

        self.main.supplier.populate_combo_box_fornecedor()
        self.main.payt_meth.populate_combo_box_forma_pagto()

        self.clear_fields_form_compra()

        self.main.nro_nota.setFocus()

        self.main.forms.setCurrentWidget(self.main.formCadastroCompra)


    # on click button add produto
    def on_click_button_add_produto(self, row):
        
        # 
        id = self.main.dt_Produto_Compra.item(row, 1).text()
        descricao = self.main.dt_Produto_Compra.item(row, 2).text()

        # spin box
        qtde = self.main.sb_compra_qtde.value()
        preco_custo = self.main.sb_compra_preco_custo.value()

        if not qtde:
            QMessageBox.warning(self.main, "Aviso", '"Quantidade" deve ser Informada.')
            return None
        
        if not preco_custo:
            QMessageBox.warning(self.main, "Aviso", '"Preço Custo" deve ser Informada.')
            return None

        for row in range(self.main.dt_Compra_Item.rowCount()):
            item = self.main.dt_Compra_Item.item(row, 1).text()
            if id == item:
                QMessageBox.warning(self.main, "Aviso", '"Produto" já adicionado à nota.')
                return None
        
        total = qtde * preco_custo
        self.total_itens += total
        self.main.sb_total_compra.setValue(self.total_itens)

        self.main.lbl_total_itens.setText(f'Total Ítens R$ {self.total_itens:.2f}'.replace('.', ','))
        
        self.main.dt_Compra_Item.setColumnCount(7)
        self.main.dt_Compra_Item.setRowCount(self.rowCount)

        self.main.dt_Compra_Item.setColumnWidth(0, 30)
        self.main.dt_Compra_Item.setColumnWidth(1, 50)
        self.main.dt_Compra_Item.setColumnWidth(2, 330)
        self.main.dt_Compra_Item.setColumnWidth(3, 50)
        self.main.dt_Compra_Item.setColumnWidth(4, 60)
        self.main.dt_Compra_Item.setColumnWidth(5, 60)
        self.main.dt_Compra_Item.setColumnWidth(6, 140)

        delete_button = QPushButton(QIcon("./icons/iconTrash.png"), "")
        delete_button.setToolTip("Excluir Produto")
        delete_button.clicked.connect(lambda checked, row=row: self.on_click_button_delete_produto(row))
        
        self.main.dt_Compra_Item.setCellWidget(self.row, 0, delete_button)
        self.main.dt_Compra_Item.setItem(self.row, 1, QTableWidgetItem(id))
        self.main.dt_Compra_Item.setItem(self.row, 2, QTableWidgetItem(descricao))
        self.main.dt_Compra_Item.setItem(self.row, 3, QTableWidgetItem(str(qtde)))
        self.main.dt_Compra_Item.setItem(self.row, 4, QTableWidgetItem(f"{preco_custo:.2f}".replace('.', ',')))
        self.main.dt_Compra_Item.setItem(self.row, 5, QTableWidgetItem(f"{total:.2f}".replace('.', ',')))
        
        lblAtualizaPrecoCusto = 'Não'
        if self.main.chk_compra_atualiza_preco_custo.isChecked():
            lblAtualizaPrecoCusto = 'Sim'
        self.main.dt_Compra_Item.setItem(self.row, 6, QTableWidgetItem(lblAtualizaPrecoCusto))

        self.main.sb_compra_qtde.setValue(0)
        self.main.sb_compra_preco_custo.setValue(0.00)
        self.main.chk_compra_atualiza_preco_custo.setChecked(False)

        # increment row
        self.row += 1
        self.rowCount += 1


    # on click button delete produto
    def on_click_button_delete_produto(self, row):

        total = self.main.dt_Compra_Item.item(self.main.dt_Compra_Item.currentRow(), 5)

        if total:
            
            self.row -= 1
            self.rowCount -= 1

            self.total_itens -= float(total.text().replace(',', '.'))
            self.main.sb_total_compra.setValue(self.total_itens)
            self.main.lbl_total_itens.setText(f'Total Ítens R$ {self.total_itens:.2f}'.replace('.', ','))

        self.main.dt_Compra_Item.removeRow(self.main.dt_Compra_Item.currentRow())

        if not self.main.dt_Compra_Item.rowCount():

            self.main.lbl_total_itens.setText('Total Ítens R$')

            self.row = 0
            self.rowCount = 1
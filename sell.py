# coding=utf-8
from qt_core import QTableWidgetItem, QMessageBox, QPushButton, QComboBox, QIcon, QDate, Qt, QDoubleSpinBox

# app
from utils import set_table_row_color, get_values_data_table, proximo_mes, get_mes_ano_referencia
from models import Produto, Venda, VendaItem, Cliente, FormaPagto, ContaReceber, getSessionDB, SQLAlchemyError


# Purchase
class Sell:

    def __init__(self, main):
        self.main = main

        # button 
        self.main.btn_form_venda.clicked.connect(self.on_click_button_form_venda)

        # button add venda
        self.main.btn_add_venda.clicked.connect(self.on_click_button_add_venda)

        # button save venda
        self.main.btn_save_venda.clicked.connect(self.on_click_button_save_venda)

        # button goback data table venda
        self.main.btn_goback_venda.clicked.connect(self.on_click_button_goback_form_data_table_venda)

        # button search pedido venda
        self.main.btn_search_pedido_venda.clicked.connect(self.on_click_button_search_pedido_cliente)

        # btn refresh data table venda
        self.main.btn_refresh_data_table_venda.clicked.connect(self.on_click_button_refresh_data_table_venda)

        # on_change search produto descricao venda
        self.main.search_produto_descricao_venda.textChanged.connect(self.populate_table_produto)


    # on click button form venda
    def on_click_button_form_venda(self, e):

        self.main.venda_data_inicial.setDate(QDate.currentDate())
        self.main.venda_data_final.setDate(QDate.currentDate())
        
        self.populate_data_table_venda()

        self.main.search_pedido_cliente_nome.setFocus()

        self.main.forms.setCurrentWidget(self.main.formDataTableVenda)


    # on click button goback form data table venda
    def on_click_button_goback_form_data_table_venda(self, e):
        self.main.forms.setCurrentWidget(self.main.formDataTableVenda)

    
    # on click button search pedido venda
    def on_click_button_search_pedido_cliente(self, e):
        self.populate_data_table_venda(flagQueryByUser=True)


    # on click button refresh data table venda
    def on_click_button_refresh_data_table_venda(self, e):
        self.populate_data_table_venda()


    # on click button save venda
    def on_click_button_save_venda(self, e):

        session = getSessionDB()

        # combo box cliente
        if not self.main.cb_venda_cliente.currentText():
            QMessageBox.warning(self.main, "Aviso", 'Cliente: deve ser selecionado.')
            self.main.cb_venda_cliente.setFocus()
            return None

        if not session.query(Cliente.id).filter_by(nome=self.main.cb_venda_cliente.currentText()).first():
            QMessageBox.warning(self.main, "Aviso", f'Cliente: "{self.main.cb_venda_cliente.currentText()}" não cadastrado.')
            self.main.cb_venda_cliente.setFocus()
            session.close()
            return None
        
        if not self.main.chk_gerar_conta_receber.isChecked():
            if not self.main.cb_venda_forma_pagto.currentText():
                QMessageBox.warning(self.main, "Aviso", f'Forma de pagamento deve ser selecionada.')
                self.main.cb_venda_forma_pagto.setFocus()
                return None

            # combo box forma de pagto
            if not session.query(FormaPagto.id).filter_by(descricao=self.main.cb_venda_forma_pagto.currentText()).first():
                QMessageBox.warning(self.main, "Aviso", f'Forma de pagamento: "{self.main.cb_venda_forma_pagto.currentText()}" não cadastrada.')
                self.main.cb_venda_forma_pagto.setFocus()
                session.close()
                return None

        # total pedido
        if not self.main.sb_total_venda.value():
            QMessageBox.warning(self.main, "Aviso", 'Campo "TOTAL" deve ser informado.')
            self.main.sb_total_venda.setFocus()
            return None

        # items na pedido
        if not self.main.dt_Venda_Item.rowCount():
            QMessageBox.warning(self.main, "Aviso", f'Deve ser informado um "PRODUTO" no pedido pelo menos.')
            return None
        
        # validar valores da pedido de venda
        if not (
            self.main.sb_venda_desconto.value() +
            self.main.sb_venda_frete.value() +
            self.total_itens) == self.main.sb_total_venda.value():

            QMessageBox.warning(self.main, "Aviso",
                f'Valores informados no Pedido estão divergentes.\nDesconto: R$ {self.main.sb_venda_desconto.value()} + Frete: R$ {self.main.sb_venda_frete.value()} + Total Itens: R$ {self.total_itens}\ndevem ser igual ao Total: R$ :{self.main.sb_total_venda.value()}')
            return None

        # check button contas a receber
        statusVenda = 'À Vista'
        if self.main.chk_gerar_conta_receber.isChecked():
            statusVenda = 'À Prazo'
            forma_pagto_id = ''
            if not self.main.sb_nro_parcelas_venda.value():
                QMessageBox.warning(self.main, "Aviso", f'Para gerar Contas a Receber "NRO PARCELAS" deve ser informado.')
                return None
        else:
            forma_pagto_id = session.query(FormaPagto.id).filter_by(descricao=self.main.cb_venda_forma_pagto.currentText()).first()[0]

        venda = Venda(
                status = statusVenda,
                data_emissao = self.main.data_emissao_venda.date().toPython(),
                data_entrega = self.main.data_entrega_venda.date().toPython(),
                data_vencimento = self.main.data_vencimento_venda.date().toPython(),
                
                desconto = self.main.sb_venda_desconto.value(),
                frete = self.main.sb_venda_frete.value(),
                total = self.main.sb_total_venda.value(),

                cliente_id = session.query(Cliente.id).filter_by(nome=self.main.cb_venda_cliente.currentText()).first()[0],
                forma_pagto_id = forma_pagto_id,

                observacao = self.main.venda_observacao.text()
            )

        # pedido de Venda
        try:
            session.add(venda)
            session.commit()

        except SQLAlchemyError as err:
            error_message = str(err).split('\n')[0]
            QMessageBox.warning(self.main,  "Erro", f'Não foi possível salvar o Pedido.\n{error_message}')
            return None

        # get all itens da pedido de Venda
        for row in get_values_data_table(self.main.dt_Venda_Item):

            vendaItem = VendaItem(
                    venda_id = venda.id,
                    produto_id = row[1],
                    qtde = row[3],
                    preco = row[4].replace(',', '.'))

            session.add(vendaItem)

        try:
            session.commit()
        except SQLAlchemyError as err:
            error_message = str(err).split('\n')[0]
            QMessageBox.warning(self.main,  "Erro", f'Não foi possível Inserir os Ítens no Pedido.\n{error_message}')
            session.close()
            return None

        # contas a receber
        if self.main.chk_gerar_conta_receber.isChecked():
                
            data_inicial = self.main.data_vencimento_venda.date().toPython()

            for parcela in range(self.main.sb_nro_parcelas_venda.value()):

                mes, ano = get_mes_ano_referencia(data_inicial)
    
                nova_conta = ContaReceber(
                        descricao = f'Recebimento Cliente: {self.main.cb_venda_cliente.currentText()[:20]}',
                        referencia = f'"{mes}/{ano}" Parcela {parcela+1} de {self.main.sb_nro_parcelas_venda.value()}.',
                        data_vcto = data_inicial,
                        data_pagto = data_inicial,
                        valor_titulo = self.main.sb_total_venda.value(),
                        valor_parcela = round(self.main.sb_total_venda.value() / self.main.sb_nro_parcelas_venda.value(), 2),
                        venda_id = venda.id,
                        cliente_id = venda.cliente_id,
                        doc_numero = venda.id)

                session.add(nova_conta)
                data_inicial = proximo_mes(data_inicial.day, data_inicial)

            try:
                session.commit()
            except SQLAlchemyError as err:
                error_message = str(err).split('\n')[0]
                QMessageBox.warning(self.main,  "Erro", f'Não foi possível Gerar Contas a Receber.\n{error_message}')
                session.close()
                return None

        self.clear_fields_form_venda()
        self.populate_data_table_venda()
        self.main.forms.setCurrentWidget(self.main.formDataTableVenda)
        session.close()


    # clear fields form venda
    def clear_fields_form_venda(self):
        self.main.sb_venda_desconto.setValue(0.00)
        self.main.sb_venda_frete.setValue(0.00)
        self.main.sb_venda_qtde.setValue(1)
        self.main.sb_total_venda.setValue(0.00)
        self.main.sb_nro_parcelas_venda.setValue(0)
        self.main.chk_gerar_conta_receber.setChecked(False)
        self.main.search_produto_descricao_venda.setText('')
        self.main.venda_observacao.setText('')
        self.main.lbl_total_itens_venda.setText('Total Ítens R$')

        self.main.data_emissao_venda.setDate(QDate.currentDate())
        self.main.data_entrega_venda.setDate(QDate.currentDate())
        self.main.data_vencimento_venda.setDate(QDate.currentDate())

        self.row = 0
        self.rowCount = 1
        self.total_itens = 0.00

        self.main.cb_venda_cliente.setCurrentIndex(-1)
        self.main.cb_venda_forma_pagto.setCurrentIndex(-1)        

        self.main.dt_Produto_Venda.setRowCount(0)
        self.main.dt_Venda_Item.setRowCount(0)


    # populate data table venda
    def populate_data_table_venda(self, flagQueryByUser=None):

        total_vendas = 0
        data_inicial = self.main.venda_data_inicial.date().toPython()
        data_final = self.main.venda_data_final.date().toPython()

        session = getSessionDB()

        if flagQueryByUser:
            vendas = session.query(Venda).join(Cliente).filter(
                                                        Cliente.nome.like(f'%{self.main.search_pedido_cliente_nome.text()}%'),
                                                        Venda.data_emissao >= data_inicial,
                                                        Venda.data_emissao <= data_final).order_by(Venda.data_emissao.desc()).all()
        else:
            vendas = session.query(Venda).order_by(Venda.data_emissao.desc()).all()


        self.main.dt_Venda.setRowCount(len(vendas))
        self.main.dt_Venda.setColumnCount(13)
        self.main.dt_Venda.setColumnWidth(0, 50)
        self.main.dt_Venda.setColumnWidth(1, 50)
        self.main.dt_Venda.setColumnWidth(2, 200)
        self.main.dt_Venda.setColumnWidth(3, 250)
        self.main.dt_Venda.setColumnWidth(5, 550)
        self.main.dt_Venda.setColumnWidth(10, 140)
        self.main.dt_Venda.setColumnWidth(13, 250)

        # insert data
        for row, venda in enumerate(vendas):

            # button remove pedido de venda
            delete_button = QPushButton(QIcon("./icons/iconTrash.png"), "")
            delete_button.setToolTip("Excluir Pedido")
            delete_button.clicked.connect(self.on_click_button_delete_venda)
           
            self.main.dt_Venda.setCellWidget(row, 0, delete_button)

            # id - 1
            id_pedido = QTableWidgetItem(str(venda.id))
            self.main.dt_Venda.setItem(row, 1, id_pedido)
            id_pedido.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.main.dt_Venda.setItem(row, 2, QTableWidgetItem(str(venda.cliente.nome)))

            # Ítens no pedido - 3
            combo_box_itens = QComboBox()
            for itens in venda.venda_item:
                combo_box_itens.addItem(str(itens))
            self.main.dt_Venda.setCellWidget(row, 3, combo_box_itens)

            # total - 4
            total = QTableWidgetItem(f'{venda.total:>9.2f}'.replace('.', ','))
            self.main.dt_Venda.setItem(row, 4, total)
            total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # contas a pagar - 5
            if venda.conta_receber:
                combo_box_conta_receber = QComboBox()
                for conta in venda.conta_receber:
                    combo_box_conta_receber.addItem(str(conta))
                self.main.dt_Venda.setCellWidget(row, 5, combo_box_conta_receber)
            else:
                self.main.dt_Venda.setItem(row, 5, QTableWidgetItem('À Vista'))

            # frete - 6
            frete = QTableWidgetItem(f'{venda.frete:>9.2f}'.replace('.', ','))
            self.main.dt_Venda.setItem(row, 6, frete)
            frete.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # desconto - 7
            desconto = QTableWidgetItem(f'{venda.desconto:>9.2f}'.replace('.', ','))
            self.main.dt_Venda.setItem(row, 7, desconto)
            desconto.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.main.dt_Venda.setItem(row, 8, QTableWidgetItem(str(venda.data_emissao.strftime('%d/%m/%Y'))))
            self.main.dt_Venda.setItem(row, 9, QTableWidgetItem(str(venda.data_entrega.strftime('%d/%m/%Y'))))
            self.main.dt_Venda.setItem(row,10, QTableWidgetItem(str(venda.data_vencimento.strftime('%d/%m/%Y'))))

            if venda.forma_pagto:
                self.main.dt_Venda.setItem(row,11, QTableWidgetItem(venda.forma_pagto.descricao))
            else:
                self.main.dt_Venda.setItem(row,11, QTableWidgetItem(''))

            self.main.dt_Venda.setItem(row,12, QTableWidgetItem(venda.observacao))

            set_table_row_color(row, self.main.dt_Venda)
        
            total_vendas += venda.total
        
        self.main.lbl_venda_total_value.setText(f'TOTAL VENDAS R$ {str(total_vendas).replace('.', ',')}')
        
        # close session
        session.close()


    # on click button delete venda
    def on_click_button_delete_venda(self, e):
        idVenda = self.main.dt_Venda.item(self.main.dt_Venda.currentRow(), 1).text()

        if QMessageBox.question(self.main, 'Excluir Pedido', f'Tem certeza que deseja excluir Pedido: "{idVenda}"?',
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
        
            session = getSessionDB()
            venda = session.query(Venda).filter_by(id=idVenda).first()

            try:
                session.delete(venda)
                session.commit()
                session.close()
            except SQLAlchemyError as err:
                error_message = str(err).split('\n')[0]
                QMessageBox.warning(self.main, 'Erro', f'Pedido: "{idVenda}" não pode ser excluído\n{error_message}.')
                session.close()
                return None

        self.main.dt_Venda.removeRow(self.main.dt_Venda.currentRow())


    # on click button add venda
    def on_click_button_add_venda(self, e):

        self.main.client.populate_combo_box_cliente()
        self.main.payt_meth.populate_combo_box_forma_pagto()

        self.clear_fields_form_venda()

        self.main.data_emissao_venda.setFocus()

        self.main.forms.setCurrentWidget(self.main.formCadastroVenda)


    # populate table product
    def populate_table_produto(self):
        session = getSessionDB()
        produto = session.query(Produto).filter(Produto.descricao.like(f'%{self.main.search_produto_descricao_venda.text()}%')).order_by(Produto.descricao.asc()).all()

        # config data table
        self.main.dt_Produto_Venda.setRowCount(len(produto))
        self.main.dt_Produto_Venda.setColumnCount(7)
        self.main.dt_Produto_Venda.setColumnWidth(0, 30)
        self.main.dt_Produto_Venda.setColumnWidth(1, 50)
        self.main.dt_Produto_Venda.setColumnWidth(2, 250)
        self.main.dt_Produto_Venda.setColumnWidth(3, 50)
        self.main.dt_Produto_Venda.setColumnWidth(6, 120)

        # insert data
        for row, prod in enumerate(produto):

            # button add produto
            add_button = QPushButton(QIcon("./icons/iconAdd.png"), "")
            add_button.setToolTip("Incluir Produto")
            add_button.clicked.connect(lambda checked, row=row: self.on_click_button_add_produto(row))
           
            self.main.dt_Produto_Venda.setCellWidget(row, 0, add_button)
            self.main.dt_Produto_Venda.setItem(row, 1, QTableWidgetItem(str(prod.id)))
            self.main.dt_Produto_Venda.setItem(row, 2, QTableWidgetItem(str(prod.descricao)))
            self.main.dt_Produto_Venda.setItem(row, 3, QTableWidgetItem(str(prod.qtde)))

            preco_varejo = QDoubleSpinBox(maximum=9999999.99)
            preco_varejo.setValue(prod.preco_varejo)
            self.main.dt_Produto_Venda.setCellWidget(row, 4, preco_varejo)
            
            preco_atacado = QDoubleSpinBox(maximum=9999999.99)
            preco_atacado.setValue(prod.preco_atacado)
            self.main.dt_Produto_Venda.setCellWidget(row, 5, preco_atacado)

            self.main.dt_Produto_Venda.setItem(row, 6, QTableWidgetItem(str(prod.qtde_atacado)))

            set_table_row_color(row, self.main.dt_Produto_Venda)

        # close session
        session.close()


    # on click button add produto
    def on_click_button_add_produto(self, row):
        
        # 
        id = self.main.dt_Produto_Venda.item(row, 1).text()
        descricao = self.main.dt_Produto_Venda.item(row, 2).text()
        preco = self.main.dt_Produto_Venda.cellWidget(row, 4).value()
        preco_atacado = self.main.dt_Produto_Venda.cellWidget(row, 5).value()
        qtde_atacado = int(self.main.dt_Produto_Venda.item(row, 6).text())

        # spin box
        qtde = self.main.sb_venda_qtde.value()
        
        if not qtde:
            QMessageBox.warning(self.main, "Aviso", '"Quantidade" deve ser Informada.')
            return None

        # qtde atacado
        if qtde_atacado:
            if qtde >= qtde_atacado:
                preco = preco_atacado

        for row in range(self.main.dt_Venda_Item.rowCount()):
            item = self.main.dt_Venda_Item.item(row, 1).text()
            if id == item:
                QMessageBox.warning(self.main, "Aviso", '"Produto" já adicionado ao pedido.')
                return None
        
        total = qtde * preco
        self.total_itens += total
        self.main.sb_total_venda.setValue(self.total_itens)

        self.main.lbl_total_itens_venda.setText(f'Total Ítens R$ {self.total_itens:.2f}'.replace('.', ','))
        
        self.main.dt_Venda_Item.setColumnCount(6)
        self.main.dt_Venda_Item.setRowCount(self.rowCount)

        self.main.dt_Venda_Item.setColumnWidth(0, 30)
        self.main.dt_Venda_Item.setColumnWidth(1, 50)
        self.main.dt_Venda_Item.setColumnWidth(2, 330)
        self.main.dt_Venda_Item.setColumnWidth(3, 50)
        self.main.dt_Venda_Item.setColumnWidth(4, 60)
        self.main.dt_Venda_Item.setColumnWidth(5, 60)
        self.main.dt_Venda_Item.setColumnWidth(6, 140)

        delete_button = QPushButton(QIcon("./icons/iconTrash.png"), "")
        delete_button.setToolTip("Excluir Produto")
        delete_button.clicked.connect(lambda checked, row=row: self.on_click_button_delete_produto(row))
        
        self.main.dt_Venda_Item.setCellWidget(self.row, 0, delete_button)
        self.main.dt_Venda_Item.setItem(self.row, 1, QTableWidgetItem(id))
        self.main.dt_Venda_Item.setItem(self.row, 2, QTableWidgetItem(descricao))
        self.main.dt_Venda_Item.setItem(self.row, 3, QTableWidgetItem(str(qtde)))
        self.main.dt_Venda_Item.setItem(self.row, 4, QTableWidgetItem(f"{preco:.2f}".replace('.', ',')))
        self.main.dt_Venda_Item.setItem(self.row, 5, QTableWidgetItem(f"{total:.2f}".replace('.', ',')))
        
        self.main.sb_venda_qtde.setValue(1)

        # increment row
        self.row += 1
        self.rowCount += 1


    # on click button delete produto
    def on_click_button_delete_produto(self, row):

        total = self.main.dt_Venda_Item.item(self.main.dt_Venda_Item.currentRow(), 5)

        if total:
            
            self.row -= 1
            self.rowCount -= 1

            self.total_itens -= float(total.text().replace(',', '.'))
            self.main.sb_total_venda.setValue(self.total_itens)
            self.main.lbl_total_itens_venda.setText(f'Total Ítens R$ {self.total_itens:.2f}'.replace('.', ','))

        self.main.dt_Venda_Item.removeRow(self.main.dt_Venda_Item.currentRow())

        if not self.main.dt_Venda_Item.rowCount():

            self.main.lbl_total_itens_venda.setText('Total Ítens R$')

            self.row = 0
            self.rowCount = 1
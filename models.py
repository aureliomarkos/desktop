# coding=utf-8

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, DateTime, Date, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

#
Base = declarative_base()


# connect sqlite 
def getSessionDB():

    # Engine, echo=True
    engine = create_engine('sqlite:///db/stok.db')

    # Create table if not exists
    Base.metadata.create_all(engine)
        
    # Create Session
    Session = sessionmaker(bind=engine)
    return Session()


# Tabela Categoria de produtos
class Categoria(Base):
    __tablename__ = 'categoria'
    id = Column(Integer, primary_key=True)
    descricao = Column(String(50), index=True, unique=True)
    ativo = Column(Integer, default=1)

    def __repr__(self):
        return self.descricao


# Tabela Marca Produtos
class Marca(Base):
    __tablename__ = 'marca'
    id = Column(Integer, primary_key=True)
    descricao = Column(String(50), index=True, unique=True)
    ativo = Column(Integer, default=1)

    def __repr__(self):
        return self.descricao


# Tabela Forma de Pagamentos
class FormaPagto(Base):
    __tablename__ = 'forma_pagto'
    id = Column(Integer, primary_key=True)
    descricao = Column(String(50), index=True, unique=True)
    ativo = Column(Integer, default=1)

    def __repr__(self):
        return self.descricao


# Tabela Produtos
class Produto(Base):
    __tablename__ = 'produto'

    id = Column(Integer, primary_key=True)
    descricao = Column(String(100), index=True, unique=True)
    imagem = Column(LargeBinary)
    observacao = Column(String(100))

    unidade = Column(String(3))
    qtde = Column(Integer, default=0)
    qtde_atacado = Column(Integer, default=0)
    estoque_minimo = Column(Integer, default=0)
    estoque_maximo = Column(Integer, default=0)

    preco_custo = Column(Numeric(9, 2), default='0.00')
    preco_varejo = Column(Numeric(9, 2), default='0.00')
    preco_atacado = Column(Numeric(9, 2), default='0.00')

    ativo = Column(Integer, default=1)

    # Chave estrangeira
    categoria_id = Column(Integer, ForeignKey('categoria.id'))
    marca_id = Column(Integer, ForeignKey('marca.id'))

    # Relacionamentos
    marca = relationship('Marca')
    categoria = relationship('Categoria')
    venda_item = relationship('VendaItem', back_populates='produto')
    compra_item = relationship('CompraItem', back_populates='produto')

    def __repr__(self):
        return self.descricao


# Tabela Centro de Custo
class CentroCusto(Base):
    __tablename__ = 'centro_custo'

    id = Column(Integer, primary_key=True)
    descricao = Column(String(50), index=True, unique=True)
    tipo = Column(String(7))

    ativo = Column(Integer, default=1)

    def __repr__(self):
        return self.descricao


# Tabela Fornecedor
class Fornecedor(Base):
    __tablename__ = 'fornecedor'
    id = Column(Integer, primary_key=True)

    nome = Column(String(80), index=True, unique=True)
    razao_social = Column(String(80))

    cnpj = Column(String(20), unique=True)
    inscricao_estadual = Column(String(20), unique=True)

    telefone = Column(String(20))
    email = Column(String(80))
    site = Column(String(80))
    observacao = Column(String(100))
    ativo = Column(Integer, default=1)

    cep = Column(String(9))
    rua = Column(String(80))
    numero = Column(String(10))
    bairro = Column(String(40))
    cidade = Column(String(50))
    estado = Column(String(2))
    complemento = Column(String(40))

    # Relacionamento com a tabela Compra
    compra = relationship('Compra', back_populates='fornecedor')
    conta_pagar = relationship('ContaPagar', back_populates='fornecedor')

    def __repr__(self):
        return self.nome


# Tabela Contas a Pagar
class ContaPagar(Base):
    __tablename__ = 'conta_pagar'

    id = Column(Integer, primary_key=True)
    descricao = Column(String(80))
    referencia = Column(String(80))
    doc_numero = Column(String(20))
    status = Column(String(15), default='Aberto')

    data_vcto = Column(Date)
    data_pagto = Column(Date)

    valor_titulo = Column(Numeric(9, 2), default='0.00')
    valor_parcela = Column(Numeric(9, 2), default='0.00')
    valor_pago = Column(Numeric(9, 2), default='0.00')

    # chave estrangeira
    compra_id = Column(Integer, ForeignKey('compra.id', ondelete='CASCADE'), nullable=True)
    fornecedor_id = Column(Integer, ForeignKey('fornecedor.id'))
    forma_pagto_id = Column(Integer, ForeignKey('forma_pagto.id'), nullable=True)
    centro_custo_id = Column(Integer, ForeignKey('centro_custo.id'), default=1)

    # Relacionamentos
    compra = relationship('Compra', back_populates='conta_pagar')
    fornecedor = relationship('Fornecedor')
    forma_pagto = relationship('FormaPagto')
    centro_custo = relationship("CentroCusto")

    def __repr__(self):
        return f'Ref: {self.referencia} {self.descricao[:20]} Vcto: {self.data_vcto.strftime('%d/%m/%Y')} Valor: {str(self.valor_parcela).replace('.', ',')} Status: {self.status}'


# Tabela Compras
class Compra(Base):
    __tablename__ = 'compra'

    id = Column(Integer, primary_key=True)
    nro_nota = Column(String(16))
    status = Column(String(6))
    observacao = Column(String(80))

    data_emissao = Column(Date)
    data_entrega = Column(Date)
    data_vencimento = Column(Date)

    frete = Column(Numeric(9, 2), default='0.00')
    total = Column(Numeric(9, 2), default='0.00')
    desconto = Column(Numeric(9, 2), default='0.00')

    # Chave estrangeira
    fornecedor_id = Column(Integer, ForeignKey('fornecedor.id'))
    forma_pagto_id = Column(Integer, ForeignKey('forma_pagto.id'))

    # Relacionamentos
    fornecedor = relationship('Fornecedor')
    forma_pagto = relationship('FormaPagto')
    compra_item = relationship('CompraItem', cascade="all, delete", back_populates='compra')
    conta_pagar = relationship('ContaPagar', cascade="all, delete", back_populates='compra')

    def __repr__(self):
        return f'ID: {self.id} {self.fornecedor.nome} Data Emissão: {self.data_emissao.strftime('%d/%m/%Y')} Valor R$: {str(self.total).replace('.', ',')}'


# Tabela itens comprados
class CompraItem(Base):
    __tablename__ = 'compra_item'

    id = Column(Integer, primary_key=True)
    qtde = Column(Integer)
    preco = Column(Numeric(9, 2), default='0.00')

    # Chave estrangeira
    compra_id = Column(Integer, ForeignKey('compra.id', ondelete='CASCADE'))
    produto_id = Column(Integer, ForeignKey('produto.id'))

    # Relacionamentos
    produto = relationship('Produto')
    compra = relationship('Compra', back_populates='compra_item')

    def __repr__(self):
        return f'ID: {self.produto_id} - {self.produto.descricao} Qtde: {self.qtde} R$: {str(self.preco).replace('.', ',')}'


# tabela Cliente
class Cliente(Base):
    __tablename__ = 'cliente'
    id = Column(Integer, primary_key=True)
    nome = Column(String(80), index=True, unique=True)

    cpf = Column(String(14), unique=True)
    rg = Column(String(15))

    telefone = Column(String(20))
    email = Column(String(80))
    observacao = Column(String(100))
    ativo = Column(Integer, default=1)

    cep = Column(String(9))
    rua = Column(String(80))
    numero = Column(String(10))
    bairro = Column(String(40))
    cidade = Column(String(50))
    estado = Column(String(2))
    complemento = Column(String(40))

    # Relacionamento com a tabela Venda
    venda = relationship('Venda', back_populates='cliente')
    conta_receber = relationship('ContaReceber', back_populates='cliente')


    def __repr__(self):
        return self.nome


# Tabela Contas a Receber
class ContaReceber(Base):
    __tablename__ = 'conta_receber'

    id = Column(Integer, primary_key=True)
    descricao = Column(String(80))
    referencia = Column(String(80))
    doc_numero = Column(String(20))
    status = Column(String(15), default='Aberto')

    data_vcto = Column(Date)
    data_pagto = Column(Date)

    valor_titulo = Column(Numeric(9, 2), default='0.00')
    valor_parcela = Column(Numeric(9, 2), default='0.00')
    valor_pago = Column(Numeric(9, 2), default='0.00')

    # chave estrangeira
    venda_id = Column(Integer, ForeignKey('venda.id', ondelete='CASCADE'), nullable=True)
    cliente_id = Column(Integer, ForeignKey('cliente.id'))
    forma_pagto_id = Column(Integer, ForeignKey('forma_pagto.id'), nullable=True)
    centro_custo_id = Column(Integer, ForeignKey('centro_custo.id'), default=2)

    # Relacionamentos
    venda = relationship('Venda', back_populates='conta_receber')
    cliente = relationship('Cliente')
    forma_pagto = relationship('FormaPagto')
    centro_custo = relationship("CentroCusto")

    def __repr__(self):
        return f'Ref: {self.referencia} {self.descricao[:20]} Vcto: {self.data_vcto.strftime('%d/%m/%Y')} Valor: {str(self.valor_parcela).replace('.', ',')} Status: {self.status}'


# Tabela Vendas
class Venda(Base):
    __tablename__ = 'venda'

    id = Column(Integer, primary_key=True)
    status = Column(String(6))
    observacao = Column(String(80))

    data_emissao = Column(Date)
    data_entrega = Column(Date)
    data_vencimento = Column(Date)

    frete = Column(Numeric(9, 2), default='0.00')
    total = Column(Numeric(9, 2), default='0.00')
    desconto = Column(Numeric(9, 2), default='0.00')

    # Chave estrangeira
    cliente_id = Column(Integer, ForeignKey('cliente.id'))
    forma_pagto_id = Column(Integer, ForeignKey('forma_pagto.id'))

    # Relacionamentos
    cliente = relationship('Cliente')
    forma_pagto = relationship('FormaPagto')
    venda_item = relationship('VendaItem', cascade="all, delete", back_populates='venda')
    conta_receber = relationship('ContaReceber', cascade="all, delete", back_populates='venda')

    def __repr__(self):
        return f'ID: {self.id} {self.cliente.nome} Data Emissão: {self.data_emissao.strftime('%d/%m/%Y')} Valor R$: {str(self.total).replace('.', ',')}'


# Tabela itens vendidos
class VendaItem(Base):
    __tablename__ = 'venda_item'

    id = Column(Integer, primary_key=True)
    qtde = Column(Integer)
    preco = Column(Numeric(9, 2), default='0.00')

    # Chave estrangeira
    venda_id = Column(Integer, ForeignKey('venda.id', ondelete='CASCADE'))
    produto_id = Column(Integer, ForeignKey('produto.id'))

    # Relacionamentos
    produto = relationship('Produto')
    venda = relationship('Venda', back_populates='venda_item')

    def __repr__(self):
        return f'ID: {self.produto_id} - {self.produto.descricao} Qtde: {self.qtde} R$: {str(self.preco).replace('.', ',')}'


# Função para inserir registros iniciais FormaPagamento
def insert_initial_records_forma_pagto(target, connection, **kw):
    Session = sessionmaker(bind=connection)
    session = Session()

    session.add_all([
                    FormaPagto(descricao='Dinheiro'),
                    FormaPagto(descricao='Pix'),
                    FormaPagto(descricao='Cartão de Débito'),
                    FormaPagto(descricao='Cartão de Crédito'),
                    FormaPagto(descricao='Boleto'),
                    FormaPagto(descricao='Transferência Bancária'),
                    FormaPagto(descricao='Cheque'),

                    ])
    session.commit()
    session.close()


# Função para inserir registros iniciais CentroCusto
def insert_initial_records_centro_custo(target, connection, **kw):
    Session = sessionmaker(bind=connection)
    session = Session()
    
    session.add_all([
                    CentroCusto(descricao='Pagamento Fornecedor', tipo='Débito'),
                    CentroCusto(descricao='Recebimento Cliente', tipo='Crédito'),
                    ])
    session.commit()
    session.close()


# Função para inserir registros iniciais Cliente
def insert_initial_records_cliente(target, connection, **kw):
    Session = sessionmaker(bind=connection)
    session = Session()
    
    session.add(Cliente(
                    nome='Cliente no Balcão',
                    cpf='',
                    rg='',
                    telefone='',
                    email='',
                    observacao='',
                    cep='',
                    rua='',
                    numero='',
                    bairro='',
                    cidade='',
                    estado='',
                    complemento=''))

    session.commit()
    session.close()


# Função para inserir registros iniciais Fornecedor
def insert_initial_records_fornecedor(target, connection, **kw):
    Session = sessionmaker(bind=connection)
    session = Session()
    
    session.add(Fornecedor(
                    nome='Fornecedor de Serviços Públicos, Internet e Afins',
                    razao_social='',
                    cnpj='',
                    inscricao_estadual='',
                    telefone='',
                    email='',
                    site='',
                    observacao='',
                    cep='',
                    rua='',
                    numero='',
                    bairro='',
                    cidade='',
                    estado='',
                    complemento=''))

    session.commit()
    session.close()


def create_trigger_venda_item(target, connection, **kw):
    Session = sessionmaker(bind=connection)
    session = Session()

    triggerVendaItemDel = \
                text(
                    """
                    CREATE TRIGGER venda_item_diminuir_qtde_produto
                    AFTER INSERT
                    ON venda_item
                    FOR EACH ROW
                    BEGIN
                        UPDATE produto SET qtde = qtde - NEW.qtde WHERE id = NEW.produto_id;
                    END;
                    """)
   
    session.execute(triggerVendaItemDel)
    
    triggerVendaItemAdd = \
                text(
                    """
                    CREATE TRIGGER venda_item_somar_qtde_produto
                    AFTER DELETE
                    ON venda_item
                    FOR EACH ROW
                    BEGIN
                        UPDATE produto SET qtde = qtde + OLD.qtde WHERE id = OLD.produto_id;
                    END;
                    """)

    session.execute(triggerVendaItemAdd)

    session.commit()
    session.close()


def create_trigger_compra_item(target, connection, **kw):
    Session = sessionmaker(bind=connection)
    session = Session()

    triggerCompraItemDel = \
                text(
                    """
                    CREATE TRIGGER compra_item_somar_qtde_produto
                    AFTER INSERT
                    ON compra_item
                    FOR EACH ROW
                    BEGIN
                        UPDATE produto SET qtde = qtde + NEW.qtde WHERE id = NEW.produto_id;
                    END;
                    """)

    session.execute(triggerCompraItemDel)

    triggerCompraItemAdd = \
                text(
                    """
                    CREATE TRIGGER compra_item_diminuir_qtde_produto
                    AFTER DELETE
                    ON compra_item
                    FOR EACH ROW
                    BEGIN
                        UPDATE produto SET qtde = qtde - OLD.qtde WHERE id = OLD.produto_id;
                    END;
                    """)

    session.execute(triggerCompraItemAdd)

    session.commit()
    session.close()


# Associar a função ao evento after_create
event.listen(FormaPagto.__table__, 'after_create', insert_initial_records_forma_pagto)
event.listen(CentroCusto.__table__, 'after_create', insert_initial_records_centro_custo)
event.listen(Cliente.__table__, 'after_create', insert_initial_records_cliente)
event.listen(Fornecedor.__table__, 'after_create', insert_initial_records_fornecedor)
event.listen(VendaItem.__table__, 'after_create', create_trigger_venda_item)
event.listen(CompraItem.__table__, 'after_create', create_trigger_compra_item)
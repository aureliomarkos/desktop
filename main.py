# coding=utf-8
import sys
from qt_core import loadUiType, QApplication

# app
from account_receivable_report import AccountReceivableReport
from down_account_receivable import DownAccountReceivable
from account_payable_report import AccountPayableReport
from down_account_payable import DownAccountPayable
from account_receivable import AccountReceivable
from account_payable import AccountPayable
from payment_method import PaymentMethod
from product_report import ProductReport
from cost_center import CostCenter
from category import Category
from purchase import Purchase
from supplier import Supplier
from product import Product
from client import Client
from logout import Logout
from brand import Brand
from home import Home
from sell import Sell


# load file main_app.ui (QtDesigner)
Ui_MainWindow, QMainWindowBase = loadUiType("main_app.ui")


# main class
class MainApp(Ui_MainWindow, QMainWindowBase):

    def __init__(self, app):
        super().__init__()
        self.setupUi(self)
        self.app = app
        
        
        # título
        self.lbl_titulo_app.setText('A & B Comércio de Eletrônicos')
        
        self.forms.setCurrentWidget(self.formHome)
        
        self.account_rec_report = AccountReceivableReport(self)
        self.account_pag_report = AccountPayableReport(self)
        self.down_account_rec = DownAccountReceivable(self)
        self.down_account_pay = DownAccountPayable(self)
        self.account_rec = AccountReceivable(self)
        self.product_report = ProductReport(self)
        self.account_pay = AccountPayable(self)
        self.payt_meth = PaymentMethod(self)
        self.cost_center = CostCenter(self)
        self.supplier = Supplier(self)
        self.purchase = Purchase(self)
        self.product = Product(self)
        self.categ = Category(self)
        self.client = Client(self)
        self.logout = Logout(self)
        self.brand = Brand(self)
        self.home = Home(self)
        self.sell = Sell(self)


# start application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp(app)
    window.show()
    sys.exit(app.exec())
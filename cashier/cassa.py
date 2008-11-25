# -*- coding=utf-8 -*-

from PyQt4 import QtCore, QtGui
import sys

import Pyro.core
import Pyro.protocol
import Pyro.constants
import Pyro.errors
from db import Object as Object
import ConfigParser

class MainWindow(QtGui.QMainWindow):
    def __init__(self, connection):
        super(MainWindow, self).__init__()
        self.connection = connection
        self.setObjectName("MainWindow")
        self.resize(530, 213)
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox_account_info = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_account_info.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_account_info.setObjectName("groupBox_account_info")
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_account_info)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_account = QtGui.QLabel(self.groupBox_account_info)
        self.label_account.setObjectName("label_account")
        self.gridLayout_3.addWidget(self.label_account, 0, 0, 1, 1)
        self.comboBox_account = QtGui.QComboBox(self.groupBox_account_info)
        self.comboBox_account.setMinimumSize(QtCore.QSize(441, 22))
        self.comboBox_account.setObjectName("comboBox_account")
        self.gridLayout_3.addWidget(self.comboBox_account, 0, 1, 1, 3)
        self.label_balance = QtGui.QLabel(self.groupBox_account_info)
        self.label_balance.setObjectName("label_balance")
        self.gridLayout_3.addWidget(self.label_balance, 1, 0, 1, 1)
        self.lineEdit_balance = QtGui.QLineEdit(self.groupBox_account_info)
        self.lineEdit_balance.setEnabled(False)
        self.lineEdit_balance.setObjectName("lineEdit_balance")
        self.gridLayout_3.addWidget(self.lineEdit_balance, 1, 1, 1, 1)
        self.label_credit = QtGui.QLabel(self.groupBox_account_info)
        self.label_credit.setObjectName("label_credit")
        self.gridLayout_3.addWidget(self.label_credit, 2, 0, 1, 1)
        self.lineEdit_label = QtGui.QLineEdit(self.groupBox_account_info)
        self.lineEdit_label.setEnabled(False)
        self.lineEdit_label.setObjectName("lineEdit_label")
        self.gridLayout_3.addWidget(self.lineEdit_label, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox_account_info, 0, 0, 1, 1)
        self.groupBox_pay = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_pay.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_pay.setObjectName("groupBox_pay")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_pay)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_sum = QtGui.QLabel(self.groupBox_pay)
        self.label_sum.setObjectName("label_sum")
        self.gridLayout_2.addWidget(self.label_sum, 0, 0, 1, 1)
        self.lineEdit_sum = QtGui.QLineEdit(self.groupBox_pay)
        self.lineEdit_sum.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_sum.setObjectName("lineEdit_sum")
        self.lineEdit_sum.setValidator(QtGui.QDoubleValidator(self.lineEdit_sum))
        
        self.gridLayout_2.addWidget(self.lineEdit_sum, 0, 1, 1, 1)
        self.pushButton_pay = QtGui.QPushButton(self.groupBox_pay)
        self.pushButton_pay.setObjectName("pushButton_pay")
        self.gridLayout_2.addWidget(self.pushButton_pay, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.groupBox_pay, 1, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()
        self.connect(self.comboBox_account, QtCore.SIGNAL("currentIndexChanged(int)"), self.refresh)
        self.connect(self.pushButton_pay, QtCore.SIGNAL("clicked()"), self.pay)
        
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Интерфейс кассира", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_account_info.setTitle(QtGui.QApplication.translate("MainWindow", "Информация о аккаунте", None, QtGui.QApplication.UnicodeUTF8))
        self.label_account.setText(QtGui.QApplication.translate("MainWindow", "Аккаунт", None, QtGui.QApplication.UnicodeUTF8))
        self.label_balance.setText(QtGui.QApplication.translate("MainWindow", "Баланс", None, QtGui.QApplication.UnicodeUTF8))
        self.label_credit.setText(QtGui.QApplication.translate("MainWindow", "Кредит", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_pay.setTitle(QtGui.QApplication.translate("MainWindow", "Зачислить", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sum.setText(QtGui.QApplication.translate("MainWindow", "Сумма", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_pay.setText(QtGui.QApplication.translate("MainWindow", "Зачислить", None, QtGui.QApplication.UnicodeUTF8))

    def fixtures(self):
        accounts = self.connection.get_models("billservice_account")
        self.connection.commit()
        i=0
        for account in accounts:
            self.comboBox_account.addItem("%s,%s" % (account.username, account.fullname))
            self.comboBox_account.setItemData(i, QtCore.QVariant(account.id))
            i+=1
        self.refresh()
            
    def refresh(self):
        selected_id = unicode(self.comboBox_account.itemData(self.comboBox_account.currentIndex()).toInt()[0])
        #print "id=", selected_id, self.comboBox_account.currentIndex()
        account = self.connection.get_model(selected_id, "billservice_account")
        self.lineEdit_balance.setText(unicode(account.ballance))
        self.lineEdit_label.setText(unicode(account.credit))
    
    def pay(self):
        if QtGui.QMessageBox.question(self, u"Произвести платёж?" , u"Вы уверены, что хотите произвести платёж?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            account = self.comboBox_account.itemData(self.comboBox_account.currentIndex()).toInt()[0]
            document = u"Платёж проведён кассиром"
            if self.connection.pay(account, float(unicode(self.lineEdit_sum.text())), document)==True:
                QtGui.QMessageBox.information(self, unicode(u"Ок"), unicode(u"Платёж произведён успешно."))
                self.lineEdit_sum.setText("")
                self.refresh()
            else:
                QtGui.QMessageBox.critical(self, unicode(u"Ошибка"), unicode(u"Возникла неизвестаня ошибка. Обратитесь к администратору."))
            
class antiMungeValidator(Pyro.protocol.DefaultConnValidator):
    def __init__(self):
        Pyro.protocol.DefaultConnValidator.__init__(self)
    def createAuthToken(self, authid, challenge, peeraddr, URI, daemon):
        return authid
    def mungeIdent(self, ident):
        return ident
      

def login():
    while True:
        try:
            print 1
            connection = Pyro.core.getProxyForURI("PYROLOC://%s:7766/rpc" % unicode(host))
            print 2
            #password = unicode(child.password.toHex())
            
            connection._setNewConnectionValidator(antiMungeValidator())
            print connection._setIdentification("%s:%s" % (str(user), str(password.toHex())))
            connection.test()
            #waitchild.hide()
            return connection

        except Exception, e:
            #print "login connection error"
            #waitchild.hide()
            if isinstance(e, Pyro.errors.ConnectionDeniedError):
                QtGui.QMessageBox.warning(None, unicode(u"Ошибка"), unicode(u"Отказано в авторизации."))
            else:
                QtGui.QMessageBox.warning(None, unicode(u"Ошибка"), unicode(u"Невозможно подключиться к серверу."))
        #waitchild.hide()
        #del waitchild


     
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    config = ConfigParser.ConfigParser()
    config.read("client_config.ini")
    host = config.get("server", "host")
    user = config.get("server", "login")
    password = config.get("server", "password")
    password = QtCore.QCryptographicHash.hash(password, QtCore.QCryptographicHash.Md5)
    
    

    global connection
    connection = login() 
    
    if connection is None:
        sys.exit()
    connection.commit()
    try:
        global mainwindow
        mainwindow = MainWindow(connection=connection)
        mainwindow.show()
        app.setStyleSheet(open("./style.qss","r").read())
        sys.exit(app.exec_())
        connection.commit()
    except Exception, ex:
        print "main-----------"
        print ex


        
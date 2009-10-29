# -*- coding=utf-8 -*-

LOG_LEVEL = 1
DEFAULT_PORT = 7771
ROLE = 1

from PyQt4 import QtCore, QtGui
import os, sys

sys.path.append(os.path.abspath('../'))

from rpc2 import rpc_protocol, client_networking
'''
import sys
import datetime
import Pyro.core
import Pyro.protocol
import Pyro.constants
import Pyro.errors
'''

import isdlogger
try:
    os.mkdir('log')
except:
    pass
import traceback

from db import Object as Object
from helpers import makeHeaders
from helpers import tableFormat
from helpers import HeaderUtil
from CustomForms import CardPreviewDialog
from CustomForms import ConnectDialog, ConnectionWaiting, InfoDialog, TransactionForm
from AccountFrame import AddAccountTarif
from helpers import dateDelim
from mako.template import Template
from ebsWindow import ebsTableWindow
strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
tr_id=0

logger = isdlogger.isdlogger('logging', loglevel=LOG_LEVEL, ident='cassa', filename='log/webcab_log')
rpc_protocol.install_logger(logger)
client_networking.install_logger(logger)

class CassaEbs(ebsTableWindow):
    def __init__(self, connection):
        columns = ['#', u"Username", u'ФИО', u'Тарифный план', u'Баланс', u'Кредит', u'Улица', u'д.', u'корп.', u'кв.']
        initargs = {"setname":"cassa_period", "objname":"CassaEbsMDI", "winsize":(0,0,1024, 642), "wintitle":"Интерфейс кассира", "tablecolumns":columns, "centralwidget":True}
        super(CassaEbs, self).__init__(connection, initargs)
        self.printer = None
        #self.tariffs = None
    def ebsInterInit(self, initargs):
        
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBox_filter = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_filter.setObjectName("groupBox_filter")
        self.gridLayout = QtGui.QGridLayout(self.groupBox_filter)
        self.gridLayout.setObjectName("gridLayout")
        self.label_fullname = QtGui.QLabel(self.groupBox_filter)
        self.label_fullname.setObjectName("label_fullname")
        self.gridLayout.addWidget(self.label_fullname, 0, 0, 1, 1)
        self.lineEdit_fullname = QtGui.QLineEdit(self.groupBox_filter)
        self.lineEdit_fullname.setObjectName("lineEdit_fullname")
        self.gridLayout.addWidget(self.lineEdit_fullname, 0, 2, 1, 7)
        self.label_street = QtGui.QLabel(self.groupBox_filter)
        self.label_street.setObjectName("label_street")
        self.gridLayout.addWidget(self.label_street, 1, 5, 1, 1)
        self.lineEdit_street = QtGui.QLineEdit(self.groupBox_filter)
        self.lineEdit_street.setObjectName("lineEdit_street")
        self.gridLayout.addWidget(self.lineEdit_street, 1, 6, 1, 1)
        self.label_house = QtGui.QLabel(self.groupBox_filter)
        self.label_house.setObjectName("label_house")
        self.gridLayout.addWidget(self.label_house, 1, 7, 1, 1)
        self.lineEdit_house = QtGui.QLineEdit(self.groupBox_filter)
        self.lineEdit_house.setObjectName("lineEdit_house")
        self.gridLayout.addWidget(self.lineEdit_house, 1, 8, 1, 1)
        self.pushButton_search = QtGui.QPushButton(self.groupBox_filter)
        self.pushButton_search.setObjectName("pushButton_search")
        self.gridLayout.addWidget(self.pushButton_search, 0, 10, 1, 1)
        self.label_username = QtGui.QLabel(self.groupBox_filter)
        self.label_username.setObjectName("label_username")
        self.gridLayout.addWidget(self.label_username, 1, 0, 1, 1)
        self.lineEdit_username = QtGui.QLineEdit(self.groupBox_filter)
        self.lineEdit_username.setObjectName("lineEdit_username")
        self.gridLayout.addWidget(self.lineEdit_username, 1, 2, 1, 1)
        self.label_city = QtGui.QLabel(self.groupBox_filter)
        self.label_city.setObjectName("label_city")
        self.gridLayout.addWidget(self.label_city, 1, 3, 1, 1)
        self.lineEdit_city = QtGui.QLineEdit(self.groupBox_filter)
        self.lineEdit_city.setObjectName("lineEdit_city")
        self.gridLayout.addWidget(self.lineEdit_city, 1, 4, 1, 1)
        self.lineEdit_bulk = QtGui.QLineEdit(self.groupBox_filter)
        self.lineEdit_bulk.setObjectName("lineEdit_bulk")
        self.gridLayout.addWidget(self.lineEdit_bulk, 2, 2, 1, 1)
        self.label_bulk = QtGui.QLabel(self.groupBox_filter)
        self.label_bulk.setObjectName("label_bulk")
        self.gridLayout.addWidget(self.label_bulk, 2, 0, 1, 1)
        self.label_room = QtGui.QLabel(self.groupBox_filter)
        self.label_room.setObjectName("label_room")
        self.gridLayout.addWidget(self.label_room, 2, 3, 1, 1)
        self.lineEdit_room = QtGui.QLineEdit(self.groupBox_filter)
        self.lineEdit_room.setObjectName("lineEdit_room")
        self.gridLayout.addWidget(self.lineEdit_room, 2, 4, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_filter, 0, 0, 1, 1)
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)
        self.gridLayout_3.addWidget(self.tableWidget, 1, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.commandLinkButton = QtGui.QCommandLinkButton(self.groupBox)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/money.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.commandLinkButton.setIcon(icon)
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.gridLayout_2.addWidget(self.commandLinkButton, 0, 0, 1, 1)
        self.commandLinkButton_traffic_limit = QtGui.QCommandLinkButton(self.groupBox)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/traffic_limit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.commandLinkButton_traffic_limit.setIcon(icon1)
        self.commandLinkButton_traffic_limit.setIconSize(QtCore.QSize(20, 20))
        self.commandLinkButton_traffic_limit.setObjectName("commandLinkButton_traffic_limit")
        self.gridLayout_2.addWidget(self.commandLinkButton_traffic_limit, 0, 1, 1, 1)
        self.commandLinkButton_prepaid_traffic = QtGui.QCommandLinkButton(self.groupBox)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/prepaid_traffic.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.commandLinkButton_prepaid_traffic.setIcon(icon2)
        self.commandLinkButton_prepaid_traffic.setObjectName("commandLinkButton_prepaid_traffic")
        self.gridLayout_2.addWidget(self.commandLinkButton_prepaid_traffic, 0, 2, 1, 1)
        self.commandLinkButton_change_tarif = QtGui.QCommandLinkButton(self.groupBox)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("images/tarif_change.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.commandLinkButton_change_tarif.setIcon(icon3)
        self.commandLinkButton_change_tarif.setObjectName("commandLinkButton_change_tarif")
        self.gridLayout_2.addWidget(self.commandLinkButton_change_tarif, 0, 3, 1, 1)
        self.commandLinkButton_addonservice = QtGui.QCommandLinkButton(self.groupBox)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("images/addonservices.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.commandLinkButton_addonservice.setIcon(icon4)
        self.commandLinkButton_addonservice.setObjectName("commandLinkButton_addonservice")
        self.gridLayout_2.addWidget(self.commandLinkButton_addonservice, 0, 4, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 2, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)


        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
  
        
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        
    def ebsPostInit(self, initargs):
        
        actList=[("setPrinter", "Настроить принтер", "images/printer.png", self.getPrinter)]
        objDict = {self.toolBar:["setPrinter",],}
        self.actionCreator(actList, objDict)
        #self.connect(self.pushButton_pay, QtCore.SIGNAL("clicked()"), self.pay)
        #self.connect(self.pushButton_pay_with_cheque, QtCore.SIGNAL("clicked()"), self.pay_with_cheque)
        self.connect(self.pushButton_search, QtCore.SIGNAL("clicked()"), self.refreshTable)
        
        self.connect(self.commandLinkButton_traffic_limit, QtCore.SIGNAL("clicked()"), self.account_limit_info)
        self.connect(self.commandLinkButton_prepaid_traffic, QtCore.SIGNAL("clicked()"), self.prepaid_traffic_info)
        self.connect(self.commandLinkButton_change_tarif, QtCore.SIGNAL("clicked()"), self.createAccountTarif)
        self.connect(self.commandLinkButton, QtCore.SIGNAL("clicked()"), self.pay)
        #self.connect(self.pushButton_change_tariff, QtCore.SIGNAL("clicked()"), self.createAccountTarif)
        #QtCore.QObject.connect(self.checkBox_promise,QtCore.SIGNAL("stateChanged(int)"),self.promise_actions)
        #QtCore.QObject.connect(self.toolButton_time_now,QtCore.SIGNAL("clicked()"),self.setPayTime)
        #QtCore.QObject.connect(self.toolButton_set_tarif_date,QtCore.SIGNAL("clicked()"),self.setTarifTime)
        
        #QtCore.QObject.connect(self.checkBox_promise_infinite,QtCore.SIGNAL("stateChanged(int)"),self.promise_actions)
        
        #QtCore.QObject.connect(self.tableWidget,QtCore.SIGNAL("itemSelectionChanged()"), self.update_info)
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.restoreWindow()
        #self.refreshTariffs()
        #self.fixtures()
        #self.promise_actions()
        #self.checkAutoTime()

        
    def retranslateUI(self, initargs):
        super(CassaEbs, self).retranslateUI(initargs)
        self.groupBox_filter.setTitle(QtGui.QApplication.translate("MainWindow", "Фильтр", None, QtGui.QApplication.UnicodeUTF8))
        self.label_fullname.setText(QtGui.QApplication.translate("MainWindow", "ФИО", None, QtGui.QApplication.UnicodeUTF8))
        self.label_street.setText(QtGui.QApplication.translate("MainWindow", "Улица", None, QtGui.QApplication.UnicodeUTF8))
        self.label_house.setText(QtGui.QApplication.translate("MainWindow", "Дом", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_search.setText(QtGui.QApplication.translate("MainWindow", "Искать", None, QtGui.QApplication.UnicodeUTF8))
        self.label_username.setText(QtGui.QApplication.translate("MainWindow", "Username", None, QtGui.QApplication.UnicodeUTF8))
        self.label_city.setText(QtGui.QApplication.translate("MainWindow", "Город", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bulk.setText(QtGui.QApplication.translate("MainWindow", "Корпус", None, QtGui.QApplication.UnicodeUTF8))
        self.label_room.setText(QtGui.QApplication.translate("MainWindow", "Квартира", None, QtGui.QApplication.UnicodeUTF8))
#===============================================================================
#        self.groupBox_tariffs.setTitle(QtGui.QApplication.translate("MainWindow", "Перевести на другой тарифный план", None, QtGui.QApplication.UnicodeUTF8))
#        self.pushButton_change_tariff.setText(QtGui.QApplication.translate("MainWindow", "Перевести", None, QtGui.QApplication.UnicodeUTF8))
#        self.groupBox_payment.setTitle(QtGui.QApplication.translate("MainWindow", "Платёжные данные", None, QtGui.QApplication.UnicodeUTF8))
#        self.summ_label.setText(QtGui.QApplication.translate("MainWindow", "Сумма", None, QtGui.QApplication.UnicodeUTF8))
#        self.payed_document_label.setText(QtGui.QApplication.translate("MainWindow", "На основании док.", None, QtGui.QApplication.UnicodeUTF8))
#        self.label.setText(QtGui.QApplication.translate("MainWindow", "Комментарий", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_paymend_date.setText(QtGui.QApplication.translate("MainWindow", "Дата платежа", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_promise.setText(QtGui.QApplication.translate("MainWindow", "Обещаный платёж", None, QtGui.QApplication.UnicodeUTF8))
#        self.checkBox_promise.setText(QtGui.QApplication.translate("MainWindow", "Да", None, QtGui.QApplication.UnicodeUTF8))
#        self.label_end_promise.setText(QtGui.QApplication.translate("MainWindow", "Истекает", None, QtGui.QApplication.UnicodeUTF8))
#        self.checkBox_promise_infinite.setText(QtGui.QApplication.translate("MainWindow", "Никогда", None, QtGui.QApplication.UnicodeUTF8))
#        self.pushButton_pay.setText(QtGui.QApplication.translate("MainWindow", "Зачислить", None, QtGui.QApplication.UnicodeUTF8))
#        self.pushButton_pay_with_cheque.setText(QtGui.QApplication.translate("MainWindow", "Зачислить и распечатать чек", None, QtGui.QApplication.UnicodeUTF8))
#        self.groupBox_limites.setTitle(QtGui.QApplication.translate("MainWindow", "Лимиты", None, QtGui.QApplication.UnicodeUTF8))
#        self.textEdit_limites.setPlainText(QtGui.QApplication.translate("MainWindow", "Нет данных", None, QtGui.QApplication.UnicodeUTF8))
#        self.groupBox_prepaid_traffic.setTitle(QtGui.QApplication.translate("MainWindow", "Предоплаченный трафик", None, QtGui.QApplication.UnicodeUTF8))
#        self.textEdit_prepaid_traffic.setPlainText(QtGui.QApplication.translate("MainWindow", "Функция недоступна", None, QtGui.QApplication.UnicodeUTF8))
#        self.toolButton_time_now.setText(QtGui.QApplication.translate("MainWindow", "#", None, QtGui.QApplication.UnicodeUTF8))
#        self.toolButton_set_tarif_date.setText(QtGui.QApplication.translate("MainWindow", "#", None, QtGui.QApplication.UnicodeUTF8))
#===============================================================================
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Действия", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton.setText(QtGui.QApplication.translate("MainWindow", "Пополнить баланс", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton.setDescription(QtGui.QApplication.translate("MainWindow", "Пополнить лицевой счёт", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_traffic_limit.setText(QtGui.QApplication.translate("MainWindow", "Лимиты", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_traffic_limit.setDescription(QtGui.QApplication.translate("MainWindow", "Состояние лимитов", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_prepaid_traffic.setText(QtGui.QApplication.translate("MainWindow", "Предоплаченный трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_prepaid_traffic.setDescription(QtGui.QApplication.translate("MainWindow", "Остаток трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_change_tarif.setText(QtGui.QApplication.translate("MainWindow", "Сменить тариф", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_change_tarif.setDescription(QtGui.QApplication.translate("MainWindow", "Сменить тарифный план", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_addonservice.setText(QtGui.QApplication.translate("MainWindow", "Подключаемые услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_addonservice.setDescription(QtGui.QApplication.translate("MainWindow", "Список подключенных услуг", None, QtGui.QApplication.UnicodeUTF8))
        
        
    def account_limit_info(self):
        id = self.getSelectedId()
        if id:
            child = InfoDialog(connection= self.connection, type="limit", account_id=id)
            child.exec_()
           
 
    def prepaid_traffic_info(self):
        id = self.getSelectedId()
        if id:
            child = InfoDialog(connection= self.connection, type="prepaidtraffic", account_id=id)
            child.exec_()
           
           
    def promise_actions(self):
        if self.checkBox_promise.isChecked():
            self.dateTimeEdit_end_promise.setEnabled(True)
            self.checkBox_promise_infinite.setEnabled(True)
            if self.checkBox_promise_infinite.isChecked():
                self.dateTimeEdit_end_promise.setEnabled(False)
            
        else:
            self.dateTimeEdit_end_promise.setEnabled(False)
            self.checkBox_promise_infinite.setEnabled(False)
    
 
    
    def setPayTime(self):
        #if self.checkBox_autotime.isChecked()==True:
        #    self.dateTimeEdit_paymend_date.setDisabled(True)
        #else:
        #    self.dateTimeEdit_paymend_date.setDisabled(False)
        self.dateTimeEdit_paymend_date.setDateTime(datetime.datetime.now())

            
    def fixtures(self):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        self._name = settings.value("user", QtCore.QVariant("")).toString()
        if self._name:
            self.systemuser_id = self.connection.sql("SELECT id FROM billservice_systemuser WHERE username='%s'" % self._name)[0].id
            self.connection.commit()
        
        self.dateTimeEdit_paymend_date.setDateTime(datetime.datetime.now())
        self.dateTimeEdit_end_promise.setDateTime(datetime.datetime.now())
        
    def addrow(self, value, x, y, color=None, enabled=True):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        if color:
            if float(value)<0:
                headerItem.setBackgroundColor(QtGui.QColor(color))
                headerItem.setTextColor(QtGui.QColor('#ffffff'))
        
        if not enabled:
            headerItem.setBackgroundColor(QtGui.QColor('#dadada'))
        
            
        if y==1:
            if enabled==True:
                headerItem.setIcon(QtGui.QIcon("images/user.png"))
            else:
                headerItem.setIcon(QtGui.QIcon("images/user_inactive.png"))
            

        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
        #self.tablewidget.setShowGrid(False)
        
        
    def refreshTable(self):
        fullname = u"%s" % self.lineEdit_fullname.text()
        username = u"%s" % self.lineEdit_username.text()
        city = u"%s" % self.lineEdit_city.text()
        street = u"%s" % self.lineEdit_street.text()
        house = u"%s" % self.lineEdit_house.text()
        bulk = u"%s" % self.lineEdit_bulk.text()
        room = u"%s" % self.lineEdit_room.text()

        
        res={'fullname':fullname, 'city':city, 'street':street, 'house':house, 'house_bulk':bulk, 'room':room, 'username': username}
        #print res

        if fullname or city or street or house or bulk or room or username:
            sql=u"SELECT *, (SELECT name FROM billservice_tariff WHERE id=get_tarif(account.id)) as tarif_name FROM billservice_account as account WHERE %s ORDER BY username ASC;" % ' AND '.join([u"%s LIKE '%s%s%s'" % (key, "%",res[key],"%") for key in res])
        else:
            sql=u"SELECT *, (SELECT name FROM billservice_tariff WHERE id=get_tarif(account.id)) as tarif_name  FROM billservice_account as account ORDER BY username ASC;"
        
        accounts = self.connection.sql(sql)
        self.connection.commit()
        i=0
        self.tableWidget.setRowCount(len(accounts))
        for account in accounts:
            self.addrow(account.id, i, 0, enabled=account.status)
            self.addrow(account.username, i, 1, enabled=account.status)
            self.addrow(account.fullname, i, 2, enabled=account.status)
            self.addrow(account.tarif_name, i, 3, enabled=account.status)
            self.addrow("%.2f" % account.ballance, i, 4, enabled=account.status)
            self.addrow(account.credit, i, 5, enabled=account.status)
            #self.addrow(account.city, i, 6, enabled=account.status)
            self.addrow(account.street, i, 6, enabled=account.status)
            self.addrow(account.house, i, 7, enabled=account.status)
            self.addrow(account.house_bulk, i, 8, enabled=account.status)
            self.addrow(account.room, i, 9, enabled=account.status)

            i+=1
  
        
    def pay(self):
        id = self.getSelectedId()
        if id:
            account = self.connection.get_model(id, "billservice_account")
            self.connection.commit()
            child = TransactionForm(self.connection, None, account)
            if child.exec_()==1:
                self.refreshTable()
        return
            
        if self.getSelectedId() and QtGui.QMessageBox.question(self, u"Произвести платёж?" , u"Вы уверены, что хотите произвести платёж?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            account = self.getSelectedId()
            document = unicode(self.lineEdit_document.text())
            description = unicode(self.lineEdit_description.text())

            created = unicode(self.dateTimeEdit_paymend_date.dateTime().toPyDateTime())
            
            promise = self.checkBox_promise.isChecked()
            summ = float(unicode(self.lineEdit_summ.text()))
            if self.checkBox_promise.isChecked() and not self.checkBox_promise_infinite.isChecked():
                end_promise = self.dateTimeEdit_end_promise.dateTime().toPyDateTime()
            else:
                end_promise = None

                
            global tr_id
            tr_id = self.connection.pay(account, summ, document, description, created, promise, end_promise, self.systemuser_id)
            if tr_id==False:
                QtGui.QMessageBox.critical(self, unicode(u"Ошибка"), unicode(u"Возникла неизвестаня ошибка. Возможно пропала связь с сервером."))
            else:
                QtGui.QMessageBox.information(self, unicode(u"Ок"), unicode(u"Платёж произведён успешно."))
                self.lineEdit_summ.setText("")
                self.lineEdit_document.setText("")
                self.lineEdit_description.setText("")
                self.refreshTable()
                
            self.lineEdit_summ.setFocus(True)
            
 
                   
    def createAccountTarif(self):
        id = self.getSelectedId()
        if id:
            account = self.connection.get_model(id, "billservice_account")
            self.connection.commit()
            child = AddAccountTarif(self.connection, account = account)
            if child.exec_()==1:
                
                self.refreshTable()
        

    def cheque_print(self, tr_id):
        if not self.printer:
            QtGui.QMessageBox.warning(self, unicode(u"Ок"), unicode(u"Настройка принтера не была произведена!"))
            return
        account_id = self.getSelectedId()
        if account_id:
            template = self.connection.get('SELECT body FROM billservice_template WHERE type_id=5')
            templ = Template(unicode(template.body), input_encoding='utf-8')
            account = self.connection.get("SELECT * FROM billservice_account WHERE id=%s LIMIT 1" % account_id)

            tarif = self.connection.get("SELECT name FROM billservice_tariff WHERE id=get_tarif(%s)" % account.id)
            transaction = self.connection.get_model(tr_id.id, "billservice_transaction")
            self.connection.commit()
            sum = 10000
            transaction.summ = transaction.summ*(-1)
            data=templ.render_unicode(account=account, tarif=tarif, transaction=transaction)
            
            #it seem that software printers can change the path!
            file= open('templates/tmp/temp.html', 'wb')
            file.write(data.encode("utf-8", 'replace'))
            file.flush()
            file.close()
            a=CardPreviewDialog(url="templates/tmp/temp.html", printer=self.printer)
            a.exec_()

    def getPrinter(self):
        printer = QtGui.QPrinter()
        dialog = QtGui.QPrintDialog(printer, self)
        dialog.setWindowTitle(self.tr("Печать"))
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return
        self.printer = printer
    

'''        
class antiMungeValidator(Pyro.protocol.DefaultConnValidator):
    def __init__(self):
        Pyro.protocol.DefaultConnValidator.__init__(self)

    def createAuthToken(self, authid, challenge, peeraddr, URI, daemon):

        return authid

    def mungeIdent(self, ident):
        return ident
'''      

def login():
    child = ConnectDialog()
    while True:

        if child.exec_() == 1:
            waitchild = ConnectionWaiting()
            waitchild.show()
            try:
                authenticator = rpc_protocol.MD5_Authenticator('client', 'AUTH')
                protocol = rpc_protocol.RPCProtocol(authenticator)
                connection = rpc_protocol.BasicClientConnection(protocol)
                connection.notifier = lambda x: QtGui.QMessageBox.warning(None, unicode(u"Exception"), unicode(x))
                if ':' in child.address:
                    host, port = str(child.address).split(':')
                else:
                    host, port = str(child.address), DEFAULT_PORT
                transport = client_networking.BlockingTcpClient(host, port)
                transport.connect()
                connection.registerConsumer_(transport)
                auth_result = connection.authenticate(str(child.name), str(child.password), ROLE)
                if not auth_result or not connection.protocol._check_status():
                    raise Exception('Status = False!')
                waitchild.hide()
                return connection

            except Exception, e:
                print repr(e), traceback.format_exc()
                if not isinstance(e, client_networking.TCPException):
                    QtGui.QMessageBox.warning(None, unicode(u"Ошибка"), unicode(u"Отказано в авторизации."))
                else:
                    QtGui.QMessageBox.warning(None, unicode(u"Ошибка"), unicode(u"Невозможно подключиться к серверу."))
            waitchild.hide()
            del waitchild
        else:
            return None


     
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    global connection
    connection = login() 
    
    if connection is None:
        sys.exit()
    #connection.commit()
    #try:
    global mainwindow
    #mainwindow = MainWindow(connection=connection)
    mainwindow = CassaEbs(connection=connection)
    mainwindow.show()
    app.setStyleSheet(open("./cassa_style.qss","r").read())
    sys.exit(app.exec_())
    connection.commit()
    #except Exception, ex:
    #    print "main-----------"
    #    print repr(ex)


        

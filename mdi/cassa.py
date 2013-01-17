# -*- coding=utf-8 -*-

LOG_LEVEL = 1
DEFAULT_PORT = 7771
ROLE = 1

from PyQt4 import QtCore, QtGui
import os, sys

sys.path.append(os.path.abspath('../'))

import isdlogger
try:
    os.mkdir('log')
except:
    pass
import traceback

from db import AttrDict
from helpers import makeHeaders
from helpers import tableFormat
from helpers import HeaderUtil
from CustomForms import CardPreviewDialog
from CustomForms import ConnectDialog, ConnectionWaiting, InfoDialog, TransactionForm
from AccountFrame import AddAccountTarif
from Reports import TransactionsReportEbs
from helpers import dateDelim
from mako.template import Template
from ebsWindow import ebsTableWindow
import datetime
from ebsadmin import HttpBot
strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
tr_id=0

logger = isdlogger.isdlogger('logging', loglevel=LOG_LEVEL, ident='cassa', filename='log/webcab_log')

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
class CassaEbs(ebsTableWindow):
    def __init__(self, connection):
        columns = [u'#', u'Договор #', u"Username", u'ФИО', u'Тарифный план', u'Баланс', u'Кредит', u'Улица', u'д.', u'корп.', u'кв.', u"Дата подключения"]
        initargs = {"setname":"cassa_period", "objname":"CassaEbsMDI", "winsize":(0,0,1024, 642), "wintitle":"Интерфейс кассира", "tablecolumns":columns, "centralwidget":True}
        super(CassaEbs, self).__init__(connection, initargs)
        self.printer = None
        #self.tariffs = None
    def ebsInterInit(self, initargs):
        
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_4 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout_4.addWidget(self.tableWidget, 1, 0, 1, 2)
        self.groupBox_filter = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_filter.setObjectName(_fromUtf8("groupBox_filter"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_filter)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_fullname = QtGui.QLabel(self.groupBox_filter)
        self.label_fullname.setObjectName(_fromUtf8("label_fullname"))
        self.gridLayout.addWidget(self.label_fullname, 0, 0, 1, 1)
        self.lineEdit_fullname = QtGui.QLineEdit(self.groupBox_filter)
        self.lineEdit_fullname.setObjectName(_fromUtf8("lineEdit_fullname"))
        self.gridLayout.addWidget(self.lineEdit_fullname, 0, 2, 1, 1)
        self.lineEdit_bulk = QtGui.QLineEdit(self.groupBox_filter)
        self.lineEdit_bulk.setObjectName(_fromUtf8("lineEdit_bulk"))
        self.gridLayout.addWidget(self.lineEdit_bulk, 5, 2, 1, 1)
        self.label_bulk = QtGui.QLabel(self.groupBox_filter)
        self.label_bulk.setObjectName(_fromUtf8("label_bulk"))
        self.gridLayout.addWidget(self.label_bulk, 5, 0, 1, 1)
        self.label_house = QtGui.QLabel(self.groupBox_filter)
        self.label_house.setObjectName(_fromUtf8("label_house"))
        self.gridLayout.addWidget(self.label_house, 4, 0, 1, 1)
        self.comboBox_house = QtGui.QComboBox(self.groupBox_filter)
        self.comboBox_house.setObjectName(_fromUtf8("comboBox_house"))
        self.gridLayout.addWidget(self.comboBox_house, 4, 2, 1, 1)
        self.label_room = QtGui.QLabel(self.groupBox_filter)
        self.label_room.setObjectName(_fromUtf8("label_room"))
        self.gridLayout.addWidget(self.label_room, 6, 0, 1, 1)
        self.lineEdit_room = QtGui.QLineEdit(self.groupBox_filter)
        self.lineEdit_room.setObjectName(_fromUtf8("lineEdit_room"))
        self.gridLayout.addWidget(self.lineEdit_room, 6, 2, 1, 1)
        self.label_username = QtGui.QLabel(self.groupBox_filter)
        self.label_username.setObjectName(_fromUtf8("label_username"))
        self.gridLayout.addWidget(self.label_username, 0, 3, 1, 1)
        self.lineEdit_username = QtGui.QLineEdit(self.groupBox_filter)
        self.lineEdit_username.setObjectName(_fromUtf8("lineEdit_username"))
        self.gridLayout.addWidget(self.lineEdit_username, 0, 4, 1, 1)
        self.label_city = QtGui.QLabel(self.groupBox_filter)
        self.label_city.setObjectName(_fromUtf8("label_city"))
        self.gridLayout.addWidget(self.label_city, 1, 0, 1, 1)
        self.comboBox_city = QtGui.QComboBox(self.groupBox_filter)
        self.comboBox_city.setObjectName(_fromUtf8("comboBox_city"))
        self.gridLayout.addWidget(self.comboBox_city, 1, 2, 1, 1)
        self.label_street = QtGui.QLabel(self.groupBox_filter)
        self.label_street.setObjectName(_fromUtf8("label_street"))
        self.gridLayout.addWidget(self.label_street, 2, 0, 1, 1)
        self.comboBox_street = QtGui.QComboBox(self.groupBox_filter)
        self.comboBox_street.setObjectName(_fromUtf8("comboBox_street"))
        self.gridLayout.addWidget(self.comboBox_street, 2, 2, 1, 1)
        self.label_contract = QtGui.QLabel(self.groupBox_filter)
        self.label_contract.setObjectName(_fromUtf8("label_contract"))
        self.gridLayout.addWidget(self.label_contract, 1, 3, 1, 1)
        self.lineEdit_contract = QtGui.QLineEdit(self.groupBox_filter)
        self.lineEdit_contract.setObjectName(_fromUtf8("lineEdit_contract"))
        self.gridLayout.addWidget(self.lineEdit_contract, 1, 4, 1, 1)
        self.label_mphone = QtGui.QLabel(self.groupBox_filter)
        self.label_mphone.setObjectName(_fromUtf8("label_mphone"))
        self.gridLayout.addWidget(self.label_mphone, 2, 3, 1, 1)
        self.lineEdit_mphone = QtGui.QLineEdit(self.groupBox_filter)
        self.lineEdit_mphone.setObjectName(_fromUtf8("lineEdit_mphone"))
        self.gridLayout.addWidget(self.lineEdit_mphone, 2, 4, 1, 1)
        self.label_hphone = QtGui.QLabel(self.groupBox_filter)
        self.label_hphone.setObjectName(_fromUtf8("label_hphone"))
        self.gridLayout.addWidget(self.label_hphone, 4, 3, 1, 1)
        self.lineEdit_hphone = QtGui.QLineEdit(self.groupBox_filter)
        self.lineEdit_hphone.setObjectName(_fromUtf8("lineEdit_hphone"))
        self.gridLayout.addWidget(self.lineEdit_hphone, 4, 4, 1, 1)
        self.pushButton_search = QtGui.QPushButton(self.groupBox_filter)
        self.pushButton_search.setObjectName(_fromUtf8("pushButton_search"))
        self.gridLayout.addWidget(self.pushButton_search, 4, 5, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_filter, 3, 0, 1, 2)
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.commandLinkButton_pay = QtGui.QCommandLinkButton(self.groupBox)
        self.commandLinkButton_pay.setObjectName(_fromUtf8("commandLinkButton_pay"))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/money.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.commandLinkButton_pay.setIcon(icon)
        self.gridLayout_2.addWidget(self.commandLinkButton_pay, 0, 0, 1, 1)
        self.commandLinkButton_prepaidtraffic = QtGui.QCommandLinkButton(self.groupBox)
        self.commandLinkButton_prepaidtraffic.setObjectName(_fromUtf8("commandLinkButton_prepaidtraffic"))
        self.gridLayout_2.addWidget(self.commandLinkButton_prepaidtraffic, 0, 1, 1, 1)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/prepaid_traffic.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.commandLinkButton_prepaidtraffic.setIcon(icon2)

        self.commandLinkButton_limit = QtGui.QCommandLinkButton(self.groupBox)
        self.commandLinkButton_limit.setObjectName(_fromUtf8("commandLinkButton_limit"))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/traffic_limit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.commandLinkButton_limit.setIcon(icon1)

        self.gridLayout_2.addWidget(self.commandLinkButton_limit, 0, 2, 1, 1)
        self.commandLinkButton_addonservices = QtGui.QCommandLinkButton(self.groupBox)
        self.commandLinkButton_addonservices.setObjectName(_fromUtf8("commandLinkButton_addonservices"))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("images/tomboy.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.commandLinkButton_addonservices.setIcon(icon4)
        
        self.gridLayout_2.addWidget(self.commandLinkButton_addonservices, 0, 3, 1, 1)
        self.commandLinkButton_change_tarif = QtGui.QCommandLinkButton(self.groupBox)
        self.commandLinkButton_change_tarif.setObjectName(_fromUtf8("commandLinkButton_change_tarif"))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("images/tarif_change.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.commandLinkButton_change_tarif.setIcon(icon3)

        self.gridLayout_2.addWidget(self.commandLinkButton_change_tarif, 0, 4, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox, 0, 0, 1, 2)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        self.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.toolBar.setIconSize(QtCore.QSize(18,18))
  
        
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        
        self.setTabOrder(self.lineEdit_fullname, self.comboBox_city)
        self.setTabOrder(self.comboBox_city, self.comboBox_street)
        self.setTabOrder(self.comboBox_street, self.comboBox_house)
        self.setTabOrder(self.comboBox_house, self.lineEdit_bulk)
        self.setTabOrder(self.lineEdit_bulk, self.lineEdit_room)
        self.setTabOrder(self.lineEdit_room, self.lineEdit_username)
        self.setTabOrder(self.lineEdit_username, self.lineEdit_contract)
        self.setTabOrder(self.lineEdit_contract, self.lineEdit_mphone)
        self.setTabOrder(self.lineEdit_mphone, self.lineEdit_hphone)
        self.setTabOrder(self.lineEdit_hphone, self.pushButton_search)
        self.setTabOrder(self.pushButton_search, self.commandLinkButton_pay)
        self.setTabOrder(self.commandLinkButton_pay, self.commandLinkButton_prepaidtraffic)
        self.setTabOrder(self.commandLinkButton_prepaidtraffic, self.commandLinkButton_limit)
        self.setTabOrder(self.commandLinkButton_limit, self.commandLinkButton_addonservices)
        self.setTabOrder(self.commandLinkButton_addonservices, self.commandLinkButton_change_tarif)
        self.setTabOrder(self.commandLinkButton_change_tarif, self.tableWidget)

        self.combo_city()

    def ebsPostInit(self, initargs):
        
        actList=[("setPrinter", "Настроить принтер", "images/printer.png", self.getPrinter)]
        objDict = {self.toolBar:["setPrinter",],}
        self.actionCreator(actList, objDict)
        #self.connect(self.pushButton_pay, QtCore.SIGNAL("clicked()"), self.pay)
        #self.connect(self.pushButton_pay_with_cheque, QtCore.SIGNAL("clicked()"), self.pay_with_cheque)
        self.connect(self.pushButton_search, QtCore.SIGNAL("clicked()"), self.refreshTable)
        
        self.connect(self.commandLinkButton_limit, QtCore.SIGNAL("clicked()"), self.account_limit_info)
        self.connect(self.commandLinkButton_prepaidtraffic, QtCore.SIGNAL("clicked()"), self.prepaid_traffic_info)
        self.connect(self.commandLinkButton_change_tarif, QtCore.SIGNAL("clicked()"), self.createAccountTarif)
        self.connect(self.commandLinkButton_pay, QtCore.SIGNAL("clicked()"), self.pay)
        self.connect(self.commandLinkButton_addonservices, QtCore.SIGNAL("clicked()"), self.transactionReport)

        self.connect(self.comboBox_city, QtCore.SIGNAL("currentIndexChanged(int)"), self.refresh_combo_street)
        self.connect(self.comboBox_street, QtCore.SIGNAL("currentIndexChanged(int)"), self.refresh_combo_house)
        
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
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Интерфейс кассира", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_filter.setTitle(QtGui.QApplication.translate("MainWindow", "Фильтр", None, QtGui.QApplication.UnicodeUTF8))
        self.label_fullname.setText(QtGui.QApplication.translate("MainWindow", "ФИО", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bulk.setText(QtGui.QApplication.translate("MainWindow", "Корпус", None, QtGui.QApplication.UnicodeUTF8))
        self.label_house.setText(QtGui.QApplication.translate("MainWindow", "Дом", None, QtGui.QApplication.UnicodeUTF8))
        self.label_room.setText(QtGui.QApplication.translate("MainWindow", "Квартира", None, QtGui.QApplication.UnicodeUTF8))
        self.label_username.setText(QtGui.QApplication.translate("MainWindow", "Username", None, QtGui.QApplication.UnicodeUTF8))
        self.label_city.setText(QtGui.QApplication.translate("MainWindow", "Город", None, QtGui.QApplication.UnicodeUTF8))
        self.label_street.setText(QtGui.QApplication.translate("MainWindow", "Улица", None, QtGui.QApplication.UnicodeUTF8))
        self.label_contract.setText(QtGui.QApplication.translate("MainWindow", "Номер договора", None, QtGui.QApplication.UnicodeUTF8))
        self.label_mphone.setText(QtGui.QApplication.translate("MainWindow", "Номер моб. телефона", None, QtGui.QApplication.UnicodeUTF8))
        self.label_hphone.setText(QtGui.QApplication.translate("MainWindow", "Номер дом. телефона", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_search.setText(QtGui.QApplication.translate("MainWindow", "Искать", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Действия", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_pay.setText(QtGui.QApplication.translate("MainWindow", "Пополнить баланс", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_pay.setDescription(QtGui.QApplication.translate("MainWindow", "Пополнить баланс", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_prepaidtraffic.setText(QtGui.QApplication.translate("MainWindow", "Остаток трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_prepaidtraffic.setDescription(QtGui.QApplication.translate("MainWindow", "Предоплаченный трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_limit.setText(QtGui.QApplication.translate("MainWindow", "Трафик по лимитам", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_limit.setDescription(QtGui.QApplication.translate("MainWindow", "Остаток трафика по лимитам", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_addonservices.setText(QtGui.QApplication.translate("MainWindow", "История платежей", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_addonservices.setDescription(QtGui.QApplication.translate("MainWindow", "Просмотр платежей и списаний", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_change_tarif.setText(QtGui.QApplication.translate("MainWindow", "Сменить тарифный план", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_change_tarif.setDescription(QtGui.QApplication.translate("MainWindow", "Смена тарифного плана", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget=tableFormat(self.tableWidget)
        columns=[u'#', u'Договор #', u"Username", u'ФИО', u'Тарифный план', u'Баланс', u'Кредит', u'Улица', u'д.', u'корп.', u'кв.', u"Дата подключения"]
        makeHeaders(columns, self.tableWidget)
        
    def refresh_combo_street(self):
        city_id = self.comboBox_city.itemData(self.comboBox_city.currentIndex()).toInt()[0]
        if city_id==0:
            self.comboBox_street.clear()
            self.comboBox_house.clear()
        if not city_id: return
        streets = self.connection.get_streets(city_id=city_id)
        self.connection.commit()
        self.comboBox_street.clear()
        self.comboBox_house.clear()
        self.comboBox_street.addItem(u"--Не указано--", QtCore.QVariant(0))
        i=1
        for street in streets:
            self.comboBox_street.addItem(street.name, QtCore.QVariant(street.id))
            i+=1

    def combo_city(self):
        cities = self.connection.get_cities()
        self.connection.commit()
        self.comboBox_city.clear()
        self.comboBox_house.clear()
        self.comboBox_street.clear()
        self.comboBox_city.addItem(u'-Не указано-', QtCore.QVariant(0))
        self.comboBox_street.addItem(u'-Не указано-', QtCore.QVariant(0))
        self.comboBox_house.addItem(u'-Не указано-', QtCore.QVariant(0))
        i=1
        for city in cities:
            self.comboBox_city.addItem(city.name, QtCore.QVariant(city.id))
            i+=1        
            
    def refresh_combo_house(self):
        street_id = self.comboBox_street.itemData(self.comboBox_street.currentIndex()).toInt()[0]
        if not street_id: return        
        items = self.connection.get_houses(street_id=street_id)
        self.connection.commit()
        self.comboBox_house.clear()
        self.comboBox_house.addItem(u"--Не указано--", QtCore.QVariant(0))
        i=1
        for item in items:
            self.comboBox_house.addItem(item.name, QtCore.QVariant(item.id))
            i+=1
            
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
           
    def transactionReport(self):
        id = self.getSelectedId()
        if id:
            account = self.connection.get_account(id)
            child = TransactionsReportEbs(parent=self, connection= self.connection, account=account, cassa=True)
            child.delete_transaction=lambda s: True
            child.show()
        
           
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
            

        if isinstance(value, basestring):            
            headerItem.setText(unicode(value))     
        elif type(value)==datetime.datetime:
            headerItem.setData(QtCore.Qt.DisplayRole, QtCore.QString(unicode(value.strftime(strftimeFormat))))      
        else:            
            headerItem.setData(0, QtCore.QVariant(value))       
            
        self.tableWidget.setItem(x,y,headerItem)
        #self.tablewidget.setShowGrid(False)
        
        
    def refreshTable(self):
        fullname = unicode(self.lineEdit_fullname.text())
        agreement = unicode(self.lineEdit_contract.text())
        username = u"%s" % unicode(self.lineEdit_username.text())
        city = self.comboBox_city.itemData(self.comboBox_city.currentIndex()).toInt()[0] or None
        street = self.comboBox_street.itemData(self.comboBox_street.currentIndex()).toInt()[0] or None
        house = self.comboBox_house.itemData(self.comboBox_house.currentIndex()).toInt()[0] or None
        bulk = u"%s" % unicode(self.lineEdit_bulk.text())
        room = u"%s" % unicode(self.lineEdit_room.text())
        phone_h = u"%s" % unicode(self.lineEdit_hphone.text())
        phone_m = u"%s" % unicode(self.lineEdit_mphone.text())

        
        
        #print res

#===============================================================================
#        if fullname or city or street or house or bulk or room or username:
#            sql=u"SELECT *, (SELECT name FROM billservice_tariff WHERE id=get_tarif(account.id)) as tarif_name FROM billservice_account as account WHERE %s ORDER BY username ASC;" % ' AND '.join([u"%s LIKE '%s%s%s'" % (key, "%",res[key],"%") for key in res])
#        else:
#            sql=u"SELECT *, (SELECT name FROM billservice_tariff WHERE id=get_tarif(account.id)) as tarif_name  FROM billservice_account as account ORDER BY username ASC;"
#===============================================================================
        
        accounts = self.connection.get_accounts_for_cachier(fullname, city, street, house, bulk, room, username, agreement, phone_h, phone_m)
        self.connection.commit()
        i=0
        self.tableWidget.setRowCount(len(accounts))
        self.tableWidget.setSortingEnabled(False)
        for account in accounts:
            self.addrow(account.id, i, 0, enabled=account.status)
            self.addrow(account.contract, i, 1, enabled=account.status)
            self.addrow(account.username, i, 2, enabled=account.status)
            self.addrow(account.fullname, i, 3, enabled=account.status)
            self.addrow(account.tarif_name, i, 4, enabled=account.status)
            self.addrow("%.2f" % account.ballance, i, 5, enabled=account.status)
            self.addrow(account.credit, i, 6, enabled=account.status)
            #self.addrow(account.city, i, 6, enabled=account.status)
            self.addrow(account.street, i, 7, enabled=account.status)
            self.addrow(account.house, i, 8, enabled=account.status)
            self.addrow(account.house_bulk, i, 9, enabled=account.status)
            self.addrow(account.room, i, 10, enabled=account.status)
            self.addrow(account.created.strftime(strftimeFormat), i, 11, enabled=account.status)

            i+=1
        self.tableWidget.setSortingEnabled(True)
  
        
    def pay(self):
        id = self.getSelectedId()
        if id:
            account = self.connection.get_account(id)
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
            account = self.connection.get_account(id)
            self.connection.commit()
            child = AddAccountTarif(self.connection, account = account)
            if child.exec_()==1:
                
                self.refreshTable()
        


    def getPrinter(self):
        printer = QtGui.QPrinter()
        dialog = QtGui.QPrintDialog(printer, self)
        dialog.setWindowTitle(self.tr("Печать"))
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return
        self.printer = printer
    

def login():
    child = ConnectDialog()
    while True:

        if child.exec_()==1:
            #waitchild = ConnectionWaiting()
            #waitchild.show()
            global splash, username, server_ip
            #pixmap = QtGui.QPixmap("splash.png")
            #splash = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
            #splash = QtGui.QSplashScreen(pixmap)
            #splash.setMask(pixmap.mask()) # this is usefull if the splashscreen is not a regular ractangle...
            #splash.show()
            #splash.showMessage(u'Интерфейс кассира. Запуск...', QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom,QtCore.Qt.yellow)
            # make sure Qt really display the splash screen
            global app
            app.processEvents()

                
                #logger  = PrintLogger()
            try:
                os.mkdir('log')
            except:
                pass
            logger = isdlogger.isdlogger('logging', loglevel=LOG_LEVEL, ident='mdi', filename='log/mdi_log')

            connection = HttpBot(widget=child, host=unicode(child.address))
            data = connection.log_in(unicode(child.name), unicode(child.password))
            username = unicode(child.name)

            if data:
                return connection
            else:
                QtGui.QMessageBox.warning(None, unicode(u"Ошибка"), unicode(u"Отказано в авторизации.\n%s" % data.message))

        else:
            #splash.hide()
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


        

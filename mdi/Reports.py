#-*-coding=utf-8-*-

import os, sys
from PyQt4 import QtCore, QtGui, QtSql, QtWebKit
from helpers import tableFormat
from db import Object as Object
from helpers import makeHeaders
from helpers import dateDelim
from helpers import HeaderUtil
from helpers import humanable_bytes
from ebsWindow import ebsTableWindow
from ebsWindow import ebsTabs_n_TablesWindow
import itertools
from itertools import count, izip
import datetime
import socket 
from reports.bpreportedit import bpReportEdit
import thread
import time


#TODO: заменить сообщение о пустой выборке пустой картинкой
_xmlpath = "reports/xml"
reppath  = "reports/genhtml"

_querydict = {\
              "get_nas"      : "SELECT name, type, ipaddress, id FROM nas_nas ORDER BY name;", \
	      "get_usernames": "SELECT username, id FROM billservice_account ORDER BY username;", \
              "get_classes"  : "SELECT name, weight, id FROM nas_trafficclass ORDER BY name;", \
              "get_groups"   : "SELECT name, id FROM billservice_group ORDER BY name;"}

_chartopts = {\
             "gstat_multi"  : [("portsTab",'groupsTab'), ('ggb_groups_checkBox',), {}],\
             "pie_gmulti"  : [("portsTab",'groupsTab'),('ggb_groups_checkBox',), {'pie':True}],\
             "gstat_globals"  : [("portsTab","classesTab", 'groupsTab'),('ggb_groups_checkBox','ggb_classes_checkBox'), {'ttype':'stat'}],\
             "groups"  : [("portsTab","classesTab", "serversTab"),('ggb_classes_checkBox', 'ggb_nas_checkBox','traffic_groupBox'), {'ttype':'group'}],\
             "sessions" : [("serversTab", "classesTab", "portsTab", 'groupsTab'), ('traffic_groupBox', 'data_groupBox', 'groupby_groupBox'), {}],\
             "trans_deb" : [("usersTab", "serversTab", "classesTab", "portsTab", 'groupsTab'), ('traffic_groupBox', 'data_groupBox', 'groupby_groupBox'), {'trtype':'deb'}],\
             "trans_crd" : [("usersTab", "serversTab", "classesTab", "portsTab", 'groupsTab'), ('traffic_groupBox', 'data_groupBox', 'groupby_groupBox'), {'trtype':'crd'}]
            }

_ports = [(25, "SMTP"), (53, "DNS"), (80, "HTTP"), (110, "POP3"), (143, "IMAP"), (443, "HTTPS"), (1080, "SOCKS"), (3128, "Web Cache"), (3306, "MySQL"), (3724, "WoW"), (5190, "ICQ"), (5222, "Jabber"), (5432, "Postgres"), (8080, "HTTP Proxy")]

class TransactionsReportEbs(ebsTableWindow):
    def __init__(self, connection,account=None, parent=None, cassa=False):
        self.account = account
        self.cassa=cassa
        columns=[u'#', u'Аккаунт', u"ФИО", u'Дата', u'Платёжный документ', u'Вид проводки', u"Выполнено", u'Тариф', u'Сумма', u'Комментарий', u"В долг", u"До числа"]
        initargs = {"setname":"transrep_frame_header", "objname":"TransactionReportEbsMDI", "winsize":(0,0,903,483), "wintitle":"История операций над лицевым счётом пользователя", "tablecolumns":columns}
        self.transactions_types = [u"Другие операции", u"Периодические услуги", u"Разовые услуги", u"За трафик", u"За время", u"Подключаемые услуги", u"Платежи QIWI"]
        self.transactions_tables = [u"billservice_transaction",u"billservice_periodicalservicehistory",u"billservice_onetimeservicehistory",u"billservice_traffictransaction",u"billservice_timetransaction","billservice_addonservicetransaction", "qiwi_invoice"]
        super(TransactionsReportEbs, self).__init__(connection, initargs, parent)
        
    def ebsInterInit(self, initargs):
        self.user_edit = QtGui.QComboBox(self)
        self.user_edit.setGeometry(QtCore.QRect(100,12,201,20))
        self.user_edit.setObjectName("user_edit")    
        
        dt_now = datetime.datetime.now()
        
        self.date_start = QtGui.QDateTimeEdit(self)
        self.date_start.setGeometry(QtCore.QRect(420,9,161,20))
        self.date_start.setCalendarPopup(True)
        self.date_start.setObjectName("date_start")
        self.date_start.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)

        self.date_end = QtGui.QDateTimeEdit(self)
        self.date_end.setGeometry(QtCore.QRect(420,42,161,20))
        self.date_end.setDate(QtCore.QDate(dt_now.year, dt_now.month, dt_now.day))
        self.date_end.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.date_end.setCalendarPopup(True)
        self.date_end.setObjectName("date_end")
        self.date_end.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            self.date_start.setDateTime(settings.value("trans_date_start", QtCore.QVariant(QtCore.QDateTime(2000,1,1,0,0))).toDateTime())
            self.date_end.setDateTime(settings.value("trans_date_end", QtCore.QVariant(QtCore.QDateTime(2000,1,1,0,0))).toDateTime())
        except Exception, ex:
            print "Transactions settings error: ", ex

        self.date_start_label = QtGui.QLabel(self)
        self.date_start_label.setMargin(10)
        self.date_start_label.setObjectName("date_start_label")

        self.date_end_label = QtGui.QLabel(self)
        self.date_end_label.setMargin(10)
        self.date_end_label.setObjectName("date_end_label")

        self.user_label = QtGui.QLabel(self)
        self.user_label.setMargin(10)
        self.user_label.setObjectName("user_label")

        self.label_transactions_type = QtGui.QLabel(self)
        self.label_transactions_type.setMargin(10)

        self.label_cashier = QtGui.QLabel(self)
        self.label_cashier.setMargin(10)
           
        self.comboBox_transactions_type = QtGui.QComboBox(self)
        self.comboBox_cashier = QtGui.QComboBox(self)
        
        
        self.go_pushButton = QtGui.QPushButton(self)
        self.go_pushButton.setGeometry(QtCore.QRect(590,40,101,25))
        self.go_pushButton.setObjectName("go_pushButton")        
        #self.system_transactions_checkbox = QtGui.QCheckBox(self)
        #self.system_transactions_checkbox.setObjectName("system_transactions_checkbox")

        self.toolBar = QtGui.QToolBar(self)      
        
        self.toolBar.addWidget(self.user_label)
        self.toolBar.addWidget(self.user_edit)
        
        self.toolBar.addWidget(self.label_transactions_type)
        self.toolBar.addWidget(self.comboBox_transactions_type)
        self.toolBar.addWidget(self.label_cashier)
        self.toolBar.addWidget(self.comboBox_cashier)
        self.toolBar.addWidget(self.date_start_label)
        self.toolBar.addWidget(self.date_start)
        self.toolBar.addWidget(self.date_end_label)
        self.toolBar.addWidget(self.date_end)
        #self.toolBar.addWidget(self.system_transactions_checkbox)
        self.toolBar.addWidget(self.go_pushButton)
        self.toolBar.addSeparator()        
        
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)
        self.columns = {}

        self.columns["billservice_periodicalservicehistory"]=['#', u'Аккаунт', u"ФИО", u'Тарифный план', u'Услуга', u'Тип', u"Сумма", u"Дата"]
        self.columns["billservice_onetimeservicehistory"]=['#', u'Аккаунт', u"ФИО", u'Тарифный план', u'Услуга', u'Тип', u"Сумма", u"Дата"]
        self.columns["billservice_traffictransaction"] = ["#", u'Аккаунт', u"ФИО", u'Тарифный план', u'Сумма', u'Дата']
        self.columns["billservice_timetransaction"] = ["#", u'Аккаунт', u"ФИО", u'Тарифный план', u'Сумма', u'Дата']
        self.columns["billservice_addonservicetransaction"] = ["#", u'Аккаунт', u"ФИО", u'Услуга', u'Тип услуги', u'Сумма', u'Дата']
        self.columns["billservice_transaction"] = [u'#', u'Аккаунт', u"ФИО", u'Дата', u'Платёжный документ', u'Вид проводки', u"Выполнено", u'Тариф', u'Сумма', u'Комментарий', u"В долг", u"До числа"]
        self.columns["qiwi_invoice"] = [u'#', u'Аккаунт', u"ФИО", u"№ инвойса", u'Создан', u"Автозачисление", u'Оплачен', u"Сумма"]
       
    def ebsPostInit(self, initargs):
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        QtCore.QObject.connect(self.go_pushButton,QtCore.SIGNAL("clicked()"),self.refresh_table)
        QtCore.QObject.connect(self.comboBox_transactions_type,QtCore.SIGNAL("currentIndexChanged(int)"),self.setTableColumns)
        
        actList=[("actionDeleteTransaction", "Отменить проводку", "images/del.png", self.delete_transaction),]
        objDict = {self.tableWidget:["actionDeleteTransaction", ]}
        if not self.cassa:
            self.actionCreator(actList, objDict)
        self.setTableColumns()
        
    def retranslateUI(self, initargs):
        super(TransactionsReportEbs, self).retranslateUI(initargs)
        self.date_start_label.setText(QtGui.QApplication.translate("Dialog", "С", None, QtGui.QApplication.UnicodeUTF8))
        self.date_end_label.setText(QtGui.QApplication.translate("Dialog", "По", None, QtGui.QApplication.UnicodeUTF8))
        self.user_label.setText(QtGui.QApplication.translate("Dialog", "Пользователь", None, QtGui.QApplication.UnicodeUTF8))
        self.go_pushButton.setText(QtGui.QApplication.translate("Dialog", "Показать", None, QtGui.QApplication.UnicodeUTF8))
        self.date_end.setDisplayFormat(QtGui.QApplication.translate("Dialog", self.datetimeFormat, None, QtGui.QApplication.UnicodeUTF8))
        self.date_start.setDisplayFormat(QtGui.QApplication.translate("Dialog", self.datetimeFormat, None, QtGui.QApplication.UnicodeUTF8))
        #self.system_transactions_checkbox.setText(QtGui.QApplication.translate("Dialog", "Включить в отчёт системные проводки", None, QtGui.QApplication.UnicodeUTF8))        
        self.label_transactions_type.setText(QtGui.QApplication.translate("Dialog", "Тип", None, QtGui.QApplication.UnicodeUTF8))
        self.label_cashier.setText(QtGui.QApplication.translate("Dialog", "Кассир", None, QtGui.QApplication.UnicodeUTF8))
    
    def refresh(self):
        systemusers = self.connection.get_models("billservice_systemuser")
        self.connection.commit()
        self.comboBox_cashier.addItem(unicode(u'--Все--'))
        self.comboBox_cashier.setItemData(0, QtCore.QVariant(0))
        i=1
        for systemuser in systemusers:
           self.comboBox_cashier.addItem(unicode(systemuser.username))
           self.comboBox_cashier.setItemData(i, QtCore.QVariant(systemuser.id))
           i+=1
           
        accounts = self.connection.sql("SELECT * FROM billservice_account ORDER BY username ASC")
        self.connection.commit()
        self.user_edit.addItem(u"-Все клиенты-")
        self.user_edit.setItemData(0, QtCore.QVariant(0))
        i=1
        for account in accounts:
            self.user_edit.addItem(account.username)
            self.user_edit.setItemData(i, QtCore.QVariant(account.id))
            i+=1
        
        if self.account:
            self.user_edit.setCurrentIndex(self.user_edit.findText(self.account.username, QtCore.Qt.MatchCaseSensitive))
            self.setWindowTitle(u"История операций над лицевым счётом пользователя %s" % self.account.username)

        i=0
        for tr_type in self.transactions_types:
            self.comboBox_transactions_type.addItem(tr_type)
            self.comboBox_transactions_type.setItemData(i, QtCore.QVariant(i))
            i+=1
    def addrow(self, value, x, y, id=None, promise=False, date = None):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=""
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/user.png"))
        
        if promise:
            headerItem.setBackgroundColor(QtGui.QColor("lightblue"))
        headerItem.setText(unicode(value))
        if id:
            headerItem.id = id
            headerItem.date = date
        self.tableWidget.setItem(x,y,headerItem)
             
    def setTableColumns(self):
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        makeHeaders(self.columns[self.transactions_tables[self.comboBox_transactions_type.currentIndex()]], self.tableWidget)   
           
    def refresh_table(self):

        self.tableWidget.setSortingEnabled(False)
        self.setWindowTitle(u"История операций над лицевым счётом пользователя %s" % unicode(self.user_edit.currentText()))
        self.tableWidget.clearContents()
        start_date = self.date_start.dateTime().toPyDateTime()
        end_date = self.date_end.dateTime().toPyDateTime()

        account_id = self.user_edit.itemData(self.user_edit.currentIndex()).toInt()[0]

        if self.transactions_tables[self.comboBox_transactions_type.currentIndex()]=="billservice_transaction":
            sql = """SELECT transaction.*, transactiontype.name as transaction_type_name, tariff.name as tariff_name, (SELECT username FROM billservice_account WHERE id=transaction.account_id) as username, (SELECT fullname FROM billservice_account WHERE id=transaction.account_id) as fullname, (SELECT username FROM billservice_systemuser WHERE id=transaction.systemuser_id) as systemuser
                                            FROM billservice_transaction as transaction
                                            JOIN billservice_transactiontype as transactiontype ON transactiontype.internal_name = transaction.type_id
                                            LEFT JOIN billservice_tariff as tariff ON tariff.id = transaction.tarif_id   
                                            WHERE transaction.created between '%s' and '%s' %%s ORDER BY transaction.created DESC""" %  (start_date, end_date,)

            if account_id:
                sql = sql % " and transaction.account_id=%s %%s" % account_id
            else:
                sql = sql % " %s"

            systemuser_id = self.comboBox_cashier.itemData(self.comboBox_cashier.currentIndex()).toInt()[0]
            #print sql
            if systemuser_id!=0:
                sql = sql % " and transaction.systemuser_id=%s " % systemuser_id
            else:
                sql = sql % " "

            items = self.connection.sql(sql)
            self.connection.commit()
            self.tableWidget.setRowCount(len(items)+1)
            i=0
            sum = 0
            for item in items:
                self.addrow(i, i, 0, id=item.id, promise = item.promise, date = item.created)
                self.addrow(item.username, i, 1, promise = item.promise)
                self.addrow(item.fullname, i, 2, promise = item.promise)
                self.addrow(item.created.strftime(self.strftimeFormat), i, 3, promise = item.promise)
                self.addrow(item.bill, i, 4, promise = item.promise)
                self.addrow(item.transaction_type_name, i, 5, promise = item.promise)
                self.addrow(item.systemuser, i, 6, promise = item.promise)
                self.addrow(item.tariff_name, i, 7, promise = item.promise)
                self.addrow(item.summ*(-1), i, 8, promise = item.promise)
                self.addrow(item.description, i, 9, promise = item.promise)
                self.addrow(item.promise, i, 10, promise = item.promise)
                sum+=item.summ*(-1)
                if item.promise:
                    try:
                        self.addrow(item.end_promise.strftime(self.strftimeFormat), i, 11, promise = item.promise)
                    except Exception, e:
                        print e
                i+=1
            self.addrow(u"Итого", i, 7)
            self.addrow(sum, i, 8)
        if self.transactions_tables[self.comboBox_transactions_type.currentIndex()]=="billservice_periodicalservicehistory":
            services = self.connection.get_models("billservice_periodicalservice")
            s = {}
            for x in services:
                s[x.id] = x.name

            tariffs = self.connection.get_models("billservice_tariff")
            t = {}
            for x in tariffs:
                t[x.id] = x.name
                               
            sql = """
            SELECT psh.id, psh.service_id, psh.datetime, psh.accounttarif_id, (SELECT tarif_id FROM billservice_accounttarif WHERE id=psh.accounttarif_id) as tarif_id, psh.summ, (SELECT username FROM billservice_account WHERE id=psh.account_id) as username, (SELECT fullname FROM billservice_account WHERE id=psh.account_id) as fullname, psh.type_id 
            FROM billservice_periodicalservicehistory as psh 
            WHERE psh.datetime between '%s' and '%s' %%s ORDER BY psh.datetime DESC
            """ % (start_date, end_date,)
            
            if account_id:
                sql = sql % " and psh.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            items = self.connection.sql(sql)
            self.connection.commit()
            self.tableWidget.setRowCount(len(items)+1)
            i=0
            
            ['#', u'Аккаунт', u'Тарифный план', u'Услуга', u'Тип', u"Сумма", u"Дата"]
            sum = 0
            for item in items:
                self.addrow(i, i, 0, id = item.id, date = item.datetime)
                self.addrow(item.username, i, 1)
                self.addrow(item.fullname, i, 2)
                self.addrow(t.get(item.tarif_id), i, 3)
                self.addrow(s.get(item.service_id), i, 4)
                self.addrow(item.type_id, i, 5)
                self.addrow(item.summ, i, 6)
                self.addrow(item.datetime.strftime(self.strftimeFormat), i, 7)
                i+=1
                sum+=item.summ
            self.addrow(u"Итого", i, 5)
            self.addrow(sum, i, 6)
        if self.transactions_tables[self.comboBox_transactions_type.currentIndex()]=="billservice_onetimeservicehistory":
            services = self.connection.get_models("billservice_onetimeservice")
            s = {}
            for x in services:
                s[x.id] = x.name
 
            tariffs = self.connection.get_models("billservice_tariff")
            t = {}
            for x in tariffs:
                t[x.id] = x.name
                               
            sql = """
            SELECT osh.id, osh.onetimeservice_id, osh.datetime, osh.accounttarif_id, (SELECT tarif_id FROM billservice_accounttarif WHERE id=osh.accounttarif_id) as tarif_id, osh.summ, (SELECT username FROM billservice_account WHERE id=osh.account_id) as username, (SELECT fullname FROM billservice_account WHERE id=osh.account_id) as fullname 
            FROM billservice_onetimeservicehistory as osh 
            WHERE osh.datetime between '%s' and '%s' %%s ORDER BY osh.datetime DESC
            """ % (start_date, end_date,)
            
            if account_id:
                sql = sql % " and osh.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            items = self.connection.sql(sql)
            self.connection.commit()
            self.tableWidget.setRowCount(len(items)+1)
            i=0
            
            ['#', u'Аккаунт', u'Тарифный план', u'Услуга', u"Сумма", u"Дата"]
            sum = 0
            for item in items:
                self.addrow(i, i, 0, id = item.id, date = item.datetime)
                self.addrow(item.username, i, 1)
                self.addrow(item.fullname, i, 2)
                self.addrow(t.get(item.tarif_id), i, 3)
                self.addrow(s.get(item.onetimeservice_id), i, 4)
                self.addrow(item.summ, i, 5)
                self.addrow(item.datetime.strftime(self.strftimeFormat), i, 6)
                i+=1
                sum += item.summ
            self.addrow(u"Итого", i, 4)
            self.addrow(sum, i, 5)                
        if self.transactions_tables[self.comboBox_transactions_type.currentIndex()]=="billservice_traffictransaction":
            tariffs = self.connection.get_models("billservice_tariff")
            t = {}
            for x in tariffs:
                t[x.id] = x.name
                               
            sql = """
            SELECT tr.id, tr.datetime, tr.accounttarif_id, (SELECT tarif_id FROM billservice_accounttarif WHERE id=tr.accounttarif_id) as tarif_id, tr.summ, (SELECT username FROM billservice_account WHERE id=tr.account_id) as username , (SELECT fullname FROM billservice_account WHERE id=tr.account_id) as fullname
            FROM billservice_traffictransaction as tr 
            WHERE tr.datetime between '%s' and '%s' %%s ORDER BY tr.datetime DESC
            """ % (start_date, end_date,)
            
            if account_id:
                sql = sql % " and tr.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            items = self.connection.sql(sql)
            self.connection.commit()
            self.tableWidget.setRowCount(len(items)+1)
            i=0
            
            ["#", u'Аккаунт', u'Тарифный план', u'Сумма', u'Дата']
            sum = 0
            for item in items:
                self.addrow(i, i, 0, id = item.id, date = item.datetime)
                self.addrow(item.username, i, 1)
                self.addrow(item.fullname, i, 2)
                self.addrow(t.get(item.tarif_id), i, 3)
                self.addrow(item.summ, i, 4)
                self.addrow(item.datetime.strftime(self.strftimeFormat), i, 5)
                i+=1
                sum+=item.summ
                
            self.addrow(u"Итого", i, 4)
            self.addrow(sum, i, 5)   
            
        if self.transactions_tables[self.comboBox_transactions_type.currentIndex()]=="billservice_timetransaction":
            #print 111
            tariffs = self.connection.get_models("billservice_tariff")
            t = {}
            for x in tariffs:
                t[x.id] = x.name
                               
            sql = """
            SELECT tr.id, tr.datetime, tr.accounttarif_id, (SELECT tarif_id FROM billservice_accounttarif WHERE id=tr.accounttarif_id) as tarif_id, tr.summ, (SELECT username FROM billservice_account WHERE id=tr.account_id) as username, (SELECT fullname FROM billservice_account WHERE id=tr.account_id) as fullname
            FROM billservice_timetransaction as tr 
            WHERE tr.datetime between '%s' and '%s' %%s ORDER BY tr.datetime DESC
            """ % (start_date, end_date,)
            
            if account_id:
                sql = sql % " and tr.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            items = self.connection.sql(sql)
            self.connection.commit()
            self.tableWidget.setRowCount(len(items)+1)
            i=0
            sum = 0
            for item in items:
                self.addrow(i, i, 0, id = item.id, date = item.datetime)
                self.addrow(item.username, i, 1)
                self.addrow(item.fullname, i, 2)
                self.addrow(t.get(item.tarif_id), i, 3)
                self.addrow(item.summ, i, 4)
                self.addrow(item.datetime.strftime(self.strftimeFormat), i, 5)
                i+=1
                sum +=item.summ
            self.addrow(u"Итого", i, 3)
            self.addrow(sum, i, 4)                                 
        self.tableWidget.setColumnHidden(0, False)
        
        if self.transactions_tables[self.comboBox_transactions_type.currentIndex()]=="billservice_addonservicetransaction":
            #print 111
            tr_types = self.connection.get_models("billservice_transactiontype")
            t = {}
            for x in tr_types:
                t[x.internal_name] = x.name
                               
            #print (start_date, end_date,)
            sql = """
            select addst.id, (SELECT name FROM billservice_addonservice WHERE id=addst.service_id) as service_name, addst.summ, addst.created, addst.type_id, (SELECT username FROM billservice_account WHERE id=addst.account_id) as username, (SELECT fullname FROM billservice_account WHERE id=addst.account_id) as fullname
            FROM billservice_addonservicetransaction as addst
            WHERE addst.created>='%s' and addst.created<='%s' %%s ORDER BY created ASC
            """ % (start_date, end_date,)
            
            if account_id:
                sql = sql % " and addst.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            items = self.connection.sql(sql)
            self.connection.commit()
            self.tableWidget.setRowCount(len(items)+1)
            i=0
            sum = 0
            ["#", u'Аккаунт', u'Услуга', u'Тип услуги', u'Сумма', u'Дата']
            for item in items:
                self.addrow(i, i, 0, id = item.id, date = item.created)
                self.addrow(item.username, i, 1)
                self.addrow(item.fullname, i, 2)
                self.addrow(item.service_name, i, 3)
                self.addrow(t[item.type_id], i, 4)
                self.addrow(item.summ, i, 5)
                self.addrow(item.created.strftime(self.strftimeFormat), i, 6)
                i+=1
                sum +=item.summ
            self.addrow(u"Итого", i, 4)
            self.addrow(sum, i, 5)                                 
        self.tableWidget.setColumnHidden(0, False)

        if self.transactions_tables[self.comboBox_transactions_type.currentIndex()]=="qiwi_invoice":
            #print 111
            #tr_types = self.connection.get_models("billservice_transactiontype")
            #t = {}
            #for x in tr_types:
            #    t[x.internal_name] = x.name
                               
            #print (start_date, end_date,)
            [u'#', u'Аккаунт', u"ФИО",  u"№ инвойса", u'Создан', u"Автозачисление", u'Оплачен', u"Сумма"]
            sql = """
            SELECT qi.id as id, (SELECT username FROM billservice_account WHERE id=qi.account_id) as username,(SELECT fullname FROM billservice_account WHERE id=qi.account_id) as fullname,qi,created as created, qi.autoaccept, qi.date_accepted, qi.summ
            FROM qiwi_invoice as qi
            WHERE qi.created>='%s' and qi.created<='%s' %%s ORDER BY created ASC
            """ % (start_date, end_date,)
            
            if account_id:
                sql = sql % " and qi.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            items = self.connection.sql(sql)
            self.connection.commit()
            self.tableWidget.setRowCount(len(items)+2)
            i=0
            sum = 0
            allsumm=0
            for item in items:
                self.addrow(i, i, 0, id = item.id, date = item.created)
                self.addrow(item.username, i, 1)
                self.addrow(item.fullname, i, 2)
                self.addrow(item.id, i, 3)
                self.addrow(item.created.strftime(self.strftimeFormat), i, 4)
                self.addrow(item.autoaccept, i, 5)
                try:
                    self.addrow(item.date_accepted.strftime(self.strftimeFormat), i, 6)
                except:
                    self.addrow('', i, 6)
                self.addrow(item.summ, i, 7)
                i+=1
                allsumm +=item.summ
                if item.date_accepted:
                    sum +=item.summ
            self.addrow(u"Инвойсов на сумму", i, 6)
            self.addrow(allsumm, i, 7)
            self.addrow(u"Оплачено на сумму", i+1, 6)
            self.addrow(sum, i+1, 7)
                                             
        self.tableWidget.setColumnHidden(0, False)

        
                
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue("trans_date_start", QtCore.QVariant(self.date_start.dateTime()))
            settings.setValue("trans_date_end", QtCore.QVariant(self.date_end.dateTime()))
        except Exception, ex:
            print "Transactions settings save error: ", ex
        #self.tableWidget.setSortingEnabled(True)
        

    def get_selected_ids(self):
        ids = []
        for r in self.tableWidget.selectedItems():
            #print r.column()
            if r.column()==0:
                ids.append((r.id, r.date))
        return ids
    
   
    def delete_transaction(self):
        ids = self.get_selected_ids()
        #print ids
        
        if self.transactions_tables[self.comboBox_transactions_type.currentIndex()]=="billservice_transaction":
            idss = []
            for id,date in ids:
                idss.append(id)
                
            self.connection.transaction_delete(idss)      
        elif  self.transactions_tables[self.comboBox_transactions_type.currentIndex()]=="billservice_periodicalservicehistory":
            for id,date in ids:
                self.connection.command("DELETE FROM billservice_periodicalservicehistory WHERE id=%s and datetime='%s'" % (id, date,))
                self.connection.commit()
        elif  self.transactions_tables[self.comboBox_transactions_type.currentIndex()]=="billservice_onetimeservicehistory":
            for id,date in ids:
                self.connection.command("DELETE FROM billservice_onetimeservicehistory WHERE id=%s and datetime='%s'" % (id, date,))
                self.connection.commit()
        elif  self.transactions_tables[self.comboBox_transactions_type.currentIndex()]=="billservice_addonservicetransaction":
            for id,date in ids:
                self.connection.command("DELETE FROM billservice_addonservicetransaction WHERE id=%s and created='%s'" % (id, date,))
                self.connection.commit()
        elif  self.transactions_tables[self.comboBox_transactions_type.currentIndex()]=="billservice_traffictransaction":
            for id,date in ids:
                self.connection.command("DELETE FROM billservice_traffictransaction WHERE id=%s and datetime='%s'" % (id, date,))
                self.connection.commit()
        elif  self.transactions_tables[self.comboBox_transactions_type.currentIndex()]=="billservice_timetransaction":
            for id,date in ids:
                self.connection.command("DELETE FROM billservice_timetransaction WHERE id=%s and datetime='%s'" % (id, date,))
                self.connection.commit()         
        elif  self.transactions_tables[self.comboBox_transactions_type.currentIndex()]=="qiwi_invoice":
            for id,date in ids:
                self.connection.command("DELETE FROM qiwi_invoice WHERE id=%s and created='%s'" % (id, date,))
                self.connection.commit()                            
        self.refresh_table()
     
class TransactionsReport(QtGui.QMainWindow):
    def __init__(self, connection ,account=None):

        super(TransactionsReport, self).__init__()
        self.setObjectName("TransactionReportMDI")
        self.account = account
        self.connection = connection
        self.connection.commit()
        self.resize(QtCore.QSize(QtCore.QRect(0,0,903,483).size()).expandedTo(self.minimumSizeHint()))
        self.datetimeFormat = "dd" + dateDelim + "MM" + dateDelim + "yyyy hh:mm:ss"
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"

        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget = tableFormat(self.tableWidget) 
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        

        self.setCentralWidget(self.tableWidget)
        
        self.user_edit = QtGui.QComboBox(self)
        self.user_edit.setGeometry(QtCore.QRect(100,12,201,20))
        self.user_edit.setObjectName("user_edit")
        
        
        
        self.date_start = QtGui.QDateTimeEdit(self)
        self.date_start.setGeometry(QtCore.QRect(420,9,161,20))
        self.date_start.setCalendarPopup(True)
        self.date_start.setObjectName("date_start")
        self.date_start.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)


        self.date_end = QtGui.QDateTimeEdit(self)
        self.date_end.setGeometry(QtCore.QRect(420,42,161,20))
        self.date_end.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.date_end.setCalendarPopup(True)
        self.date_end.setObjectName("date_end")
        self.date_end.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            self.date_start.setDateTime(settings.value("trans_date_start", QtCore.QVariant(QtCore.QDateTime(2000,1,1,0,0))).toDateTime())
            self.date_end.setDateTime(settings.value("trans_date_end", QtCore.QVariant(QtCore.QDateTime(2000,1,1,0,0))).toDateTime())
        except Exception, ex:
            print "Transactions settings error: ", ex

        self.date_start_label = QtGui.QLabel(self)
        self.date_start_label.setMargin(10)
        self.date_start_label.setObjectName("date_start_label")

        self.date_end_label = QtGui.QLabel(self)
        self.date_end_label.setMargin(10)
        self.date_end_label.setObjectName("date_end_label")

        self.user_label = QtGui.QLabel(self)
        self.user_label.setMargin(10)
        self.user_label.setObjectName("user_label")

        self.go_pushButton = QtGui.QPushButton(self)
        self.go_pushButton.setGeometry(QtCore.QRect(590,40,101,25))
        self.go_pushButton.setObjectName("go_pushButton")


        
        self.system_transactions_checkbox = QtGui.QCheckBox(self)
        self.system_transactions_checkbox.setObjectName("system_transactions_checkbox")

        self.toolBar = QtGui.QToolBar(self)
        
        
        self.toolBar.addWidget(self.user_label)
        self.toolBar.addWidget(self.user_edit)
        
        self.toolBar.addWidget(self.date_start_label)
        self.toolBar.addWidget(self.date_start)
        self.toolBar.addWidget(self.date_end_label)
        self.toolBar.addWidget(self.date_end)
        self.toolBar.addWidget(self.system_transactions_checkbox)
        self.toolBar.addWidget(self.go_pushButton)
        self.toolBar.addSeparator()      
        
        
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)
        
        self.actionDeleteTransaction = QtGui.QAction(self)
        self.actionDeleteTransaction.setIcon(QtGui.QIcon("images/del.png"))
        self.actionDeleteTransaction.setObjectName("actionDeleteTransaction")
        
        self.tableWidget.addAction(self.actionDeleteTransaction)
        
        self.retranslateUi()
        QtCore.QObject.connect(self.actionDeleteTransaction, QtCore.SIGNAL("triggered()"), self.delete_transaction)

        #QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        #QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        
        QtCore.QObject.connect(self.go_pushButton,QtCore.SIGNAL("clicked()"),self.refresh_table)
        self.fixtures()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "История операций над лицевым счётом пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.date_start_label.setText(QtGui.QApplication.translate("Dialog", "С", None, QtGui.QApplication.UnicodeUTF8))
        self.date_end_label.setText(QtGui.QApplication.translate("Dialog", "По", None, QtGui.QApplication.UnicodeUTF8))
        self.user_label.setText(QtGui.QApplication.translate("Dialog", "Пользователь", None, QtGui.QApplication.UnicodeUTF8))
        self.go_pushButton.setText(QtGui.QApplication.translate("Dialog", "Пыщь", None, QtGui.QApplication.UnicodeUTF8))
        self.date_end.setDisplayFormat(QtGui.QApplication.translate("Dialog", self.datetimeFormat, None, QtGui.QApplication.UnicodeUTF8))
        self.date_start.setDisplayFormat(QtGui.QApplication.translate("Dialog", self.datetimeFormat, None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()

        columns = [u'#', u'Дата', u'Платёжный документ', u'Вид проводки', u'Тариф', u'Сумма', u'Комментарий']
        makeHeaders(columns, self.tableWidget)
        
        #self.save_pushButton.setText(QtGui.QApplication.translate("Dialog", "Сохранить", None, QtGui.QApplication.UnicodeUTF8))
        self.system_transactions_checkbox.setText(QtGui.QApplication.translate("Dialog", "Включить в отчёт системные проводки", None, QtGui.QApplication.UnicodeUTF8))
        #self.write_off_label.setText(QtGui.QApplication.translate("Dialog", "Списано:", None, QtGui.QApplication.UnicodeUTF8))
        #self.write_off.setText(QtGui.QApplication.translate("Dialog", "0", None, QtGui.QApplication.UnicodeUTF8))
        #self.write_on_label.setText(QtGui.QApplication.translate("Dialog", "Начислено", None, QtGui.QApplication.UnicodeUTF8))
        #self.write_on.setText(QtGui.QApplication.translate("Dialog", "0", None, QtGui.QApplication.UnicodeUTF8))
        #self.ballance_label.setText(QtGui.QApplication.translate("Dialog", "Баланс на конец периода", None, QtGui.QApplication.UnicodeUTF8))
        #self.ballance.setText(QtGui.QApplication.translate("Dialog", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDeleteTransaction.setText(u"Отменить проводку")
        
    def fixtures(self):
        accounts = self.connection.sql("SELECT * FROM billservice_account ORDER BY username ASC")
        self.connection.commit()
        for account in accounts:
            self.user_edit.addItem(account.username)
        
        if self.account:
            self.user_edit.setCurrentIndex(self.user_edit.findText(self.account.username, QtCore.Qt.MatchCaseSensitive))
            self.setWindowTitle(u"История операций над лицевым счётом пользователя %s" % self.account.username)


    def addrow(self, value, x, y):
        if value==None:
            value=""
            
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
                
    def refresh_table(self):
        self.tableWidget.setSortingEnabled(False)
        self.setWindowTitle(u"История операций над лицевым счётом пользователя %s" % unicode(self.user_edit.currentText()))
        self.tableWidget.clearContents()
        start_date = self.date_start.dateTime().toPyDateTime()
        end_date = self.date_end.dateTime().toPyDateTime()
        
        if self.system_transactions_checkbox.checkState()==2:
            transactions = self.connection.sql("""SELECT transaction.*, transactiontype.name as transaction_type_name, tariff.name as tariff_name FROM billservice_transaction as transaction
                                            JOIN billservice_transactiontype as transactiontype ON transactiontype.internal_name = transaction.type_id
                                            LEFT JOIN billservice_tariff as tariff ON tariff.id = transaction.tarif_id   
                                            WHERE transaction.created between '%s' and '%s' and transaction.account_id=%d ORDER BY transaction.created DESC""" %  (start_date, end_date, self.connection.get("SELECT * FROM billservice_account WHERE username='%s'" % unicode(self.user_edit.currentText())).id))
        else:
            transactions = self.connection.sql("""SELECT transaction.*,transactiontype.name as transaction_type_name, tariff.name as tariff_name
            FROM billservice_transaction as transaction
            JOIN billservice_transactiontype as transactiontype ON transactiontype.internal_name = transaction.type_id
            LEFT JOIN billservice_tariff as tariff ON tariff.id = transaction.tarif_id
            WHERE transaction.type_id='MANUAL_TRANSACTION' and transaction.created between '%s' and '%s' and transaction.account_id=%d  ORDER BY transaction.created DESC""" %  (start_date, end_date, self.connection.get("SELECT * FROM billservice_account WHERE username='%s'" % unicode(self.user_edit.currentText())).id))            
        self.connection.commit()
        self.tableWidget.setRowCount(len(transactions))
        i=0
        ballance = 0
        write_on = 0
        write_off = 0
        for transaction in transactions:
            self.addrow(transaction.id, i, 0)
            self.addrow(transaction.created.strftime(self.strftimeFormat), i, 1)
            self.addrow(transaction.bill, i, 2)
            self.addrow(transaction.transaction_type_name, i, 3)
            self.addrow(transaction.tariff_name, i, 4)
            self.addrow(transaction.summ, i, 5)
            self.addrow(transaction.description, i, 6)
            i+=1
            #if transaction.summ<0:
            #    write_on +=transaction.summ*(-1)                             
            #if transaction.summ>0:
            #    write_off +=transaction.summ
        self.tableWidget.setColumnHidden(0, True)
                
        #self.write_off.setText(unicode(write_off))
        #self.write_on.setText(unicode(write_on))
        #self.ballance.setText(unicode(write_on-write_off))
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue("trans_date_start", QtCore.QVariant(self.date_start.dateTime()))
            settings.setValue("trans_date_end", QtCore.QVariant(self.date_end.dateTime()))
        except Exception, ex:
            print "Transactions settings save error: ", ex
        self.tableWidget.setSortingEnabled(True)
        
    def delete_transaction(self):
        ids = []
        #import Pyro
        for index in self.tableWidget.selectedIndexes():
            #print index.row(), index.column()
            if not index.column()==0:
                continue
            
            i=unicode(self.tableWidget.item(index.row(), 0).text())
            try:
                ids.append(int(i))
            except Exception, e:
                print "can not convert transaction id to int"      
        
        self.connection.transaction_delete(ids)      
        self.connection.commit()
        self.refresh_table()
        
class ReportPropertiesDialog(QtGui.QDialog):
    def __init__(self, connection):
        super(ReportPropertiesDialog, self).__init__()
        self.connection = connection
        self.datetimeFormat = "dd" + dateDelim + "MM" + dateDelim + "yyyy hh:mm:ss"
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        self.users = []
        self.classes = []
        self.nas = None
        self.start_date = datetime.datetime.now()
        self.end_date = datetime.datetime.now()
        
        self.resize(QtCore.QSize(QtCore.QRect(0,0,381,450).size()).expandedTo(self.minimumSizeHint()))

        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setGeometry(QtCore.QRect(0,8,381,391))
        self.tabWidget.setObjectName("tabWidget")

        self.general_tab = QtGui.QWidget()
        self.general_tab.setObjectName("general_tab")

        self.nas_label = QtGui.QLabel(self.general_tab)
        self.nas_label.setGeometry(QtCore.QRect(10,70,86,20))
        self.nas_label.setObjectName("nas_label")

        self.to_label = QtGui.QLabel(self.general_tab)
        self.to_label.setGeometry(QtCore.QRect(10,36,82,20))
        self.to_label.setObjectName("to_label")

        self.nas_comboBox = QtGui.QComboBox(self.general_tab)
        self.nas_comboBox.setGeometry(QtCore.QRect(100,70,134,20))
        self.nas_comboBox.setObjectName("nas_comboBox")

        self.to_dateTimeEdit = QtGui.QDateTimeEdit(self.general_tab)
        self.to_dateTimeEdit.setGeometry(QtCore.QRect(100,36,134,20))
        self.to_dateTimeEdit.setMinimumDate(QtCore.QDate(2008,1,1))
        self.to_dateTimeEdit.setCalendarPopup(True)
        self.to_dateTimeEdit.setObjectName("to_dateTimeEdit")
        self.to_dateTimeEdit.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)

        self.all_users_listWidget = QtGui.QListWidget(self.general_tab)
        self.all_users_listWidget.setGeometry(QtCore.QRect(10,120,161,192))
        self.all_users_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.all_users_listWidget.setSelectionRectVisible(True)
        self.all_users_listWidget.setObjectName("all_users_listWidget")

        self.selected_users_listWidget = QtGui.QListWidget(self.general_tab)
        self.selected_users_listWidget.setGeometry(QtCore.QRect(210,120,161,192))
        self.selected_users_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.selected_users_listWidget.setObjectName("selected_users_listWidget")

        self.from_dateTimeEdit = QtGui.QDateTimeEdit(self.general_tab)
        self.from_dateTimeEdit.setGeometry(QtCore.QRect(100,10,134,20))
        self.from_dateTimeEdit.setMinimumDate(QtCore.QDate(2008,1,1))
        self.from_dateTimeEdit.setCalendarPopup(True)
        self.from_dateTimeEdit.setObjectName("from_dateTimeEdit")
        self.from_dateTimeEdit.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)

        self.from_label = QtGui.QLabel(self.general_tab)
        self.from_label.setGeometry(QtCore.QRect(10,10,82,20))
        self.from_label.setObjectName("from_label")

        self.all_users_label = QtGui.QLabel(self.general_tab)
        self.all_users_label.setGeometry(QtCore.QRect(10,100,161,16))
        self.all_users_label.setObjectName("all_users_label")

        self.selected_users_label = QtGui.QLabel(self.general_tab)
        self.selected_users_label.setGeometry(QtCore.QRect(210,100,161,16))
        self.selected_users_label.setObjectName("selected_users_label")

        self.remove_user_toolButton = QtGui.QToolButton(self.general_tab)
        self.remove_user_toolButton.setGeometry(QtCore.QRect(181,207,21,20))
        self.remove_user_toolButton.setObjectName("remove_user_toolButton")

        self.select_user_toolButton = QtGui.QToolButton(self.general_tab)
        self.select_user_toolButton.setGeometry(QtCore.QRect(181,181,21,20))
        self.select_user_toolButton.setObjectName("select_user_toolButton")

        self.with_grouping_checkBox = QtGui.QCheckBox(self.general_tab)
        self.with_grouping_checkBox.setGeometry(QtCore.QRect(10,320,231,19))
        self.with_grouping_checkBox.setObjectName("with_grouping_checkBox")

        self.order_by_desc = QtGui.QCheckBox(self.general_tab)
        self.order_by_desc.setGeometry(QtCore.QRect(10,340,231,19))
        self.order_by_desc.setObjectName("order_by_desc")
        self.tabWidget.addTab(self.general_tab,"")

        self.classes_tab = QtGui.QWidget()
        self.classes_tab.setObjectName("classes_tab")

        self.selected_classes_listWidget = QtGui.QListWidget(self.classes_tab)
        self.selected_classes_listWidget.setGeometry(QtCore.QRect(210,20,161,291))
        self.selected_classes_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.selected_classes_listWidget.setObjectName("selected_classes_listWidget")

        self.all_classes_listWidget = QtGui.QListWidget(self.classes_tab)
        self.all_classes_listWidget.setGeometry(QtCore.QRect(10,20,161,291))
        self.all_classes_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.all_classes_listWidget.setSelectionRectVisible(True)
        self.all_classes_listWidget.setObjectName("all_classes_listWidget")

        self.all_classes_label = QtGui.QLabel(self.classes_tab)
        self.all_classes_label.setGeometry(QtCore.QRect(10,0,161,16))
        self.all_classes_label.setObjectName("all_classes_label")

        self.selected_classes_label = QtGui.QLabel(self.classes_tab)
        self.selected_classes_label.setGeometry(QtCore.QRect(210,0,161,16))
        self.selected_classes_label.setObjectName("selected_classes_label")

        self.select_class_toolButton = QtGui.QToolButton(self.classes_tab)
        self.select_class_toolButton.setGeometry(QtCore.QRect(181,111,21,20))
        self.select_class_toolButton.setObjectName("select_class_toolButton")

        self.remove_class_toolButton = QtGui.QToolButton(self.classes_tab)
        self.remove_class_toolButton.setGeometry(QtCore.QRect(181,137,21,20))
        self.remove_class_toolButton.setObjectName("remove_class_toolButton")
        self.tabWidget.addTab(self.classes_tab,"")

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(100,410,171,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        
        self.retranslateUi()
        
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"),self.reject)
        
        QtCore.QObject.connect(self.select_user_toolButton, QtCore.SIGNAL("clicked()"),self.addUser)
        QtCore.QObject.connect(self.remove_user_toolButton, QtCore.SIGNAL("clicked()"),self.delUser)

        QtCore.QObject.connect(self.all_users_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"),self.addUser)
        QtCore.QObject.connect(self.selected_users_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"),self.delUser)        
        

        QtCore.QObject.connect(self.select_class_toolButton, QtCore.SIGNAL("clicked()"), self.addClass)
        QtCore.QObject.connect(self.remove_class_toolButton, QtCore.SIGNAL("clicked()"), self.delClass)
        
        QtCore.QObject.connect(self.all_classes_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.addClass)
        QtCore.QObject.connect(self.selected_classes_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.delClass)

        self.fixtures()
        #QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройки отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.select_user_toolButton.setText(QtGui.QApplication.translate("Dialog", ">", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_user_toolButton.setText(QtGui.QApplication.translate("Dialog", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.nas_label.setText(QtGui.QApplication.translate("Dialog", "Сервер доступа:", None, QtGui.QApplication.UnicodeUTF8))
        self.to_label.setText(QtGui.QApplication.translate("Dialog", "До:", None, QtGui.QApplication.UnicodeUTF8))
        self.to_dateTimeEdit.setDisplayFormat(QtGui.QApplication.translate("Dialog", self.datetimeFormat, None, QtGui.QApplication.UnicodeUTF8))
        self.from_dateTimeEdit.setDisplayFormat(QtGui.QApplication.translate("Dialog", self.datetimeFormat, None, QtGui.QApplication.UnicodeUTF8))
        self.from_label.setText(QtGui.QApplication.translate("Dialog", "От:", None, QtGui.QApplication.UnicodeUTF8))
        self.all_users_label.setText(QtGui.QApplication.translate("Dialog", "Доступные пользователи", None, QtGui.QApplication.UnicodeUTF8))
        self.selected_users_label.setText(QtGui.QApplication.translate("Dialog", "Выбранные пользователи", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.general_tab), QtGui.QApplication.translate("Dialog", "Общие настройки", None, QtGui.QApplication.UnicodeUTF8))
        self.select_class_toolButton.setText(QtGui.QApplication.translate("Dialog", ">", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_class_toolButton.setText(QtGui.QApplication.translate("Dialog", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.all_classes_label.setText(QtGui.QApplication.translate("Dialog", "Доступные классы", None, QtGui.QApplication.UnicodeUTF8))
        self.selected_classes_label.setText(QtGui.QApplication.translate("Dialog", "Выбранные классы", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.classes_tab), QtGui.QApplication.translate("Dialog", "Классы трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.with_grouping_checkBox.setText(QtGui.QApplication.translate("Dialog", "С группировкой", None, QtGui.QApplication.UnicodeUTF8))
        self.order_by_desc.setText(QtGui.QApplication.translate("Dialog", "Выводить в обратном порядке", None, QtGui.QApplication.UnicodeUTF8))
        #self.with_grouping_checkBox.setCheckState(QtCore.Qt.Checked)
        #self.order_by_desc.setCheckState(QtCore.Qt.Checked)
        
    def fixtures(self):
        users = self.connection.sql("SELECT * FROM billservice_account ORDER BY username ASC")
        self.connection.commit()
        for user in users:
            item = QtGui.QListWidgetItem()
            item.setText(user.username)
            item.id = user.id
            self.all_users_listWidget.addItem(item)
            
        
        classes = self.connection.sql("SELECT * FROM nas_trafficclass ORDER BY name ASC")
        self.connection.commit()
        for clas in classes:
            item = QtGui.QListWidgetItem()
            item.setText(clas.name)
            item.id = clas.id
            self.all_classes_listWidget.addItem(item)
            
        nasses = self.connection.sql("SELECT * FROM nas_nas")
        self.connection.commit()
        self.nas_comboBox.addItem('')
        for nas in nasses:
            self.nas_comboBox.addItem(nas.name)
        
    def addUser(self):
        selected_items = self.all_users_listWidget.selectedItems()
        
        for item in selected_items:
            self.all_users_listWidget.takeItem(self.all_users_listWidget.row(item))
            self.selected_users_listWidget.addItem(item)
            
        self.selected_users_listWidget.sortItems()
        
    def delUser(self):
        selected_items = self.selected_users_listWidget.selectedItems()
        
        for item in selected_items:
            self.selected_users_listWidget.takeItem(self.selected_users_listWidget.row(item))
            self.all_users_listWidget.addItem(item)
        self.all_users_listWidget.sortItems()
        
    def addClass(self):
        selected_items = self.all_classes_listWidget.selectedItems()
        #print 1
        for item in selected_items:
            self.all_classes_listWidget.takeItem(self.all_classes_listWidget.row(item))
            self.selected_classes_listWidget.addItem(item)
        self.selected_classes_listWidget.sortItems()
        
    def delClass(self):
        selected_items = self.selected_classes_listWidget.selectedItems()
        #print 2
        for item in selected_items:
            self.selected_classes_listWidget.takeItem(self.selected_classes_listWidget.row(item))
            self.all_classes_listWidget.addItem(item)
        self.all_classes_listWidget.sortItems()
        
        
    def accept(self):
        self.users = []
        self.classes = []
        self.nas = None
        for x in xrange(0, self.selected_users_listWidget.count()):
            self.users.append(self.selected_users_listWidget.item(x).id)
            
        for x in xrange(0, self.selected_classes_listWidget.count()):
            self.classes.append(self.selected_classes_listWidget.item(x).id)
            
        if self.nas_comboBox.currentText()!='':
            self.nas = self.connection.get("SELECT * FROM nas_nas WHERE name='%s'" % unicode(self.nas_comboBox.currentText()))
            self.connection.commit()
        self.start_date = self.from_dateTimeEdit.dateTime().toPyDateTime()
        self.end_date = self.to_dateTimeEdit.dateTime().toPyDateTime()
        QtGui.QDialog.accept(self)
        
        
class NetFlowReportEbs(ebsTabs_n_TablesWindow):
    def __init__(self, connection):
        #columns_t0=['#', u'Аккаунт', u'Класс трафика', u'Протокол', u'Источник',  u'Получатель', u'Передано', u'Дата']
        columns_t0=['#', u'Аккаунт', u'Источник', u'Получатель', u'Передано',u'Дата']
        columns_t1=[u'Класс', u'Принято',u'Передано', u'Сумма',''] 
        initargs = {"setname":"netflow_frame_header", "objname":"NetFlowReportEbsMDI", "winsize":(0,0,800,587), "wintitle":"Сетевая статистика"}
        tabargs= [["tab0", columns_t0, "Детальная статистика"], ["tab1", columns_t1, "Сводная статистика"]]
        self.child = ReportPropertiesDialog(connection = connection)
        self.used = False
        super(NetFlowReportEbs, self).__init__(connection, initargs, tabargs)
        
    def ebsPreInit(self, initargs, tabargs):
        self.current_page=0
        self.protocols_reverse = {
          '0':'',
          '37': 'ddp',
          '98': 'encap',
          '3': 'ggp',
          '47': 'gre',
          '20': 'hmp',
          '1' : 'ICMP',
          '38':'idpr-cmtp',
          '2': 'igmp',
          '4': 'ipencap',
          '94': 'ipip',
          '89': 'ospf',
          '27': 'rdp',
          '6' : 'TCP',
          '17': 'UDP'
          }
        
        
    def ebsInterInit(self, initargs, tabargs):
        self.label = QtGui.QLabel(u"Навигатор")
        self.button_start = QtGui.QPushButton()
        self.button_start.setText(u"|<<")
        self.button_start.setMaximumHeight(19)
        self.button_start.setMaximumWidth(28)
        
        self.button_back = QtGui.QPushButton()
        self.button_back.setText(u"<")
        self.button_back.setMaximumHeight(19)
        self.button_back.setMaximumWidth(28)

        self.button_forward = QtGui.QPushButton()
        self.button_forward.setText(u">")
        self.button_forward.setMaximumHeight(19)
        self.button_forward.setMaximumWidth(28)
        self.status_label= QtGui.QLabel()
        
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        
        self.statusBar().addWidget(self.label)
        self.statusBar().addWidget(self.button_start)
        self.statusBar().addWidget(self.button_back)
        self.statusBar().addWidget(self.button_forward)
        self.statusBar().addWidget(self.status_label)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)
        self.tab0_tableWidget.setColumnHidden(0, False)
        self.tab1_tableWidget.setColumnHidden(0, False)
        
    def ebsPostInit(self, initargs, tabargs):
        QtCore.QObject.connect(self.button_start, QtCore.SIGNAL("clicked()"), self.startPage)
        QtCore.QObject.connect(self.button_forward, QtCore.SIGNAL("clicked()"), self.addPage)
        QtCore.QObject.connect(self.button_back, QtCore.SIGNAL("clicked()"), self.delPage)
        
        actList=[("configureAction", "Конфигурировать", "images/configure.png", self.configure)]
        objDict = {self.toolBar:["configureAction"]}
        self.actionCreator(actList, objDict)
        
        self.tableWidget = self.tab0_tableWidget
        self.tableWidget_summary = self.tab1_tableWidget
        
    def retranslateUI(self, initargs, tabargs):
        super(NetFlowReportEbs, self).retranslateUI(initargs, tabargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
    
    def addrow(self, value, x, y, color=None):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        if color:
            headerItem.setBackgroundColor(QtGui.QColor(color))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/user.png"))
        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
 
    def startPage(self):
        #self.current_page=0
        self.refresh('home')
         
    def addPage(self):
        #self.current_page+=1
        self.refresh('next')
        
    def delPage(self):
        #if self.current_page-1>=0:
        #    self.current_page-=1
        self.refresh('prev')
        
    def getProtocol(self, value):
        if str(value) in self.protocols_reverse:
            return self.protocols_reverse['%s' % value]
        return value
        
    def configure(self):
        if self.child.exec_()!=1:
            return
        if self.tabWidget.currentIndex()==0:
            #self.current_page=0
            self.used = True
            self.refresh('start')
        elif self.tabWidget.currentIndex()==1:
            self.refresh_summary()
        
    def addRowSummary(self, value, x, y, color=None, user=False):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        if color:
            headerItem.setBackgroundColor(QtGui.QColor(color))

        if user==True:
            headerItem.setIcon(QtGui.QIcon("images/user.png"))

        headerItem.setText(unicode(value))
        self.tableWidget_summary.setItem(x,y,headerItem)

    def summ(self, x,y):
        if x==None:
            x=0
        if y==None:
            y=0
        return x+y
                
    def refresh_summary(self):            
        sql_acc = ""
        if len(self.child.users)>0:
            sql_acc= """ AND bgs.account_id IN (%s) """ % ','.join(map(str, self.child.users))
            
        sql="""SELECT class.name AS name, class.color AS color, 
                      SUM(bgs.classbytes[bgs.classes#class.id][1]) AS input_summ, SUM(bgs.classbytes[bgs.classes#class.id][2]) AS output_summ 
                      FROM billservice_globalstat AS bgs
                      JOIN nas_trafficclass as class ON (bgs.classes#class.id !=0)
                      WHERE bgs.datetime BETWEEN '%s' AND '%s' %s
            """ % (self.child.start_date, self.child.end_date, sql_acc)

        if len(self.child.classes)>0:
            sql+=""" AND class.id IN (%s) """  % ','.join(map(str, self.child.classes))            
                    
        sql+="GROUP BY class.name,class.color;"
        
        #print sql
        data = self.connection.sql(sql)
        self.connection.commit()
        i=0
        self.tableWidget_summary.clearContents()
        classes_count = len(data)+1
        self.tableWidget_summary.setRowCount(classes_count)
        self.tableWidget_summary.setSpan(i,0,0,5)
        self.addRowSummary(u"Общая статистика по классам", i, 0, color='#ffffff')
        i+=1
        for flow in data:
            self.addRowSummary(flow.name, i, 0, color=flow.color)
            self.addRowSummary(humanable_bytes(flow.input_summ), i, 1, color=flow.color)
            self.addRowSummary(humanable_bytes(flow.output_summ), i, 2, color=flow.color)
            self.addRowSummary(humanable_bytes(self.summ(flow.output_summ,flow.input_summ)), i, 3, color=flow.color)
            self.addRowSummary(u'', i, 4, color=flow.color)
            i+=1


        if sql_acc:
            if len(self.child.users)>0:
                sql_acc= """ (%s) """ % ','.join(map(str, self.child.users))

            sql="""SELECT account.username AS username , class.name AS name, class.color AS color, 
                          SUM(bgs.classbytes[bgs.classes#class.id][1]) AS input_summ, SUM(bgs.classbytes[bgs.classes#class.id][2]) AS output_summ 
                          FROM billservice_globalstat AS bgs 
                          JOIN billservice_account as account ON bgs.account_id = account.id
                          JOIN nas_trafficclass as class ON (bgs.classes#class.id !=0) 
                          WHERE (bgs.datetime BETWEEN '%s' AND '%s') AND (account.id IN %s)             
               """ % (self.child.start_date, self.child.end_date, sql_acc)
    
            if len(self.child.classes)>0:
                sql+=""" AND class.id in (%s) """  % ','.join(map(str, self.child.classes))              
                        
            sql+="GROUP BY account.id, account.username, class.name, class.color ORDER BY account.id,class.name;"
            
            
            data = self.connection.sql(sql)
            self.connection.commit()
            #i=0
            self.tableWidget_summary.setRowCount(classes_count+len(data)+len(self.child.users)+1)
            oldusername = ''
            self.tableWidget_summary.setSpan(i,0,0,5)
            self.addRowSummary(u"Подробно", i, 0, color='#ffffff')
            i+=1
            for flow in data:
                if flow.username!=oldusername:
                    self.tableWidget_summary.setRowHeight(i,22)
                    self.tableWidget_summary.setSpan(i,0,0,5)
                    self.addRowSummary(flow.username, i, 0, color='#ffffff', user=True)
                    i+=1
                self.addRowSummary(flow.name, i, 0, color=flow.color)
                self.addRowSummary(humanable_bytes(flow.input_summ), i, 1, color=flow.color)
                self.addRowSummary(humanable_bytes(flow.output_summ), i, 2, color=flow.color)
                self.addRowSummary(humanable_bytes(self.summ(flow.output_summ,flow.input_summ)), i, 3, color=flow.color)
                self.addRowSummary(u'', i, 4, color=flow.color)
                oldusername=flow.username
                i+=1 
        
        HeaderUtil.getHeader(self.setname+"_tab_1", self.tableWidget_summary)

                    
    def refresh(self, rep_command):        
        self.status_label.setText(u"Подождите, идёт обработка.")
        self.repaint()
        i = 0
        c = 0
        users = {}
        for x in xrange(0, self.child.selected_users_listWidget.count()):
                users[self.child.selected_users_listWidget.item(x).id] = unicode(self.child.selected_users_listWidget.item(x).text())
        if rep_command == 'start':
            
            
            icount = 0
            users_str = ''
            if len(self.child.users) > 0:
                users_str = ','.join(map(str, self.child.users))                
            if not users_str:
                flows = self.connection.text_report(['start', self.child.start_date, self.child.end_date, ['none']])
            else:
                flows = self.connection.text_report(['start', self.child.start_date, self.child.end_date, ['accounts', users_str]])
        else:
            flows = self.connection.text_report([rep_command]) 
        
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(flows))
        
        #['#', u'Аккаунт', u'Источник', u'Получатель', u'Передано',u'Дата']
        for flowstr in flows:                   
            flow = flowstr.split(' ')
            self.addrow(c, i, 0)
            self.addrow(users.get(int(flow[0]), ""), i, 1)   #acc_id      
            self.addrow("%s:%s" % (flow[1], flow[2]), i, 2) #src ip, port
            self.addrow("%s:%s" % (flow[3], flow[4]), i, 3) #dst
            self.addrow(humanable_bytes(int(flow[5])), i, 4) #octets
            self.addrow(datetime.datetime.fromtimestamp(float(flow[6])).strftime(self.strftimeFormat), i, 5)  #date        
            i+=1
            c+=1
        
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname+"_tab_0", self.tableWidget)
        self.status_label.setText(u"Готово")
  
    def closeEvent(self, event):
        if self.used:
            self.connection.text_report(['finish'])
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        settings.setValue("window-geometry-%s" % unicode(self.objectName()), QtCore.QVariant(self.saveGeometry()))
        event.accept()    
        

class NetFlowReport(QtGui.QMainWindow):
    def __init__(self, connection):
        """
        Допускается открыт
        """
        super(NetFlowReport, self).__init__()
        self.connection = connection
        self.datetimeFormat = "dd" + dateDelim + "MM" + dateDelim + "yyyy hh:mm:ss"
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        self.current_page=0
        self.setname = "netflow_frame_header"
        self.setname_summary = "netflow_frame_summary_header"
        self.protocols_reverse = {
                  '0':'',
                  '37': 'ddp',
                  '98': 'encap',
                  '3': 'ggp',
                  '47': 'gre',
                  '20': 'hmp',
                  '1' : 'ICMP',
                  '38':'idpr-cmtp',
                  '2': 'igmp',
                  '4': 'ipencap',
                  '94': 'ipip',
                  '89': 'ospf',
                  '27': 'rdp',
                  '6' : 'TCP',
                  '17': 'UDP'
                  }
        self.datetimeFormat = "dd" + dateDelim + "MM" + dateDelim + "yyyy hh:mm:ss"
        self.child = ReportPropertiesDialog(connection = self.connection)
        self.resize(QtCore.QSize(QtCore.QRect(0,0,800,587).size()).expandedTo(self.minimumSizeHint()))
        self.label = QtGui.QLabel(u"Навигатор")
        self.button_start = QtGui.QPushButton()
        self.button_start.setText(u"|<<")
        self.button_start.setMaximumHeight(19)
        self.button_start.setMaximumWidth(28)
        #self.button_start.setFlat(True)
        
        self.button_back = QtGui.QPushButton()
        self.button_back.setText(u"<")
        self.button_back.setMaximumHeight(19)
        self.button_back.setMaximumWidth(28)
        #self.button_back.setFlat(True)
        self.button_forward = QtGui.QPushButton()
        self.button_forward.setText(u">")
        self.button_forward.setMaximumHeight(19)
        self.button_forward.setMaximumWidth(28)
        self.status_label= QtGui.QLabel()
        #self.status_label.setMinimumWidth(600)
        
        self.centralwidget = QtGui.QWidget()
        self.centralwidget.setObjectName("centralwidget")

        self.gridlayout = QtGui.QGridLayout(self.centralwidget)
        self.gridlayout.setObjectName("gridlayout")

        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.gridlayout1 = QtGui.QGridLayout(self.tab)
        self.gridlayout1.setObjectName("gridlayout1")
        
        self.tableWidget = QtGui.QTableWidget(self.tab)
        self.tableWidget = tableFormat(self.tableWidget)
        self.gridlayout1.addWidget(self.tableWidget,0,0,1,1)
        self.tabWidget.addTab(self.tab,"")
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.gridlayout2 = QtGui.QGridLayout(self.tab_2)
        self.gridlayout2.setObjectName("gridlayout2")

        self.tableWidget_summary = QtGui.QTableWidget(self.tab_2)
        self.tableWidget_summary = tableFormat(self.tableWidget_summary)
        self.tableWidget_summary.setObjectName("tableWidget_2")
        self.gridlayout2.addWidget(self.tableWidget_summary,0,0,1,1)
        self.tabWidget.addTab(self.tab_2,"")
        
        self.setCentralWidget(self.centralwidget)
        self.gridlayout.addWidget(self.tabWidget,0,0,1,1)
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        
        #self.toolBar.addWidget(self.combobox)
        self.statusBar().addWidget(self.label)
        self.statusBar().addWidget(self.button_start)
        self.statusBar().addWidget(self.button_back)
        self.statusBar().addWidget(self.button_forward)
        self.statusBar().addWidget(self.status_label)
        #self.statusBar().addWidget(self.button_end)

        
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)

        self.configureAction = QtGui.QAction(self)
        self.configureAction.setIcon(QtGui.QIcon("images/configure.png"))
        self.configureAction.setObjectName("configureAction")
        self.toolBar.addAction(self.configureAction)
        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        QtCore.QObject.connect(self.configureAction, QtCore.SIGNAL("triggered()"), self.configure)
        
        QtCore.QObject.connect(self.button_start, QtCore.SIGNAL("clicked()"), self.startPage)
        QtCore.QObject.connect(self.button_forward, QtCore.SIGNAL("clicked()"), self.addPage)
        QtCore.QObject.connect(self.button_back, QtCore.SIGNAL("clicked()"), self.delPage)
        self.retranslateUi()
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Сетевая статистика", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("MainWindow", "Детальная статистика", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("MainWindow", "Сводная статистика", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()

        columns = ['#', u'Аккаунт', u'Класс трафика', u'Протокол', u'Источник',  u'Получатель', u'Передано', u'Дата']
        makeHeaders(columns, self.tableWidget)
        self.tableWidget.setColumnHidden(0, False)
        HeaderUtil.nullifySaved(self.setname)
        columns = [u'Класс', u'Принято',u'Передано', u'Сумма','']
        
        makeHeaders(columns, self.tableWidget_summary)
        self.tableWidget_summary.setColumnHidden(0, False)
        HeaderUtil.nullifySaved(self.setname_summary)
        #self.tableWidget_summary.setS
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.configureAction.setText(QtGui.QApplication.translate("MainWindow", "configureAction", None, QtGui.QApplication.UnicodeUTF8))

    def addrow(self, value, x, y, color=None):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        if color:
            headerItem.setBackgroundColor(QtGui.QColor(color))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/account.png"))
        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
 
    def startPage(self):
        self.current_page=0
        self.refresh()
         
    def addPage(self):
        self.current_page+=1
        self.refresh()
        
    def delPage(self):
        if self.current_page-1>=0:
            self.current_page-=1
            self.refresh()
        
    def getProtocol(self, value):
        if str(value) in self.protocols_reverse:
            return self.protocols_reverse['%s' % value]
        return value
        
    def saveHeader(self, *args):
        HeaderUtil.saveHeader(self.setname, self.tableWidget)
    def configure(self):
        if self.child.exec_()!=1:
            return
        if self.tabWidget.currentIndex()==0:
            self.current_page=0
            self.refresh()
        elif self.tabWidget.currentIndex()==1:
            self.refresh_summary()
        
    def addRowSummary(self, value, x, y, color=None, user=False):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        if color:
            headerItem.setBackgroundColor(QtGui.QColor(color))

        if user==True:
            headerItem.setIcon(QtGui.QIcon("images/account.png"))

        headerItem.setText(unicode(value))
        self.tableWidget_summary.setItem(x,y,headerItem)

    def summ(self, x,y):
        if x==None:
            x=0
        if y==None:
            y=0
        return x+y
                
    def refresh_summary(self):

            
        sql_acc=''
        if len(self.child.users)>0:
            sql_acc= """ AND account_id IN (%s) """ % ','.join(map(str, self.child.users))
            
        sql="""
        SELECT class.name, class.color, 
        (SELECT sum(octets) FROM billservice_netflowstream WHERE traffic_class_id=class.id %s and direction='INPUT' and date_start between '%s' and '%s') as input_summ,
        (SELECT sum(octets) FROM billservice_netflowstream WHERE traffic_class_id=class.id %s and direction='OUTPUT' and date_start between '%s' and '%s') as output_summ
        FROM nas_trafficnode as node
        JOIN nas_trafficclass as class ON class.id=node.traffic_class_id
        """ % (sql_acc, self.child.start_date, self.child.end_date, sql_acc, self.child.start_date, self.child.end_date)

        if len(self.child.classes)>0:
            sql+="""WHERE class.id in (%s) """  % ','.join(map(str, self.child.classes))
            
                    
        sql+="GROUP BY class.id, class.name,class.color"
        
        #print sql
        data = self.connection.sql(sql)
        i=0
        self.tableWidget_summary.clearContents()
        classes_count = len(data)+1
        self.tableWidget_summary.setRowCount(classes_count)
        self.tableWidget_summary.setSpan(i,0,0,5)
        self.addRowSummary(u"Общая статистика по классам", i, 0, color='#ffffff')
        i+=1
        for flow in data:
            self.addRowSummary(flow.name, i, 0, color=flow.color)
            self.addRowSummary(humanable_bytes(flow.input_summ), i, 1, color=flow.color)
            self.addRowSummary(humanable_bytes(flow.output_summ), i, 2, color=flow.color)
            self.addRowSummary(humanable_bytes(self.summ(flow.output_summ,flow.input_summ)), i, 3, color=flow.color)
            self.addRowSummary(u'', i, 4, color=flow.color)
            i+=1

  
        if sql_acc!="":
            if len(self.child.users)>0:
                sql_acc= """ (%s) """ % ','.join(map(str, self.child.users))

            sql="""
            SELECT account.username, class.name, class.color, 
            (SELECT sum(octets) FROM billservice_netflowstream WHERE account_id=account.id and traffic_class_id=class.id and direction='INPUT' and date_start between '%s' and '%s') as input_summ,
            (SELECT sum(octets) FROM billservice_netflowstream WHERE account_id=account.id and traffic_class_id=class.id and direction='OUTPUT' and date_start between '%s' and '%s') as output_summ
            FROM nas_trafficnode as node
            JOIN nas_trafficclass as class ON class.id=node.traffic_class_id
            JOIN billservice_account as account ON account.id IN %s
            """ % (self.child.start_date, self.child.end_date, self.child.start_date, self.child.end_date, sql_acc)
    
            if len(self.child.classes)>0:
                sql+="""WHERE class.id in (%s) """  % ','.join(map(str, self.child.classes))
                
                        
            sql+="GROUP BY account.id, account.username,class.id, class.name,class.color ORDER BY account.id,class.name"
            
            #print sql
            data = self.connection.sql(sql)
            #i=0
            self.tableWidget_summary.setRowCount(classes_count+len(data)+len(self.child.users)+1)
            oldusername = ''
            self.tableWidget_summary.setSpan(i,0,0,5)
            self.addRowSummary(u"Подробно", i, 0, color='#ffffff')
            i+=1
            for flow in data:
                if flow.username!=oldusername:
                    self.tableWidget_summary.setRowHeight(i,22)
                    self.tableWidget_summary.setSpan(i,0,0,5)
                    self.addRowSummary(flow.username, i, 0, color='#ffffff', user=True)
                    i+=1
                self.addRowSummary(flow.name, i, 0, color=flow.color)
                self.addRowSummary(humanable_bytes(flow.input_summ), i, 1, color=flow.color)
                self.addRowSummary(humanable_bytes(flow.output_summ), i, 2, color=flow.color)
                self.addRowSummary(humanable_bytes(self.summ(flow.output_summ,flow.input_summ)), i, 3, color=flow.color)
                self.addRowSummary(u'', i, 4, color=flow.color)
                oldusername=flow.username
                i+=1
            

            
                    
    def refresh(self):

        
        self.status_label.setText(u"Подождите, идёт обработка.")

        #self.tableWidget.setSortingEnabled(False)
        if self.child.with_grouping_checkBox.checkState()==0:
            sql="""SELECT netflowstream.id,netflowstream.date_start, netflowstream.direction, netflowstream.protocol, 
            netflowstream.src_addr, netflowstream.dst_addr, netflowstream.src_port, netflowstream.dst_port, netflowstream.octets,  
            account.username as account_username, class.name as class_name, class.color as class_color, ports.name as port_name, 
            ports.description as port_description, ports1.name as port_name1, ports1.description as port_description1
            FROM billservice_netflowstream as netflowstream
            LEFT JOIN billservice_ports as ports ON ports.protocol = netflowstream.protocol and netflowstream.src_port = ports.port
            LEFT JOIN billservice_ports as ports1 ON ports1.protocol = netflowstream.protocol and netflowstream.dst_port = ports1.port
            JOIN billservice_account as account ON account.id = netflowstream.account_id
            JOIN nas_trafficclass as class ON class.id = netflowstream.traffic_class_id
             
            WHERE date_start between '%s' and '%s'""" % (self.child.start_date, self.child.end_date) 
            #print 1
        elif self.child.with_grouping_checkBox.checkState()==2:
            sql="""SELECT netflowstream.direction, netflowstream.protocol, netflowstream.src_addr, netflowstream.dst_addr,  account.username as account_username, class.name as class_name,  class.color as class_color, sum(netflowstream.octets) as octets
            FROM billservice_netflowstream as netflowstream

            JOIN billservice_account as account ON account.id = netflowstream.account_id
            JOIN nas_trafficclass as class ON class.id = netflowstream.traffic_class_id
            
            WHERE date_start between '%s' and '%s'
            
            """ % (self.child.start_date, self.child.end_date)
            #print 2            
        
        if len(self.child.users)>0 or len(self.child.classes)>0:
            sql+=" AND " 
        
        if len(self.child.users)>0:
            sql+= """ netflowstream.account_id IN (%s) """ % ','.join(map(str, self.child.users))
            
        if len(self.child.users)>0 and len(self.child.classes)>0:
            sql+=""" and """
        
        if len(self.child.classes)>0:
            sql+=""" netflowstream.traffic_class_id in (%s)"""  % ','.join(map(str, self.child.classes))
            
        if self.child.with_grouping_checkBox.checkState()==2:
            sql+="""GROUP BY netflowstream.direction, netflowstream.protocol, netflowstream.src_addr, netflowstream.dst_addr,  account.username, class.name, class.color"""
        
        if self.child.with_grouping_checkBox.checkState()==0 and self.child.order_by_desc.checkState()==0:
            sql+="ORDER BY netflowstream.id ASC"
        elif self.child.with_grouping_checkBox.checkState()==0 and self.child.order_by_desc.checkState()==2:
            sql+="ORDER BY netflowstream.id DESC"
            
        if self.current_page==0:
            sql+=" LIMIT 100"
        else:
            
            sql+=" LIMIT 100 OFFSET %d" % (self.current_page*100)
            
        #print sql
        import time
        a=time.clock()
        flows = self.connection.sql(sql)
        self.connection.commit()
        #print "request time=", time.clock()-a
        i=0
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(flows))
        octets_in_summ=0
        octets_out_summ=0

        c=self.current_page*500
        #['id',  u'Аккаунт', u'Дата', u'Класс', u'Направление', u'Протокол', u'IP источника', u'IP получателя', u'Порт источника', u'Порт получателя', u'Передано байт']
        for flow in flows:
            self.addrow(c, i, 0)
            if self.child.with_grouping_checkBox.checkState()==0:

                if flow.direction=='INPUT':
                    octets_in_summ+=int(flow.octets)
                elif flow.direction=='OUTPUT':
                    octets_out_summ+=int(flow.octets)

                
                if flow.direction=="INPUT" or (flow.direction=="INPUT" and flow.port_name1==None):
                
                    if flow.port_name==None and flow.port_name1!=None:
                        flow.port_name=flow.port_name1
                        flow.port_description=flow.port_description1
                    elif flow.port_name==None:
                        flow.port_description=''
    
                        
                    if flow.port_name!='' and flow.port_name is not None:
                        self.addrow("%s (%s)" % (self.getProtocol(flow.protocol), flow.port_name), i, 3)
                    else:
                        self.addrow("%s" % (self.getProtocol(flow.protocol), ), i, 3)
                    self.tableWidget.item(i,3).setToolTip(flow.port_description)
                
                 
                elif flow.direction=="OUTPUT" or (flow.direction=="OUTPUT" and flow.port_name==None):
                
                    if flow.port_name1==None and flow.port_name!=None:
                        flow.port_name1 = flow.port_name
                        flow.port_description1 = flow.port_description
                    elif flow.port_name1==None: 
                        flow.port_name1=""    
                        flow.port_description1 = ""   
                    if flow.port_name1!='' and flow.port_name1 is not None:
                        self.addrow("%s (%s)" % (self.getProtocol(flow.protocol), flow.port_name1), i, 3)
                    else:
                        self.addrow("%s" % (self.getProtocol(flow.protocol), ), i, 3)
                    self.tableWidget.item(i,3).setToolTip(flow.port_description1)       
                else:
                    self.addrow("%s" % (self.getProtocol(flow.protocol)), i, 3)


                self.addrow(flow.date_start.strftime(self.strftimeFormat), i, 7)
                self.addrow("%s:%s" % (flow.src_addr, flow.src_port), i, 4)
    
                self.addrow("%s:%s" % (flow.dst_addr, flow.dst_port), i, 5)
            else:
                self.addrow("%s" % (self.getProtocol(flow.protocol)), i, 3)
                self.addrow(flow.src_addr, i, 4)
                self.addrow(flow.dst_addr, i, 5)
                
            self.addrow(flow.account_username, i, 1)
            
            self.addrow(humanable_bytes(flow.octets), i, 6)
            self.addrow("%s %s" % (flow.class_name, flow.direction), i, 2, color=flow.class_color)
            
            self.tableWidget.setRowHeight(i, 16)
            
            i+=1
            c+=1

        #self.tableWidget.sortByColumn(3)        
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        #self.tableWidget.resizeRowsToContents()
        #self.statusBar().showMessage(u"Всего принято: %s МБ. Отправлено: %s МБ. Транзитного трафика: %s МБ" % (float(octets_in_summ)/(1024*1024), float(octets_out_summ)/(1024*1024), float(octets_transit_summ)/(1024*1024) ))
        #self.status_label.setText(u"Всего принято: %s МБ. Отправлено: %s МБ. Транзитного трафика: %s МБ" % (float(octets_in_summ)/(1024*1024), float(octets_out_summ)/(1024*1024), float(octets_transit_summ)/(1024*1024) ))
        self.status_label.setText(u"Готово")
        #print "Interface generation time=", time.clock()-a
        #self.tableWidget.setSortingEnabled(True)    
        
        


class StatReport(QtGui.QMainWindow):
    def __init__(self, connection, chartinfo):
        super(StatReport, self).__init__()
        self.connection = connection
        self.chartinfo = chartinfo
        self.child = ReportOptionsDialog(self.connection, self.chartinfo[1][0])
        self.resize(QtCore.QSize(QtCore.QRect(0,0,1050,700).size()).expandedTo(self.minimumSizeHint()))
        self.textedit = QtGui.QTextEdit(self)
        
        self.setCentralWidget(self.textedit)
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.toolBar.setIconSize(QtCore.QSize(18,18))

        
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)

        self.configureAction = QtGui.QAction(self)
        self.configureAction.setIcon(QtGui.QIcon("images/configure.png"))
        self.configureAction.setObjectName("configureAction")
        self.toolBar.addAction(self.configureAction)
        
        self.printAction = QtGui.QAction(self)
        self.printAction.setIcon(QtGui.QIcon("images/printer.png"))
        self.printAction.setObjectName("printAction")
        self.toolBar.addAction(self.printAction)
        
        QtCore.QObject.connect(self.configureAction, QtCore.SIGNAL("triggered()"), self.configure)
        QtCore.QObject.connect(self.printAction, QtCore.SIGNAL("triggered()"), self.printDocument)
        
        self.retranslateUi()
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", self.chartinfo[2], None, QtGui.QApplication.UnicodeUTF8))
    
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.configureAction.setText(QtGui.QApplication.translate("MainWindow", "configureAction", None, QtGui.QApplication.UnicodeUTF8))

        
    def configure(self):        
        if self.child.exec_()!=1:
            return
        
        self.refresh()
                
    def refresh(self):
        kwargs = {}
        kwargs['options'] = {}
        if self.child.lgb_antialias_checkBox.checkState() == 0:
            kwargs['options']['antialias'] = False
        else:
            kwargs['options']['antialias'] = True
            
        if self.child.lgb_grid_checkBox.checkState() == 0:
            kwargs['options']['autoticks'] = True
        else:
            kwargs['options']['autoticks'] = False
          
        if self.child.users:
            kwargs['users']   = self.child.users
            
        if self.child.classes:
            kwargs['classes'] = self.child.classes
            
        if self.child.servers:
            kwargs['servers'] = self.child.servers
        if self.child.groups:
            kwargs['groups']   = self.child.groups
        if self.child.ports:
            kwargs['ports']   = self.child.ports
        
        kwargs['type'] = self.chartinfo[1][0]
        chOpts = _chartopts[kwargs['type']]
        kwargs.update(chOpts[2])
        kwargs.update(self.child.opts)
        brep = bpReportEdit()
        editor  = brep.createreport(_xmlpath+"/" +self.chartinfo[0], [(self.child.start_date, self.child.end_date)], [kwargs], connection=self.connection)
        self.textedit = None
        #print editor.physicalDpiX()
        #print editor.logicalDpiX()
        fname = reppath + "/" +self.chartinfo[1][0] + str(time.time()) + ".html"
        f = open(fname, "wb")
        f.write(editor.document().toHtml("utf-8").toUtf8())
        f.close()
        webv = QtWebKit.QWebView()
        #webv.setHtml(sht)
        lfurl = QtCore.QUrl.fromLocalFile(os.path.abspath(fname))
        #print lfurl.toString()
        webv.load(lfurl)

        self.setCentralWidget(webv)
            
    def printDocument(self):
        document = self.centralWidget()
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        printer.setPageSize(QtGui.QPrinter.A4)
        dialog = QtGui.QPrintDialog(printer, self)
        dialog.setWindowTitle(self.tr("Print Document"))
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return
        printer.setFullPage(True)
        document.print_(printer)
        

    

class ReportOptionsDialog(QtGui.QDialog):
    def __init__(self, connection, chartclass):
        super(ReportOptionsDialog, self).__init__()
        self.connection = connection
        self.chartclass = chartclass
        self.users   = []
        self.classes = []
        self.servers = []
        self.groups  = []
        self.ports   = []
        self.opts    = {}
        self.start_date = datetime.datetime.now()
        self.end_date   = datetime.datetime.now()
        self.datetimeFormat = "dd" + dateDelim + "MM" + dateDelim + "yyyy hh:mm:ss"
        self.resize(475, 535)
        self.gridLayout_4 = QtGui.QGridLayout(self)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.mainTab = QtGui.QWidget()
        self.mainTab.setObjectName("mainTab")
        self.gridLayout_3 = QtGui.QGridLayout(self.mainTab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.inter_groupBox = QtGui.QGroupBox(self.mainTab)
        self.inter_groupBox.setMaximumSize(QtCore.QSize(16777215, 100))
        self.inter_groupBox.setObjectName("inter_groupBox")
        self.gridLayout_2 = QtGui.QGridLayout(self.inter_groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.from_label = QtGui.QLabel(self.inter_groupBox)
        self.from_label.setObjectName("from_label")
        self.gridLayout_2.addWidget(self.from_label, 0, 0, 1, 1)        
        self.to_label = QtGui.QLabel(self.inter_groupBox)
        self.to_label.setObjectName("to_label")
        self.gridLayout_2.addWidget(self.to_label, 1, 0, 1, 1)
        self.from_dateTimeEdit = QtGui.QDateTimeEdit(self.inter_groupBox)
        self.from_dateTimeEdit.setMinimumDate(QtCore.QDate(2008, 1, 1))
        self.from_dateTimeEdit.setCalendarPopup(True)
        self.from_dateTimeEdit.setDisplayFormat(self.datetimeFormat)
        self.from_dateTimeEdit.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        dt_now = datetime.datetime.now()
        self.from_dateTimeEdit.setDate(QtCore.QDate(dt_now.year, dt_now.month, dt_now.day))
        self.from_dateTimeEdit.setObjectName("from_dateTimeEdit")
        self.gridLayout_2.addWidget(self.from_dateTimeEdit, 0, 1, 1, 1)
        self.to_dateTimeEdit = QtGui.QDateTimeEdit(self.inter_groupBox)
        self.to_dateTimeEdit.setMinimumDate(QtCore.QDate(2008, 1, 1))
        self.to_dateTimeEdit.setCalendarPopup(True)
        self.to_dateTimeEdit.setDisplayFormat(self.datetimeFormat)
        self.to_dateTimeEdit.setObjectName("to_dateTimeEdit")
        self.to_dateTimeEdit.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        self.gridLayout_2.addWidget(self.to_dateTimeEdit, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.inter_groupBox, 0, 0, 1, 2)

        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            self.from_dateTimeEdit.setDateTime(settings.value("chrep_date_start", QtCore.QVariant(QtCore.QDateTime(2000,1,1,0,0))).toDateTime())
            self.to_dateTimeEdit.setDateTime(settings.value("chrep_date_end", QtCore.QVariant(QtCore.QDateTime(2000,1,1,0,0))).toDateTime())
        except Exception, ex:
            print "Chart reports settings error: ", ex
        
        self.data_groupBox = QtGui.QGroupBox(self.mainTab)
        self.data_groupBox.setMaximumSize(QtCore.QSize(1000, 120))
        self.data_groupBox.setObjectName("data_groupBox")
        self.gridLayout_6 = QtGui.QGridLayout(self.data_groupBox)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.dgb_traffic_radioButton = QtGui.QRadioButton(self.data_groupBox)
        self.dgb_traffic_radioButton.setObjectName("dgb_traffic_radioButton")
        self.dgb_traffic_radioButton.setChecked(True)
        self.gridLayout_6.addWidget(self.dgb_traffic_radioButton, 0, 0, 1, 1)
        self.dgb_speed_radioButton = QtGui.QRadioButton(self.data_groupBox)
        self.dgb_speed_radioButton.setObjectName("dgb_speed_radioButton")
        self.gridLayout_6.addWidget(self.dgb_speed_radioButton, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.data_groupBox, 1, 0, 1, 1)
        self.layout_groupBox = QtGui.QGroupBox(self.mainTab)
        self.layout_groupBox.setMaximumSize(QtCore.QSize(1000, 120))
        self.layout_groupBox.setObjectName("layout_groupBox")
        self.gridLayout_5 = QtGui.QGridLayout(self.layout_groupBox)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.lgb_grid_checkBox = QtGui.QCheckBox(self.layout_groupBox)
        self.lgb_grid_checkBox.setObjectName("lgb_grid_checkBox")
        self.gridLayout_5.addWidget(self.lgb_grid_checkBox, 0, 0, 1, 1)
        self.lgb_antialias_checkBox = QtGui.QCheckBox(self.layout_groupBox)
        self.lgb_antialias_checkBox.setObjectName("lgb_antialias_checkBox")
        self.gridLayout_5.addWidget(self.lgb_antialias_checkBox, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.layout_groupBox, 1, 1, 1, 1)
        self.groupby_groupBox = QtGui.QGroupBox(self.mainTab)
        self.groupby_groupBox.setMaximumSize(QtCore.QSize(1000, 200))
        self.groupby_groupBox.setObjectName("groupby_groupBox")
        self.gridLayout_8 = QtGui.QGridLayout(self.groupby_groupBox)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.ggb_accounts_checkBox = QtGui.QCheckBox(self.groupby_groupBox)
        self.ggb_accounts_checkBox.setObjectName("ggb_accounts_checkBox")
        self.gridLayout_8.addWidget(self.ggb_accounts_checkBox, 0, 0, 1, 1)
        self.ggb_groups_checkBox = QtGui.QCheckBox(self.groupby_groupBox)
        self.ggb_groups_checkBox.setObjectName("ggb_groups_checkBox")
        self.gridLayout_8.addWidget(self.ggb_groups_checkBox, 1, 0, 1, 1)
        self.ggb_nas_checkBox = QtGui.QCheckBox(self.groupby_groupBox)
        self.ggb_nas_checkBox.setObjectName("ggb_nas_checkBox")
        self.gridLayout_8.addWidget(self.ggb_nas_checkBox, 2, 0, 1, 1)
        self.ggb_classes_checkBox = QtGui.QCheckBox(self.groupby_groupBox)
        self.ggb_classes_checkBox.setObjectName("ggb_classes_checkBox")
        self.gridLayout_8.addWidget(self.ggb_classes_checkBox, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.groupby_groupBox, 2, 0, 1, 1)
        self.traffic_groupBox = QtGui.QGroupBox(self.mainTab)
        self.traffic_groupBox.setMaximumSize(QtCore.QSize(16777215, 200))
        self.traffic_groupBox.setObjectName("traffic_groupBox")
        self.gridLayout_7 = QtGui.QGridLayout(self.traffic_groupBox)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.gbt_input_radioButton = QtGui.QRadioButton(self.traffic_groupBox)
        self.gbt_input_radioButton.setObjectName("gbt_input_radioButton")
        self.gridLayout_7.addWidget(self.gbt_input_radioButton, 0, 0, 1, 1)
        self.tgb_output_radioButton = QtGui.QRadioButton(self.traffic_groupBox)
        self.tgb_output_radioButton.setObjectName("tgb_output_radioButton")
        self.gridLayout_7.addWidget(self.tgb_output_radioButton, 1, 0, 1, 1)
        self.tgb_sum_radioButton = QtGui.QRadioButton(self.traffic_groupBox)
        self.tgb_sum_radioButton.setObjectName("tgb_sum_radioButton")
        self.tgb_sum_radioButton.setChecked(True)
        self.gridLayout_7.addWidget(self.tgb_sum_radioButton, 2, 0, 1, 1)
        self.tgb_max_radioButton = QtGui.QRadioButton(self.traffic_groupBox)
        self.tgb_max_radioButton.setObjectName("tgb_max_radioButton")
        self.gridLayout_7.addWidget(self.tgb_max_radioButton, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.traffic_groupBox, 2, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 1, 0, 1, 1)
        self.tmp_groupBox_2 = QtGui.QGroupBox(self.mainTab)
        self.tmp_groupBox_2.setVisible(False)
        self.tmp_groupBox_2.setMaximumSize(QtCore.QSize(16777215, 40))
        self.tmp_groupBox_2.setObjectName("tmp_groupBox_2")
        self.gridLayout_3.addWidget(self.tmp_groupBox_2, 3, 0, 1, 1)
        self.tmp_groupBox_3 = QtGui.QGroupBox(self.mainTab)
        self.tmp_groupBox_3.setVisible(False)
        self.tmp_groupBox_3.setMaximumSize(QtCore.QSize(16777215, 20))
        self.tmp_groupBox_3.setObjectName("tmp_groupBox_3")
        self.gridLayout_3.addWidget(self.tmp_groupBox_3, 0, 0, 1, 1)

        self.tabWidget.addTab(self.mainTab,"")

        self.usersTab = QtGui.QWidget()
        self.usersTab.setObjectName("usersTab")

        self.all_users_listWidget = QtGui.QListWidget(self.usersTab)
        self.all_users_listWidget.setGeometry(QtCore.QRect(10,30,181,401))
        self.all_users_listWidget.setObjectName("all_users_listWidget")
        self.all_users_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.all_users_listWidget.setSelectionRectVisible(True)

        self.selected_users_listWidget = QtGui.QListWidget(self.usersTab)
        self.selected_users_listWidget.setGeometry(QtCore.QRect(240,30,191,401))
        self.selected_users_listWidget.setObjectName("selected_users_listWidget")
        self.selected_users_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.selected_users_listWidget.setSelectionRectVisible(True)

        self.add_user_toolButton = QtGui.QToolButton(self.usersTab)
        self.add_user_toolButton.setGeometry(QtCore.QRect(200,160,27,23))
        self.add_user_toolButton.setObjectName("add_user_toolButton")

        self.del_user_toolButton = QtGui.QToolButton(self.usersTab)
        self.del_user_toolButton.setGeometry(QtCore.QRect(200,200,27,23))
        self.del_user_toolButton.setObjectName("del_user_toolButton")

        self.all_users_label = QtGui.QLabel(self.usersTab)
        self.all_users_label.setGeometry(QtCore.QRect(10,10,171,18))
        self.all_users_label.setObjectName("all_users_label")

        self.selected_users_label = QtGui.QLabel(self.usersTab)
        self.selected_users_label.setGeometry(QtCore.QRect(240,10,191,18))
        self.selected_users_label.setObjectName("selected_users_label")
        self.tabWidget.addTab(self.usersTab,"")

        self.serversTab = QtGui.QWidget()
        self.serversTab.setObjectName("serversTab")

        self.selected_servers_listWidget = QtGui.QListWidget(self.serversTab)
        self.selected_servers_listWidget.setGeometry(QtCore.QRect(240,30,191,401))
        self.selected_servers_listWidget.setObjectName("selected_servers_listWidget")
        self.selected_servers_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.selected_servers_listWidget.setSelectionRectVisible(True)

        self.all_servers_listWidget = QtGui.QListWidget(self.serversTab)
        self.all_servers_listWidget.setGeometry(QtCore.QRect(10,30,181,401))
        self.all_servers_listWidget.setObjectName("all_servers_listWidget")
        self.all_servers_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.all_servers_listWidget.setSelectionRectVisible(True)

        self.del_server_toolButton = QtGui.QToolButton(self.serversTab)
        self.del_server_toolButton.setGeometry(QtCore.QRect(200,200,27,23))
        self.del_server_toolButton.setObjectName("del_server_toolButton")

        self.add_server_toolButton = QtGui.QToolButton(self.serversTab)
        self.add_server_toolButton.setGeometry(QtCore.QRect(200,160,27,23))
        self.add_server_toolButton.setObjectName("add_server_toolButton")

        self.all_servers_label = QtGui.QLabel(self.serversTab)
        self.all_servers_label.setGeometry(QtCore.QRect(10,10,151,18))
        self.all_servers_label.setObjectName("all_servers_label")

        self.selected_servers_label = QtGui.QLabel(self.serversTab)
        self.selected_servers_label.setGeometry(QtCore.QRect(240,10,151,18))
        self.selected_servers_label.setObjectName("selected_servers_label")
        self.tabWidget.addTab(self.serversTab,"")

        self.classesTab = QtGui.QWidget()
        self.classesTab.setObjectName("classesTab")

        self.all_classes_label = QtGui.QLabel(self.classesTab)
        self.all_classes_label.setGeometry(QtCore.QRect(10,10,151,18))
        self.all_classes_label.setObjectName("all_classes_label")

        self.all_classes_listWidget = QtGui.QListWidget(self.classesTab)
        self.all_classes_listWidget.setGeometry(QtCore.QRect(10,30,181,401))
        self.all_classes_listWidget.setObjectName("all_classes_listWidget")
        self.all_classes_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.all_classes_listWidget.setSelectionRectVisible(True)

        self.del_class_toolButton = QtGui.QToolButton(self.classesTab)
        self.del_class_toolButton.setGeometry(QtCore.QRect(200,200,27,23))
        self.del_class_toolButton.setObjectName("del_class_toolButton")

        self.add_class_toolButton = QtGui.QToolButton(self.classesTab)
        self.add_class_toolButton.setGeometry(QtCore.QRect(200,160,27,23))
        self.add_class_toolButton.setObjectName("add_class_toolButton")

        self.selected_classes_label = QtGui.QLabel(self.classesTab)
        self.selected_classes_label.setGeometry(QtCore.QRect(240,10,191,18))
        self.selected_classes_label.setObjectName("selected_classes_label")

        self.selected_classes_listWidget = QtGui.QListWidget(self.classesTab)
        self.selected_classes_listWidget.setGeometry(QtCore.QRect(240,30,191,401))
        self.selected_classes_listWidget.setObjectName("selected_classes_listWidget")
        self.selected_classes_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.selected_classes_listWidget.setSelectionRectVisible(True)
        self.tabWidget.addTab(self.classesTab,"")
        
        
        self.groupsTab = QtGui.QWidget()
        self.groupsTab.setObjectName("groupsTab")

        self.all_groups_label = QtGui.QLabel(self.groupsTab)
        self.all_groups_label.setGeometry(QtCore.QRect(10,10,151,18))
        self.all_groups_label.setObjectName("all_groups_label")

        self.all_groups_listWidget = QtGui.QListWidget(self.groupsTab)
        self.all_groups_listWidget.setGeometry(QtCore.QRect(10,30,181,401))
        self.all_groups_listWidget.setObjectName("all_groups_listWidget")
        self.all_groups_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.all_groups_listWidget.setSelectionRectVisible(True)

        self.del_group_toolButton = QtGui.QToolButton(self.groupsTab)
        self.del_group_toolButton.setGeometry(QtCore.QRect(200,200,27,23))
        self.del_group_toolButton.setObjectName("del_group_toolButton")

        self.add_group_toolButton = QtGui.QToolButton(self.groupsTab)
        self.add_group_toolButton.setGeometry(QtCore.QRect(200,160,27,23))
        self.add_group_toolButton.setObjectName("add_group_toolButton")

        self.selected_groups_label = QtGui.QLabel(self.groupsTab)
        self.selected_groups_label.setGeometry(QtCore.QRect(240,10,191,18))
        self.selected_groups_label.setObjectName("selected_groups_label")

        self.selected_groups_listWidget = QtGui.QListWidget(self.groupsTab)
        self.selected_groups_listWidget.setGeometry(QtCore.QRect(240,30,191,401))
        self.selected_groups_listWidget.setObjectName("selected_groups_listWidget")
        self.selected_groups_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.selected_groups_listWidget.setSelectionRectVisible(True)
        self.tabWidget.addTab(self.groupsTab,"")

        self.portsTab = QtGui.QWidget()
        self.portsTab.setObjectName("portsTab")

        self.ports_groupBox = QtGui.QGroupBox(self.portsTab)
        self.ports_groupBox.setGeometry(QtCore.QRect(10,10,421,361))
        self.ports_groupBox.setObjectName("ports_groupBox")

        self.ports_listWidget = QtGui.QListWidget(self.ports_groupBox)
        self.ports_listWidget.setGeometry(QtCore.QRect(10,20,251,331))
        self.ports_listWidget.setObjectName("ports_listWidget")

        self.ports_description_label = QtGui.QLabel(self.ports_groupBox)
        self.ports_description_label.setGeometry(QtCore.QRect(270,20,141,331))
        self.ports_description_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.ports_description_label.setWordWrap(True)
        self.ports_description_label.setObjectName("ports_description_label")

        self.extra_ports_lineEdit = QtGui.QLineEdit(self.portsTab)
        self.extra_ports_lineEdit.setGeometry(QtCore.QRect(10,400,391,23))
        self.extra_ports_lineEdit.setObjectName("extra_ports_lineEdit")

        self.extra_ports_label = QtGui.QLabel(self.portsTab)
        self.extra_ports_label.setGeometry(QtCore.QRect(10,380,287,18))
        self.extra_ports_label.setObjectName("extra_ports_label")
        self.tabWidget.addTab(self.portsTab,"")
        self.to_label.setBuddy(self.to_dateTimeEdit)
        self.from_label.setBuddy(self.from_dateTimeEdit)
        
        self.gridLayout_4.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.gridLayout_4.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        
        QtCore.QObject.connect(self.add_user_toolButton, QtCore.SIGNAL("clicked()"),self.addUser)
        QtCore.QObject.connect(self.del_user_toolButton, QtCore.SIGNAL("clicked()"),self.delUser)

        QtCore.QObject.connect(self.all_users_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"),self.addUser)
        QtCore.QObject.connect(self.selected_users_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"),self.delUser)        
        

        QtCore.QObject.connect(self.add_class_toolButton, QtCore.SIGNAL("clicked()"), self.addClass)
        QtCore.QObject.connect(self.del_class_toolButton, QtCore.SIGNAL("clicked()"), self.delClass)
        
        QtCore.QObject.connect(self.all_classes_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.addClass)
        QtCore.QObject.connect(self.selected_classes_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.delClass)
        
        QtCore.QObject.connect(self.add_group_toolButton, QtCore.SIGNAL("clicked()"), self.addGroup)
        QtCore.QObject.connect(self.del_group_toolButton, QtCore.SIGNAL("clicked()"), self.delGroup)
        
        QtCore.QObject.connect(self.all_groups_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.addGroup)
        QtCore.QObject.connect(self.selected_groups_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.delGroup)
        
        QtCore.QObject.connect(self.add_server_toolButton, QtCore.SIGNAL("clicked()"), self.addServer)
        QtCore.QObject.connect(self.del_server_toolButton, QtCore.SIGNAL("clicked()"), self.delServer)
        
        QtCore.QObject.connect(self.all_servers_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.addServer)
        QtCore.QObject.connect(self.selected_servers_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.delServer)
        
        self.chkButtons = [self.ggb_accounts_checkBox, self.ggb_groups_checkBox, self.ggb_nas_checkBox, self.ggb_classes_checkBox]
        self.chkLambdas = [lambda bl: self.chbToggled(bl, 0), lambda bl: self.chbToggled(bl,1), lambda bl: self.chbToggled(bl,2), lambda bl: self.chbToggled(bl, 3)]
        counter = itertools.count()
        for btn in self.chkButtons:
            QtCore.QObject.connect(btn, QtCore.SIGNAL("clicked(bool)"), self.chkLambdas[counter.next()])
        if 1:
            self.setTabOrder(self.tabWidget, self.from_dateTimeEdit)
            self.setTabOrder(self.from_dateTimeEdit, self.to_dateTimeEdit)
            self.setTabOrder(self.to_dateTimeEdit, self.dgb_traffic_radioButton)
            self.setTabOrder(self.dgb_traffic_radioButton, self.dgb_speed_radioButton)
            self.setTabOrder(self.dgb_speed_radioButton, self.lgb_grid_checkBox)
            self.setTabOrder(self.lgb_grid_checkBox, self.lgb_antialias_checkBox)
            self.setTabOrder(self.lgb_antialias_checkBox, self.ggb_accounts_checkBox)
            self.setTabOrder(self.ggb_accounts_checkBox, self.ggb_groups_checkBox)
            self.setTabOrder(self.ggb_groups_checkBox, self.ggb_nas_checkBox)
            self.setTabOrder(self.ggb_nas_checkBox, self.ggb_classes_checkBox)
            self.setTabOrder(self.ggb_classes_checkBox, self.gbt_input_radioButton)
            self.setTabOrder(self.gbt_input_radioButton, self.tgb_output_radioButton)
            self.setTabOrder(self.tgb_output_radioButton, self.tgb_sum_radioButton)
            self.setTabOrder(self.tgb_sum_radioButton, self.tgb_max_radioButton)
            self.setTabOrder(self.tgb_max_radioButton, self.add_user_toolButton)
            self.setTabOrder(self.all_users_listWidget,self.add_user_toolButton)
            self.setTabOrder(self.add_user_toolButton,self.del_user_toolButton)
            self.setTabOrder(self.del_user_toolButton,self.selected_users_listWidget)
            self.setTabOrder(self.selected_users_listWidget,self.all_servers_listWidget)
            self.setTabOrder(self.all_servers_listWidget,self.add_server_toolButton)
            self.setTabOrder(self.add_server_toolButton,self.del_server_toolButton)
            self.setTabOrder(self.del_server_toolButton,self.selected_servers_listWidget)
            self.setTabOrder(self.selected_servers_listWidget,self.all_classes_listWidget)
            self.setTabOrder(self.all_classes_listWidget,self.add_class_toolButton)
            self.setTabOrder(self.add_class_toolButton,self.del_class_toolButton)
            self.setTabOrder(self.del_class_toolButton,self.selected_classes_listWidget)
            self.setTabOrder(self.selected_classes_listWidget,self.all_groups_listWidget)
            self.setTabOrder(self.all_groups_listWidget,self.add_group_toolButton)
            self.setTabOrder(self.add_group_toolButton,self.del_group_toolButton)
            self.setTabOrder(self.del_group_toolButton,self.selected_groups_listWidget)
            self.setTabOrder(self.selected_groups_listWidget,self.ports_listWidget)
            self.setTabOrder(self.ports_listWidget,self.extra_ports_lineEdit)
            self.setTabOrder(self.extra_ports_lineEdit,self.buttonBox)
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройки отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.data_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Данные", None, QtGui.QApplication.UnicodeUTF8))
        self.dgb_traffic_radioButton.setText(QtGui.QApplication.translate("Dialog", "Трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.dgb_speed_radioButton.setText(QtGui.QApplication.translate("Dialog", "Скорость", None, QtGui.QApplication.UnicodeUTF8))
        self.layout_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Внешний вид", None, QtGui.QApplication.UnicodeUTF8))
        self.lgb_grid_checkBox.setText(QtGui.QApplication.translate("Dialog", "Сетка", None, QtGui.QApplication.UnicodeUTF8))
        self.lgb_antialias_checkBox.setText(QtGui.QApplication.translate("Dialog", "Сглаживание", None, QtGui.QApplication.UnicodeUTF8))
        self.groupby_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Группировать по...", None, QtGui.QApplication.UnicodeUTF8))
        self.ggb_accounts_checkBox.setText(QtGui.QApplication.translate("Dialog", "Клиенты", None, QtGui.QApplication.UnicodeUTF8))
        self.ggb_groups_checkBox.setText(QtGui.QApplication.translate("Dialog", "Группы", None, QtGui.QApplication.UnicodeUTF8))
        self.ggb_nas_checkBox.setText(QtGui.QApplication.translate("Dialog", "NAS", None, QtGui.QApplication.UnicodeUTF8))
        self.ggb_classes_checkBox.setText(QtGui.QApplication.translate("Dialog", "Классы", None, QtGui.QApplication.UnicodeUTF8))
        self.traffic_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.gbt_input_radioButton.setText(QtGui.QApplication.translate("Dialog", "Только входящий", None, QtGui.QApplication.UnicodeUTF8))
        self.tgb_output_radioButton.setText(QtGui.QApplication.translate("Dialog", "Только исходящий", None, QtGui.QApplication.UnicodeUTF8))
        self.tgb_sum_radioButton.setText(QtGui.QApplication.translate("Dialog", "Сумма", None, QtGui.QApplication.UnicodeUTF8))
        self.tgb_max_radioButton.setText(QtGui.QApplication.translate("Dialog", "Наибольший", None, QtGui.QApplication.UnicodeUTF8))
        self.inter_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Интервал", None, QtGui.QApplication.UnicodeUTF8))
        self.from_label.setText(QtGui.QApplication.translate("Dialog", "Начало:", None, QtGui.QApplication.UnicodeUTF8))
        self.from_dateTimeEdit.setDisplayFormat(QtGui.QApplication.translate("Dialog", "yyyy-MM-dd H:mm:ss", None, QtGui.QApplication.UnicodeUTF8))
        self.to_dateTimeEdit.setDisplayFormat(QtGui.QApplication.translate("Dialog", "yyyy-MM-dd H:mm:ss", None, QtGui.QApplication.UnicodeUTF8))
        self.to_label.setText(QtGui.QApplication.translate("Dialog", "Конец:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.mainTab), QtGui.QApplication.translate("Dialog", "Общее", None, QtGui.QApplication.UnicodeUTF8))
        self.add_user_toolButton.setText(QtGui.QApplication.translate("Dialog", ">", None, QtGui.QApplication.UnicodeUTF8))
        self.del_user_toolButton.setText(QtGui.QApplication.translate("Dialog", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.all_users_label.setText(QtGui.QApplication.translate("Dialog", "Доступные пользователи", None, QtGui.QApplication.UnicodeUTF8))
        self.selected_users_label.setText(QtGui.QApplication.translate("Dialog", "Выбранные пользователи", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.usersTab), QtGui.QApplication.translate("Dialog", "Пользователи", None, QtGui.QApplication.UnicodeUTF8))
        self.del_server_toolButton.setText(QtGui.QApplication.translate("Dialog", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.add_server_toolButton.setText(QtGui.QApplication.translate("Dialog", ">", None, QtGui.QApplication.UnicodeUTF8))
        self.all_servers_label.setText(QtGui.QApplication.translate("Dialog", "Доступные серверы", None, QtGui.QApplication.UnicodeUTF8))
        self.selected_servers_label.setText(QtGui.QApplication.translate("Dialog", "Выбранные серверы", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.serversTab), QtGui.QApplication.translate("Dialog", "Серверы доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.all_classes_label.setText(QtGui.QApplication.translate("Dialog", "Доступные классы", None, QtGui.QApplication.UnicodeUTF8))
        self.del_class_toolButton.setText(QtGui.QApplication.translate("Dialog", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.add_class_toolButton.setText(QtGui.QApplication.translate("Dialog", ">", None, QtGui.QApplication.UnicodeUTF8))
        self.selected_classes_label.setText(QtGui.QApplication.translate("Dialog", "Выбранные классы", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.classesTab), QtGui.QApplication.translate("Dialog", "Классы", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.groupsTab), QtGui.QApplication.translate("Dialog", "Группы", None, QtGui.QApplication.UnicodeUTF8))
        self.all_groups_label.setText(QtGui.QApplication.translate("Dialog", "Доступные группы", None, QtGui.QApplication.UnicodeUTF8))
        self.del_group_toolButton.setText(QtGui.QApplication.translate("Dialog", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.add_group_toolButton.setText(QtGui.QApplication.translate("Dialog", ">", None, QtGui.QApplication.UnicodeUTF8))
        self.selected_groups_label.setText(QtGui.QApplication.translate("Dialog", "Выбранные группы", None, QtGui.QApplication.UnicodeUTF8))
        self.ports_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Выберите порты", None, QtGui.QApplication.UnicodeUTF8))
        self.ports_description_label.setText(QtGui.QApplication.translate("Dialog", "Отметьте флажками нужные порты", None, QtGui.QApplication.UnicodeUTF8))
        self.extra_ports_label.setText(QtGui.QApplication.translate("Dialog", "Введите дополнительные порты через запятую:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.portsTab), QtGui.QApplication.translate("Dialog", "Порты", None, QtGui.QApplication.UnicodeUTF8))

    def fixtures(self):
        
        chOpts = _chartopts[self.chartclass]
        hidetabs  = chOpts[0]
        hideelems = chOpts[1]
        #self.data_groupBox.setEnabled(False)
        for hidetab in hidetabs:
            htObj = getattr(self, hidetab, None)
            self.tabWidget.removeTab(self.tabWidget.indexOf(htObj))
            
        for hideelem in hideelems:
            heObj = getattr(self, hideelem, None)
            if heObj:
                heObj.setEnabled(False)
            
            
        if "usersTab" not in hidetabs:
            users = self.connection.sql(_querydict['get_usernames'])
            
            for user in users:
                item = QtGui.QListWidgetItem()
                item.setText(user.username)
                item.id = user.id
                self.all_users_listWidget.addItem(item)
            
        if "classesTab" not in hidetabs:
            classes = self.connection.sql(_querydict['get_classes'])
            
            for clas in classes:
                item = QtGui.QListWidgetItem()
                item.setText(clas.name)
                item.id = clas.id
                self.all_classes_listWidget.addItem(item)
          
        if "serversTab" not in hidetabs:        
            servers = self.connection.sql(_querydict['get_nas'])
            
            for serv in servers:
                item = QtGui.QListWidgetItem()
                item.setText(serv.name)
                item.id = serv.id
                self.all_servers_listWidget.addItem(item)
                
        if "groupsTab" not in hidetabs:
            groups = self.connection.sql(_querydict['get_groups'])
            for grp in groups:
                item = QtGui.QListWidgetItem()
                item.setText(grp.name)
                item.id = grp.id
                self.all_groups_listWidget.addItem(item)
                
        if "portsTab" not in hidetabs:  
            for port in _ports:
                item = QtGui.QListWidgetItem()
                item.setText(port[1])
                item.id = port[0]
                item.setCheckState(QtCore.Qt.Unchecked)
                self.ports_listWidget.addItem(item)
        
    def addUser(self):
        selected_items = self.all_users_listWidget.selectedItems()        
        for item in selected_items:
            self.all_users_listWidget.takeItem(self.all_users_listWidget.row(item))
            self.selected_users_listWidget.addItem(item)
            
        self.selected_users_listWidget.sortItems()
        
    def delUser(self):
        selected_items = self.selected_users_listWidget.selectedItems()        
        for item in selected_items:
            self.selected_users_listWidget.takeItem(self.selected_users_listWidget.row(item))
            self.all_users_listWidget.addItem(item)
        self.all_users_listWidget.sortItems()
        
    def addServer(self):
        selected_items = self.all_servers_listWidget.selectedItems()        
        for item in selected_items:
            self.all_servers_listWidget.takeItem(self.all_servers_listWidget.row(item))
            self.selected_servers_listWidget.addItem(item)
            
        self.selected_servers_listWidget.sortItems()
        
    def delServer(self):
        selected_items = self.selected_servers_listWidget.selectedItems()        
        for item in selected_items:
            self.selected_servers_listWidget.takeItem(self.selected_servers_listWidget.row(item))
            self.all_servers_listWidget.addItem(item)
        self.all_servers_listWidget.sortItems()
        
    def addClass(self):       
        selected_items = self.all_classes_listWidget.selectedItems()
        for item in selected_items:
            self.all_classes_listWidget.takeItem(self.all_classes_listWidget.row(item))
            self.selected_classes_listWidget.addItem(item)
        self.selected_classes_listWidget.sortItems()
        
    def delClass(self):
        selected_items = self.selected_classes_listWidget.selectedItems()
        for item in selected_items:
            self.selected_classes_listWidget.takeItem(self.selected_classes_listWidget.row(item))
            self.all_classes_listWidget.addItem(item)
        self.all_classes_listWidget.sortItems()
        
    def addGroup(self):                
        selected_items = self.all_groups_listWidget.selectedItems()        
        for item in selected_items:
            self.all_groups_listWidget.takeItem(self.all_groups_listWidget.row(item))
            self.selected_groups_listWidget.addItem(item)            
        self.selected_groups_listWidget.sortItems()      
        
    def delGroup(self):
        selected_items = self.selected_groups_listWidget.selectedItems()        
        for item in selected_items:
            self.selected_groups_listWidget.takeItem(self.selected_groups_listWidget.row(item))
            self.all_groups_listWidget.addItem(item)
        self.all_groups_listWidget.sortItems()
        
    def chbToggled(self, toggled, btn_id):
        if toggled:
            for counter, btn in izip(count(), self.chkButtons):
                if btn.isChecked() and (btn_id != counter):
                    btn.setChecked(False)
                    
    def accept(self):
        #check the buttons!
        self.users   = []
        self.classes = []
        self.servers = []
        self.ports   = []
        self.groups  = []
        self.opts    = {}
        
        buttons ={'speed' :{self.dgb_traffic_radioButton:False, self.dgb_speed_radioButton:True}, \
                  'by_col':{self.ggb_accounts_checkBox:'users', self.ggb_groups_checkBox:'groups', self.ggb_nas_checkBox:'servers', self.ggb_classes_checkBox:'classes'}, \
                  'gtype' :{self.gbt_input_radioButton:1, self.tgb_output_radioButton:2, self.tgb_sum_radioButton:3, self.tgb_max_radioButton:4}}
        
        for ckey, vdct in buttons.iteritems():
            for bkey, bval in vdct.iteritems():
                if bkey.isChecked():
                    self.opts[ckey] = bval
                    break

        for x in xrange(0, self.selected_users_listWidget.count()):
            self.users.append(self.selected_users_listWidget.item(x).id)
            
        for x in xrange(0, self.selected_classes_listWidget.count()):
            self.classes.append(self.selected_classes_listWidget.item(x).id)
            
        for x in xrange(0, self.selected_servers_listWidget.count()):
            self.servers.append(self.selected_servers_listWidget.item(x).id)
            
        for x in xrange(0, self.selected_groups_listWidget.count()):
            self.groups.append(self.selected_groups_listWidget.item(x).id)
            
        for x in xrange(0, self.ports_listWidget.count()):
            if self.ports_listWidget.item(x).checkState() == 2:
                self.ports.append(self.ports_listWidget.item(x).id)
                
        if self.extra_ports_lineEdit.text():
            try:
                extra_ports_str = self.extra_ports_lineEdit.text().split(',')
            except Exception, ex:
                raise ex
            extra_ports = []
            for eps in extra_ports_str:
                try:
                    extra_ports.append(int(eps))
                except Exception, ex:
                    print ex
            for eport in extra_ports:
                if eport not in self.ports: self.ports.append(eport)
                
            
                    
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue("chrep_date_start", QtCore.QVariant(self.from_dateTimeEdit.dateTime()))
            settings.setValue("chrep_date_end", QtCore.QVariant(self.to_dateTimeEdit.dateTime()))
        except Exception, ex:
            print "Chart reports settings save error: ", ex
            
        self.start_date = self.from_dateTimeEdit.dateTime().toPyDateTime()
        self.end_date   = self.to_dateTimeEdit.dateTime().toPyDateTime()

        QtGui.QDialog.accept(self)
        
        
class LogViewWindow(QtGui.QMainWindow):
    def __init__(self, connection):
        super(LogViewWindow, self).__init__()
        self.connection = connection
        self.setObjectName("LogViewWindow")
        self.resize(800, 600)
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.plainTextEdit = QtGui.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setBackgroundVisible(False)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.gridLayout.addWidget(self.plainTextEdit, 1, 0, 1, 2)
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.comboBox = QtGui.QComboBox(self.groupBox)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout_2.addWidget(self.comboBox, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 2, 1, 1)
        self.spinBox = QtGui.QSpinBox(self.groupBox)
        self.spinBox.setMinimumSize(QtCore.QSize(100, 0))
        self.spinBox.setObjectName("spinBox")
        self.spinBox.setMaximum(10000000)
        self.spinBox.setValue(100)
        self.gridLayout_2.addWidget(self.spinBox, 0, 3, 1, 1)
        self.checkBox = QtGui.QCheckBox(self.groupBox)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout_2.addWidget(self.checkBox, 0, 4, 1, 1)
        self.pushButton = QtGui.QPushButton(self.groupBox)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_2.addWidget(self.pushButton, 0, 6, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 5, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)
        self.setCentralWidget(self.centralwidget)
        
        self.connect(self.pushButton, QtCore.SIGNAL("clicked()"), self.get_tail)
        self.connect(self.checkBox, QtCore.SIGNAL("stateChanged(int)"), self.checkbox_action)
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Просмотр лог-файлов", None, QtGui.QApplication.UnicodeUTF8))
        #self.plainTextEdit.setPlainText(QtGui.QApplication.translate("MainWindow", "цукцукцук", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Параметры", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Имя лог-файла", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Количество последних строк", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("MainWindow", "Всё", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "Получить с сервера", None, QtGui.QApplication.UnicodeUTF8))


    def checkbox_action(self):
        if self.checkBox.isChecked():
            self.spinBox.setDisabled(True)
        else:
            self.spinBox.setDisabled(False)
    def fixtures(self):
        #self.connection
        
        logs = self.connection.list_logfiles()
        #print logs
        i=0
        for log in logs:
           self.comboBox.addItem(unicode(log))
           self.comboBox.setItemData(i, QtCore.QVariant(log))
           i+=1

    def get_tail(self):
        
        log_name = unicode(self.comboBox.itemData(self.comboBox.currentIndex()).toString())

        log_count = int(self.spinBox.value())

        if self.checkBox.isChecked()==True:
            a = self.connection.get_tail_log(log_name, log_count, all_file = True)
        else:
            a = self.connection.get_tail_log(log_name, log_count)
        #print a
        u = a[1]
        self.plainTextEdit.setPlainText(u)
        #self.plainTextEdit.setPla
        
        
class SimpleReportEbs(ebsTableWindow):
    def __init__(self, connection, report_type='radius_authlog', account_id=None, subaccount_id=None, nas_id=None):
        self.report_type=report_type
        self.connection=connection
        self.account_id = account_id
        if self.report_type=='radius_authlog':
            columns=[u'#', u'Аккаунт', u"Субаккаунт", u'Сервер доступа', u'Способ доступа', u'Тип события', u"Событие", u'Дата']
            initargs = {"setname":"%s_frame_header" % self.report_type, "objname":"%sSimpleReportEbs" % self.report_type, "winsize":(0,0,903,483), "wintitle":"История авторизаций пользователя пользователя", "tablecolumns":columns}
            #self.transactions_types = [u"Другие операции", u"Периодические услуги", u"Разовые услуги", u"За трафик", u"За время", u"Подключаемые услуги"]
            #self.transactions_tables = [u"billservice_transaction",u"billservice_periodicalservicehistory",u"billservice_onetimeservicehistory",u"billservice_traffictransaction",u"billservice_timetransaction","billservice_addonservicetransaction"]
        elif  self.report_type=='balance_log':
            columns=[u'#', u'Аккаунт', u"Новый баланс", u'Дата']
            initargs = {"setname":"%s_frame_header" % self.report_type, "objname":"%sSimpleReportEbs" % self.report_type, "winsize":(0,0,903,483), "wintitle":"История изменения баланса", "tablecolumns":columns}
            
        super(SimpleReportEbs, self).__init__(connection, initargs)
        
    def ebsInterInit(self, initargs):
        
        self.comboBox_account = QtGui.QComboBox(self)
        self.comboBox_account.setGeometry(QtCore.QRect(100,12,201,20))
        self.comboBox_account.setObjectName("comboBox_account")    
        
        dt_now = datetime.datetime.now()
        
        self.dateTimeEdit_date_start = QtGui.QDateTimeEdit(self)
        self.dateTimeEdit_date_start.setGeometry(QtCore.QRect(420,9,161,20))
        self.dateTimeEdit_date_start.setCalendarPopup(True)
        self.dateTimeEdit_date_start.setObjectName("dateTimeEdit_date_start")
        self.dateTimeEdit_date_start.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)

        self.dateTimeEdit_date_end = QtGui.QDateTimeEdit(self)
        self.dateTimeEdit_date_end.setGeometry(QtCore.QRect(420,42,161,20))
        self.dateTimeEdit_date_end.setDate(QtCore.QDate(dt_now.year, dt_now.month, dt_now.day))
        self.dateTimeEdit_date_end.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.dateTimeEdit_date_end.setCalendarPopup(True)
        self.dateTimeEdit_date_end.setObjectName("dateTimeEdit_date_end")
        self.dateTimeEdit_date_end.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            self.dateTimeEdit_date_start.setDateTime(settings.value("%strans_date_start" % self.report_type, QtCore.QVariant(QtCore.QDateTime(2010,1,1,0,0))).toDateTime())
            self.dateTimeEdit_date_end.setDateTime(settings.value("%strans_date_end" % self.report_type, QtCore.QVariant(QtCore.QDateTime(2010,1,1,0,0))).toDateTime())
        except Exception, ex:
            print "Transactions settings error: ", ex
        
        self.label_date_start = QtGui.QLabel(self)
        self.label_date_start.setMargin(10)
        self.label_date_start.setObjectName("label_date_start")

        self.label_date_end = QtGui.QLabel(self)
        self.label_date_end.setMargin(10)
        self.label_date_end.setObjectName("label_date_end")

        self.label_account = QtGui.QLabel(self)
        self.label_account.setMargin(10)
        self.label_account.setObjectName("user_label")
        """
        self.label_transactions_type = QtGui.QLabel(self)
        self.label_transactions_type.setMargin(10)

        self.label_cashier = QtGui.QLabel(self)
        self.label_cashier.setMargin(10)
           
        self.comboBox_transactions_type = QtGui.QComboBox(self)
        self.comboBox_cashier = QtGui.QComboBox(self)
        """
        
        self.go_pushButton = QtGui.QPushButton(self)
        self.go_pushButton.setGeometry(QtCore.QRect(590,40,101,25))
        self.go_pushButton.setObjectName("go_pushButton")        
        #self.system_transactions_checkbox = QtGui.QCheckBox(self)
        #self.system_transactions_checkbox.setObjectName("system_transactions_checkbox")

        self.toolBar = QtGui.QToolBar(self)      
        
        self.toolBar.addWidget(self.label_account)
        self.toolBar.addWidget(self.comboBox_account)
        
        #self.toolBar.addWidget(self.label_transactions_type)
        #self.toolBar.addWidget(self.comboBox_transactions_type)
        #self.toolBar.addWidget(self.label_cashier)
        #self.toolBar.addWidget(self.comboBox_cashier)
        self.toolBar.addWidget(self.label_date_start)
        self.toolBar.addWidget(self.dateTimeEdit_date_start)
        self.toolBar.addWidget(self.label_date_end)
        self.toolBar.addWidget(self.dateTimeEdit_date_end)
        #self.toolBar.addWidget(self.system_transactions_checkbox)
        
        self.toolBar.addWidget(self.go_pushButton)
        self.toolBar.addSeparator()        
        
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)
        
        self.columns = {}
       
        #if self.report_type=='radius_authlog':
        #    self.radius_auth_fixtures()   
                
    def ebsPostInit(self, initargs):
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        if self.report_type=='radius_authlog':
            QtCore.QObject.connect(self.go_pushButton,QtCore.SIGNAL("clicked()"),self.radius_auth_fixtures)
        if self.report_type=='balance_log':
            QtCore.QObject.connect(self.go_pushButton,QtCore.SIGNAL("clicked()"),self.balance_log_fixtures)

        #QtCore.QObject.connect(self.comboBox_transactions_type,QtCore.SIGNAL("currentIndexChanged(int)"),self.setTableColumns)
        
        #actList=[("actionDeleteTransaction", "Удалить", "images/del.png", self.delete_transaction),]
        #objDict = {self.tableWidget:["actionDeleteTransaction", ]}
        #self.actionCreator(actList, objDict)
        #self.setTableColumns()
        self.fixtures()
        
    def retranslateUI(self, initargs):
        super(SimpleReportEbs, self).retranslateUI(initargs)
        
        self.label_date_start.setText(QtGui.QApplication.translate("Dialog", "С", None, QtGui.QApplication.UnicodeUTF8))
        self.label_date_end.setText(QtGui.QApplication.translate("Dialog", "По", None, QtGui.QApplication.UnicodeUTF8))
        self.label_account.setText(QtGui.QApplication.translate("Dialog", "Пользователь", None, QtGui.QApplication.UnicodeUTF8))
        self.dateTimeEdit_date_end.setDisplayFormat(QtGui.QApplication.translate("Dialog", self.datetimeFormat, None, QtGui.QApplication.UnicodeUTF8))
        self.dateTimeEdit_date_start.setDisplayFormat(QtGui.QApplication.translate("Dialog", self.datetimeFormat, None, QtGui.QApplication.UnicodeUTF8))
        #self.system_transactions_checkbox.setText(QtGui.QApplication.translate("Dialog", "Включить в отчёт системные проводки", None, QtGui.QApplication.UnicodeUTF8))        
        #self.label_transactions_type.setText(QtGui.QApplication.translate("Dialog", "Тип", None, QtGui.QApplication.UnicodeUTF8))
        #self.label_cashier.setText(QtGui.QApplication.translate("Dialog", "Кассир", None, QtGui.QApplication.UnicodeUTF8))
        
        self.go_pushButton.setText(QtGui.QApplication.translate("Dialog", "Показать", None, QtGui.QApplication.UnicodeUTF8))


    def addrow(self, value, x, y, id=None, promise=False, date = None):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=""
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/user.png"))
        
        if y==5 and value!='AUTH_OK':
            headerItem.setBackgroundColor(QtGui.QColor("red"))
        elif y==5 and value=='AUTH_OK':
            headerItem.setBackgroundColor(QtGui.QColor("lightgreen"))
        headerItem.setText(unicode(value))
        if id:
            headerItem.id = id
            headerItem.date = date
        self.tableWidget.setItem(x,y,headerItem)
             
    def radius_auth_fixtures(self):
        self.tableWidget.clearContents()
        account_id = self.comboBox_account.itemData(self.comboBox_account.currentIndex()).toInt()[0]
        acc_str = ''
        if account_id:
            acc_str = " and account_id=%s" % account_id
        start_date = self.dateTimeEdit_date_start.dateTime().toPyDateTime()
        end_date = self.dateTimeEdit_date_end.dateTime().toPyDateTime()
        items = self.connection.sql("""SELECT ra.id as id, ra.account_id as account_id,(SELECT username FROM billservice_account WHERE id=ra.account_id) as account_username,
        ra.type as type, ra.service as service, (SELECT username FROM billservice_subaccount WHERE id=ra.subaccount_id) as subaccount_username, (SELECT name FROM nas_nas WHERE id=ra.nas_id) as nas_name, ra.cause as cause, ra.datetime as datetime FROM radius_authlog as ra 
        WHERE datetime between '%s' and '%s' %s
        ORDER BY datetime DESC""" % (start_date, end_date, acc_str))
        
        [u'#', u'Аккаунт', u"Субаккаунт", u'Сервер доступа', u'Способ доступа', u'Тип события', u"Событие", u'Дата']
        self.connection.commit()
        self.tableWidget.setRowCount(len(items)+1)
        i=0
        for item in items:
            self.addrow(i, i, 0, id=item.id, )
            self.addrow(item.account_username, i, 1)
            self.addrow(item.subaccount_username, i, 2)
            self.addrow(item.nas_name, i, 3)
            self.addrow(item.service, i, 4)
            self.addrow(item.type, i, 5)
            self.addrow(item.cause, i, 6)
            self.addrow(item.datetime.strftime(self.strftimeFormat), i, 7)
            i+=1

        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue("%strans_date_start" % self.report_type, QtCore.QVariant(self.dateTimeEdit_date_start.dateTime()))
            settings.setValue("%strans_date_end" % self.report_type, QtCore.QVariant(self.dateTimeEdit_date_end.dateTime()))
        except Exception, ex:
            print "Transactions settings save error: ", ex
            
    def balance_log_fixtures(self):
        self.tableWidget.clearContents()
        account_id = self.comboBox_account.itemData(self.comboBox_account.currentIndex()).toInt()[0]
        acc_str = ''
        if account_id:
            acc_str = " and account_id=%s" % account_id
        start_date = self.dateTimeEdit_date_start.dateTime().toPyDateTime()
        end_date = self.dateTimeEdit_date_end.dateTime().toPyDateTime()
        items = self.connection.sql("""SELECT bah.id,(SELECT username FROM billservice_account WHERE id=bah.account_id) as account_username, bah.balance as balance, bah.datetime as datetime FROM billservice_balancehistory as bah 
        WHERE datetime between '%s' and '%s' %s
        ORDER BY datetime DESC""" % (start_date, end_date, acc_str))
        
        [u'#', u'Аккаунт', u"Баланс", u'Дата']
        self.connection.commit()
        self.tableWidget.setRowCount(len(items)+1)
        i=0
        for item in items:
            self.addrow(i, i, 0, id=item.id, )
            self.addrow(item.account_username, i, 1)
            self.addrow(item.balance, i, 2)
            self.addrow(item.datetime.strftime(self.strftimeFormat), i, 3)
            i+=1

        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue("%strans_date_start" % self.report_type, QtCore.QVariant(self.dateTimeEdit_date_start.dateTime()))
            settings.setValue("%strans_date_end" % self.report_type, QtCore.QVariant(self.dateTimeEdit_date_end.dateTime()))
        except Exception, ex:
            print "Transactions settings save error: ", ex
            
    def fixtures(self):            
        accounts = self.connection.sql("SELECT id, username FROM billservice_account ORDER BY username ASC")
        self.connection.commit()
        self.comboBox_account.addItem(u"-Все клиенты-")
        self.comboBox_account.setItemData(0, QtCore.QVariant(0))
        i=1
        for account in accounts:
            self.comboBox_account.addItem(account.username)
            self.comboBox_account.setItemData(i, QtCore.QVariant(account.id))
            if self.account_id==account.id:
                self.comboBox_account.setCurrentIndex(i)
            i+=1
        
            
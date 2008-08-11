#-*-coding=utf-8-*-

import os, sys
from PyQt4 import QtCore, QtGui
from helpers import tableFormat
from helpers import Object as Object
from helpers import makeHeaders
import datetime
import socket 
from reports.bpreportedit import bpReportEdit
import thread
import time

#TODO: nullify the arguments lists (self.users, self.classes) after each report generation
_xmlpath = "reports/xml"
_querydict = {\
              "get_nas"      : "SELECT name, type, ipaddress, id FROM nas_nas ORDER BY name;", \
	      "get_usernames": "SELECT username, id FROM billservice_account ORDER BY username;", \
              "get_classes"  : "SELECT name, weight, id FROM nas_trafficclass ORDER BY name;"
             }
_charthidetabs = {\
             "nfs_user_traf"  : ("portsTab",),\
             "nfs_user_speed" : ("portsTab",),\
             "nfs_total_users_traf" : ("portsTab",),\
             "nfs_total_users_speed" : ("portsTab",),\
             "nfs_total_traf" : ("portsTab", "usersTab"),\
             "nfs_total_speed" : ("portsTab", "usersTab"),\
             "nfs_total_traf_bydir" : ("portsTab", "usersTab"),\
             "nfs_total_speed_bydir" : ("portsTab", "usersTab"),\
             "nfs_port_speed" : ("usersTab", "serversTab", "classesTab"),\
             "nfs_nas_traf" : ("usersTab", "classesTab", "portsTab"),\
             "nfs_total_nass_traf" : ("usersTab", "classesTab", "portsTab"),\
             "nfs_total_classes_speed" : ("usersTab", "serversTab", "portsTab"),\
             "userstrafpie" : ("serversTab", "classesTab", "portsTab"),\
             "sessions" : ("serversTab", "classesTab", "portsTab"),\
             "trans_deb" : ("usersTab", "serversTab", "classesTab", "portsTab"),\
             "trans_crd" : ("usersTab", "serversTab", "classesTab", "portsTab")
            }
_restrictions = {\
                 "one_user"  :("nfs_user_traf", "nfs_user_speed"),\
                 "one_server":("nfs_nas_traf"),\
                 "one_class" :()\
                }
_ports = [(25, "SMTP"), (53, "DNS"), (80, "HTTP"), (110, "POP3"), (143, "IMAP"), (443, "HTTPS"), (1080, "SOCKS"), (3128, "Web Cache"), (3306, "MySQL"), (3724, "WoW"), (5190, "ICQ"), (5222, "Jabber"), (5432, "Postgres"), (8080, "HTTP Proxy")]
class TransactionsReport(QtGui.QMainWindow):
    def __init__(self, connection ,account=None):
        super(TransactionsReport, self).__init__()
        self.account = account
        self.connection = connection
        self.resize(QtCore.QSize(QtCore.QRect(0,0,903,483).size()).expandedTo(self.minimumSizeHint()))
        

        self.user_edit = QtGui.QComboBox(self)
        self.user_edit.setGeometry(QtCore.QRect(100,12,201,20))
        self.user_edit.setObjectName("user_edit")

        self.date_start = QtGui.QDateTimeEdit(self)
        self.date_start.setGeometry(QtCore.QRect(420,9,161,20))
        self.date_start.setCalendarPopup(True)
        self.date_start.setObjectName("date_start")

        self.date_end = QtGui.QDateTimeEdit(self)
        self.date_end.setGeometry(QtCore.QRect(420,42,161,20))
        self.date_end.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.date_end.setCalendarPopup(True)
        self.date_end.setObjectName("date_end")

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

        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget = tableFormat(self.tableWidget) 
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        

        self.setCentralWidget(self.tableWidget)
        
        self.system_transactions_checkbox = QtGui.QCheckBox(self)
        #self.system_transactions_checkbox.setMargin(10)
        self.system_transactions_checkbox.setObjectName("system_transactions_checkbox")


        self.toolBar = QtGui.QToolBar(self)
        
        self.toolBar.addWidget(self.user_label)
        #self.toolBar.addSeparator()
        self.toolBar.addWidget(self.user_edit)
        
        self.toolBar.addWidget(self.date_start_label)
        #self.toolBar.addSeparator()
        self.toolBar.addWidget(self.date_start)
        #self.toolBar.addSeparator()
        self.toolBar.addWidget(self.date_end_label)
        #self.toolBar.addSeparator()
        self.toolBar.addWidget(self.date_end)
        #self.toolBar.addSeparator()
        self.toolBar.addWidget(self.system_transactions_checkbox)
        #self.toolBar.addSeparator()
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
        for account in accounts:
            self.user_edit.addItem(account.username)
        
        if self.account:
            self.user_edit.setCurrentIndex(self.user_edit.findText(self.account.username, QtCore.Qt.MatchCaseSensitive))
            self.setWindowTitle(u"История операций над лицевым счётом пользователя %s" % self.account.username)


    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
                
    def refresh_table(self):
        self.setWindowTitle(u"История операций над лицевым счётом пользователя %s" % unicode(self.user_edit.currentText()))
        self.tableWidget.clearContents()
        start_date = self.date_start.dateTime().toPyDateTime()
        end_date = self.date_end.dateTime().toPyDateTime()
        
        if self.system_transactions_checkbox.checkState()==2:
            transactions = self.connection.sql("""SELECT transaction.*, transactiontype.name as transaction_type_name, tariff.name as tariff_name FROM billservice_transaction as transaction
                                            JOIN billservice_transactiontype as transactiontype ON transactiontype.internal_name = transaction.type_id
                                            LEFT JOIN billservice_tariff as tariff ON tariff.id = transaction.tarif_id   
                                            WHERE transaction.created between '%s' and '%s' and transaction.account_id=%d""" %  (start_date, end_date, self.connection.get("SELECT * FROM billservice_account WHERE username='%s'" % unicode(self.user_edit.currentText())).id))
        else:
            transactions = self.connection.sql("""SELECT transaction.*,transactiontype.name as transaction_type_name, tariff.name as tariff_name
            FROM billservice_transaction as transaction
            JOIN billservice_transactiontype as transactiontype ON transactiontype.internal_name = transaction.type_id
            LEFT JOIN billservice_tariff as tariff ON tariff.id = transaction.tarif_id
            WHERE transaction.type_id='MANUAL_TRANSACTION' and transaction.created between '%s' and '%s' and transaction.account_id=%d""" %  (start_date, end_date, self.connection.get("SELECT * FROM billservice_account WHERE username='%s'" % unicode(self.user_edit.currentText())).id))            

        self.tableWidget.setRowCount(len(transactions))
        i=0
        ballance = 0
        write_on = 0
        write_off = 0
        for transaction in transactions:
            self.addrow(transaction.id, i, 0)
            self.addrow(transaction.created.strftime("%d-%m-%Y %H:%M:%S"), i, 1)
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
        
    def delete_transaction(self):
        ids = []
        import Pyro
        for index in self.tableWidget.selectedIndexes()[0:6]:
            i=unicode(self.tableWidget.item(index.row(), 0).text())
            try:
                ids.append(int(i))
            except Exception, e:
                print "can not convert transaction id to int"
        try:
            self.connection.transaction_delete(ids)
        except Exception, e:
            print ''.join(Pyro.util.getPyroTraceback(e))
            
        self.refresh_table()
        
class ReportPropertiesDialog(QtGui.QDialog):
    def __init__(self, connection):
        super(ReportPropertiesDialog, self).__init__()
        self.connection = connection
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
        self.to_dateTimeEdit.setDisplayFormat(QtGui.QApplication.translate("Dialog", "yyyy-MM-dd H:mm:ss", None, QtGui.QApplication.UnicodeUTF8))
        self.from_dateTimeEdit.setDisplayFormat(QtGui.QApplication.translate("Dialog", "yyyy-MM-dd H:mm:ss", None, QtGui.QApplication.UnicodeUTF8))
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
        
        for user in users:
            item = QtGui.QListWidgetItem()
            item.setText(user.username)
            item.id = user.id
            self.all_users_listWidget.addItem(item)
            
        
        classes = self.connection.sql("SELECT * FROM nas_trafficclass ORDER BY name ASC")
        
        for clas in classes:
            item = QtGui.QListWidgetItem()
            item.setText(clas.name)
            item.id = clas.id
            self.all_classes_listWidget.addItem(item)
            
        nasses = self.connection.sql("SELECT * FROM nas_nas")
        
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
        print 1
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
        for x in xrange(0, self.selected_users_listWidget.count()):
            self.users.append(self.selected_users_listWidget.item(x).id)
            
        for x in xrange(0, self.selected_classes_listWidget.count()):
            self.classes.append(self.selected_classes_listWidget.item(x).id)
            
        if self.nas_comboBox.currentText()!='':
            self.nas = self.connection.get("SELECT * FROM nas_nas WHERE name='%s'" % unicode(self.nas_comboBox.currentText()))
        print self.users
        self.start_date = self.from_dateTimeEdit.dateTime().toPyDateTime()
        self.end_date = self.to_dateTimeEdit.dateTime().toPyDateTime()
        QtGui.QDialog.accept(self)
        
class NetFlowReport(QtGui.QMainWindow):
    def __init__(self, connection):
        super(NetFlowReport, self).__init__()
        self.connection = connection
        
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
        #self.button_forward.setFlat(True)

        #self.button.setMaximumHeight(17)
        self.status_label= QtGui.QLabel()
        #self.status_label.setMinimumWidth(600)
        
        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget = tableFormat(self.tableWidget)
        #self.tableWidget.setColumnHidden(0, False)
        
        self.setCentralWidget(self.tableWidget)

        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        
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
        
        QtCore.QObject.connect(self.configureAction, QtCore.SIGNAL("triggered()"), self.configure)
        
        QtCore.QObject.connect(self.button_start, QtCore.SIGNAL("clicked()"), self.startPage)
        QtCore.QObject.connect(self.button_forward, QtCore.SIGNAL("clicked()"), self.addPage)
        QtCore.QObject.connect(self.button_back, QtCore.SIGNAL("clicked()"), self.delPage)
        self.retranslateUi()
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Сетевая статистика", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()

        columns = ['#', u'Аккаунт', u'Трафик', u'Сетевой протокол', u'IP источника', u'Порт источника', u'IP получателя',  u'Порт получателя', u'Передано байт', u'Дата']
        makeHeaders(columns, self.tableWidget)
        self.tableWidget.setColumnHidden(0, False)
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
        
    def configure(self):
        if self.child.exec_()!=1:
            return

        self.current_page=0
        self.refresh()
                
    def refresh(self):
        
        self.status_label.setText(u"Подождите, идёт обработка.")

        
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
            print 1
        elif self.child.with_grouping_checkBox.checkState()==2:
            sql="""SELECT netflowstream.direction, netflowstream.protocol, netflowstream.src_addr, netflowstream.dst_addr,  account.username as account_username, class.name as class_name,  class.color as class_color, sum(netflowstream.octets) as octets
            FROM billservice_netflowstream as netflowstream

            JOIN billservice_account as account ON account.id = netflowstream.account_id
            JOIN nas_trafficclass as class ON class.id = netflowstream.traffic_class_id
            
            WHERE date_start between '%s' and '%s'
            
            """ % (self.child.start_date, self.child.end_date)
            print 2            
        
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
            sql+="ORDER BY netflowstream.date_start ASC"
        elif self.child.with_grouping_checkBox.checkState()==0 and self.child.order_by_desc.checkState()==2:
            sql+="ORDER BY netflowstream.date_start DESC"
            
        if self.current_page==0:
            sql+=" LIMIT 100"
        else:
            
            sql+=" LIMIT 100 OFFSET %d" % (self.current_page*100)
            
        import time
        a=time.clock()
        flows = self.connection.sql(sql)
        print "request time=", time.clock()-a
        i=0
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(flows))
        octets_in_summ=0
        octets_out_summ=0

        c=self.current_page*100
        #['id',  u'Аккаунт', u'Дата', u'Класс', u'Направление', u'Протокол', u'IP источника', u'IP получателя', u'Порт источника', u'Порт получателя', u'Передано байт']
        for flow in flows:
            self.addrow(c, i, 0)
            if self.child.with_grouping_checkBox.checkState()==0:
                
                
                self.addrow(flow.src_port, i, 5)
                self.addrow(flow.dst_port, i, 7)
                
                #self.addrow(flow.nas_name, i, 1)
                #self.addrow(flow.tarif_name, i, 3)
                
                if flow.direction=='INPUT':
                    octets_in_summ+=int(flow.octets)
                elif flow.direction=='OUTPUT':
                    octets_out_summ+=int(flow.octets)

                
                if flow.direction=="INPUT" or (flow.direction=="INPUT" and flow.port_name1=="Null"):
                
                    if flow.port_name=="Null" and flow.port_name1!="Null":
                        flow.port_name=flow.port_name1
                        flow.port_description=flow.port_description1
                    elif flow.port_name=="Null":
                        flow.port_description=''
    
                        
                    
                    self.addrow("%s (%s)" % (self.getProtocol(flow.protocol), flow.port_name), i, 3)
                    self.tableWidget.item(i,3).setToolTip(flow.port_description)
                
                 
                elif flow.direction=="OUTPUT" or (flow.direction=="OUTPUT" and flow.port_name=="Null"):
                
                    if flow.port_name1=="Null" and flow.port_name!="Null":
                        flow.port_name1 = flow.port_name
                        flow.port_description1 = flow.port_description
                    elif flow.port_name1=="Null": 
                        flow.port_name1=""    
                        flow.port_description1 = ""   
    
                    self.addrow("%s (%s)" % (self.getProtocol(flow.protocol), flow.port_name1), i, 3)
                    self.tableWidget.item(i,3).setToolTip(flow.port_description1)       
                else:
                    self.addrow("%s" % (self.getProtocol(flow.protocol)), i, 3)


                self.addrow(flow.date_start.strftime("%d-%m-%Y %H:%M:%S"), i, 9)
            else:
                self.addrow("%s" % (self.getProtocol(flow.protocol)), i, 3)
                
            self.addrow(flow.account_username, i, 1)
            
            self.addrow("%s KB" % (float(flow.octets)/1024), i, 8)
            self.addrow(flow.class_name, i, 2, color=flow.class_color)
            #self.addrow(flow.direction, i, 4)
            
            
            
            
            #print dns.reversename.to_address(n)
            #try:
           #     self.addrow(socket.gethostbyaddr(flow.src_addr)[0], i, 5)
            #except:
            #    self.addrow(flow.src_addr, i, 5)
            self.addrow(flow.src_addr, i, 4)
                
            #try:
            #    self.addrow(socket.gethostbyaddr(flow.dst_addr)[0], i, 7)
            #except:
            #    self.addrow(flow.dst_addr, i, 7)
            self.addrow(flow.dst_addr, i, 6)
            
            self.tableWidget.setRowHeight(i, 16)
            
            i+=1
            c+=1

        #self.tableWidget.sortByColumn(3)        
        self.tableWidget.resizeColumnsToContents()
        #self.tableWidget.resizeRowsToContents()
        #self.statusBar().showMessage(u"Всего принято: %s МБ. Отправлено: %s МБ. Транзитного трафика: %s МБ" % (float(octets_in_summ)/(1024*1024), float(octets_out_summ)/(1024*1024), float(octets_transit_summ)/(1024*1024) ))
        #self.status_label.setText(u"Всего принято: %s МБ. Отправлено: %s МБ. Транзитного трафика: %s МБ" % (float(octets_in_summ)/(1024*1024), float(octets_out_summ)/(1024*1024), float(octets_transit_summ)/(1024*1024) ))
        self.status_label.setText(u"Готово")
        print "Interface generation time=", time.clock()-a    
        
        

class ReportSelectDialog(QtGui.QDialog):
    def __init__(self,  connection):
        super(ReportSelectDialog, self).__init__()
        self.setObjectName("reportSelectDialog")
        self.chartinfo = []
        self.selectedId = -1
        self.resize(QtCore.QSize(QtCore.QRect(0,0,482,510).size()).expandedTo(self.minimumSizeHint()))

        self.reportSelectButtonBox = QtGui.QDialogButtonBox(self)
        self.reportSelectButtonBox.setGeometry(QtCore.QRect(-20,460,340,30))
        self.reportSelectButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.reportSelectButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton)
        self.reportSelectButtonBox.setObjectName("reportSelectButtonBox")

        self.reportSelectList = QtGui.QListWidget(self)
        self.reportSelectList.setGeometry(QtCore.QRect(10,10,461,430))
        self.reportSelectList.setObjectName("reportSelectList")

        self.retranslateUi()
        
        QtCore.QObject.connect(self.reportSelectList, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.accept)
        #QtCore.QObject.connect(self.reportSelectButtonBox,QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.reportSelectButtonBox,QtCore.SIGNAL("rejected()"), self.reject)
        #QtCore.QMetaObject.connectSlotsByName(reportSelectDialog)
        self.fixtures()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("reportSelectDialog", "Выберите отчет", None, QtGui.QApplication.UnicodeUTF8))
    
    def fixtures(self):
        try:
            philes = os.listdir(_xmlpath)
        except Exception, ex:
            print ex
            return None
        philes = [phile for phile in philes if phile.endswith(".xml")]
        self.chartinfo = []
        #ilelement
        for phile in philes:
            try:
                f = open(_xmlpath+ "/" + phile)
                descstate = -3
                descstr = ''
                chtype  = []
                for infoline in f:
                    if descstate == -3:
                        if infoline.find("<description>") != -1:
                            descstate = infoline.find("<description>") + len("<description>")
                            descstr   = infoline.rstrip()[descstate:]

                        
                    if descstate != -2 and descstate != -3:
                        if infoline.find("</description>") != -1:
                            descend = infoline.find("</description>")
                            if descstate == -1: 
                                descstr += " " + infoline[0:descend].lstrip()
                                descstate = -2
                            else:
                                descstr   = infoline[descstate:descend]
                                descstate = -2
                        else:
                            if descstate == -1:
                                descstr += " " + infoline.lstrip().rstrip()
                                descstate = -1
                            descstate = -1
                        
                    
                    chindex = infoline.find("<chart")
                    if  chindex != -1:
                        chindex += len("<chart")
                        #attribs = infoline[chindex:infoline.find(">", chindex)]
                        chtypes = infoline.find('''type="''', chindex) + len('''type="''')
                        chtype.append(infoline[chtypes:infoline.find('''"''', chtypes)])
                        break
                        
                if not chtype:
                    break
                
                if not descstr:
                    descstr = phile
                self.chartinfo.append([phile, chtype, descstr])
                            
            except Exception, ex:
                print ex
        
        print self.chartinfo
        i = 0
        for infotuple in self.chartinfo:
            item = QtGui.QListWidgetItem()
            item.setText(QtCore.QString.fromUtf8(infotuple[2]))
            item.id = i
            self.reportSelectList.addItem(item)
            i += 1
    
    def accept(self):
        self.selectedId = self.reportSelectList.selectedItems()[0].id
        QtGui.QDialog.accept(self)

class StatReport(QtGui.QMainWindow):
    def __init__(self, connection, chartinfo):
        super(StatReport, self).__init__()
        self.connection = connection
        self.chartinfo = chartinfo
        
        self.child = ReportOptionsDialog(self.connection, self.chartinfo[1][0])
        self.resize(QtCore.QSize(QtCore.QRect(0,0,800,587).size()).expandedTo(self.minimumSizeHint()))
        self.textedit = QtGui.QTextEdit(self)
        
        self.setCentralWidget(self.textedit)
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        
 
        #self.statusBar().addWidget(self.button_end)

        
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)

        self.configureAction = QtGui.QAction(self)
        self.configureAction.setIcon(QtGui.QIcon("images/configure.png"))
        self.configureAction.setObjectName("configureAction")
        self.toolBar.addAction(self.configureAction)
        
        QtCore.QObject.connect(self.configureAction, QtCore.SIGNAL("triggered()"), self.configure)
        
        self.retranslateUi()
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Сетевая статистика", None, QtGui.QApplication.UnicodeUTF8))
    
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.configureAction.setText(QtGui.QApplication.translate("MainWindow", "configureAction", None, QtGui.QApplication.UnicodeUTF8))

        
    def configure(self):
        
        if self.child.exec_()!=1:
            return

    
        self.refresh()
                
    def refresh(self):
        kwargs = {}
        kwargs['options'] = {}
        if self.child.antialiasing_checkBox.checkState() == 0:
            kwargs['options']['antialias'] = False
        else:
            kwargs['options']['antialias'] = True
            
        if self.child.grid_checkBox.checkState() == 0:
            kwargs['options']['autoticks'] = True
        else:
            kwargs['options']['autoticks'] = False
          
        #if self.child.users:
        kwargs['users']   = self.child.users
            
        #if self.child.classes:
        kwargs['classes'] = self.child.classes
            
        #if self.child.servers:
        kwargs['servers'] = self.child.servers
        #if self.child.ports:
        kwargs['ports']   = self.child.ports
        
        print kwargs
        brep = bpReportEdit()
        editor  = brep.createreport(_xmlpath+"/" +self.chartinfo[0], [(self.child.start_date, self.child.end_date)], [kwargs], connection=self.connection)
        self.textedit = None
        
        if self.child.read_only_checkBox.checkState() == 2:
            editor.setReadOnly(True)
        #self.textedit.setDocument(editor.document())
        self.setCentralWidget(editor)

        if self.child.send_to_printer_checkBox.checkState() == 2:
            print "arrgh"
            #self.print_report(self.centralWidget().document(), 5)
            thread.start_new_thread(self.print_report, (self.centralWidget().document(), 2))
            
    def print_report(self, printdoc, sleeptime):
        time.sleep(sleeptime)
        document = printdoc
        printer = QtGui.QPrinter()
    
        dialog = QtGui.QPrintDialog(printer, self)
        dialog.setWindowTitle(self.tr("Print Document"))
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return
        document.print_(printer)
        
class ReportOptionsDialog(QtGui.QDialog):
    def __init__(self, connection, chartclass):
        super(ReportOptionsDialog, self).__init__()
        self.connection = connection
        self.chartclass = chartclass
        self.users   = []
        self.classes = []
        self.servers = []
        self.ports   = []
        self.start_date = datetime.datetime.now()
        self.end_date   = datetime.datetime.now()
        self.one_user   = False
        self.one_server = False
        self.one_class  = False
        self.resize(QtCore.QSize(QtCore.QRect(0,0,442,535).size()).expandedTo(self.minimumSizeHint()))

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(270,490,160,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setGeometry(QtCore.QRect(0,10,441,471))
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")

        self.mainTab = QtGui.QWidget()
        self.mainTab.setObjectName("mainTab")

        self.intervals_groupBox = QtGui.QGroupBox(self.mainTab)
        self.intervals_groupBox.setGeometry(QtCore.QRect(10,10,411,101))
        self.intervals_groupBox.setFlat(False)
        self.intervals_groupBox.setCheckable(False)
        self.intervals_groupBox.setChecked(False)
        self.intervals_groupBox.setObjectName("intervals_groupBox")

        self.date_end_dateTimeEdit = QtGui.QDateTimeEdit(self.intervals_groupBox)
        self.date_end_dateTimeEdit.setGeometry(QtCore.QRect(120,60,194,23))
        dt_now = datetime.datetime.now()
        self.date_end_dateTimeEdit.setMinimumDate(QtCore.QDate(2008,1,1))
        self.date_end_dateTimeEdit.setDate(QtCore.QDate(dt_now.year, dt_now.month, dt_now.day))
        self.date_end_dateTimeEdit.setCalendarPopup(True)
        self.date_end_dateTimeEdit.setObjectName("date_end_dateTimeEdit")

        self.date_start_label = QtGui.QLabel(self.intervals_groupBox)
        self.date_start_label.setGeometry(QtCore.QRect(20,30,91,18))
        self.date_start_label.setObjectName("date_start_label")

        self.date_start_dateTimeEdit = QtGui.QDateTimeEdit(self.intervals_groupBox)
        self.date_start_dateTimeEdit.setGeometry(QtCore.QRect(120,30,194,23))
        self.date_start_dateTimeEdit.setMinimumDate(QtCore.QDate(2008,1,1))
        self.date_start_dateTimeEdit.setCalendarPopup(True)
        self.date_start_dateTimeEdit.setObjectName("date_start_dateTimeEdit")
        
        self.date_end_label = QtGui.QLabel(self.intervals_groupBox)
        self.date_end_label.setGeometry(QtCore.QRect(20,60,91,18))
        self.date_end_label.setObjectName("date_end_label")

        self.settings_groupBox = QtGui.QGroupBox(self.mainTab)
        self.settings_groupBox.setGeometry(QtCore.QRect(10,120,411,151))
        self.settings_groupBox.setObjectName("settings_groupBox")

        self.grid_checkBox = QtGui.QCheckBox(self.settings_groupBox)
        self.grid_checkBox.setGeometry(QtCore.QRect(20,20,191,21))
        self.grid_checkBox.setObjectName("grid_checkBox")

        self.antialiasing_checkBox = QtGui.QCheckBox(self.settings_groupBox)
        self.antialiasing_checkBox.setGeometry(QtCore.QRect(20,50,191,21))
        self.antialiasing_checkBox.setObjectName("antialiasing_checkBox")

        self.read_only_checkBox = QtGui.QCheckBox(self.settings_groupBox)
        self.read_only_checkBox.setGeometry(QtCore.QRect(20,80,191,21))
        self.read_only_checkBox.setObjectName("read_only_checkBox")

        self.send_to_printer_checkBox = QtGui.QCheckBox(self.settings_groupBox)
        self.send_to_printer_checkBox.setGeometry(QtCore.QRect(20,110,261,21))
        self.send_to_printer_checkBox.setObjectName("send_to_printer_checkBox")
        self.tabWidget.addTab(self.mainTab,"")

        self.usersTab = QtGui.QWidget()
        self.usersTab.setObjectName("usersTab")

        self.all_users_listWidget = QtGui.QListWidget(self.usersTab)
        self.all_users_listWidget.setGeometry(QtCore.QRect(10,30,181,401))
        self.all_users_listWidget.setObjectName("all_users_listWidget")

        self.selected_users_listWidget = QtGui.QListWidget(self.usersTab)
        self.selected_users_listWidget.setGeometry(QtCore.QRect(240,30,191,401))
        self.selected_users_listWidget.setObjectName("selected_users_listWidget")

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

        self.all_servers_listWidget = QtGui.QListWidget(self.serversTab)
        self.all_servers_listWidget.setGeometry(QtCore.QRect(10,30,181,401))
        self.all_servers_listWidget.setObjectName("all_servers_listWidget")

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
        self.tabWidget.addTab(self.classesTab,"")

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
        self.date_start_label.setBuddy(self.date_start_dateTimeEdit)
        self.date_end_label.setBuddy(self.date_end_dateTimeEdit)

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
        
        QtCore.QObject.connect(self.add_server_toolButton, QtCore.SIGNAL("clicked()"), self.addServer)
        QtCore.QObject.connect(self.del_server_toolButton, QtCore.SIGNAL("clicked()"), self.delServer)
        
        QtCore.QObject.connect(self.all_servers_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.addServer)
        QtCore.QObject.connect(self.selected_servers_listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.delServer)
        if 1:
            self.setTabOrder(self.tabWidget,self.date_start_dateTimeEdit)
            self.setTabOrder(self.date_start_dateTimeEdit,self.date_end_dateTimeEdit)
            self.setTabOrder(self.date_end_dateTimeEdit,self.grid_checkBox)
            self.setTabOrder(self.grid_checkBox,self.antialiasing_checkBox)
            self.setTabOrder(self.antialiasing_checkBox,self.read_only_checkBox)
            self.setTabOrder(self.read_only_checkBox,self.send_to_printer_checkBox)
            self.setTabOrder(self.send_to_printer_checkBox,self.all_users_listWidget)
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
            self.setTabOrder(self.selected_classes_listWidget,self.ports_listWidget)
            self.setTabOrder(self.ports_listWidget,self.extra_ports_lineEdit)
            self.setTabOrder(self.extra_ports_lineEdit,self.buttonBox)
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройки отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.intervals_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Интервал дат", None, QtGui.QApplication.UnicodeUTF8))
        self.date_end_dateTimeEdit.setDisplayFormat(QtGui.QApplication.translate("Dialog", "yyyy-MM-dd H:mm:ss", None, QtGui.QApplication.UnicodeUTF8))
        self.date_start_label.setText(QtGui.QApplication.translate("Dialog", "Начало", None, QtGui.QApplication.UnicodeUTF8))
        self.date_start_dateTimeEdit.setDisplayFormat(QtGui.QApplication.translate("Dialog", "yyyy-MM-dd H:mm:ss", None, QtGui.QApplication.UnicodeUTF8))
        self.date_end_label.setText(QtGui.QApplication.translate("Dialog", "Конец", None, QtGui.QApplication.UnicodeUTF8))
        self.settings_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Настройки", None, QtGui.QApplication.UnicodeUTF8))
        self.grid_checkBox.setText(QtGui.QApplication.translate("Dialog", "Сетка", None, QtGui.QApplication.UnicodeUTF8))
        self.antialiasing_checkBox.setText(QtGui.QApplication.translate("Dialog", "Сглаживание", None, QtGui.QApplication.UnicodeUTF8))
        self.read_only_checkBox.setText(QtGui.QApplication.translate("Dialog", "Запретить редактирование", None, QtGui.QApplication.UnicodeUTF8))
        self.send_to_printer_checkBox.setText(QtGui.QApplication.translate("Dialog", "Отправить на печать после создания", None, QtGui.QApplication.UnicodeUTF8))
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
        self.all_classes_label.setText(QtGui.QApplication.translate("Dialog", "Доступные направления", None, QtGui.QApplication.UnicodeUTF8))
        self.del_class_toolButton.setText(QtGui.QApplication.translate("Dialog", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.add_class_toolButton.setText(QtGui.QApplication.translate("Dialog", ">", None, QtGui.QApplication.UnicodeUTF8))
        self.selected_classes_label.setText(QtGui.QApplication.translate("Dialog", "Выбранные направления", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.classesTab), QtGui.QApplication.translate("Dialog", "Направления", None, QtGui.QApplication.UnicodeUTF8))
        self.ports_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Выберите порты", None, QtGui.QApplication.UnicodeUTF8))
        self.ports_description_label.setText(QtGui.QApplication.translate("Dialog", "Отметьте флажками нужные порты", None, QtGui.QApplication.UnicodeUTF8))
        self.extra_ports_label.setText(QtGui.QApplication.translate("Dialog", "Введите дополнительные порты через запятую:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.portsTab), QtGui.QApplication.translate("Dialog", "Порты", None, QtGui.QApplication.UnicodeUTF8))

    def fixtures(self):
        '''import random
        i = random.randint(2, 22)
        objj = getattr(self, "date_start_dateTimeEdit", None)
        obj2 = getattr(self, "classesTab", None)
        print "zomg"
        objj.hide()
        self.tabWidget.removeTab(self.tabWidget.indexOf(obj2))
        print self.date_end_dateTimeEdit.isVisible()
        print self.date_start_dateTimeEdit.isVisible()
        for x in xrange(0, self.selected_classes_listWidget.count()):
            self.classes.append(self.selected_classes_listWidget.item(x).id)
        print self.classes'''
        
        if self.chartclass in _restrictions['one_user']:
            self.one_user = True
            
        if self.chartclass in _restrictions['one_server']:
            self.one_server = True
            
        if self.chartclass in _restrictions['one_class']:
            self.one_class = True
        
        
        hidetabs = _charthidetabs[self.chartclass]
        
        for hidetab in hidetabs:
            htObj = getattr(self, hidetab, None)
            print hidetab
            self.tabWidget.removeTab(self.tabWidget.indexOf(htObj))
            
            
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
                
        if "portsTab" not in hidetabs:  
            for port in _ports:
                item = QtGui.QListWidgetItem()
                item.setText(port[1])
                item.id = port[0]
                item.setCheckState(QtCore.Qt.Unchecked)
                self.ports_listWidget.addItem(item)
        
    def addUser(self):
        if self.one_user:
            if self.selected_users_listWidget.count() == 1:
                return
            else:
                selected_items = self.all_users_listWidget.selectedItems()
                if selected_items:
                    self.all_users_listWidget.takeItem(self.all_users_listWidget.row(selected_items[0]))
                    self.selected_users_listWidget.addItem(selected_items[0])
                    return
                
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
        if self.one_server:
            if self.selected_servers_listWidget.count() == 1:
                return
            else:
                selected_items = self.all_servers_listWidget.selectedItems()
                if selected_items:
                    self.all_servers_listWidget.takeItem(self.all_servers_listWidget.row(selected_items[0]))
                    self.selected_servers_listWidget.addItem(selected_items[0])
                    return
        
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
        if self.one_class:
            if self.selected_classes_listWidget.count() == 1:
                return
            else:
                selected_items = self.all_classes_listWidget.selectedItems()
                if selected_items:
                    self.all_classes_listWidget.takeItem(self.all_classes_listWidget.row(selected_items[0]))
                    self.selected_classes_listWidget.addItem(selected_items[0])
                    return        
        
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
        
    def accept(self):
        self.users   = []
        self.classes = []
        self.servers = []
        self.ports   = []
        for x in xrange(0, self.selected_users_listWidget.count()):
            self.users.append(self.selected_users_listWidget.item(x).id)
            
        for x in xrange(0, self.selected_classes_listWidget.count()):
            self.classes.append(self.selected_classes_listWidget.item(x).id)
            
        for x in xrange(0, self.selected_servers_listWidget.count()):
            self.servers.append(self.selected_servers_listWidget.item(x).id)
            
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
            
                    
            
        self.start_date = self.date_start_dateTimeEdit.dateTime().toPyDateTime()
        self.end_date   = self.date_end_dateTimeEdit.dateTime().toPyDateTime()
        print self.users  
        print self.classes
        print self.servers 
        print self.ports
        QtGui.QDialog.accept(self)
        
        
    
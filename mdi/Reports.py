#-*-coding=utf-8-*-

import os, sys
from PyQt4 import QtCore, QtGui
from helpers import tableFormat
from helpers import Object as Object
from helpers import makeHeaders
import datetime
import socket 

class TransactionsReport(QtGui.QDialog):
    def __init__(self, connection ,account=None):
        super(TransactionsReport, self).__init__()
        self.account = account
        self.connection = connection
        self.resize(QtCore.QSize(QtCore.QRect(0,0,703,483).size()).expandedTo(self.minimumSizeHint()))
        
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(94,441,346,25))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

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
        self.date_start_label.setGeometry(QtCore.QRect(402,9,43,20))
        self.date_start_label.setObjectName("date_start_label")

        self.date_end_label = QtGui.QLabel(self)
        self.date_end_label.setGeometry(QtCore.QRect(402,42,43,20))
        self.date_end_label.setObjectName("date_end_label")

        self.user_label = QtGui.QLabel(self)
        self.user_label.setGeometry(QtCore.QRect(11,12,202,20))
        self.user_label.setObjectName("user_label")

        self.go_pushButton = QtGui.QPushButton(self)
        self.go_pushButton.setGeometry(QtCore.QRect(590,40,101,25))
        self.go_pushButton.setObjectName("go_pushButton")

        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(10,70,681,331))
        self.tableWidget = tableFormat(self.tableWidget) 

        self.save_pushButton = QtGui.QPushButton(self)
        self.save_pushButton.setGeometry(QtCore.QRect(11,441,77,25))
        self.save_pushButton.setObjectName("save_pushButton")

        self.system_transactions_checkbox = QtGui.QCheckBox(self)
        self.system_transactions_checkbox.setGeometry(QtCore.QRect(11,39,409,18))
        self.system_transactions_checkbox.setObjectName("system_transactions_checkbox")

        self.write_off_label = QtGui.QLabel(self)
        self.write_off_label.setGeometry(QtCore.QRect(12,412,103,19))
        self.write_off_label.setObjectName("write_off_label")

        self.write_off = QtGui.QLabel(self)
        self.write_off.setGeometry(QtCore.QRect(121,412,103,19))
        self.write_off.setObjectName("write_off")

        self.write_on_label = QtGui.QLabel(self)
        self.write_on_label.setGeometry(QtCore.QRect(230,412,102,19))
        self.write_on_label.setObjectName("write_on_label")

        self.write_on = QtGui.QLabel(self)
        self.write_on.setGeometry(QtCore.QRect(338,412,103,19))
        self.write_on.setObjectName("write_on")

        self.ballance_label = QtGui.QLabel(self)
        self.ballance_label.setGeometry(QtCore.QRect(447,412,135,19))
        self.ballance_label.setObjectName("ballance_label")

        self.ballance = QtGui.QLabel(self)
        self.ballance.setGeometry(QtCore.QRect(588,412,103,19))
        self.ballance.setObjectName("ballance")

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        
        QtCore.QObject.connect(self.go_pushButton,QtCore.SIGNAL("clicked()"),self.refresh_table)
        self.fixtures()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "История операций над лицевым счётом пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.date_start_label.setText(QtGui.QApplication.translate("Dialog", "С", None, QtGui.QApplication.UnicodeUTF8))
        self.date_end_label.setText(QtGui.QApplication.translate("Dialog", "По", None, QtGui.QApplication.UnicodeUTF8))
        self.user_label.setText(QtGui.QApplication.translate("Dialog", "Пользователь", None, QtGui.QApplication.UnicodeUTF8))
        self.go_pushButton.setText(QtGui.QApplication.translate("Dialog", "Пыщь", None, QtGui.QApplication.UnicodeUTF8))
        
        self.tableWidget.clear()

        columns = [u'Id', u'Дата', u'Платёжный документ', u'Вид проводки', u'Тариф', u'Сумма', u'Комментарий']
        makeHeaders(columns, self.tableWidget)
        
        self.save_pushButton.setText(QtGui.QApplication.translate("Dialog", "Сохранить", None, QtGui.QApplication.UnicodeUTF8))
        self.system_transactions_checkbox.setText(QtGui.QApplication.translate("Dialog", "Включить в отчёт системные проводки", None, QtGui.QApplication.UnicodeUTF8))
        self.write_off_label.setText(QtGui.QApplication.translate("Dialog", "Списано:", None, QtGui.QApplication.UnicodeUTF8))
        self.write_off.setText(QtGui.QApplication.translate("Dialog", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.write_on_label.setText(QtGui.QApplication.translate("Dialog", "Начислено", None, QtGui.QApplication.UnicodeUTF8))
        self.write_on.setText(QtGui.QApplication.translate("Dialog", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.ballance_label.setText(QtGui.QApplication.translate("Dialog", "Балланс на конец периода", None, QtGui.QApplication.UnicodeUTF8))
        self.ballance.setText(QtGui.QApplication.translate("Dialog", "0", None, QtGui.QApplication.UnicodeUTF8))
        
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
            if transaction.summ<0:
                write_on +=transaction.summ*(-1)                             
            if transaction.summ>0:
                write_off +=transaction.summ
        self.tableWidget.setColumnHidden(0, True)
                
        self.write_off.setText(unicode(write_off))
        self.write_on.setText(unicode(write_on))
        self.ballance.setText(unicode(write_on-write_off))
        
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

        self.only_unique_checkBox = QtGui.QCheckBox(self.general_tab)
        self.only_unique_checkBox.setGeometry(QtCore.QRect(10,340,231,19))
        self.only_unique_checkBox.setObjectName("only_unique_checkBox")
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

        QtCore.QObject.connect(self.select_class_toolButton, QtCore.SIGNAL("clicked()"), self.addClass)
        
        QtCore.QObject.connect(self.remove_class_toolButton, QtCore.SIGNAL("clicked()"), self.delClass)
        
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
        self.only_unique_checkBox.setText(QtGui.QApplication.translate("Dialog", "Только уникальные значения", None, QtGui.QApplication.UnicodeUTF8))
        self.with_grouping_checkBox.setCheckState(QtCore.Qt.Checked)
        self.only_unique_checkBox.setCheckState(QtCore.Qt.Checked)
        
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
            
    def delUser(self):
        selected_items = self.selected_users_listWidget.selectedItems()
        
        for item in selected_items:
            self.selected_users_listWidget.takeItem(self.selected_users_listWidget.row(item))
            self.all_users_listWidget.addItem(item)
    
    def addClass(self):
        selected_items = self.all_classes_listWidget.selectedItems()
        print 1
        for item in selected_items:
            self.all_classes_listWidget.takeItem(self.all_classes_listWidget.row(item))
            self.selected_classes_listWidget.addItem(item)
    
    def delClass(self):
        selected_items = self.selected_classes_listWidget.selectedItems()
        #print 2
        for item in selected_items:
            self.selected_classes_listWidget.takeItem(self.selected_classes_listWidget.row(item))
            self.all_classes_listWidget.addItem(item)
        
    def accept(self):
        for x in xrange(0, self.selected_users_listWidget.count()):
            self.users.append(self.selected_users_listWidget.item(x).id)
            
        for x in xrange(0, self.selected_classes_listWidget.count()):
            self.classes.append(self.selected_classes_listWidget.item(x).id)
            
        if self.nas_comboBox.currentText()!='':
            self.nas = self.connection.get("SELECT * FROM nas_nas WHERE name='%s'" % unicode(self.nas_comboBox.currentText()))
            
        self.start_date = self.from_dateTimeEdit.dateTime().toPyDateTime()
        self.end_date = self.to_dateTimeEdit.dateTime().toPyDateTime()
        QtGui.QDialog.accept(self)
        
class NetFlowReport(QtGui.QMainWindow):
    def __init__(self, connection):
        super(NetFlowReport, self).__init__()
        self.connection = connection
        self.resize(QtCore.QSize(QtCore.QRect(0,0,800,587).size()).expandedTo(self.minimumSizeHint()))
        self.current_page=0
        self.protocols={'':0,
           'ddp':37,
           'encap':98, 
           'ggp':3, 
           'gre':47, 
           'hmp':20, 
           'icmp':1, 
           'idpr-cmtp':38, 
           'igmp':2, 
           'ipencap':4, 
           'ipip':94,  
           'ospf':89, 
           'rdp':27, 
           'tcp':6, 
           'udp':17
           }
        self.child = None
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
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()

        columns = ['id', u'Сервер доступа', u'Аккаунт', u'Тариф', u'Дата', u'Класс', u'Направление', u'Протокол', u'IP источника', u'IP получателя', u'Порт источника', u'Порт получателя', u'Передано байт']
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
        
        
    def configure(self):
        if not self.child:
            child = ReportPropertiesDialog(connection = self.connection)
        else:
            child = self.child

        if child.exec_()!=1:
            return
            #print 123
            pass
        self.child = child
        self.current_page=0
        self.refresh()
                
    def refresh(self):
        
        child = self.child


        
        if child.with_grouping_checkBox.checkState()==0:
            sql="""SELECT netflowstream.id,netflowstream.date_start, netflowstream.direction, netflowstream.protocol, netflowstream.src_addr, netflowstream.dst_addr, netflowstream.src_port, netflowstream.dst_port, netflowstream.octets, nas.name as nas_name, account.username as account_username, class.name as class_name, tarif.name as tarif_name, class.color as class_color 
            FROM billservice_netflowstream as netflowstream
            JOIN nas_nas as nas ON nas.id=netflowstream.nas_id
            JOIN billservice_account as account ON account.id = netflowstream.account_id
            JOIN nas_trafficclass as class ON class.id = netflowstream.traffic_class_id
            JOIN billservice_tariff as tarif ON tarif.id=get_tarif(netflowstream.account_id, netflowstream.date_start) 
            WHERE date_start between '%s' and '%s'""" % (child.start_date, child.end_date) 
            print 1
        elif child.with_grouping_checkBox.checkState()==2:
            sql="""SELECT netflowstream.direction, netflowstream.protocol, netflowstream.src_addr, netflowstream.dst_addr,  account.username as account_username, class.name as class_name,  class.color as class_color, sum(netflowstream.octets) as octets
            FROM billservice_netflowstream as netflowstream

            JOIN billservice_account as account ON account.id = netflowstream.account_id
            JOIN nas_trafficclass as class ON class.id = netflowstream.traffic_class_id
            
            WHERE date_start between '%s' and '%s'
            
            """ % (child.start_date, child.end_date)
            print 2            
        
        if len(child.users)>0 or len(child.classes)>0:
            sql+=" AND " 
        
        if len(child.users)>0:
            sql+= """ netflowstream.account_id IN (%s) """ % ','.join(map(str, child.users))
            
        if len(child.users)>0 and len(child.classes)>0:
            sql+=""" and """
        
        if len(child.classes)>0:
            sql+=""" netflowstream.traffic_class_id in (%s)"""  % ','.join(map(str, child.classes))
            
        if child.with_grouping_checkBox.checkState()==2:
            sql+="""GROUP BY netflowstream.direction, netflowstream.protocol, netflowstream.src_addr, netflowstream.dst_addr,  account.username, class.name, class.color"""
        
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
        octets_transit_summ=0
        c=self.current_page*100
        for flow in flows:
            self.addrow(c, i, 0)
            if child.with_grouping_checkBox.checkState()==0:
                
                
                self.addrow(flow.src_port, i, 10)
                self.addrow(flow.dst_port, i, 11)
                
                self.addrow(flow.nas_name, i, 1)
                self.addrow(flow.tarif_name, i, 3)
                
                if flow.direction=='INPUT':
                    octets_in_summ+=int(flow.octets)
                elif flow.direction=='OUTPUT':
                    octets_out_summ+=int(flow.octets)
                elif flow.direction=='TRANSIT':
                    octets_transit_summ+=int(flow.octets)
                    
                self.addrow(flow.date_start.strftime("%d-%m-%Y %H:%M:%S"), i, 4)

            self.addrow(flow.account_username, i, 2)
            
            self.addrow(flow.octets, i, 12)
            self.addrow(flow.class_name, i, 5, color=flow.class_color)
            self.addrow(flow.direction, i, 6)
            self.addrow(flow.protocol, i, 7)
            
            
            #print dns.reversename.to_address(n)
            try:
                self.addrow(socket.gethostbyaddr(flow.src_addr)[0], i, 8)
            except:
                self.addrow(flow.src_addr, i, 8)
                
            try:
                self.addrow(socket.gethostbyaddr(flow.dst_addr), i, 9)
            except:
                self.addrow(flow.dst_addr, i, 9)

            
            i+=1
            c+=1

        #self.tableWidget.sortByColumn(3)        
        #self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        #self.statusBar().showMessage(u"Всего принято: %s МБ. Отправлено: %s МБ. Транзитного трафика: %s МБ" % (float(octets_in_summ)/(1024*1024), float(octets_out_summ)/(1024*1024), float(octets_transit_summ)/(1024*1024) ))
        self.status_label.setText(u"Всего принято: %s МБ. Отправлено: %s МБ. Транзитного трафика: %s МБ" % (float(octets_in_summ)/(1024*1024), float(octets_out_summ)/(1024*1024), float(octets_transit_summ)/(1024*1024) ))
        
        print "Interface generation time=", time.clock()-a    
        
        
    
        
#-*-coding=utf-8*-

import os
from PyQt4 import QtCore, QtGui, QtSql
from Reports import TransactionsReport
from helpers import makeHeaders
from helpers import tableFormat
from helpers import sqliteDbAccess, connectDBName



class CheckBoxDialog(QtGui.QDialog):
    def __init__(self, all_items, selected_items, select_mode='checkbox'):
        super(CheckBoxDialog, self).__init__()
        self.all_items=all_items
        self.selected_items = selected_items
        self.select_mode = select_mode
        
        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,400,300).size()).expandedTo(self.minimumSizeHint()))
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,400,300).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,400,300).size()))
        
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(30,240,341,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setGeometry(QtCore.QRect(0,30,256,192))
        self.listWidget.setObjectName("listWidget")
        
  
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.listWidget)
        vbox.addWidget(self.buttonBox)
        
        self.setLayout(vbox)


        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        
        self.fixtures()


    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        
    def fixtures(self):
        selected_items = [x.id for x in self.selected_items]
        for ai in self.all_items:
            item = QtGui.QListWidgetItem(ai.name)
            if ai.id in selected_items:
                if self.select_mode == 'checkbox':
                    item.setCheckState(QtCore.Qt.Checked)
                else:
                    item.setSelected(True)
            else:
                if self.select_mode == 'checkbox':
                    item.setCheckState(QtCore.Qt.Unchecked)
                
            self.listWidget.addItem(item)
            
    def accept(self):
        self.selected_items=[]
        for x in xrange(0,self.listWidget.count()):
            if self.listWidget.item(x).checkState()==QtCore.Qt.Checked:
                self.selected_items.append(self.all_items[x])
        
        print self.selected_items
        QtGui.QDialog.accept(self)        
        
            
class ComboBoxDialog(QtGui.QDialog):
    def __init__(self, items, selected_item=None, title=''):
        super(ComboBoxDialog, self).__init__()
        self.items = items
        self.selected_item = selected_item
        self.title = title
        
        self.resize(QtCore.QSize(QtCore.QRect(0,0,318,89).size()).expandedTo(self.minimumSizeHint()))
        
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,318,89).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,318,89).size()))

        self.vboxlayout = QtGui.QVBoxLayout()


        self.comboBox = QtGui.QComboBox()

        self.vboxlayout.addWidget(self.comboBox)

        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)

        self.vboxlayout.addWidget(self.buttonBox)
        self.setLayout(self.vboxlayout)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        
        self.fixtures()

    def retranslateUi(self):
        if self.title=="":
            self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Диалог выбора", None, QtGui.QApplication.UnicodeUTF8))
        else:
            self.setWindowTitle(unicode(self.title))
        

    def fixtures(self):
        i=0
        for item in self.items:
            self.comboBox.addItem(item.name)
            if unicode(item.name) == unicode(self.selected_item):
                self.comboBox.setCurrentIndex(i)
            i+=1
            
class SpeedEditDialog(QtGui.QDialog):
    def __init__(self, item, title):
        super(SpeedEditDialog, self).__init__()
        self.item = item
        self.title = title
        self.resultstring = ""
        self.resize(QtCore.QSize(QtCore.QRect(0,0,415,132).size()).expandedTo(self.minimumSizeHint()))
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,415,132).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,415,132).size()))
        
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(120,95,171,25))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.speed_out_label = QtGui.QLabel(self)
        self.speed_out_label.setGeometry(QtCore.QRect(220,44,171,16))
        self.speed_out_label.setObjectName("speed_out_label")

        self.speed_in_label = QtGui.QLabel(self)
        self.speed_in_label.setGeometry(QtCore.QRect(20,44,171,16))
        self.speed_in_label.setObjectName("speed_in_label")

        self.in_postfix = QtGui.QComboBox(self)
        self.in_postfix.setGeometry(QtCore.QRect(140,60,69,21))
        self.in_postfix.setObjectName("in_postfix")
        self.in_postfix.addItem("")

        self.out_postfix = QtGui.QComboBox(self)
        self.out_postfix.setGeometry(QtCore.QRect(340,60,69,21))
        self.out_postfix.setObjectName("out_postfix")
        self.out_postfix.addItem("")

        self.description_label = QtGui.QLabel(self)
        self.description_label.setGeometry(QtCore.QRect(11,11,428,25))
        self.description_label.setObjectName("description_label")

        self.speed_in_edit = QtGui.QLineEdit(self)
        self.speed_in_edit.setGeometry(QtCore.QRect(20,60,113,21))
        self.speed_in_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"[0-9]{1,}"), self))

        self.speed_out_edit = QtGui.QLineEdit(self)
        self.speed_out_edit.setGeometry(QtCore.QRect(220,60,113,21))
        self.speed_out_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"[0-9]{1,}"), self))

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)

        self.setTabOrder(self.speed_in_edit,self.in_postfix)
        self.setTabOrder(self.in_postfix,self.speed_out_edit)
        self.setTabOrder(self.speed_out_edit,self.out_postfix)
        self.setTabOrder(self.out_postfix,self.buttonBox)

        self.fixtures()
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_out_label.setText(QtGui.QApplication.translate("Dialog", "Исходящий", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_in_label.setText(QtGui.QApplication.translate("Dialog", "Входящий", None, QtGui.QApplication.UnicodeUTF8))
        self.in_postfix.addItem(QtGui.QApplication.translate("Dialog", "k", None, QtGui.QApplication.UnicodeUTF8))
        self.in_postfix.addItem(QtGui.QApplication.translate("Dialog", "M", None, QtGui.QApplication.UnicodeUTF8))
        self.out_postfix.addItem(QtGui.QApplication.translate("Dialog", "k", None, QtGui.QApplication.UnicodeUTF8))
        self.out_postfix.addItem(QtGui.QApplication.translate("Dialog", "M", None, QtGui.QApplication.UnicodeUTF8))
        self.description_label.setText("<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><span style=\" font-size:12pt; color:#000080;\">%s</span></p></body></html>" % self.title)
        
    def fixtures(self):
        if self.item=="" or self.item.rfind("/")==-1:
            return
        
        nodes = self.item.split("/")

        if nodes[0].endswith(u"k") or nodes[0].endswith(u"M"):
            self.in_postfix.setCurrentIndex(self.in_postfix.findText(nodes[0][-1], QtCore.Qt.MatchCaseSensitive))
            
            self.speed_in_edit.setText(nodes[0][0:-1])
        else:
            self.speed_in_edit.setText(nodes[0])
            
        if nodes[1].endswith(u"k") or nodes[1].endswith(u"M"):
            self.out_postfix.setCurrentIndex(self.in_postfix.findText(nodes[1][-1], QtCore.Qt.MatchCaseSensitive))
            self.speed_out_edit.setText(nodes[1][0:-1])
        else:
            self.speed_out_edit.setText(nodes[1])
            
            
    def accept(self): 
        if (self.speed_in_edit.text()=="" and self.in_postfix.currentText()=="") and (self.speed_out_edit.text()=="" and self.out_postfix.currentText()=="") :
            self.resultstring=""
        elif (self.speed_in_edit.text()!="" and self.speed_out_edit.text()=="") or (self.speed_in_edit.text()=="" and self.speed_out_edit.text()!=""):
            return
        elif self.speed_in_edit.text()!="" or  self.in_postfix.currentText()!="" or self.speed_out_edit.text()!="" or self.out_postfix.currentText()!="":     
            self.resultstring = "%s%s/%s%s" % (self.speed_in_edit.text(), self.in_postfix.currentText(), self.speed_out_edit.text(), self.out_postfix.currentText())
        QtGui.QDialog.accept(self)
        
class TransactionForm(QtGui.QDialog):
    def __init__(self, connection, model=None, account=None):
        super(TransactionForm, self).__init__()
        self.model = model
        self.account = account
        self.connection = connection
        
        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,385,166).size()).expandedTo(self.minimumSizeHint()))

        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setGeometry(QtCore.QRect(10,40,371,81))
        self.groupBox.setObjectName("groupBox")

        self.summ_edit = QtGui.QLineEdit(self.groupBox)
        self.summ_edit.setGeometry(QtCore.QRect(130,20,231,20))
        self.summ_edit.setObjectName("summ_edit")

        self.summ_label = QtGui.QLabel(self.groupBox)
        self.summ_label.setGeometry(QtCore.QRect(10,20,111,20))
        self.summ_label.setObjectName("summ_label")

        self.payed_document_edit = QtGui.QLineEdit(self.groupBox)
        self.payed_document_edit.setGeometry(QtCore.QRect(130,50,231,20))
        self.payed_document_edit.setFrame(True)
        self.payed_document_edit.setObjectName("payed_document_edit")

        self.payed_document_label = QtGui.QLabel(self.groupBox)
        self.payed_document_label.setGeometry(QtCore.QRect(10,50,115,20))
        self.payed_document_label.setObjectName("payed_document_label")

        self.pay_type_label = QtGui.QLabel(self)
        self.pay_type_label.setGeometry(QtCore.QRect(13,10,111,20))
        self.pay_type_label.setObjectName("pay_type_label")

        self.transactions_pushButton = QtGui.QPushButton(self)
        self.transactions_pushButton.setGeometry(QtCore.QRect(10,130,106,26))
        self.transactions_pushButton.setObjectName("transactions_pushButton")

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(210,130,167,26))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.payed_type_edit = QtGui.QComboBox(self)
        self.payed_type_edit.setGeometry(QtCore.QRect(140,10,241,20))
        self.payed_type_edit.setObjectName("payed_type_edit")


        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        
        QtCore.QObject.connect(self.transactions_pushButton,QtCore.SIGNAL("clicked()"),self.transactions_report)

    def retranslateUi(self):
        self.setWindowTitle(u"Новая проводка для %s" % self.account.username)
        self.payed_document_label.setText(QtGui.QApplication.translate("Dialog", "Платёжный документ", None, QtGui.QApplication.UnicodeUTF8))
        self.pay_type_label.setText(QtGui.QApplication.translate("Dialog", "Вид платежа", None, QtGui.QApplication.UnicodeUTF8))
        self.payed_type_edit.addItem(QtGui.QApplication.translate("Dialog", "Пополнить балланс", None, QtGui.QApplication.UnicodeUTF8))
        self.payed_type_edit.addItem(QtGui.QApplication.translate("Dialog", "Списать с балланса", None, QtGui.QApplication.UnicodeUTF8))
        self.summ_label.setText(QtGui.QApplication.translate("Dialog", "Сумма", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Платёжные данные", None, QtGui.QApplication.UnicodeUTF8))
        self.transactions_pushButton.setText(QtGui.QApplication.translate("Dialog", "История проводок", None, QtGui.QApplication.UnicodeUTF8))
    
    def accept(self):
        if self.payed_type_edit.currentText()==u"Пополнить балланс":
            self.result = int(self.summ_edit.text()) * (-1)
        else:
            self.result = int(self.summ_edit.text())
            
        QtGui.QDialog.accept(self)
        
    def transactions_report(self):
        if self.account:
            child = TransactionsReport(connection=self.connection, account = self.account)
            child.exec_()
            
class ConnectDialog(QtGui.QDialog):
    _connectsql = {}
    def __init__(self):
        super(ConnectDialog, self).__init__()
        
        self.setObjectName("MainWindow")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,341,280).size()).expandedTo(self.minimumSizeHint()))
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,341,280).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,341,280).size()))
        
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.encryption_checkBox = QtGui.QCheckBox(self.centralwidget)
        self.encryption_checkBox.setGeometry(QtCore.QRect(60,100,191,18))
        self.encryption_checkBox.setObjectName("encryption_checkBox")

        '''self.compress_checkbox = QtGui.QCheckBox(self.centralwidget)
        self.compress_checkbox.setGeometry(QtCore.QRect(60,124,191,18))
        self.compress_checkbox.setObjectName("compress_checkbox")'''

        self.connect_pushButton = QtGui.QPushButton(self.centralwidget)
        self.connect_pushButton.setGeometry(QtCore.QRect(260,10,75,24))
        self.connect_pushButton.setObjectName("connect_pushButton")

        self.remove_pushButton = QtGui.QPushButton(self.centralwidget)
        self.remove_pushButton.setGeometry(QtCore.QRect(260,124,75,24))
        self.remove_pushButton.setObjectName("remove_pushButton")

        self.save_checkBox = QtGui.QCheckBox(self.centralwidget)
        self.save_checkBox.setGeometry(QtCore.QRect(60,124,191,18))
        self.save_checkBox.setObjectName("save_checkBox")

        self.exit_pushButton = QtGui.QPushButton(self.centralwidget)
        self.exit_pushButton.setGeometry(QtCore.QRect(260,40,75,24))
        self.exit_pushButton.setObjectName("exit_pushButton")

        self.tableWidget = QtGui.QTableView(self.centralwidget)
        try:
            '''model = self.getModel("exbill_users")
            model.removeColumn(0)
            print model.record(0).value(1).toString()
            print "----------getmodel-------"
            model.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant("IP"))
            model.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant("Username"))
            self.tableWidget.setModel(model)
            print self.tableWidget.model().record(0).value(1).toString()'''
            '''self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
            self.db.setDatabaseName("exbillusers")
            self.db.open()
            self.model = QtSql.QSqlTableModel()
            self.model.setTable("exbill_users")
            self.model.select()
            self.model.removeColumn(0)
            self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
            self.model.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant("IP"))
            self.model.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant("Username"))
            self.tableWidget.setModel(self.model)
            self.tableWidget.setGeometry(QtCore.QRect(0,170,341,91))
            self.tableWidget.setObjectName("tableWidget")
            #self.tableWidget.setColumnHidden(0, True)
            #self.tableWidget = tableFormat(self.tableWidget)
            #self.tableWidget.update()
            self.tableWidget.show()'''
            self.model = self.getModel("exbill_users")
            #self.model.removeColumn(0)
            self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
            self.model.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant("IP"))
            self.model.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant("Username"))
            height = self.tableWidget.fontMetrics().height()
            self.tableWidget.verticalHeader().setDefaultSectionSize(height+3)
            self.tableWidget.setModel(self.model)
            self.tableWidget.setGeometry(QtCore.QRect(0,150,341,128))
            self.tableWidget.setObjectName("tableWidget")
            self.tableWidget = tableFormat(self.tableWidget)
            self.tableWidget.setColumnHidden(3, True)
            #self.tableWidget.setRowHeight(-1, 17)
            #self.tableWidget.resizeRowsToContents()
            self.tableWidget.setr
            self.tableWidget.show()
            self.twIndex = -1
            #columns = [u'IP', 'Username']
        except Exception, ex:
            print ex

        self.save_pushButton = QtGui.QPushButton(self.centralwidget)
        self.save_pushButton.setGeometry(QtCore.QRect(260,70,75,23))
        self.save_pushButton.setObjectName("save_pushButton")

        self.password_label = QtGui.QLabel(self.centralwidget)
        self.password_label.setGeometry(QtCore.QRect(11,70,41,20))
        self.password_label.setObjectName("password_label")

        self.password_edit = QtGui.QLineEdit(self.centralwidget)
        self.password_edit.setGeometry(QtCore.QRect(58,70,192,20))
        self.password_edit.setObjectName("password_edit")
        self.password_edit.setEchoMode(QtGui.QLineEdit.Password)

        self.name_edit = QtGui.QLineEdit(self.centralwidget)
        self.name_edit.setGeometry(QtCore.QRect(58,40,192,20))
        self.name_edit.setObjectName("name_edit")

        self.address_edit = QtGui.QLineEdit(self.centralwidget)
        self.address_edit.setGeometry(QtCore.QRect(58,11,192,20))
        self.address_edit.setObjectName("address_edit")

        self.name_label = QtGui.QLabel(self.centralwidget)
        self.name_label.setGeometry(QtCore.QRect(11,40,41,20))
        self.name_label.setObjectName("name_label")

        self.address_label = QtGui.QLabel(self.centralwidget)
        self.address_label.setGeometry(QtCore.QRect(11,11,41,20))
        self.address_label.setObjectName("address_label")
        #self.setCentralWidget(self.centralwidget)

        #self.statusbar = QtGui.QStatusBar(self)
        #self.statusbar.setObjectName("statusbar")
        #self.setStatusBar(self.statusbar)

        self.setTabOrder(self.address_edit,self.name_edit)
        self.setTabOrder(self.name_edit,self.password_edit)
        self.setTabOrder(self.password_edit,self.encryption_checkBox)
        #self.setTabOrder(self.encryption_checkBox,self.compress_checkbox)
        #self.setTabOrder(self.compress_checkbox,self.save_checkBox)
        self.setTabOrder(self.encryption_checkBox, self.save_checkBox)
        self.setTabOrder(self.save_checkBox,self.connect_pushButton)
        self.setTabOrder(self.connect_pushButton,self.exit_pushButton)
        self.setTabOrder(self.exit_pushButton,self.save_pushButton)
        self.setTabOrder(self.save_pushButton,self.remove_pushButton)
        self.setTabOrder(self.remove_pushButton,self.tableWidget)
        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)
        self.passRx = QtCore.QRegExp(r"^\w{3,}")
        self.passValidator = QtGui.QRegExpValidator(self.passRx, self)
        self.retranslateUi()
        self.fixtures()
        self.tableSelection = self.tableWidget.selectionModel()
        QtCore.QObject.connect(self.connect_pushButton, QtCore.SIGNAL("clicked()"), self.accept)
        QtCore.QObject.connect(self.exit_pushButton, QtCore.SIGNAL("clicked()"), self.reject)
        QtCore.QObject.connect(self.save_pushButton, QtCore.SIGNAL("clicked()"), self.save)
        QtCore.QObject.connect(self.remove_pushButton, QtCore.SIGNAL("clicked()"), self.remove)
        #QtCore.QObject.connect(self.tableSelection, QtCore.SIGNAL("selectionChanged(QModelIndex, QModelIndex)"), self.tableClicked)
        #self.connect(self.tableWidget, QtCore.SIGNAL("currentChanged(previous, current)"), QtCore.SLOT("self.tableClicked(self, previous, current)"))
        #QtCore.QObject.connect(self.tableWidget, QtCore.SIGNAL("clicked(const QModelIndex&)"), self.tableClicked)
        QtCore.QObject.connect(self.tableWidget, QtCore.SIGNAL("clicked(QModelIndex)"), self.tableClicked)
        #QtCore.QObject.connect(self.tableWidget, QtCore.SIGNAL("selectionChanged(const QModelIndex&, const QModelIndex&)"), )"), )"), self.tableClicked)
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Expert Billing Client", None, QtGui.QApplication.UnicodeUTF8))
        self.encryption_checkBox.setText(QtGui.QApplication.translate("MainWindow", "Использовать шифрование", None, QtGui.QApplication.UnicodeUTF8))
        #self.compress_checkbox.setText(QtGui.QApplication.translate("MainWindow", "Использовать сжатие", None, QtGui.QApplication.UnicodeUTF8))
        self.connect_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Connect", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.save_checkBox.setText(QtGui.QApplication.translate("MainWindow", "Запомнить", None, QtGui.QApplication.UnicodeUTF8))
        self.address_edit.setValidator(self.ipValidator)
        self.password_edit.setValidator(self.passValidator)
        self.exit_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        #self.tableWidget.clear()

        #makeHeaders(columns, self.tableWidget)
        
        self.save_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.password_label.setText(QtGui.QApplication.translate("MainWindow", "Пароль:", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("MainWindow", "Имя:", None, QtGui.QApplication.UnicodeUTF8))
        self.address_label.setText(QtGui.QApplication.translate("MainWindow", "Адрес:", None, QtGui.QApplication.UnicodeUTF8))

    def fixtures(self):
        self._password = ''
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            #print settings.value("ip", QtCore.QVariant(""))
            if settings.value("save", QtCore.QVariant("")).toBool:
                self.save_checkBox.setCheckState(QtCore.Qt.Checked)
            else: self.save_checkBox.setCheckState(QtCore.Qt.Unchecked)
                

            self._address = settings.value("ip", QtCore.QVariant("")).toString()
            self._name = settings.value("user", QtCore.QVariant("")).toString()
            self._password = settings.value("password", QtCore.QVariant("")).toByteArray()
            self.address_edit.setText(self._address)
            self.name_edit.setText(self._name)
            self.password_edit.setText("*******")
        except Exception, ex:
            print ex
        '''dbi = self.db.select("select * from exbill_users;")
        p1 = QtCore.QCryptographicHash.hash(QtCore.QString("arrgh").toUtf8(), QtCore.QCryptographicHash.Md5)
        p2 = dbi[4].value(3).toByteArray()
        print p1, p2
        print p1 == p2'''
        
    def getModel(self, table):
        self.db = sqliteDbAccess(connectDBName, 'system')
        if (self.db.filestat == 2) or (self.db.filestat == 4):
            self.db.action("CREATE TABLE exbill_users (ID INTEGER PRIMARY KEY, IP TEXT, Username TEXT, Password Text);", '')
        dbmodel = self.db.getTableModel(table)
        dbmodel.select()
        return dbmodel
    
    def accept(self):
        psd = self.passValidator.validate(self.password_edit.text(), 0)[0]
        try:
            self.password = ''

            if not ((self.ipValidator.validate(self.address_edit.text(), 0)[0] == QtGui.QValidator.Acceptable) and (self.name_edit)):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Введите адрес и имя пользователя"))
                return
            if (psd == QtGui.QValidator.Acceptable):
                self.password = QtCore.QCryptographicHash.hash(self.password_edit.text().toUtf8(), QtCore.QCryptographicHash.Md5)
            else:
                print "aaaa"
                print self._name
                print self.name_edit.text()
                if (self._name == self.name_edit.text()) and (self._address == self.address_edit.text()):
                    self.password = self._password
                else:
                    model = self.tableWidget.model()
                    for i in range(model.rowCount()):
                        if (model.record(i).value(2).toString() == self.name_edit.text()) and (model.record(i).value(1).toString() == self.address_edit.text()):
                            #print "zomg"
                            #print model.record(i).value(3).toUtf8()
                            self.password = model.record(i).value(3).toByteArray()
                            print self.password
                            break
                    if not self.password:
                        print self.password
                        QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Пароль не совпадает с именем пользователя"))
                        return
            
            self.address = self.address_edit.text()
            self.name    = self.name_edit.text()
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            if self.save_checkBox.isChecked() == True:
                settings.setValue("ip", QtCore.QVariant(self.address))
                settings.setValue("user", QtCore.QVariant(self.name))
                settings.setValue("password", QtCore.QVariant(self.password))                
            settings.setValue("save", QtCore.QVariant(self.save_checkBox.isChecked()))
            QtGui.QDialog.accept(self)
        except Exception, ex:
            print "accept error"
            print ex
    def save(self):
        try:
            if self.address_edit.text() and (self.ipValidator.validate(self.address_edit.text(), 0)[0]  == QtGui.QValidator.Acceptable):
                ip = self.address_edit.text()
            else:
                QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Введите адрес."))
                return
            if self.name_edit.text():
                name = self.name_edit.text()
            else:
                QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Введите имя."))
                return
            if self.password_edit.text():
                if self.passValidator.validate(self.password_edit.text(), 0)[0]  != QtGui.QValidator.Acceptable:
                    if self._password and (self._name == self.name_edit.text()) and (self._address == self.address_edit.text()):
                        password = self._password
                    else:
                        QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Пароль должен быть длиной минимум 3 символа и не содержать спецефических символов."))
                        return
                else: password = QtCore.QCryptographicHash.hash(self.password_edit.text().toUtf8(), QtCore.QCryptographicHash.Md5)
            else:
                QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Введите пароль."))
                return
            model = self.tableWidget.model()
            update = False
            row = -1
            try:
                if self.tableWidget.selectedIndexes():
                    if model.record(self.tableWidget.selectedIndexes()[0].row()).value(1).toString() == ip:
                        update = True
                        row = self.tableWidget.selectedIndexes()[0].row()
            except Exception, ex: print ex
                
            record = model.record()
            record.setValue(1, QtCore.QVariant(ip))
 
            record.setValue(2, QtCore.QVariant(name))

            record.setValue(3, QtCore.QVariant(password))
            if update:
                model.setRecord(row, record)
            else:
                model.insertRecord(row, record)
        except Exception, ex:
            raise Exception("Couln't save properly: " + str(ex))
        
    def remove(self):
        try:
            print "------------zomg"
            self.tableWidget.model().removeRow(self.tableWidget.selectedIndexes()[0].row())
        except Exception, ex:
            print ex
    
    def tableClicked(self, *args):
        #if args[0].row() != self.twIndex:
        try:
            selRec = self.tableWidget.model().record(args[0].row())
            self.address_edit.setText(selRec.value(1).toString())
            self.name_edit.setText(selRec.value(2).toString())
            self.password_edit.setText("*******")
            
        except Exception, ex:
            print ex
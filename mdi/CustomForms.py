#-*-coding=utf-8*-

import os
from PyQt4 import QtCore, QtGui, QtSql, QtWebKit
from Reports import TransactionsReport
from helpers import makeHeaders
from helpers import tableFormat
from helpers import tableHeight
from helpers import sqliteDbAccess, connectDBName
from helpers import Object
from helpers import dateDelim
from mako.template import Template
strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"

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
        self.selected_id = None
        
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
            self.comboBox.setItemData(i, QtCore.QVariant(item.id))
            if unicode(item.name) == unicode(self.selected_item):
                self.comboBox.setCurrentIndex(i)
                
            i+=1
            
    def accept(self):
        self.selected_id = self.comboBox.itemData(self.comboBox.currentIndex()).toInt()[0]
        QtGui.QDialog.accept(self)
        
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
        #self.parent = parent
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
        self.summ_edit.setValidator(QtGui.QDoubleValidator(self.summ_edit))

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

        self.pushButton_cheque_print = QtGui.QPushButton(self)
        self.pushButton_cheque_print.setGeometry(QtCore.QRect(10,130,106,26))
        self.pushButton_cheque_print.setObjectName("pushButton_cheque_print")

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
        
        QtCore.QObject.connect(self.pushButton_cheque_print,QtCore.SIGNAL("clicked()"),self.cheque_print)

    def retranslateUi(self):
        self.setWindowTitle(u"Новая проводка для %s" % self.account.username)
        self.payed_document_label.setText(QtGui.QApplication.translate("Dialog", "Платёжный документ", None, QtGui.QApplication.UnicodeUTF8))
        self.pay_type_label.setText(QtGui.QApplication.translate("Dialog", "Вид платежа", None, QtGui.QApplication.UnicodeUTF8))
        self.payed_type_edit.addItem(QtGui.QApplication.translate("Dialog", "Пополнить балланс", None, QtGui.QApplication.UnicodeUTF8))
        self.payed_type_edit.addItem(QtGui.QApplication.translate("Dialog", "Списать с балланса", None, QtGui.QApplication.UnicodeUTF8))
        self.summ_label.setText(QtGui.QApplication.translate("Dialog", "Сумма", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Платёжные данные", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_cheque_print.setText(QtGui.QApplication.translate("Dialog", "Печать чека", None, QtGui.QApplication.UnicodeUTF8))
    
    def accept(self):
        if self.payed_type_edit.currentText()==u"Пополнить балланс":
            self.result = int(self.summ_edit.text()) * (-1)
        else:
            self.result = int(self.summ_edit.text())
            
        QtGui.QDialog.accept(self)
        
    def cheque_print(self):
        if self.account:
            import datetime
            account = self.connection.get("SELECT * FROM billservice_account WHERE id=%s LIMIT 1" % self.account.id)
            #child = TransactionsReport(connection=self.connection, account = self.account)
            templ = Template(filename="templates/cheque.htm", input_encoding='utf-8')
            data=templ.render_unicode(account=account, sum=unicode(self.summ_edit.text()), document = unicode(self.payed_document_edit.text()), created=datetime.datetime.now().strftime(strftimeFormat))

            file= open('templates/tmp/cheque.html', 'wb')
            file.write(data.encode("utf-8", 'replace'))
            file.flush()
            a=CardPreviewDialog(url="templates/tmp/cheque.html")
            a.exec_()
            
            #print self.parentWidget().parent().workspace.addWindow(child)
            #self.parent().workspace.addWindow(child)
            #print "mainwindow", mainwindow
            #child.show()
            
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
        self.encryption_checkBox.setDisabled(True)
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
            #height = self.tableWidget.fontMetrics().height()
            #self.tableWidget.verticalHeader().setDefaultSectionSize(height+3)
            #print height
            self.tableWidget.verticalHeader().setDefaultSectionSize(tableHeight)
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
                if (self._name == self.name_edit.text()) and (self._address == self.address_edit.text()):
                    self.password = self._password
                else:
                    model = self.tableWidget.model()
                    for i in range(model.rowCount()):
                        if (model.record(i).value(2).toString() == self.name_edit.text()) and (model.record(i).value(1).toString() == self.address_edit.text()):
                            #print "zomg"
                            #print model.record(i).value(3).toUtf8()
                            self.password = model.record(i).value(3).toByteArray()
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

class OperatorDialog(QtGui.QDialog):
    def __init__(self, connection):
        super(OperatorDialog, self).__init__()
        self.connection = connection
        self.op_model = None
        self.bank_model = None
        self.setObjectName("Operator")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,573, 575).size()).expandedTo(self.minimumSizeHint()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,573, 575).size()))
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,573, 575).size()))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab1")
        self.groupBox_contact = QtGui.QGroupBox(self.tab)
        self.groupBox_contact.setGeometry(QtCore.QRect(10, 10, 531, 321))
        self.groupBox_contact.setObjectName("groupBox_contact")
        self.lineEdit_postaddress = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_postaddress.setGeometry(QtCore.QRect(120, 229, 383, 20))
        self.lineEdit_postaddress.setObjectName("lineEdit_postaddress")
        self.label_organization = QtGui.QLabel(self.groupBox_contact)
        self.label_organization.setGeometry(QtCore.QRect(9, 20, 111, 20))
        self.label_organization.setObjectName("label_organization")
        self.lineEdit_fax = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_fax.setGeometry(QtCore.QRect(120, 199, 191, 20))
        self.lineEdit_fax.setObjectName("lineEdit_fax")
        self.lineEdit_phone = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_phone.setGeometry(QtCore.QRect(120, 169, 191, 20))
        self.lineEdit_phone.setObjectName("lineEdit_phone")
        self.lineEdit_organization = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_organization.setGeometry(QtCore.QRect(120, 20, 381, 20))
        self.lineEdit_organization.setObjectName("lineEdit_organization")
        self.label_director = QtGui.QLabel(self.groupBox_contact)
        self.label_director.setGeometry(QtCore.QRect(9, 139, 111, 20))
        self.label_director.setObjectName("label_director")
        self.label_postaddress = QtGui.QLabel(self.groupBox_contact)
        self.label_postaddress.setGeometry(QtCore.QRect(9, 229, 111, 20))
        self.label_postaddress.setObjectName("label_postaddress")
        self.label_contactperson = QtGui.QLabel(self.groupBox_contact)
        self.label_contactperson.setGeometry(QtCore.QRect(9, 109, 111, 20))
        self.label_contactperson.setObjectName("label_contactperson")
        self.lineEdit_director = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_director.setGeometry(QtCore.QRect(120, 139, 381, 20))
        self.lineEdit_director.setObjectName("lineEdit_director")
        self.label_phone = QtGui.QLabel(self.groupBox_contact)
        self.label_phone.setGeometry(QtCore.QRect(9, 169, 111, 20))
        self.label_phone.setObjectName("label_phone")
        self.lineEdit_contactperson = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_contactperson.setGeometry(QtCore.QRect(120, 109, 381, 20))
        self.lineEdit_contactperson.setObjectName("lineEdit_contactperson")
        self.label_fax = QtGui.QLabel(self.groupBox_contact)
        self.label_fax.setGeometry(QtCore.QRect(9, 199, 111, 20))
        self.label_fax.setObjectName("label_fax")
        self.lineEdit_uraddress = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_uraddress.setGeometry(QtCore.QRect(120, 259, 383, 20))
        self.lineEdit_uraddress.setObjectName("lineEdit_uraddress")
        self.label_uraddress = QtGui.QLabel(self.groupBox_contact)
        self.label_uraddress.setGeometry(QtCore.QRect(10, 259, 111, 20))
        self.label_uraddress.setObjectName("label_uraddress")
        self.lineEdit_email = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_email.setGeometry(QtCore.QRect(120, 289, 381, 20))
        self.lineEdit_email.setObjectName("lineEdit_email")
        self.label_email = QtGui.QLabel(self.groupBox_contact)
        self.label_email.setGeometry(QtCore.QRect(10, 290, 111, 20))
        self.label_email.setObjectName("label_email")
        self.lineEdit_okpo = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_okpo.setGeometry(QtCore.QRect(120, 80, 191, 20))
        self.lineEdit_okpo.setObjectName("lineEdit_okpo")
        self.lineEdit_unp = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_unp.setGeometry(QtCore.QRect(120, 50, 191, 20))
        self.lineEdit_unp.setObjectName("lineEdit_unp")
        self.label_unp = QtGui.QLabel(self.groupBox_contact)
        self.label_unp.setGeometry(QtCore.QRect(9, 50, 111, 20))
        self.label_unp.setObjectName("label_unp")
        self.label_okpo = QtGui.QLabel(self.groupBox_contact)
        self.label_okpo.setGeometry(QtCore.QRect(9, 80, 111, 20))
        self.label_okpo.setObjectName("label_okpo")
        self.groupBox_bankdata = QtGui.QGroupBox(self.tab)
        self.groupBox_bankdata.setGeometry(QtCore.QRect(10, 340, 531, 141))
        self.groupBox_bankdata.setObjectName("groupBox_bankdata")
        self.label_rs = QtGui.QLabel(self.groupBox_bankdata)
        self.label_rs.setGeometry(QtCore.QRect(10, 80, 111, 20))
        self.label_rs.setObjectName("label_rs")
        self.label_bank = QtGui.QLabel(self.groupBox_bankdata)
        self.label_bank.setGeometry(QtCore.QRect(9, 20, 111, 20))
        self.label_bank.setObjectName("label_bank")
        self.lineEdit_rs = QtGui.QLineEdit(self.groupBox_bankdata)
        self.lineEdit_rs.setGeometry(QtCore.QRect(120, 80, 383, 20))
        self.lineEdit_rs.setObjectName("lineEdit_rs")
        self.lineEdit_bank = QtGui.QLineEdit(self.groupBox_bankdata)
        self.lineEdit_bank.setGeometry(QtCore.QRect(120, 20, 383, 20))
        self.lineEdit_bank.setObjectName("lineEdit_bank")
        self.lineEdit_bankcode = QtGui.QLineEdit(self.groupBox_bankdata)
        self.lineEdit_bankcode.setGeometry(QtCore.QRect(120, 50, 151, 20))
        self.lineEdit_bankcode.setObjectName("lineEdit_bankcode")
        self.label_bankcode = QtGui.QLabel(self.groupBox_bankdata)
        self.label_bankcode.setGeometry(QtCore.QRect(10, 50, 111, 16))
        self.label_bankcode.setObjectName("label_bankcode")
        self.lineEdit_currency = QtGui.QLineEdit(self.groupBox_bankdata)
        self.lineEdit_currency.setGeometry(QtCore.QRect(120, 110, 151, 23))
        self.lineEdit_currency.setObjectName("lineEdit_currency")
        self.label_ = QtGui.QLabel(self.groupBox_bankdata)
        self.label_.setGeometry(QtCore.QRect(10, 110, 111, 18))
        self.label_.setObjectName("label_")
        self.tabWidget.addTab(self.tab, "tab1")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.setLayout(self.gridLayout)
        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        self.fixtures()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        #QtCore.QMetaObject.connectSlotsByName()
        self.setTabOrder(self.tabWidget, self.lineEdit_organization)
        self.setTabOrder(self.lineEdit_organization, self.lineEdit_unp)
        self.setTabOrder(self.lineEdit_unp, self.lineEdit_okpo)
        self.setTabOrder(self.lineEdit_okpo, self.lineEdit_contactperson)
        self.setTabOrder(self.lineEdit_contactperson, self.lineEdit_director)
        self.setTabOrder(self.lineEdit_director, self.lineEdit_phone)
        self.setTabOrder(self.lineEdit_phone, self.lineEdit_fax)
        self.setTabOrder(self.lineEdit_fax, self.lineEdit_postaddress)
        self.setTabOrder(self.lineEdit_postaddress, self.lineEdit_uraddress)
        self.setTabOrder(self.lineEdit_uraddress, self.lineEdit_email)
        self.setTabOrder(self.lineEdit_email, self.lineEdit_bank)
        self.setTabOrder(self.lineEdit_bank, self.lineEdit_bankcode)
        self.setTabOrder(self.lineEdit_bankcode, self.lineEdit_rs)
        self.setTabOrder(self.lineEdit_rs, self.lineEdit_currency)
        self.setTabOrder(self.lineEdit_currency, self.buttonBox)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Operator", "Настройки системы", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_contact.setTitle(QtGui.QApplication.translate("Operator", "Контактные данные", None, QtGui.QApplication.UnicodeUTF8))
        self.label_organization.setText(QtGui.QApplication.translate("Operator", "Организация", None, QtGui.QApplication.UnicodeUTF8))
        self.label_director.setText(QtGui.QApplication.translate("Operator", "ФИО директора", None, QtGui.QApplication.UnicodeUTF8))
        self.label_postaddress.setText(QtGui.QApplication.translate("Operator", "Почтовый адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_contactperson.setText(QtGui.QApplication.translate("Operator", "Контактное лицо", None, QtGui.QApplication.UnicodeUTF8))
        self.label_phone.setText(QtGui.QApplication.translate("Operator", "Телефон", None, QtGui.QApplication.UnicodeUTF8))
        self.label_fax.setText(QtGui.QApplication.translate("Operator", "Факс", None, QtGui.QApplication.UnicodeUTF8))
        self.label_uraddress.setText(QtGui.QApplication.translate("Operator", "Юридический адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_email.setText(QtGui.QApplication.translate("Operator", "E-mail", None, QtGui.QApplication.UnicodeUTF8))
        self.label_unp.setText(QtGui.QApplication.translate("Operator", "УНП", None, QtGui.QApplication.UnicodeUTF8))
        self.label_okpo.setText(QtGui.QApplication.translate("Operator", "ОКПО", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_bankdata.setTitle(QtGui.QApplication.translate("Operator", "Банковские реквизиты", None, QtGui.QApplication.UnicodeUTF8))
        self.label_rs.setText(QtGui.QApplication.translate("Operator", "Р/с", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bank.setText(QtGui.QApplication.translate("Operator", "Банк", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bankcode.setText(QtGui.QApplication.translate("Operator", "Код банка", None, QtGui.QApplication.UnicodeUTF8))
        self.label_.setText(QtGui.QApplication.translate("Operator", "Валюта расчётов", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("Operator", "Данные о организации", None, QtGui.QApplication.UnicodeUTF8))

    def fixtures(self):
        try:
            self.op_model =self.connection.get("SELECT * FROM billservice_operator LIMIT 1;")
        except Exception, e:
            print e
            return
        try:
            self.bank_model=self.connection.get("SELECT * FROM billservice_bankdata WHERE id=%d" % self.op_model.bank_id)
        except Exception, e:
            print e
            return
            
        self.lineEdit_organization.setText(self.op_model.organization)
        self.lineEdit_okpo.setText(self.op_model.okpo)
        self.lineEdit_unp.setText(self.op_model.unp)
        self.lineEdit_contactperson.setText(self.op_model.contactperson)
        self.lineEdit_director.setText(self.op_model.director)
        self.lineEdit_phone.setText(self.op_model.phone)
        self.lineEdit_fax.setText(self.op_model.fax)
        self.lineEdit_postaddress.setText(self.op_model.postaddress)
        self.lineEdit_uraddress.setText(self.op_model.uraddress)
        self.lineEdit_email.setText(self.op_model.email)
        
        self.lineEdit_bank.setText(self.bank_model.bank)
        self.lineEdit_bankcode.setText(self.bank_model.bankcode)
        self.lineEdit_rs.setText(self.bank_model.rs)
        self.lineEdit_currency.setText(self.bank_model.currency)
        
    def accept(self):
        if self.op_model:
            op_model = self.op_model
        else:
            op_model = Object()
            
        if self.bank_model:
            bank_model = self.bank_model
        else:
            bank_model = Object()
        
        bank_model.bank = unicode(self.lineEdit_bank.text())
        bank_model.bankcode = unicode(self.lineEdit_bankcode.text())
        bank_model.rs = unicode(self.lineEdit_rs.text())
        bank_model.currency = unicode(self.lineEdit_currency.text())

        try:
            self.bank_model.id = self.connection.save(bank_model.save("billservice_bankdata"))
        except Exception, e:
            print e
            self.connection.rollback()
            QtGui.QMessageBox.warning(self, u"Ошибка!",
                                u"Невозможно сохранить данные!")
            return
        print "bank_id", self.bank_model.id
        
        op_model.organization = unicode(self.lineEdit_organization.text())
        op_model.okpo = unicode(self.lineEdit_okpo.text())
        op_model.unp = unicode(self.lineEdit_unp.text())
        op_model.contactperson = unicode(self.lineEdit_contactperson.text())
        op_model.director = unicode(self.lineEdit_director.text())
        op_model.phone = unicode(self.lineEdit_phone.text())
        op_model.fax = unicode(self.lineEdit_fax.text())
        op_model.postaddress = unicode(self.lineEdit_postaddress.text())
        op_model.uraddress = unicode(self.lineEdit_uraddress.text())
        op_model.email = unicode(self.lineEdit_email.text())
        op_model.bank_id = self.bank_model.id
        
        


        try:
            self.connection.create(op_model.save("billservice_operator"))
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()
            QtGui.QMessageBox.warning(self, u"Ошибка!",
                                u"Невозможно сохранить данные об организации!")
            return


        QtGui.QDialog.accept(self)
        
class ConnectionWaiting(QtGui.QDialog):
    def __init__(self):
        super(ConnectionWaiting, self).__init__()
        self.setObjectName("ConnectionWaiting")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,199,66).size()).expandedTo(self.minimumSizeHint()))
        self.setMinimumSize(QtCore.QSize(199,66))
        self.setMaximumSize(QtCore.QSize(199,66))
        #self.setModal(True)

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(10,30,181,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")

        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(10,6,181,20))
        self.label.setObjectName("label")

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        #QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Подключение...", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Подключаемся", None, QtGui.QApplication.UnicodeUTF8))
        
class CardPreviewDialog(QtGui.QDialog):
    def __init__(self, url):
        super(CardPreviewDialog, self).__init__()
        self.setObjectName("CardPreviewDialog")
        #self.filelist=[]
        self.url = url
        self.setObjectName("Dialog")
        self.resize(472, 636)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.webView = QtWebKit.QWebView(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.webView.sizePolicy().hasHeightForWidth())
        self.webView.setSizePolicy(sizePolicy)
        self.webView.setUrl(QtCore.QUrl("about:blank"))
        self.webView.setObjectName("webView")
        self.verticalLayout.addWidget(self.webView)
        self.commandLinkButton_print = QtGui.QCommandLinkButton(self)
        self.commandLinkButton_print.setMinimumSize(QtCore.QSize(0, 40))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/printer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.commandLinkButton_print.setIcon(icon)
        self.commandLinkButton_print.setObjectName("commandLinkButton_print")
        self.verticalLayout.addWidget(self.commandLinkButton_print)
        
        QtCore.QObject.connect(self.commandLinkButton_print, QtCore.SIGNAL("clicked()"), self.printCard)

        self.retranslateUi()
        self.fixtures()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Предпросмотр", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_print.setText(QtGui.QApplication.translate("Dialog", "Печатать", None, QtGui.QApplication.UnicodeUTF8))
        #self.fixtures()
        #QtCore.QMetaObject.connectSlotsByName()
        
    def fixtures(self):
        lfurl = QtCore.QUrl.fromLocalFile(os.path.abspath(self.url))
        self.webView.load(lfurl)
        #self.webView.settings().setAttribute(QtWebKit.QWebSettings.PrintBackgrounds, True)
        #self.webView.settings().setShouldPrintBackground(True)
        
    def printCard(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        #printer.setResolution(120)
        printer.setPageSize(QtGui.QPrinter.A4)
        dialog = QtGui.QPrintDialog(printer, self)
        dialog.setWindowTitle(self.tr("Print Document"))
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return
        printer.setFullPage(True)
        #printer.setResolution(120)
        #printer.setOutputFileName("lol.pdf")
        #print printer.resolution()
        self.webView.print_(printer)
                            
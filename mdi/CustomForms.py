#-*-coding=utf-8*-

import os, sys
from PyQt4 import QtCore, QtGui, QtSql, QtWebKit
from Reports import TransactionsReport
from helpers import makeHeaders
from helpers import tableFormat
from helpers import tableHeight
from helpers import sqliteDbAccess, connectDBName , get_free_addreses_from_pool
from db import Object as Object
from helpers import dateDelim
from mako.template import Template

strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
import datetime
from decimal import Decimal
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
        
        #print self.selected_items
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
            try:
                if unicode(item.id) == unicode(self.selected_item):
                    self.comboBox.setCurrentIndex(i)
            except:
                pass
                 
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
        
        self.resize(399, 275)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pay_type_label = QtGui.QLabel(self)
        self.pay_type_label.setObjectName("pay_type_label")
        self.gridLayout_2.addWidget(self.pay_type_label, 0, 0, 1, 1)
        self.payed_type_edit = QtGui.QComboBox(self)
        self.payed_type_edit.setObjectName("payed_type_edit")
        self.gridLayout_2.addWidget(self.payed_type_edit, 0, 1, 1, 2)
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.summ_label = QtGui.QLabel(self.groupBox)
        self.summ_label.setObjectName("summ_label")
        self.gridLayout.addWidget(self.summ_label, 0, 0, 1, 1)
        self.summ_edit = QtGui.QLineEdit(self.groupBox)
        self.summ_edit.setObjectName("summ_edit")
        self.gridLayout.addWidget(self.summ_edit, 0, 1, 1, 1)
        self.payed_document_label = QtGui.QLabel(self.groupBox)
        self.payed_document_label.setObjectName("payed_document_label")
        self.gridLayout.addWidget(self.payed_document_label, 1, 0, 1, 1)
        self.payed_document_edit = QtGui.QLineEdit(self.groupBox)
        self.payed_document_edit.setFrame(True)
        self.payed_document_edit.setObjectName("payed_document_edit")
        self.gridLayout.addWidget(self.payed_document_edit, 1, 1, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.lineEdit = QtGui.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 2, 1, 1, 1)
        self.label_paymend_date = QtGui.QLabel(self.groupBox)
        self.label_paymend_date.setObjectName("label_paymend_date")
        self.gridLayout.addWidget(self.label_paymend_date, 3, 0, 1, 1)
        self.dateTimeEdit_paymend_date = QtGui.QDateTimeEdit(self.groupBox)
        self.dateTimeEdit_paymend_date.setFrame(True)
        self.dateTimeEdit_paymend_date.setDateTime(QtCore.QDateTime(QtCore.QDate(2009, 1, 1), QtCore.QTime(0, 0, 0)))
        self.dateTimeEdit_paymend_date.setCalendarPopup(True)
        self.dateTimeEdit_paymend_date.setObjectName("dateTimeEdit_paymend_date")
        self.gridLayout.addWidget(self.dateTimeEdit_paymend_date, 3, 1, 1, 1)
        self.label_promise = QtGui.QLabel(self.groupBox)
        self.label_promise.setObjectName("label_promise")
        self.gridLayout.addWidget(self.label_promise, 4, 0, 1, 1)
        self.checkBox_temporary_blocked_promise = QtGui.QCheckBox(self.groupBox)
        self.checkBox_temporary_blocked_promise.setObjectName("checkBox_promise")
        self.gridLayout.addWidget(self.checkBox_temporary_blocked_promise, 4, 1, 1, 1)
        self.label_end_promise = QtGui.QLabel(self.groupBox)
        self.label_end_promise.setObjectName("label_end_promise")
        self.gridLayout.addWidget(self.label_end_promise, 5, 0, 1, 1)
        self.dateTimeEdit_end_promise = QtGui.QDateTimeEdit(self.groupBox)
        self.dateTimeEdit_end_promise.setCalendarPopup(True)
        self.dateTimeEdit_end_promise.setObjectName("dateTimeEdit_end_promise")
        self.gridLayout.addWidget(self.dateTimeEdit_end_promise, 5, 1, 1, 1)
        self.checkBox_temporary_blocked_promise_infinite = QtGui.QCheckBox(self.groupBox)
        self.checkBox_temporary_blocked_promise_infinite.setObjectName("checkBox_promise_infinite")
        self.gridLayout.addWidget(self.checkBox_temporary_blocked_promise_infinite, 5, 2, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 1, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 2, 2, 1, 1)


        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        QtCore.QObject.connect(self.checkBox_temporary_blocked_promise,QtCore.SIGNAL("stateChanged(int)"),self.promise_actions)
        QtCore.QObject.connect(self.checkBox_temporary_blocked_promise_infinite,QtCore.SIGNAL("stateChanged(int)"),self.promise_actions)
        
        #QtCore.QObject.connect(self.pushButton_cheque_print,QtCore.SIGNAL("clicked()"),self.cheque_print)
        
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        self._name = settings.value("user", QtCore.QVariant("")).toString()
        if self._name:
            self.systemuser_id = self.connection.sql("SELECT id FROM billservice_systemuser WHERE username='%s'" % self._name)[0].id
            self.connection.commit()

        self.fixtures()
        self.promise_actions()
    def retranslateUi(self):
        self.setWindowTitle(u"Новая проводка для %s" % self.account.username)
        self.pay_type_label.setText(QtGui.QApplication.translate("Dialog", "Вид платежа", None, QtGui.QApplication.UnicodeUTF8))
        self.payed_type_edit.addItem(QtGui.QApplication.translate("Dialog", "Пополнить балланс", None, QtGui.QApplication.UnicodeUTF8))
        self.payed_type_edit.addItem(QtGui.QApplication.translate("Dialog", "Списать с балланса", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Платёжные данные", None, QtGui.QApplication.UnicodeUTF8))
        self.summ_label.setText(QtGui.QApplication.translate("Dialog", "Сумма", None, QtGui.QApplication.UnicodeUTF8))
        self.payed_document_label.setText(QtGui.QApplication.translate("Dialog", "На основании док.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Комментарий", None, QtGui.QApplication.UnicodeUTF8))
        self.label_paymend_date.setText(QtGui.QApplication.translate("Dialog", "Дата платежа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_promise.setText(QtGui.QApplication.translate("Dialog", "Обещаный платёж", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_temporary_blocked_promise.setText(QtGui.QApplication.translate("Dialog", "Да", None, QtGui.QApplication.UnicodeUTF8))
        self.label_end_promise.setText(QtGui.QApplication.translate("Dialog", "Истекает", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_temporary_blocked_promise_infinite.setText(QtGui.QApplication.translate("Dialog", "Никогда", None, QtGui.QApplication.UnicodeUTF8))
    
    def fixtures(self):
        now = datetime.datetime.now()
        self.dateTimeEdit_paymend_date.setDateTime(now)
        self.dateTimeEdit_end_promise.setDateTime(now)
    
        self.payed_type_edit.setItemData(0, QtCore.QVariant(0))
        self.payed_type_edit.setItemData(1, QtCore.QVariant(1))
        
    def promise_actions(self):
        if self.checkBox_temporary_blocked_promise.isChecked():
            self.dateTimeEdit_end_promise.setEnabled(True)
            self.checkBox_temporary_blocked_promise_infinite.setEnabled(True)
            if self.checkBox_temporary_blocked_promise_infinite.isChecked():
                self.dateTimeEdit_end_promise.setEnabled(False)
            
        else:
            self.dateTimeEdit_end_promise.setEnabled(False)
            self.checkBox_temporary_blocked_promise_infinite.setEnabled(False)
            
    def accept(self):
        #print self.payed_type_edit.itemData(self.payed_type_edit.currentIndex()).toInt()[0]
        if self.payed_type_edit.itemData(self.payed_type_edit.currentIndex()).toInt()[0]==0:
            self.result = Decimal("%s" % self.summ_edit.text()) * (-1)
        else:
            self.result = Decimal("%s" % self.summ_edit.text())
        
        transaction = Object()
        transaction.account_id=self.account.id
        transaction.type_id = "MANUAL_TRANSACTION"
        transaction.approved = True
        transaction.description = unicode(self.lineEdit.text())
        transaction.summ=self.result
        transaction.bill=unicode(self.payed_document_edit.text())
        transaction.systemuser_id = self.systemuser_id
        transaction.created = self.dateTimeEdit_paymend_date.dateTime().toPyDateTime()
        
        transaction.promise = self.checkBox_temporary_blocked_promise.isChecked()
        if self.checkBox_temporary_blocked_promise.isChecked() and not self.checkBox_temporary_blocked_promise_infinite.isChecked():
            transaction.end_promise = self.dateTimeEdit_end_promise.dateTime().toPyDateTime()

            
        try:
            
            self.connection.save(transaction, "billservice_transaction")
            self.connection.commit()
        except Exception, e:
            print "Exception", e
            self.connection.rollback()
        QtGui.QDialog.accept(self)
        
    def cheque_print(self):
        if self.account:
            template = self.connection.get('SELECT body FROM billservice_template WHERE type_id=5')
            templ = Template(unicode(template.body), input_encoding='utf-8')
            account = self.connection.get("SELECT * FROM billservice_account WHERE id=%s LIMIT 1" % self.account.id)

            tarif = self.connection.get("SELECT name FROM billservice_tariff WHERE id=get_tarif(%s)" % account.id)
            self.connection.commit()
            sum = 10000

            data=templ.render_unicode(account=account, tarif=tarif, sum=unicode(self.summ_edit.text()), document = unicode(self.payed_document_edit.text()), created=datetime.datetime.now().strftime(strftimeFormat))

            file= open('templates/tmp/temp.html', 'wb')
            file.write(data.encode("utf-8", 'replace'))
            file.flush()
            a=CardPreviewDialog(url="templates/tmp/temp.html")
            a.exec_()

            
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
        self.encryption_checkBox.setChecked(True)
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

        self.model = self.getModel("exbill_users")

        #self.model.removeColumn(0)
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant("IP"))
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant("Username"))

        self.tableWidget.verticalHeader().setDefaultSectionSize(tableHeight)
        self.tableWidget.setModel(self.model)
        self.tableWidget.setGeometry(QtCore.QRect(0,150,341,128))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)
        self.tableWidget.setColumnHidden(3, True)

        
        self.tableWidget.show()
        self.twIndex = -1

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
        #self.address_edit.setValidator(self.ipValidator) <-НЕ ТРОГАТЬ! Там этот валидатор не нужен
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
            print >>sys.stderr, ex
        '''dbi = self.db.select("select * from exbill_users;")
        p1 = QtCore.QCryptographicHash.hash(QtCore.QString("arrgh").toUtf8(), QtCore.QCryptographicHash.Md5)
        p2 = dbi[4].value(3).toByteArray()
        print p1, p2
        print p1 == p2'''
        
    def getModel(self, table):
        
        self.db = sqliteDbAccess(connectDBName, 'system')
        #sys.stdin=sys.stderr
        #print >>sys.stderr, "db", self.db, (self.db.filestat == 2) or (self.db.filestat == 4)
        if (self.db.filestat == 2) or (self.db.filestat == 4):
            self.db.action("CREATE TABLE exbill_users (ID INTEGER PRIMARY KEY, IP TEXT, Username TEXT, Password Text);", '')
        dbmodel = self.db.getTableModel(table)
        dbmodel.select()
        #print >>sys.stderr, dbmodel, table
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
                        QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Введите пароль"))
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
            #self.password_edit.setText("*******")
            
        except Exception, ex:
            print ex

class OperatorDialog(QtGui.QDialog):
    def __init__(self, connection):
        super(OperatorDialog, self).__init__()
        self.connection = connection
        self.connection.commit()
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
#        self.op_model = self.connection.get_model(1, "billservice_operator")
        try:
            self.op_model =self.connection.get_operator()[0]
            #print self.op_model
            try:
                self.bank_model=self.connection.get_bank_for_operator(self.op_model.id)
            except:
                pass
            self.connection.commit()
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
        
        except Exception, e:
            print e
            
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
            bank_model.id = self.connection.save(bank_model,"billservice_bankdata")
            self.bank_model = bank_model
        except Exception, e:
            print e
            self.connection.rollback()
            QtGui.QMessageBox.warning(self, u"Ошибка!",
                                u"Невозможно сохранить данные!")
            return
        #print "bank_id", self.bank_model.id
        
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
            self.connection.save(op_model,"billservice_operator")
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
    def __init__(self, url, printer=None):
        super(CardPreviewDialog, self).__init__()
        self.setObjectName("CardPreviewDialog")
        #self.filelist=[]
        self.url = url
        self.printer = printer
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
        self.webView.setUrl(QtCore.QUrl.fromLocalFile(os.path.abspath(self.url)))
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
        #self.fixtures()
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
        if not self.printer:
            printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
            printer.setPageSize(QtGui.QPrinter.A4)
            dialog = QtGui.QPrintDialog(printer, self)
            dialog.setWindowTitle(self.tr("Print Document"))
            if dialog.exec_() != QtGui.QDialog.Accepted:
                return
            printer.setFullPage(True)
        else:
            printer = self.printer

        self.webView.print_(printer)

class tableImageWidget(QtGui.QWidget):
    def __init__(self, nops=True, balance_blocked=False, trafic_limit=False, ipn_status=False, ipn_added=False):
        super(tableImageWidget,self).__init__()
        
        #self.resize(78, 20)
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout.setMargin(0)

        self.toolButton_balance_blocked = QtGui.QToolButton(self)
        self.toolButton_balance_blocked.setMinimumSize(QtCore.QSize(17, 17))
        self.toolButton_balance_blocked.setMaximumSize(QtCore.QSize(17, 17))
        

        self.toolButton_balance_blocked.resize(17,17)
        self.horizontalLayout.addWidget(self.toolButton_balance_blocked)
        
        self.toolButton_trafic_limit = QtGui.QToolButton(self)
        self.toolButton_trafic_limit.setMinimumSize(QtCore.QSize(17, 17))
        self.toolButton_trafic_limit.setMaximumSize(QtCore.QSize(17, 17))
        self.toolButton_trafic_limit.resize(17,17)
        self.horizontalLayout.addWidget(self.toolButton_trafic_limit)

        self.toolButton_ipn_status = QtGui.QToolButton(self)
        self.toolButton_ipn_status.setMinimumSize(QtCore.QSize(17, 17))
        self.toolButton_ipn_status.setMaximumSize(QtCore.QSize(17, 17))
        self.toolButton_ipn_status.resize(17,17)
        self.horizontalLayout.addWidget(self.toolButton_ipn_status)
        
        self.toolButton_ipn_added = QtGui.QToolButton(self)
        self.toolButton_ipn_added.setMinimumSize(QtCore.QSize(17, 17))
        self.toolButton_ipn_added.setMaximumSize(QtCore.QSize(17, 17))
        self.toolButton_ipn_added.resize(17,17)
        self.horizontalLayout.addWidget(self.toolButton_ipn_added)

    
        if balance_blocked==True:
            self.toolButton_balance_blocked.setIcon(QtGui.QIcon("images/money_false.png"))
            self.toolButton_balance_blocked.setToolTip(u"На счету недостаточно средств для активации пользователя в этом расчётном периоде")
        else:
            self.toolButton_balance_blocked.setIcon(QtGui.QIcon("images/money_true.png"))
            self.toolButton_balance_blocked.setToolTip(u"На счету достаточно средств")
        
        if trafic_limit==True: 
            self.toolButton_trafic_limit.setIcon(QtGui.QIcon("images/false.png"))
            self.toolButton_trafic_limit.setToolTip(u"Пользователь исчерпал лимит трафика")
        else:
            self.toolButton_trafic_limit.setIcon(QtGui.QIcon("images/ok.png"))
            self.toolButton_trafic_limit.setToolTip(u"Пользователь не исчерпал лимит трафика")

        if ipn_status==True: 
            self.toolButton_ipn_status.setIcon(QtGui.QIcon("images/ok.png"))
            self.toolButton_ipn_status.setToolTip(u"Пользователь активен в ACL на NAS")
        else:
            self.toolButton_ipn_status.setIcon(QtGui.QIcon("images/false.png"))
            self.toolButton_ipn_status.setToolTip(u"Пользователь не активен в ACL на NAS")
            

        if ipn_added==True: 
            self.toolButton_ipn_added.setIcon(QtGui.QIcon("images/ok.png"))
            self.toolButton_ipn_added.setToolTip(u"Пользователь добавлен в ACL на NAS")
        else:
            self.toolButton_ipn_added.setIcon(QtGui.QIcon("images/false.png"))
            self.toolButton_ipn_added.setToolTip(u"Пользователь не добавлен в ACL на NAS")
            
                            
class CustomWidget(QtGui.QTableWidgetItem):
    def __init__(self, parent, models, *args, **kwargs):
        super(CustomWidget, self).__init__()
        self.models=models
        label=""
        for model in models:
            if "passthrough" in model.__dict__:
                if  model.passthrough==True:
                    label += "%s(passthrough)\n" % model.name
                else:
                    label += "%s \n" % model.name
            else:
                label += "%s \n" % model.name
        
        self.setText(label)
        
class TemplatesWindow(QtGui.QMainWindow):
    def __init__(self, connection):
        super(TemplatesWindow, self).__init__()
        self.connection = connection
        self.setObjectName("MainWindow")
        self.resize(891, 583)
        self.setIconSize(QtCore.QSize(18, 18))
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.treeWidget = QtGui.QTreeWidget(self.centralwidget)
        self.treeWidget.setMaximumSize(QtCore.QSize(250, 16777215))
        self.treeWidget.setObjectName("treeWidget")
        tree_header = self.treeWidget.headerItem()
        sz = QtCore.QSize()
        hght = 17
        sz.setHeight(hght)
        tree_header.setSizeHint(0,sz)

        self.titles = ['',u'Договор на подключение для физ. лиц',
                  u'Договор на подключение для юр. лиц',
                  u'Счет-фактура',
                  u'Акт выполненных работ',
                  u'Кассовый чек',
                  u'Накладная на карты экспресс оплаты',
                  u'Карты экспресс-оплаты',
                  ]
        
        self.gridLayout.addWidget(self.treeWidget, 0, 0, 2, 1)
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.lineEdit_name = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit_name.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.gridLayout.addWidget(self.lineEdit_name, 0, 2, 1, 1)
        self.textBrowser_remplate_body = QtGui.QTextBrowser(self.centralwidget)
        #self.textBrowser_remplate_body = QtGui.QTextEdit(self.centralwidget)
        #self.textBrowser_remplate_body.setFrameShape(QtGui.QFrame.StyledPanel)
        #self.textBrowser_remplate_body.setFrameShadow(QtGui.QFrame.Sunken)
        #self.textBrowser_remplate_body.setLineWidth(1)
        self.textBrowser_remplate_body.setUndoRedoEnabled(True)
        self.textBrowser_remplate_body.setReadOnly(False)
        self.textBrowser_remplate_body.setAcceptRichText(False)
        self.textBrowser_remplate_body.setOpenLinks(False)
        self.textBrowser_remplate_body.setObjectName("textBrowser_remplate_body")
        self.gridLayout.addWidget(self.textBrowser_remplate_body, 1, 1, 1, 2)
        self.setCentralWidget(self.centralwidget)
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setAllowedAreas(QtCore.Qt.TopToolBarArea)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setFloatable(False)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.statusBar = QtGui.QStatusBar(self)
        self.statusBar.setObjectName("statusBar")
        self.setStatusBar(self.statusBar)
        self.actionAddTemplate = QtGui.QAction(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAddTemplate.setIcon(icon)
        self.actionAddTemplate.setObjectName("actionAddTemplate")
        self.actionDeleteTemplate = QtGui.QAction(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/del.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDeleteTemplate.setIcon(icon1)
        self.actionDeleteTemplate.setObjectName("actionDeleteTemplate")
        self.actionSave = QtGui.QAction(self)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave.setIcon(icon2)
        self.actionSave.setObjectName("actionSave")
        self.actionPreview = QtGui.QAction(self)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("images/preview.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPreview.setIcon(icon3)
        self.actionPreview.setObjectName("actionPreview")
        self.toolBar.addAction(self.actionAddTemplate)
        self.toolBar.addAction(self.actionDeleteTemplate)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionPreview)

        
        self.connect(self.treeWidget, QtCore.SIGNAL("currentItemChanged(QTreeWidgetItem *,QTreeWidgetItem *)"), self.editTemplate)
        self.connect(self.actionSave, QtCore.SIGNAL("triggered()"), self.saveTemplate)
        self.connect(self.actionPreview, QtCore.SIGNAL("triggered()"), self.preview)
        self.connect(self.actionAddTemplate, QtCore.SIGNAL("triggered()"), self.addCardTemplate)
        self.connect(self.actionDeleteTemplate, QtCore.SIGNAL("triggered()"), self.delCardTemplate)
        
        self.retranslateUi()
        self.refresh()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Шаблоны", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(0, QtGui.QApplication.translate("MainWindow", "Шаблоны", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Название шаблона", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAddTemplate.setText(QtGui.QApplication.translate("MainWindow", "Добавить шаблон", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDeleteTemplate.setText(QtGui.QApplication.translate("MainWindow", "Удалить шаблон", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setText(QtGui.QApplication.translate("MainWindow", "Сохранить", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreview.setText(QtGui.QApplication.translate("MainWindow", "Предпросмотр", None, QtGui.QApplication.UnicodeUTF8))
        
        
    def addCardTemplate(self):
        model = Object()
        model.type_id = 7
        item = QtGui.QTreeWidgetItem(self.treeWidget)
        item.model = model
        self.lineEdit_name.clear()
        self.textBrowser_remplate_body.clear()
        self.treeWidget.setCurrentItem(item)

    def delCardTemplate(self):
        model = self.treeWidget.currentItem().model
        if model.type_id==7:
            self.connection.iddelete(model.id, "billservice_template")
            self.connection.commit()
            self.refresh()
            self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(0))
    
    def editTemplate(self, item1, item2):
        
        try:
            model = self.treeWidget.currentItem().model
            id = model.id
        except:
            return
        self.textBrowser_remplate_body.clear()


        template = self.connection.get_model(model.id, "billservice_template")
        self.connection.commit()
        
        self.treeWidget.currentItem().model = template
        if template:
            self.lineEdit_name.setText(unicode(template.name))
            self.textBrowser_remplate_body.setPlainText(template.body)
            

        elif template.type_id!=7 and not template:
            self.lineEdit_name.setText(unicode(''))
            self.textBrowser_remplate_body.setPlainText("""<html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            </head>
            <body>
            
            
            
            </body>
            </html>""")
        elif id==7 and not template:
            self.lineEdit_name.setText(unicode(''))
            self.textBrowser_remplate_body.setPlainText("""<br />""")            
 

            
    
    def saveTemplate(self):
        if self.treeWidget.currentItem().model:
            model = self.treeWidget.currentItem().model
        else:
            model = Object()

        model.name = unicode(self.lineEdit_name.text())
        model.body = unicode(self.textBrowser_remplate_body.toPlainText())
 
        #for x in model.__dict__:
        #    print x, model.__dict__[x]

        model.id = self.connection.save(model, "billservice_template")
        self.treeWidget.currentItem().model = model
        
        self.connection.commit()
        self.refresh()
        
    def refresh(self):
        """
        1;"Договор на подключение физ. лиц"
        2;"Договор на подключение юр. лиц"
        3;"Счёт фактура"
        4;"Акт выполненных работ"
        5;"Кассовый чек"
        6;"Накладная на карты экспресс оплаты"
        7;"Карты экспресс-оплаты"
        """
        ind = self.treeWidget.currentItem()
        self.treeWidget.clear()
        card_templates = self.connection.sql("""SELECT * FROM billservice_template as template ORDER BY type_id ASC""")
        self.connection.commit()
        
        for ct in card_templates:
            item = QtGui.QTreeWidgetItem(self.treeWidget)
            item.model=ct
            item.setText(0, ct.name)
            try:
                if ind.model.id==ct.id:
                    self.treeWidget.setCurrentItem(item)
            except:
                pass

            
    def preview(self):
        id = self.treeWidget.currentItem().model.type_id
        templ = Template(unicode(self.textBrowser_remplate_body.toPlainText()), input_encoding='utf-8')
        if id==1:

            account = self.connection.sql("SELECT * FROM billservice_account LIMIT 1" )[0]
            tarif = self.connection.get("SELECT name FROM billservice_tariff WHERE id=get_tarif(%s)" % account.id)
            try:
                data=templ.render_unicode(account=account, tarif=tarif, created=datetime.datetime.now().strftime(strftimeFormat))
            except Exception, e:
                data=u"Error %s" % str(e)
        if id==2:
            account = self.connection.sql("SELECT * FROM billservice_account LIMIT 1" )[0]
            organization = self.connection.sql("SELECT * FROM billservice_organization LIMIT 1" )[0]
            bank = self.connection.sql("SELECT * FROM billservice_bankdata LIMIT 1" )[0]
            tarif = self.connection.get("SELECT name FROM billservice_tariff WHERE id=get_tarif(%s)" % account.id)
            try:
                data=templ.render_unicode(account=account, tarif=tarif, bank=bank, organization=organization,   created=datetime.datetime.now().strftime(strftimeFormat))
            except Exception, e:
                data=u"Error %s" % str(e)

        if id==5:
            account = self.connection.sql("SELECT * FROM billservice_account LIMIT 1" )[0]
            tarif = self.connection.get("SELECT name FROM billservice_tariff WHERE id=get_tarif(%s)" % account.id)
            transaction = self.connection.sql("SELECT * FROM billservice_transaction LIMIT 1")[0]
            sum = 10000
            document=u"Банковский перевод №112432"
            try:
                data=templ.render_unicode(account=account, tarif = tarif, transaction = transaction)
            except Exception, e:
                data=u"Error %s" % str(e)
            

        if id==6:
            data=u"Preview for this type of documents unavailable. For preview go to Express Cards->Sale Cards->Print Invoice"
        
        if id in (3,4):
            data=u"Preview for this type of documents unavailable. Please still waiting for next version of ExpertBilling"
                                
        if id ==7:
            try:
                operator =self.connection.get_operator()[0]
                
            except Exception, e:
                print e
                QtGui.QMessageBox.warning(self, u"Внимание!", u"Заполните информацию о провайдере в меню Help!")
                return
    
            try:
                bank =self.connection.get_bank_for_operator(operator.id)
            except Exception, e:
                print e
                QtGui.QMessageBox.warning(self, u"Внимание!", u"Заполните информацию о провайдере в меню Help!")
                return
            
            card = Object()
            card.pin = '12345678901234'
            card.login = 'user'
            card.nominal = 10000
            card.start_date = datetime.datetime.now().strftime(strftimeFormat)
            card.end_date = datetime.datetime.now().strftime(strftimeFormat)
            card.series = 64
            card.tarif = 'Тестовый тариф'
            data="""
            <html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            </head>
            <body>
            """;
            try:
                data+=templ.render_unicode(operator = operator, bank=bank, card=card)
            except Exception, e:
                data=u"Error %s" % str(e)
            data+="</body></html>"
                        
        self.connection.commit()
        file= open('templates/tmp/temp.html', 'wb')
        file.write(data.encode("utf-8", 'replace'))
        file.flush()
        a=CardPreviewDialog(url="templates/tmp/temp.html")
        a.exec_()

        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
            
class SuspendedPeriodForm(QtGui.QDialog):
    def __init__(self):
        super(SuspendedPeriodForm, self).__init__()
        
        self.setObjectName("SuspendedPeriodForm")
        self.resize(480, 108)
        self.start_date = None
        self.end_date = None
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_start_date = QtGui.QLabel(self.groupBox)
        self.label_start_date.setObjectName("label_start_date")
        self.gridLayout_2.addWidget(self.label_start_date, 0, 0, 1, 1)
        self.dateTimeEdit_start_date = QtGui.QDateTimeEdit(self.groupBox)
        self.dateTimeEdit_start_date.setMinimumSize(QtCore.QSize(0, 22))
        self.dateTimeEdit_start_date.setDateTime(QtCore.QDateTime(QtCore.QDate(2008, 1, 1), QtCore.QTime(0, 0, 0)))
        self.dateTimeEdit_start_date.setCalendarPopup(True)
        self.dateTimeEdit_start_date.setObjectName("dateTimeEdit_start_date")
        self.dateTimeEdit_start_date.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        self.gridLayout_2.addWidget(self.dateTimeEdit_start_date, 0, 1, 1, 1)
        self.label_end_date = QtGui.QLabel(self.groupBox)
        self.label_end_date.setObjectName("label_end_date")
        self.gridLayout_2.addWidget(self.label_end_date, 0, 2, 1, 1)
        self.dateTimeEdit_end_date = QtGui.QDateTimeEdit(self.groupBox)
        self.dateTimeEdit_end_date.setMinimumSize(QtCore.QSize(0, 22))
        self.dateTimeEdit_end_date.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.dateTimeEdit_end_date.setDateTime(QtCore.QDateTime(QtCore.QDate(2009, 1, 1), QtCore.QTime(0, 0, 0)))
        self.dateTimeEdit_end_date.setMinimumDateTime(QtCore.QDateTime(QtCore.QDate(2008, 9, 14), QtCore.QTime(0, 0, 0)))
        self.dateTimeEdit_end_date.setCalendarPopup(True)
        self.dateTimeEdit_end_date.setObjectName("dateTimeEdit_end_date")
        self.dateTimeEdit_end_date.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        self.gridLayout_2.addWidget(self.dateTimeEdit_end_date, 0, 3, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi()
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Выберите период", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Выберите период, в течении которого не должны списываться периодические услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.label_start_date.setText(QtGui.QApplication.translate("Dialog", "Начало", None, QtGui.QApplication.UnicodeUTF8))
        self.label_end_date.setText(QtGui.QApplication.translate("Dialog", "Окончание", None, QtGui.QApplication.UnicodeUTF8))
        
    def accept(self):
        self.start_date = self.dateTimeEdit_start_date.dateTime().toPyDateTime()
        self.end_date = self.dateTimeEdit_end_date.dateTime().toPyDateTime()
        
        QtGui.QDialog.accept(self)
        
class GroupsDialog(QtGui.QDialog):
    def __init__(self, connection,default_id=None):
        super(GroupsDialog, self).__init__()
        self.connection = connection
        self.selected_group = -1
        self.default_id=default_id
        self.directions = {"1":u"Входящий", "2":u"Исходящий", "3":u"Сумма Вх + Исх", "4":u"Максимальный"}
        self.types = {"1":u"Сумма классов", "2":u"Максимальный класс"}
        self.setObjectName("GroupsDialog")
        self.resize(655, 278)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.commandLinkButton = QtGui.QCommandLinkButton(self)
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.horizontalLayout.addWidget(self.commandLinkButton)
        self.commandLinkButton_2 = QtGui.QCommandLinkButton(self)
        self.commandLinkButton_2.setObjectName("commandLinkButton_2")
        self.horizontalLayout.addWidget(self.commandLinkButton_2)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        
        self.connect(self.commandLinkButton, QtCore.SIGNAL("clicked()"), self.add_group)
        self.connect(self.commandLinkButton_2, QtCore.SIGNAL("clicked()"), self.del_group)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_group)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Выберите группу трафика", None, QtGui.QApplication.UnicodeUTF8))
        columns = [u"#",u"Название группы",u"Классы",u"Направления", u"Тип"]
        makeHeaders(columns, self.tableWidget)
        
        self.commandLinkButton.setText(QtGui.QApplication.translate("Dialog", "Добавить группу", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton.setDescription(QtGui.QApplication.translate("Dialog", "Добавить новую группу трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_2.setText(QtGui.QApplication.translate("Dialog", "Удалить группу", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_2.setDescription(QtGui.QApplication.translate("Dialog", "Удалить существующую группу", None, QtGui.QApplication.UnicodeUTF8))

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/tp_small.png"))
        if y==0:
            headerItem.id=value
        if y!=0:
            if y==2:
                
                value = u", ".join([vstr.decode('utf-8') for vstr in value])
                headerItem.setText(value)
            else:
                headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
        
    def fixtures(self):
        groups = self.connection.sql("SELECT gr.*, ARRAY((SELECT name FROM nas_trafficclass WHERE id IN (SELECT trafficclass_id FROM billservice_group_trafficclass WHERE group_id=gr.id))) as classnames FROM billservice_group as gr")
        self.connection.commit()
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(groups))
        i=0
        for a in groups:
            
            self.addrow(a.id, i, 0)
            self.addrow(a.name, i, 1)
            self.addrow(a.classnames, i, 2)
            self.addrow(self.directions["%s" % a.direction], i, 3)
            self.addrow(self.types["%s" % a.type], i, 4)
            if a.id==self.default_id:
                self.tableWidget.selectRow(i)
            i+=1
        self.tableWidget.resizeColumnsToContents()
        
    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).id)
    
    def add_group(self):
        child = GroupEditDialog(connection=self.connection)
        if child.exec_()==1:
            self.fixtures()
        
    def edit_group(self):
        model = self.connection.get_model(self.getSelectedId(), "billservice_group")
        self.connection.commit()
        child = GroupEditDialog(connection=self.connection, model=model)
        if child.exec_()==1:
            self.fixtures()
        
    def del_group(self):
        if QtGui.QMessageBox.question(self, u"Удалить группу?" , u"При удалении группы будут удалены все её связи с лимитами трафика.\nВы уверены что хотите это сделать?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            self.connection.iddelete(self.getSelectedId(), "billservice_group")
            self.connection.commit()
            self.fixtures()
    
    def accept(self):
        self.selected_group = self.getSelectedId()
        QtGui.QDialog.accept(self)
        
class GroupEditDialog(QtGui.QDialog):
    def __init__(self, connection, model=None):
        super(GroupEditDialog, self).__init__()
        self.connection=connection
        self.model = model
        self.directions = {"1":u"Входящий", "2":u"Исходящий", "3":u"Сумма Вх + Исх", "4":u"Максимальный"}
        self.types = {"1":u"Сумма классов", "2":u"Максимальный класс"}
        
        self.setObjectName("GroupEditDialog")
        self.resize(346, 376)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtGui.QLabel(self)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.groupBox_params = QtGui.QGroupBox(self)
        self.groupBox_params.setObjectName("groupBox_params")
        self.gridLayout = QtGui.QGridLayout(self.groupBox_params)
        self.gridLayout.setObjectName("gridLayout")
        self.label_directions = QtGui.QLabel(self.groupBox_params)
        self.label_directions.setObjectName("label_directions")
        self.gridLayout.addWidget(self.label_directions, 0, 0, 1, 1)
        self.comboBox_directions = QtGui.QComboBox(self.groupBox_params)
        self.comboBox_directions.setObjectName("comboBox_directions")

        self.gridLayout.addWidget(self.comboBox_directions, 0, 1, 1, 1)
        self.comboBox_grouptype = QtGui.QComboBox(self.groupBox_params)
        self.comboBox_grouptype.setObjectName("comboBox_grouptype")

        self.gridLayout.addWidget(self.comboBox_grouptype, 1, 1, 1, 1)
        self.label_grouptype = QtGui.QLabel(self.groupBox_params)
        self.label_grouptype.setObjectName("label_grouptype")
        self.gridLayout.addWidget(self.label_grouptype, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_params, 2, 0, 1, 2)
        self.lineEdit_name = QtGui.QLineEdit(self)
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.gridLayout_2.addWidget(self.lineEdit_name, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 3, 0, 1, 2)
        self.groupBox_classes = QtGui.QGroupBox(self)
        self.groupBox_classes.setObjectName("groupBox_classes")
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_classes)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.listWidget_classes = QtGui.QListWidget(self.groupBox_classes)
        self.listWidget_classes.setObjectName("listWidget_classes")
        QtGui.QListWidgetItem(self.listWidget_classes)
        QtGui.QListWidgetItem(self.listWidget_classes)
        self.gridLayout_3.addWidget(self.listWidget_classes, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_classes, 1, 0, 1, 2)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Редактирование группы", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_params.setTitle(QtGui.QApplication.translate("Dialog", "Параметры группы", None, QtGui.QApplication.UnicodeUTF8))
        self.label_directions.setText(QtGui.QApplication.translate("Dialog", "Направление в классах", None, QtGui.QApplication.UnicodeUTF8))
        self.label_grouptype.setText(QtGui.QApplication.translate("Dialog", "Тип группы", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_classes.setTitle(QtGui.QApplication.translate("Dialog", "Классы", None, QtGui.QApplication.UnicodeUTF8))
        #self.listWidget_classes.setSortingEnabled(True)

        
        
    def fixtures(self):
        selected_classes = []
        if self.model:
            self.lineEdit_name.setText(unicode(self.model.name))
            selected_classes = self.connection.sql("SELECT trafficclass_id as id FROM billservice_group_trafficclass WHERE group_id=%s" % self.model.id)
            selected_classes = [x.id for x in selected_classes]
        classes = self.connection.get_models("nas_trafficclass")
        self.connection.commit()
        self.listWidget_classes.clear()
        for clas in classes:
            item = QtGui.QListWidgetItem(unicode(clas.name))
            item.setCheckState(QtCore.Qt.Unchecked)
            for x in selected_classes:
                if  clas.id in selected_classes: 
                    item.setCheckState(QtCore.Qt.Checked) 
                    
            item.id = clas.id
            self.listWidget_classes.addItem(item)
            
        
        
        i=0
        for direction in self.directions:
            self.comboBox_directions.addItem(self.directions[direction])
            self.comboBox_directions.setItemData(i, QtCore.QVariant(direction))
            if self.model:
                #print direction, self.model.direction,type(direction), type(self.model.direction) 
                if int(direction)==self.model.direction:
                    #print "current index=", i
                    self.comboBox_directions.setCurrentIndex(i)
            i+=1

        
        
        i=0
        for gtype in self.types:
            self.comboBox_grouptype.addItem(self.types[gtype])
            self.comboBox_grouptype.setItemData(i, QtCore.QVariant(gtype))
            if self.model:
                if int(gtype)==self.model.type:
                    #print "current index=", i
                    self.comboBox_grouptype.setCurrentIndex(i)
            i+=1            
        

            
    def accept(self):
        if self.model:
            model = self.model
        else:
            model = Object()
        traffic_classes=[]
        for i in xrange(self.listWidget_classes.count()):
            clas = self.listWidget_classes.item(i)
            if clas.checkState()==QtCore.Qt.Checked:
                traffic_classes.append(clas.id)
        if unicode(self.lineEdit_name.text())=="" or self.listWidget_classes.count()==0 or traffic_classes==[]: 
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверьте введённые вами данные."))
            return
        
        try:
            
            model.name = u"%s" % self.lineEdit_name.text()
            model.direction = self.comboBox_directions.itemData(self.comboBox_directions.currentIndex()).toInt()[0]
            model.type = self.comboBox_grouptype.itemData(self.comboBox_grouptype.currentIndex()).toInt()[0]
            model.id = self.connection.save(model, "billservice_group")
            

            #Удаляем старые связи и добавляем только нужные новые
            self.connection.command("DELETE FROM billservice_group_trafficclass WHERE group_id=%s;" % model.id)
            for tc in traffic_classes:
                node = Object()
                node.group_id = model.id
                node.trafficclass_id = tc
                self.connection.save(node, "billservice_group_trafficclass")
            self.connection.commit()
        except Exception, e:
            self.connection.rollback()
            print e
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Ошибка при создании группы."))
            return
        QtGui.QDialog.accept(self)


class SpeedLimitDialog(QtGui.QDialog):
    def __init__(self, connection, model=None):
        super(SpeedLimitDialog, self).__init__()
        self.setObjectName("SpeedLimitDialog")
        self.resize(421, 329)
        self.model = model
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.groupBox_speed_settings = QtGui.QGroupBox(self)
        self.groupBox_speed_settings.setObjectName("groupBox_speed_settings")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_speed_settings)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_tx = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_tx.setObjectName("label_tx")
        self.gridLayout_2.addWidget(self.label_tx, 4, 1, 1, 1)
        self.label_rx = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_rx.setObjectName("label_rx")
        self.gridLayout_2.addWidget(self.label_rx, 4, 2, 1, 1)
        self.label_max = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_max.setObjectName("label_max")
        self.gridLayout_2.addWidget(self.label_max, 5, 0, 1, 1)
        self.spinBox_max_tx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_max_tx.setMaximum(100000)
        self.spinBox_max_tx.setObjectName("spinBox_max_tx")
        self.gridLayout_2.addWidget(self.spinBox_max_tx, 5, 1, 1, 1)
        self.label_burst_treshold = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_burst_treshold.setObjectName("label_burst_treshold")
        self.gridLayout_2.addWidget(self.label_burst_treshold, 8, 0, 1, 1)
        self.spinBox_burst_treshold_tx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_burst_treshold_tx.setMaximum(100000)
        self.spinBox_burst_treshold_tx.setObjectName("spinBox_burst_treshold_tx")
        self.gridLayout_2.addWidget(self.spinBox_burst_treshold_tx, 8, 1, 1, 1)
        self.label_burst_time = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_burst_time.setObjectName("label_burst_time")
        self.gridLayout_2.addWidget(self.label_burst_time, 9, 0, 1, 1)
        self.spinBox_burst_time_tx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_burst_time_tx.setMaximum(100000)
        self.spinBox_burst_time_tx.setObjectName("spinBox_burst_time_tx")
        self.gridLayout_2.addWidget(self.spinBox_burst_time_tx, 9, 1, 1, 1)
        self.label_min = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_min.setObjectName("label_min")
        self.gridLayout_2.addWidget(self.label_min, 10, 0, 1, 1)
        self.spinBox_min_tx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_min_tx.setMaximum(100000)
        self.spinBox_min_tx.setObjectName("spinBox_min_tx")
        self.gridLayout_2.addWidget(self.spinBox_min_tx, 10, 1, 1, 1)
        self.label_priority = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_priority.setObjectName("label_priority")
        self.gridLayout_2.addWidget(self.label_priority, 11, 0, 1, 1)
        self.spinBox_priority = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_priority.setMinimum(1)
        self.spinBox_priority.setMaximum(8)
        self.spinBox_priority.setProperty("value", QtCore.QVariant(1))
        self.spinBox_priority.setObjectName("spinBox_priority")
        self.gridLayout_2.addWidget(self.spinBox_priority, 11, 1, 1, 1)
        self.label_burst = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_burst.setObjectName("label_burst")
        self.gridLayout_2.addWidget(self.label_burst, 7, 0, 1, 1)
        self.spinBox_burst_tx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_burst_tx.setMaximum(100000)
        self.spinBox_burst_tx.setObjectName("spinBox_burst_tx")
        self.gridLayout_2.addWidget(self.spinBox_burst_tx, 7, 1, 1, 1)
        self.spinBox_max_rx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_max_rx.setMaximum(100000)
        self.spinBox_max_rx.setObjectName("spinBox_max_rx")
        self.gridLayout_2.addWidget(self.spinBox_max_rx, 5, 2, 1, 1)
        self.spinBox_burst_rx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_burst_rx.setMaximum(100000)
        self.spinBox_burst_rx.setObjectName("spinBox_burst_rx")
        self.gridLayout_2.addWidget(self.spinBox_burst_rx, 7, 2, 1, 1)
        self.spinBox_burst_treshold_rx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_burst_treshold_rx.setMaximum(100000)
        self.spinBox_burst_treshold_rx.setObjectName("spinBox_burst_treshold_rx")
        self.gridLayout_2.addWidget(self.spinBox_burst_treshold_rx, 8, 2, 1, 1)
        self.spinBox_burst_time_rx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_burst_time_rx.setMaximum(100000)
        self.spinBox_burst_time_rx.setObjectName("spinBox_burst_time_rx")
        self.gridLayout_2.addWidget(self.spinBox_burst_time_rx, 9, 2, 1, 1)
        self.spinBox_min_rx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_min_rx.setMaximum(100000)
        self.spinBox_min_rx.setObjectName("spinBox_min_rx")
        self.gridLayout_2.addWidget(self.spinBox_min_rx, 10, 2, 1, 1)
        self.comboBox_unit = QtGui.QComboBox(self.groupBox_speed_settings)
        self.comboBox_unit.setObjectName("comboBox_unit")
        self.gridLayout_2.addWidget(self.comboBox_unit, 2, 1, 1, 2)
        self.radioButton_speed_add = QtGui.QRadioButton(self.groupBox_speed_settings)
        self.radioButton_speed_add.setChecked(True)
        self.radioButton_speed_add.setObjectName("radioButton_speed_add")
        self.gridLayout_2.addWidget(self.radioButton_speed_add, 0, 1, 1, 1)
        self.label = QtGui.QLabel(self.groupBox_speed_settings)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 2, 0, 1, 1)
        self.radioButton_speed_abs = QtGui.QRadioButton(self.groupBox_speed_settings)
        self.radioButton_speed_abs.setObjectName("radioButton_speed_abs")
        self.gridLayout_2.addWidget(self.radioButton_speed_abs, 0, 2, 1, 1)
        self.pushButton_advanced = QtGui.QPushButton(self.groupBox_speed_settings)
        self.pushButton_advanced.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButton_advanced.setMaximumSize(QtCore.QSize(16777215, 16))
        self.pushButton_advanced.setObjectName("pushButton_advanced")
        self.gridLayout_2.addWidget(self.pushButton_advanced, 6, 1, 1, 2)
        self.gridLayout.addWidget(self.groupBox_speed_settings, 0, 0, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.pushButton_advanced, QtCore.SIGNAL("clicked()"), self.advancedAction)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()
        self.layout().setSizeConstraint(QtGui.QLayout.SetFixedSize)
        #self.advancedAction()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Изменить скорость", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_speed_settings.setTitle(QtGui.QApplication.translate("Dialog", "Настройки скорости", None, QtGui.QApplication.UnicodeUTF8))
        self.label_tx.setText(QtGui.QApplication.translate("Dialog", "TX", None, QtGui.QApplication.UnicodeUTF8))
        self.label_rx.setText(QtGui.QApplication.translate("Dialog", "RX", None, QtGui.QApplication.UnicodeUTF8))
        self.label_max.setText(QtGui.QApplication.translate("Dialog", "MAX", None, QtGui.QApplication.UnicodeUTF8))
        self.label_burst_treshold.setText(QtGui.QApplication.translate("Dialog", "Burst Treshold", None, QtGui.QApplication.UnicodeUTF8))
        self.label_burst_time.setText(QtGui.QApplication.translate("Dialog", "Burst time", None, QtGui.QApplication.UnicodeUTF8))
        self.spinBox_burst_time_tx.setSuffix(QtGui.QApplication.translate("Dialog", " c", None, QtGui.QApplication.UnicodeUTF8))
        self.label_min.setText(QtGui.QApplication.translate("Dialog", "MIN", None, QtGui.QApplication.UnicodeUTF8))
        self.label_priority.setText(QtGui.QApplication.translate("Dialog", "Priority", None, QtGui.QApplication.UnicodeUTF8))
        self.label_burst.setText(QtGui.QApplication.translate("Dialog", "Burst", None, QtGui.QApplication.UnicodeUTF8))
        self.spinBox_burst_time_rx.setSuffix(QtGui.QApplication.translate("Dialog", " c", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_speed_add.setText(QtGui.QApplication.translate("Dialog", "Добавить к текущей", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Единицы измерения", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_speed_abs.setText(QtGui.QApplication.translate("Dialog", "Абсолютные значения", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_advanced.setText(QtGui.QApplication.translate("Dialog", "Advanced", None, QtGui.QApplication.UnicodeUTF8))

    def advancedAction(self):
        if self.label_burst.isHidden()==False:
            self.label_burst.hide()
            self.spinBox_burst_tx.hide()
            self.spinBox_burst_rx.hide()
            self.label_burst_treshold.hide()
            self.spinBox_burst_treshold_tx.hide()
            self.spinBox_burst_treshold_rx.hide()
            self.label_burst_time.hide()
            self.spinBox_burst_time_tx.hide()
            self.spinBox_burst_time_rx.hide()
            self.label_min.hide()
            self.spinBox_min_tx.hide()
            self.spinBox_min_rx.hide()
            self.label_priority.hide()
            self.spinBox_priority.hide()
            self.setMaximumHeight(150)
            self.setMinimumHeight(150)
            

        else:
            self.label_burst.show()
            self.spinBox_burst_tx.show()
            self.spinBox_burst_rx.show()
            self.label_burst_treshold.show()
            self.spinBox_burst_treshold_tx.show()
            self.spinBox_burst_treshold_rx.show()
            self.label_burst_time.show()
            self.spinBox_burst_time_tx.show()
            self.spinBox_burst_time_rx.show()
            self.label_min.show()
            self.spinBox_min_tx.show()
            self.spinBox_min_rx.show()
            self.label_priority.show()
            self.spinBox_priority.show()
            self.setMaximumHeight(350)
            self.setMinimumHeight(350)

            
        
    def fixtures(self):
        
        x = ['Kbps', 'Mbps','%']
        i=0
        for a in x:
            self.comboBox_unit.addItem(unicode(a))
            
            if self.model:
                if self.model.speed_units == a:
                    self.comboBox_unit.setCurrentIndex(i)
            i+=1
                    
        if self.model:
            #self.model = self.connection.get_model(self.model.id, "billservice_speedlimit")
            #self.connection.commit()
            #print "fixturemodel", self.model
            if self.model.change_speed_type=='abs':
                self.radioButton_speed_abs.setChecked(True)
                
            self.spinBox_max_tx.setValue(int(self.model.max_tx))
            self.spinBox_max_rx.setValue(int(self.model.max_rx))
            #print int(self.model.burst_tx) or int(self.model.burst_rx) or int(self.model.burst_treshold_tx) or int(self.model.burst_treshold_rx) or int(self.model.burst_time_tx) or int(self.model.burst_time_rx) or int(self.model.min_tx) or int(self.model.min_rx)
            #print int(self.model.burst_tx) , int(self.model.burst_rx) , int(self.model.burst_treshold_tx) , int(self.model.burst_treshold_rx) , int(self.model.burst_time_tx) , int(self.model.burst_time_rx) , int(self.model.min_tx) , int(self.model.min_rx)
            if int(self.model.burst_tx) or int(self.model.burst_rx) or int(self.model.burst_treshold_tx) or int(self.model.burst_treshold_rx) or int(self.model.burst_time_tx) or int(self.model.burst_time_rx) or int(self.model.min_tx) or int(self.model.min_rx):
                self.spinBox_burst_tx.setValue(int(self.model.burst_tx))
                self.spinBox_burst_rx.setValue(int(self.model.burst_rx))
    
                self.spinBox_burst_treshold_tx.setValue(int(self.model.burst_treshold_tx))
                self.spinBox_burst_treshold_rx.setValue(int(self.model.burst_treshold_rx))
    
                self.spinBox_burst_time_tx.setValue(int(self.model.burst_time_tx))
                self.spinBox_burst_time_rx.setValue(int(self.model.burst_time_rx))
                
                self.spinBox_min_tx.setValue(int(self.model.min_tx))
                self.spinBox_min_rx.setValue(int(self.model.min_rx))
                
                self.spinBox_priority.setValue(int(self.model.priority))
                self.label_burst.show()
                self.spinBox_burst_tx.show()
                self.spinBox_burst_rx.show()
                self.label_burst_treshold.show()
                self.spinBox_burst_treshold_tx.show()
                self.spinBox_burst_treshold_rx.show()
                self.label_burst_time.show()
                self.spinBox_burst_time_tx.show()
                self.spinBox_burst_time_rx.show()
                self.label_min.show()
                self.spinBox_min_tx.show()
                self.spinBox_min_rx.show()
                self.label_priority.show()
                self.spinBox_priority.show()
            else:
                #self.spinBox_max_tx.setValue(0)
                #self.spinBox_max_rx.setValue(0)
                
                self.spinBox_burst_tx.setValue(0)
                self.spinBox_burst_rx.setValue(0)
    
                self.spinBox_burst_treshold_tx.setValue(0)
                self.spinBox_burst_treshold_rx.setValue(0)
    
                self.spinBox_burst_time_tx.setValue(0)
                self.spinBox_burst_time_rx.setValue(0)
                
                self.spinBox_min_tx.setValue(0)
                self.spinBox_min_rx.setValue(0)
                
                self.spinBox_priority.setValue(8)
                self.label_burst.hide()
                self.spinBox_burst_tx.hide()
                self.spinBox_burst_rx.hide()
                self.label_burst_treshold.hide()
                self.spinBox_burst_treshold_tx.hide()
                self.spinBox_burst_treshold_rx.hide()
                self.label_burst_time.hide()
                self.spinBox_burst_time_tx.hide()
                self.spinBox_burst_time_rx.hide()
                self.label_min.hide()
                self.spinBox_min_tx.hide()
                self.spinBox_min_rx.hide()
                self.label_priority.hide()
                self.spinBox_priority.hide()
            
        else:
            self.spinBox_max_tx.setValue(0)
            self.spinBox_max_rx.setValue(0)
            
            self.spinBox_burst_tx.setValue(0)
            self.spinBox_burst_rx.setValue(0)

            self.spinBox_burst_treshold_tx.setValue(0)
            self.spinBox_burst_treshold_rx.setValue(0)

            self.spinBox_burst_time_tx.setValue(0)
            self.spinBox_burst_time_rx.setValue(0)
            
            self.spinBox_min_tx.setValue(0)
            self.spinBox_min_rx.setValue(0)
            
            self.spinBox_priority.setValue(8)
            self.label_burst.hide()
            self.spinBox_burst_tx.hide()
            self.spinBox_burst_rx.hide()
            self.label_burst_treshold.hide()
            self.spinBox_burst_treshold_tx.hide()
            self.spinBox_burst_treshold_rx.hide()
            self.label_burst_time.hide()
            self.spinBox_burst_time_tx.hide()
            self.spinBox_burst_time_rx.hide()
            self.label_min.hide()
            self.spinBox_min_tx.hide()
            self.spinBox_min_rx.hide()
            self.label_priority.hide()
            self.spinBox_priority.hide()
            
    def accept(self):
        if self.model==None:
            self.model = Object()
            
        self.model.speed_units = unicode(self.comboBox_unit.currentText())
        self.model.change_speed_type = "add" if self.radioButton_speed_add.isChecked() == True else "abs"
        self.model.max_tx = unicode(self.spinBox_max_tx.value())
        self.model.max_rx = unicode(self.spinBox_max_rx.value())
        
        if self.label_burst.isHidden()==False:
            self.model.burst_tx = unicode(self.spinBox_burst_tx.value())
            self.model.burst_rx = unicode(self.spinBox_burst_rx.value())
    
            self.model.burst_treshold_tx = unicode(self.spinBox_burst_treshold_tx.value())
            self.model.burst_treshold_rx = unicode(self.spinBox_burst_treshold_rx.value())
    
            self.model.burst_time_tx = unicode(self.spinBox_burst_time_tx.value())
            self.model.burst_time_rx = unicode(self.spinBox_burst_time_rx.value())
    
            self.model.min_tx = unicode(self.spinBox_min_tx.value())
            self.model.min_rx = unicode(self.spinBox_min_rx.value())
    
            self.model.priority = unicode(self.spinBox_priority.value())
        else:
            self.model.burst_tx = 0
            self.model.burst_rx = 0
    
            self.model.burst_treshold_tx = 0
            self.model.burst_treshold_rx = 0
    
            self.model.burst_time_tx = 0
            self.model.burst_time_rx = 0
    
            self.model.min_tx = 0
            self.model.min_rx = 0
    
            self.model.priority = 8
            
        #self.model.limit_id = self.limit_id
        #for x in self.model.__dict__:
        #    print x, self.model.__dict__[x]

        #self.model.id = self.connection.save(self.model, "billservice_speedlimit")
        #self.connection.commit()
        QtGui.QDialog.accept(self)


class SqlDialog(QtGui.QDialog):
    def __init__(self, connection):
        super(SqlDialog, self).__init__()
        self.connection = connection
        self.setObjectName("Dialog")
        self.resize(604, 358)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.plainTextEdit = QtGui.QPlainTextEdit(self)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.gridLayout.addWidget(self.plainTextEdit, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "SQL Command Window", None, QtGui.QApplication.UnicodeUTF8))
        
        
    def accept(self):
        
        if unicode(self.plainTextEdit.toPlainText()):
            try:
                self.connection.sql(unicode(self.plainTextEdit.toPlainText()))
                self.connection.commit()
                QtGui.QMessageBox.information(self, u"Ok", unicode(u"Запрос успешно выполнен."))
            except:
                self.connection.rollback()
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"При выполнении запроса возникла ошибка."))
                return
        else:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Введите текст запроса."))
            return
        QtGui.QDialog.accept(self)
    
        
class InfoDialog(QtGui.QDialog):
    def __init__(self, connection, type, account_id):
        super(InfoDialog, self).__init__()
        self.connection = connection
        self.type = type
        self.account_id = account_id
        self.setObjectName("InfoDialog")
        dateDelim = '.'
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        self.resize(550, 300)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.refresh()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Информация", None, QtGui.QApplication.UnicodeUTF8))
        
       
    def addrow(self, value, x, y, id=None, color=None, enabled=True, ctext=None, setdata=False):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        if color:
            if float(value)<0:
                headerItem.setBackgroundColor(QtGui.QColor(color))
                headerItem.setTextColor(QtGui.QColor('#ffffff'))
            elif float(value)==0:
                headerItem.setBackgroundColor(QtGui.QColor("#ffdc51"))
                #headerItem.setTextColor(QtGui.QColor('#ffffff'))
                                
        if not enabled:
            headerItem.setBackgroundColor(QtGui.QColor('#dadada'))
        
            
        if y==1:
            if enabled==True:
                headerItem.setIcon(QtGui.QIcon("images/user.png"))
            else:
                headerItem.setIcon(QtGui.QIcon("images/user_inactive.png"))
        if setdata:
            headerItem.setData(39, QtCore.QVariant(value))   
        if ctext is not None:
            headerItem.setText(unicode(ctext))
        else:
            headerItem.setText(unicode(value))
        
        headerItem.id = id
        self.tableWidget.setItem(x,y,headerItem)
         
    def refresh(self):
        
        if self.type == "limit":
            columns=["#", u"Название", u"Количество", u"Израсходовано", u"Начало", u"Окончание"]
            makeHeaders(columns, self.tableWidget)
            items = self.connection.get_limites(self.account_id)
            
            self.connection.commit()
            self.tableWidget.setRowCount(len(items))
            i=0
            for a in items:            
                self.addrow(i, i,0)
                self.addrow(a['limit_name'], i,1)
                self.addrow("%s KB" % (a['limit_size']/1024), i,2)
                self.addrow("%s KB" % (a['size']/1024), i,3)
                try:
                    self.addrow(a.get('settlement_period_start').strftime(self.strftimeFormat), i,4)
                    self.addrow(a.get('settlement_period_end').strftime(self.strftimeFormat), i,5)
                except Exception, e:
                    print e
                i+=1
            self.tableWidget.resizeRowsToContents()
            
        else:
            columns=["#", u"Группа", u"Количество", u"Израсходовано", ]
            makeHeaders(columns, self.tableWidget)
            items = self.connection.sql("""
            SELECT   ppt.size as size, ppt.datetime, pp.size as pp_size, (SELECT name FROM billservice_group WHERE id=pp.group_id) as group_name FROM billservice_accountprepaystrafic as ppt
            JOIN billservice_prepaidtraffic as pp ON pp.id=ppt.prepaid_traffic_id
            WHERE account_tarif_id=(SELECT id FROM billservice_accounttarif WHERE account_id=%s and datetime<now() ORDER BY datetime DESC LIMIT 1);""" % (self.account_id,)            
            )

            
            self.connection.commit()
            self.tableWidget.setRowCount(len(items))
            i=0
            for a in items:            
                self.addrow(i, i,0)
                self.addrow(a.group_name, i,1)
                self.addrow("%s KB" % (a.pp_size/1024), i, 2)
                self.addrow("%s KB" % (a.size/1024), i, 3)
                i+=1
            self.tableWidget.resizeRowsToContents()            

        
class RadiusAttrsDialog(QtGui.QDialog):
    def __init__(self, tarif_id, connection):
        super(RadiusAttrsDialog, self).__init__()
        self.tarif_id = tarif_id
        self.connection = connection
        
        self.setObjectName("RadiusAttrsDialog")
        self.resize(450, 475)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox_edit = QtGui.QGroupBox(self)
        self.groupBox_edit.setObjectName("groupBox_edit")
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_edit)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_vendor = QtGui.QLabel(self.groupBox_edit)
        self.label_vendor.setObjectName("label_vendor")
        self.gridLayout_3.addWidget(self.label_vendor, 0, 0, 1, 1)
        self.lineEdit_vendor = QtGui.QLineEdit(self.groupBox_edit)
        self.lineEdit_vendor.setObjectName("lineEdit_vendor")
        self.gridLayout_3.addWidget(self.lineEdit_vendor, 0, 1, 1, 1)
        self.label_attrid = QtGui.QLabel(self.groupBox_edit)
        self.label_attrid.setObjectName("label_attrid")
        self.gridLayout_3.addWidget(self.label_attrid, 0, 2, 1, 1)
        self.lineEdit_attrid = QtGui.QLineEdit(self.groupBox_edit)
        self.lineEdit_attrid.setObjectName("lineEdit_attrid")
        self.gridLayout_3.addWidget(self.lineEdit_attrid, 0, 3, 1, 1)
        self.label_value = QtGui.QLabel(self.groupBox_edit)
        self.label_value.setObjectName("label_value")
        self.gridLayout_3.addWidget(self.label_value, 0, 4, 1, 1)
        self.lineEdit_value = QtGui.QLineEdit(self.groupBox_edit)
        self.lineEdit_value.setObjectName("lineEdit_value")
        self.gridLayout_3.addWidget(self.lineEdit_value, 0, 5, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.commandLinkButton_add = QtGui.QCommandLinkButton(self.groupBox_edit)
        self.commandLinkButton_add.setCheckable(False)
        self.commandLinkButton_add.setObjectName("commandLinkButton_add")
        self.horizontalLayout.addWidget(self.commandLinkButton_add)
        self.commandLinkButton_del = QtGui.QCommandLinkButton(self.groupBox_edit)
        self.commandLinkButton_del.setObjectName("commandLinkButton_del")
        self.horizontalLayout.addWidget(self.commandLinkButton_del)
        self.gridLayout_3.addLayout(self.horizontalLayout, 1, 0, 1, 6)
        self.gridLayout_2.addWidget(self.groupBox_edit, 0, 0, 1, 1)
        self.groupBox_table = QtGui.QGroupBox(self)
        self.groupBox_table.setObjectName("groupBox_table")
        self.gridLayout = QtGui.QGridLayout(self.groupBox_table)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtGui.QTableWidget(self.groupBox_table)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_table, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.commandLinkButton_add, QtCore.SIGNAL("clicked()"), self.save)
        QtCore.QObject.connect(self.commandLinkButton_del, QtCore.SIGNAL("clicked()"), self.delete)
        #self.connect(self.tableWidget, QtCore.SIGNAL("itemClicked(QTableWidgetItem *)"), self.set_data)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройка RADIUS атрибутов", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_edit.setTitle(QtGui.QApplication.translate("Dialog", "Настройки", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vendor.setText(QtGui.QApplication.translate("Dialog", "Vendor ID", None, QtGui.QApplication.UnicodeUTF8))
        self.label_attrid.setText(QtGui.QApplication.translate("Dialog", "Attr.ID", None, QtGui.QApplication.UnicodeUTF8))
        self.label_value.setText(QtGui.QApplication.translate("Dialog", "Value", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_add.setText(QtGui.QApplication.translate("Dialog", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_add.setDescription(QtGui.QApplication.translate("Dialog", "Поместить в таблицу", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_del.setText(QtGui.QApplication.translate("Dialog", "Удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_del.setDescription(QtGui.QApplication.translate("Dialog", "Удалить из таблицы", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_table.setTitle(QtGui.QApplication.translate("Dialog", "Сохранённые значения", None, QtGui.QApplication.UnicodeUTF8))
        columns = ["Vendor ID", "Attr ID", "Value"]
        makeHeaders(columns, self.tableWidget)
        
    def addrow(self, value, x, y, id=None):
        headerItem = QtGui.QTableWidgetItem()
        if id:
            headerItem.id=id

        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
        
#===============================================================================
#    def set_data(self):
#        id = self.getSelectedId()
#        item = self.connection.get_model(id, "billservice_radiusattrs")
#        self.connection.commit()
#        self.lineEdit_vendor.setText(unicode(item.vendor))
#        self.lineEdit_attrid.setText(unicode(item.attrid))
#        self.lineEdit_value.setText(unicode(item.value))
#===============================================================================
        
    def save(self):
        model = Object()
        model.tarif_id = self.tarif_id
        model.vendor = unicode(self.lineEdit_vendor.text()) or 0
        model.attrid = unicode(self.lineEdit_attrid.text())
        model.value = unicode(self.lineEdit_value.text())
        
        try:
            
            self.connection.save(model, "billservice_radiusattrs")
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()
        self.fixtures()
      
    def delete(self):
        id = self.getSelectedId()
        self.connection.iddelete(id, "billservice_radiusattrs")
        self.connection.commit()
        self.fixtures()
              
    def getSelectedId(self):
        return self.tableWidget.item(self.tableWidget.currentRow(), 0).id
    
    def fixtures(self):
        attrs = self.connection.get_models("billservice_radiusattrs", where={'tarif_id':self.tarif_id,})
        self.connection.commit()
        self.tableWidget.setRowCount(len(attrs))
        i=0
        for attr in attrs:
            print attr.vendor
            self.addrow(attr.vendor, i, 0, id = attr.id)
            self.addrow(attr.attrid, i, 1)
            self.addrow(attr.value, i, 2)
            i+=1
            

class PSCreatedForm(QtGui.QDialog):
    def __init__(self, date):
        super(PSCreatedForm, self).__init__()
        self.date = date
        self.setObjectName("PSCreatedForm")
        self.resize(266, 95)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.dateTimeEdit = QtGui.QDateTimeEdit(self)
        self.dateTimeEdit.setCalendarPopup(True)
        self.dateTimeEdit.setObjectName("dateTimeEdit")
        self.gridLayout.addWidget(self.dateTimeEdit, 0, 0, 1, 1)
        self.checkBox_temporary_blocked_w = QtGui.QCheckBox(self)
        self.checkBox_temporary_blocked_w.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox_temporary_blocked_w, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi()
        self.checkBox_temporary_blockedAction()
        self.connect(self.checkBox_temporary_blocked_w, QtCore.SIGNAL("stateChanged(int)"), self.checkBox_temporary_blockedAction)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        #self.connect(self.checkBox_temporary_blocked, QtCore.SIGNAL("stateChanged(int)"), self.checkBox_temporary_blockedAction)
        
        #QtCore.QMetaObject.connectSlotsByName(self)
        
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройки периодической услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_temporary_blocked_w.setText(QtGui.QApplication.translate("Dialog", "С начала расчётного периода", None, QtGui.QApplication.UnicodeUTF8))
        
        
    def checkBoxAction(self):
        if self.checkBox_temporary_blocked_w.checkState() == QtCore.Qt.Checked:
            self.dateTimeEdit.setDisabled(True)
        else:
            self.dateTimeEdit.setDisabled(False)
            
            
    def fixtures(self):
        if self.date:
            self.dateTimeEdit.setDateTime(self.date)
        else:
            self.checkBox_temporary_blocked_w.setChecked(True)
            self.dateTimeEdit.setDateTime(datetime.datetime.now())
            
            
    def accept(self):
        if self.checkBox_temporary_blocked_w.checkState() == QtCore.Qt.Checked:
            self.date = None
        else:
            self.date = self.dateTimeEdit.dateTime().toPyDateTime()
        QtGui.QDialog.accept(self)
        
        
class AccountAddonServiceEdit(QtGui.QDialog):
    def __init__(self, connection, model=None, account_model = None):
        super(AccountAddonServiceEdit, self).__init__()
        self.setObjectName("AccountAddonServiceEdit")
        self.model = model
        self.account_model = account_model
        self.connection = connection
        self.resize(437, 194)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label_service = QtGui.QLabel(self.groupBox)
        self.label_service.setObjectName("label_service")
        self.gridLayout.addWidget(self.label_service, 0, 0, 1, 1)
        self.comboBox_service = QtGui.QComboBox(self.groupBox)
        self.comboBox_service.setObjectName("comboBox_service")
        self.gridLayout.addWidget(self.comboBox_service, 0, 1, 1, 2)
        self.label_activation = QtGui.QLabel(self.groupBox)
        self.label_activation.setObjectName("label_activation")
        self.gridLayout.addWidget(self.label_activation, 1, 0, 1, 1)
        self.dateTimeEdit_activation = QtGui.QDateTimeEdit(self.groupBox)
        self.dateTimeEdit_activation.setCalendarPopup(True)
        self.dateTimeEdit_activation.setObjectName("dateTimeEdit_activation")
        self.gridLayout.addWidget(self.dateTimeEdit_activation, 1, 1, 1, 2)
        self.toolButton_activation_now = QtGui.QToolButton(self.groupBox)
        self.toolButton_activation_now.setObjectName("toolButton_activation_now")
        self.gridLayout.addWidget(self.toolButton_activation_now, 1, 3, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.groupBox)
        self.groupBox_2.setCheckable(True)
        self.groupBox_2.setChecked(False)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_deactivation = QtGui.QLabel(self.groupBox_2)
        self.label_deactivation.setObjectName("label_deactivation")
        self.gridLayout_3.addWidget(self.label_deactivation, 0, 0, 1, 1)
        self.dateTimeEdit_deactivation = QtGui.QDateTimeEdit(self.groupBox_2)
        self.dateTimeEdit_deactivation.setMinimumSize(QtCore.QSize(230, 0))
        self.dateTimeEdit_deactivation.setCalendarPopup(True)
        self.dateTimeEdit_deactivation.setObjectName("dateTimeEdit_deactivation")
        self.gridLayout_3.addWidget(self.dateTimeEdit_deactivation, 0, 1, 1, 1)
        self.toolButton_deactivation = QtGui.QToolButton(self.groupBox_2)
        self.toolButton_deactivation.setObjectName("toolButton_deactivation")
        self.gridLayout_3.addWidget(self.toolButton_deactivation, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 3, 0, 1, 4)
        self.checkBox_temporary_blocked = QtGui.QCheckBox(self.groupBox)
        self.checkBox_temporary_blocked.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkBox_temporary_blocked.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox_temporary_blocked, 2, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.toolButton_activation_now,QtCore.SIGNAL("clicked()"),self.setActivatedTime)
        QtCore.QObject.connect(self.toolButton_deactivation,QtCore.SIGNAL("clicked()"),self.setDeactivatedTime)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Параметры подключаемой услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Параметры подключаемой услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.label_service.setText(QtGui.QApplication.translate("Dialog", "Услуга", None, QtGui.QApplication.UnicodeUTF8))
        self.label_activation.setText(QtGui.QApplication.translate("Dialog", "Дата активаци", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_activation_now.setText(QtGui.QApplication.translate("Dialog", "N", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Dialog", "Закончить действие услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.label_deactivation.setText(QtGui.QApplication.translate("Dialog", "Дата деактивации", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_deactivation.setText(QtGui.QApplication.translate("Dialog", "N", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_temporary_blocked.setText(QtGui.QApplication.translate("Dialog", "Временная блокировка", None, QtGui.QApplication.UnicodeUTF8))
    
    def fixtures(self):
        addonservices = self.connection.get_models("billservice_addonservice")
        self.connection.commit()
        i=0
        for adds in addonservices:
           self.comboBox_service.addItem(unicode(adds.name))
           self.comboBox_service.setItemData(i, QtCore.QVariant(adds.id))
           i+=1
        
        if self.model:
            for i in xrange(self.comboBox_service.count()):
                if self.comboBox_service.itemData(i).toInt()[0]==self.model.service_id:
                    self.comboBox_service.setCurrentIndex(i)
                       

            self.checkBox_temporary_blocked.setChecked(self.model.temporary_blocked is not None)
            if self.model.deactivated:
                self.groupBox_2.setDisabled(True)
            self.dateTimeEdit_activation.setDateTime(self.model.activated)
            
            if self.model.deactivated:
                self.dateTimeEdit_deactivation.setDateTime(self.model.deactivated)
                self.dateTimeEdit_deactivation.setDisabled(True)
                
            self.comboBox_service.setDisabled(True)
        else:
            self.dateTimeEdit_activation.setDateTime(datetime.datetime.now())
            self.dateTimeEdit_deactivation.setDateTime(datetime.datetime.now())
            
    def accept(self):
        if self.model:
            model = self.model
        else:
            model = Object()
            
        model.account_id = self.account_model.id
        model.service_id = self.comboBox_service.itemData(self.comboBox_service.currentIndex()).toInt()[0]
        model.activated = self.dateTimeEdit_activation.dateTime().toPyDateTime()
        if self.model:
            if not self.model.temporary_blocked:
                model.temporary_blocked = "now()" if   self.checkBox_temporary_blocked.isChecked()==True else None
            elif self.checkBox_temporary_blocked.isChecked()==False:
                model.temporary_blocked = None
        else:
            model.temporary_blocked = "now()" if   self.checkBox_temporary_blocked.isChecked()==True else None
            
        
        if self.groupBox_2.isChecked()==True:
            if self.dateTimeEdit_deactivation.dateTime().toPyDateTime()<model.activated:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Дата окончания действия услуги не должна быть меньше даты начала действия"))
                return                
            model.deactivated = self.dateTimeEdit_deactivation.dateTime().toPyDateTime()
            
        try:
            self.connection.save(model, "billservice_accountaddonservice")
            self.connection.commit()
        except Exception, e:
            print e
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Возникла непредвиденная ошибка"))
            return
            
        
        QtGui.QDialog.accept(self)
    
    def setActivatedTime(self):
        self.dateTimeEdit_activation.setDateTime(datetime.datetime.now())

    def setDeactivatedTime(self):
        self.dateTimeEdit_deactivation.setDateTime(datetime.datetime.now())
        
class IPAddressSelectForm(QtGui.QDialog):
    def __init__(self, connection, pool_id):
        super(IPAddressSelectForm, self).__init__()
        self.connection = connection
        self.pool_id = pool_id
        self.selected_ip = None
        self.setObjectName("IPAddressSelectForm")
        self.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, -1)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Свободные IP адреса в выбранном пуле", None, QtGui.QApplication.UnicodeUTF8))
        
        self.tableWidget = tableFormat(self.tableWidget)
        columns=['#', 'IP']
        makeHeaders(columns, self.tableWidget)
        self.refresh()

        
    def accept(self):
        self.selected_ip = unicode(self.tableWidget.item(self.tableWidget.currentRow(),1).text())
        QtGui.QDialog.accept(self)
    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/tp_small.png"))
        if y==0:
            headerItem.id=value
            #headerItem.setCheckState(QtCore.Qt.Unchecked)
        if y!=0:
            headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
        
    def refresh(self):
        items = get_free_addreses_from_pool(self.connection, self.pool_id)
        self.connection.commit()
        self.tableWidget.setRowCount(len(items))
        i=0
        for item in items:
            self.addrow('', i, 0)
            self.addrow(item, i, 1)
            i+=1
            
        self.tableWidget.resizeColumnsToContents()
            
        
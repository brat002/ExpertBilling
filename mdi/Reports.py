#-*-coding=utf-8-*-

import os, sys
from PyQt4 import QtCore, QtGui
from helpers import tableFormat
from helpers import Object as Object
#import mdi_rc

#sys.path.append('d:/projects/mikrobill/webadmin')
#sys.path.append('d:/projects/mikrobill/webadmin/mikrobill')

#os.environ['DJANGO_SETTINGS_MODULE'] = 'mikrobill.settings'

#from billservice.models import Transaction, Account, TransactionType


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
        self.tableWidget.setColumnCount(7)

        headerItem2 = QtGui.QTableWidgetItem()
        headerItem2.setText(QtGui.QApplication.translate("Dialog", "id", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(0,headerItem2)

        headerItem3 = QtGui.QTableWidgetItem()
        headerItem3.setText(QtGui.QApplication.translate("Dialog", "Дата", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(1,headerItem3)

        headerItem4 = QtGui.QTableWidgetItem()
        headerItem4.setText(QtGui.QApplication.translate("Dialog", "Платёжный документ", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(2,headerItem4)

        headerItem5 = QtGui.QTableWidgetItem()
        headerItem5.setText(QtGui.QApplication.translate("Dialog", "Вид платежа", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(3,headerItem5)

        headerItem6 = QtGui.QTableWidgetItem()
        headerItem6.setText(QtGui.QApplication.translate("Dialog", "По тарифу", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(4,headerItem6)

        headerItem7 = QtGui.QTableWidgetItem()
        headerItem7.setText(QtGui.QApplication.translate("Dialog", "Сумма", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(5,headerItem7)
        
        headerItem8 = QtGui.QTableWidgetItem()
        headerItem8.setText(QtGui.QApplication.translate("Dialog", "Комментарий", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(6,headerItem8)
        
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
        
        
        
# -*- coding=utf-8 -*-

from PyQt4 import QtCore, QtGui
import sys
import datetime
import Pyro.core
import Pyro.protocol
import Pyro.constants
import Pyro.errors
from db import Object as Object
from helpers import makeHeaders
from helpers import tableFormat
from helpers import HeaderUtil
from CustomForms import CardPreviewDialog
from CustomForms import ConnectDialog, ConnectionWaiting
from helpers import dateDelim
from mako.template import Template
from ebsWindow import ebsTableWindow
strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
tr_id=0

class CassaEbs(ebsTableWindow):
    def __init__(self, connection):
        columns = ['#', u"Username", u'ФИО', u'Тарифный план', u'Баланс', u'Кредит', u'Улица', u'д.', u'к.', u'кв.']
        initargs = {"setname":"cassa_period", "objname":"CassaEbsMDI", "winsize":(0,0,1024, 642), "wintitle":"Интерфейс кассира", "tablecolumns":columns, "centralwidget":True}
        super(CassaEbs, self).__init__(connection, initargs)
        self.printer = None
    def ebsInterInit(self, initargs):
        
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_4 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName("gridLayout_4")
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
        self.gridLayout_4.addWidget(self.groupBox_filter, 1, 0, 1, 3)

        self.gridLayout_4.addWidget(self.tableWidget, 0, 0, 1, 3)
        self.groupBox_tariffs = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_tariffs.setMinimumSize(QtCore.QSize(450, 0))
        self.groupBox_tariffs.setMaximumSize(QtCore.QSize(16777215, 60))
        self.groupBox_tariffs.setObjectName("groupBox_tariffs")
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_tariffs)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.comboBox_tariff = QtGui.QComboBox(self.groupBox_tariffs)
        self.comboBox_tariff.setObjectName("comboBox_tariff")
        self.gridLayout_3.addWidget(self.comboBox_tariff, 0, 0, 1, 1)
        self.dateTime = QtGui.QDateTimeEdit(self.groupBox_tariffs)
        self.dateTime.setCalendarPopup(True)
        self.dateTime.setDateTime(datetime.datetime.now())
        #self.dateTime.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.dateTime.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        self.gridLayout_3.addWidget(self.dateTime, 0, 1, 1, 1)
        self.pushButton_change_tariff = QtGui.QPushButton(self.groupBox_tariffs)
        self.pushButton_change_tariff.setMaximumSize(QtCore.QSize(75, 16777215))
        self.pushButton_change_tariff.setObjectName("pushButton_change_tariff")
        self.gridLayout_3.addWidget(self.pushButton_change_tariff, 0, 2, 1, 1)

        self.gridLayout_4.addWidget(self.groupBox_tariffs, 2, 0, 1, 2)
        self.groupBox_payment = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_payment.setMinimumSize(QtCore.QSize(400, 0))
        self.groupBox_payment.setObjectName("groupBox_payment")
        self.gridLayout_6 = QtGui.QGridLayout(self.groupBox_payment)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.summ_label = QtGui.QLabel(self.groupBox_payment)
        self.summ_label.setObjectName("summ_label")
        self.gridLayout_6.addWidget(self.summ_label, 1, 0, 1, 1)
        self.lineEdit_summ = QtGui.QLineEdit(self.groupBox_payment)
        self.lineEdit_summ.setObjectName("lineEdit_summ")
        self.gridLayout_6.addWidget(self.lineEdit_summ, 1, 1, 1, 2)
        self.payed_document_label = QtGui.QLabel(self.groupBox_payment)
        self.payed_document_label.setObjectName("payed_document_label")
        self.gridLayout_6.addWidget(self.payed_document_label, 3, 0, 1, 1)
        self.lineEdit_document = QtGui.QLineEdit(self.groupBox_payment)
        self.lineEdit_document.setFrame(True)
        self.lineEdit_document.setObjectName("lineEdit_document")
        self.gridLayout_6.addWidget(self.lineEdit_document, 3, 1, 1, 2)
        self.label = QtGui.QLabel(self.groupBox_payment)
        self.label.setObjectName("label")
        self.gridLayout_6.addWidget(self.label, 5, 0, 1, 1)
        self.lineEdit_description= QtGui.QLineEdit(self.groupBox_payment)
        self.lineEdit_description.setObjectName("lineEdit_description")
        self.gridLayout_6.addWidget(self.lineEdit_description, 5, 1, 1, 2)
        self.label_paymend_date = QtGui.QLabel(self.groupBox_payment)
        self.label_paymend_date.setObjectName("label_paymend_date")
        self.gridLayout_6.addWidget(self.label_paymend_date, 7, 0, 1, 1)
        self.dateTimeEdit_paymend_date = QtGui.QDateTimeEdit(self.groupBox_payment)
        self.dateTimeEdit_paymend_date.setFrame(True)
        self.dateTimeEdit_paymend_date.setDateTime(QtCore.QDateTime(QtCore.QDate(2009, 1, 1), QtCore.QTime(0, 0, 0)))
        self.dateTimeEdit_paymend_date.setCalendarPopup(True)
        self.dateTimeEdit_paymend_date.setObjectName("dateTimeEdit_paymend_date")
        self.checkBox_autotime = QtGui.QCheckBox(self.groupBox_payment)
        self.gridLayout_6.addWidget(self.dateTimeEdit_paymend_date, 7, 1, 1, 2)
        self.gridLayout_6.addWidget(self.checkBox_autotime, 7, 3)
        self.label_promise = QtGui.QLabel(self.groupBox_payment)
        self.label_promise.setObjectName("label_promise")
        self.gridLayout_6.addWidget(self.label_promise, 8, 0, 1, 1)
        self.checkBox_promise = QtGui.QCheckBox(self.groupBox_payment)
        self.checkBox_promise.setObjectName("checkBox_promise")
        self.gridLayout_6.addWidget(self.checkBox_promise, 8, 1, 1, 1)
        self.label_end_promise = QtGui.QLabel(self.groupBox_payment)
        self.label_end_promise.setObjectName("label_end_promise")
        self.gridLayout_6.addWidget(self.label_end_promise, 9, 0, 1, 1)
        self.dateTimeEdit_end_promise = QtGui.QDateTimeEdit(self.groupBox_payment)
        self.dateTimeEdit_end_promise.setCalendarPopup(True)
        self.dateTimeEdit_end_promise.setObjectName("dateTimeEdit_end_promise")
        
        self.gridLayout_6.addWidget(self.dateTimeEdit_end_promise, 9, 1, 1, 2)
        self.checkBox_promise_infinite = QtGui.QCheckBox(self.groupBox_payment)
        self.checkBox_promise_infinite.setObjectName("checkBox_promise_infinite")
        self.gridLayout_6.addWidget(self.checkBox_promise_infinite, 9, 3, 1, 1)
        self.pushButton_pay = QtGui.QPushButton(self.groupBox_payment)
        self.pushButton_pay.setObjectName("pushButton_pay")
        self.gridLayout_6.addWidget(self.pushButton_pay, 10, 0, 1, 1)
        self.checkBox = QtGui.QCheckBox(self.groupBox_payment)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout_6.addWidget(self.checkBox, 10, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_payment, 2, 2, 2, 1)
        self.groupBox_limites = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_limites.setObjectName("groupBox_limites")
        self.gridLayout_5 = QtGui.QGridLayout(self.groupBox_limites)
        self.gridLayout_5.setObjectName("gridLayout_5")
        #self.label_limites = QtGui.QLabel(self.groupBox_limites)
        #self.label_limites.setObjectName("label_limites")
        #self.label_limites.setMaximumWidth(275)
        #self.label_limites.setMinimumWidth(275)
        self.textEdit_limites = QtGui.QTextEdit(self.groupBox_limites)
        self.textEdit_limites.setDisabled(True)
        self.gridLayout_5.addWidget(self.textEdit_limites, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_limites, 3, 0, 1, 1)
        self.groupBox_prepaid_traffic = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_prepaid_traffic.setObjectName("groupBox_prepaid_traffic")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_prepaid_traffic)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.textEdit_prepaid_traffic = QtGui.QTextEdit(self.groupBox_limites)
        self.textEdit_prepaid_traffic.setDisabled(True)
        self.gridLayout_2.addWidget(self.textEdit_prepaid_traffic, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_prepaid_traffic, 3, 1, 1, 1)
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
        self.connect(self.pushButton_pay, QtCore.SIGNAL("clicked()"), self.pay)
        self.connect(self.pushButton_search, QtCore.SIGNAL("clicked()"), self.refreshTable)
        self.connect(self.pushButton_change_tariff, QtCore.SIGNAL("clicked()"), self.createAccountTarif)
        QtCore.QObject.connect(self.checkBox_promise,QtCore.SIGNAL("stateChanged(int)"),self.promise_actions)
        QtCore.QObject.connect(self.checkBox_autotime,QtCore.SIGNAL("stateChanged(int)"),self.checkAutoTime)
        
        QtCore.QObject.connect(self.checkBox_promise_infinite,QtCore.SIGNAL("stateChanged(int)"),self.promise_actions)
        
        QtCore.QObject.connect(self.tableWidget,QtCore.SIGNAL("itemSelectionChanged()"), self.update_info)
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.restoreWindow()
        self.refreshTariffs()
        self.fixtures()
        self.promise_actions()
        self.checkAutoTime()

        
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
        self.groupBox_tariffs.setTitle(QtGui.QApplication.translate("MainWindow", "Перевести на другой тарифный план", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_change_tariff.setText(QtGui.QApplication.translate("MainWindow", "Перевести", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_payment.setTitle(QtGui.QApplication.translate("MainWindow", "Платёжные данные", None, QtGui.QApplication.UnicodeUTF8))
        self.summ_label.setText(QtGui.QApplication.translate("MainWindow", "Сумма", None, QtGui.QApplication.UnicodeUTF8))
        self.payed_document_label.setText(QtGui.QApplication.translate("MainWindow", "На основании док.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Комментарий", None, QtGui.QApplication.UnicodeUTF8))
        self.label_paymend_date.setText(QtGui.QApplication.translate("MainWindow", "Дата платежа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_promise.setText(QtGui.QApplication.translate("MainWindow", "Обещаный платёж", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_promise.setText(QtGui.QApplication.translate("MainWindow", "Да", None, QtGui.QApplication.UnicodeUTF8))
        self.label_end_promise.setText(QtGui.QApplication.translate("MainWindow", "Истекает", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_promise_infinite.setText(QtGui.QApplication.translate("MainWindow", "Никогда", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_pay.setText(QtGui.QApplication.translate("MainWindow", "Зачислить", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("MainWindow", "Печать", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_limites.setTitle(QtGui.QApplication.translate("MainWindow", "Лимиты", None, QtGui.QApplication.UnicodeUTF8))
        self.textEdit_limites.setPlainText(QtGui.QApplication.translate("MainWindow", "Нет данных", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_prepaid_traffic.setTitle(QtGui.QApplication.translate("MainWindow", "Предоплаченный трафик", None, QtGui.QApplication.UnicodeUTF8))
        self.textEdit_prepaid_traffic.setPlainText(QtGui.QApplication.translate("MainWindow", "Функция недоступна", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_autotime.setText(QtGui.QApplication.translate("MainWindow", "Auto", None, QtGui.QApplication.UnicodeUTF8))
        
    def promise_actions(self):
        if self.checkBox_promise.isChecked():
            self.dateTimeEdit_end_promise.setEnabled(True)
            self.checkBox_promise_infinite.setEnabled(True)
            if self.checkBox_promise_infinite.isChecked():
                self.dateTimeEdit_end_promise.setEnabled(False)
            
        else:
            self.dateTimeEdit_end_promise.setEnabled(False)
            self.checkBox_promise_infinite.setEnabled(False)
    
    def update_info(self):
        account = self.getSelectedId()
        if account:
            limites = self.connection.get_limites(account)
            if not limites: self.textEdit_limites.setPlainText(u"Нет данных"); return
            r=[]
            for limit in limites:
                r.append(u"Название %s Размер %s Расходовано %s Начало %s Конец %s" % (limit["limit_name"], limit["limit_size"], limit["size"] or "0", limit["settlement_period_start"].strftime(self.strftimeFormat),limit["settlement_period_end"].strftime(self.strftimeFormat) ))
            #self.label_limites.setText('\n'.join(r))
            self.textEdit_limites.setPlainText('\n'.join(r))
            #prepaid = self.connection.get_prepaid(account)
        else:
            self.textEdit_limites.setPlainText(u"Нет данных")
        
    
    def checkAutoTime(self):
        if self.checkBox_autotime.isChecked()==True:
            self.dateTimeEdit_paymend_date.setDisabled(True)
        else:
            self.dateTimeEdit_paymend_date.setDisabled(False)
                
    def refreshTariffs(self):
        #accounts = self.connection.get_models("billservice_account")
        tariffs = self.connection.sql("SELECT id, name from billservice_tariff WHERE deleted IS NOT TRUE;")
        self.connection.commit()
        i=0
        for tariff in tariffs:
            self.comboBox_tariff.addItem("%s" % tariff.name)
            self.comboBox_tariff.setItemData(i, QtCore.QVariant(tariff.id))
            i+=1
        #self.refresh()
            
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
            self.addrow(account.ballance, i, 4, enabled=account.status)
            self.addrow(account.credit, i, 5, enabled=account.status)
            #self.addrow(account.city, i, 6, enabled=account.status)
            self.addrow(account.street, i, 6, enabled=account.status)
            self.addrow(account.house, i, 7, enabled=account.status)
            self.addrow(account.house_bulk, i, 8, enabled=account.status)
            self.addrow(account.room, i, 9, enabled=account.status)

            i+=1
  
        
    def pay(self):
        if self.getSelectedId() and QtGui.QMessageBox.question(self, u"Произвести платёж?" , u"Вы уверены, что хотите произвести платёж?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            account = self.getSelectedId()
            document = unicode(self.lineEdit_document.text())
            description = unicode(self.lineEdit_description.text())
            if self.checkBox_autotime.isChecked()==False:
                created = unicode(self.dateTimeEdit_paymend_date.dateTime().toPyDateTime())
            else:
                created = "now()"
            promise = self.checkBox_promise.isChecked()
            summ = float(unicode(self.lineEdit_summ.text()))
            if self.checkBox_promise.isChecked() and not self.checkBox_promise_infinite.isChecked():
                end_promise = self.dateTimeEdit_end_promise.dateTime().toPyDateTime()
            else:
                end_promise = None

                
            global tr_id
            
            tr_id = self.connection.pay(account, summ, document, description, created, promise, end_promise, self.systemuser_id)
            
            if tr_id!=False:
                QtGui.QMessageBox.information(self, unicode(u"Ок"), unicode(u"Платёж произведён успешно."))
                if self.checkBox.isChecked() and QtGui.QMessageBox.question(self, u"Печатать чек?" , u"Напечатать чек?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
                    if not self.printer:
                        QtGui.QMessageBox.warning(self, unicode(u"Ок"), unicode(u"Настройка принтера не была произведена!"))
                        self.getPrinter()
                    if self.printer:
                        self.cheque_print()
                
                self.lineEdit_summ.setText("")
                self.lineEdit_document.setText("")
                self.lineEdit_description.setText("")
                
                self.refreshTable()
            else:
                QtGui.QMessageBox.critical(self, unicode(u"Ошибка"), unicode(u"Возникла неизвестаня ошибка. Обратитесь к администратору."))
            self.lineEdit_summ.setFocus(True)
            
    
    def createAccountTarif(self):
        account_id = self.getSelectedId()
        tarif_id = unicode(self.comboBox_tariff.itemData(self.comboBox_tariff.currentIndex()).toInt()[0])
        if account_id and tarif_id and QtGui.QMessageBox.question(self, u"Произвести перевод пользователя на нвоый тарифный план?" , u"Вы уверены, что хотите перевести пользователя на выбранный тарифный план?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            dtime = self.dateTime.dateTime().toPyDateTime()
            self.connection.createAccountTarif(account_id, tarif_id, dtime)
            self.connection.commit()
            self.refreshTable()
            self.dateTime.setDateTime(datetime.datetime.now())
        

    def cheque_print(self):
        if not self.printer:
            QtGui.QMessageBox.warning(self, unicode(u"Ок"), unicode(u"Настройка принтера не была произведена!"))
            return
        account_id = self.getSelectedId()
        if account_id:
            template = self.connection.get('SELECT body FROM billservice_template WHERE type_id=5')
            templ = Template(unicode(template.body), input_encoding='utf-8')
            account = self.connection.get("SELECT * FROM billservice_account WHERE id=%s LIMIT 1" % account_id)

            tarif = self.connection.get("SELECT name FROM billservice_tariff WHERE id=get_tarif(%s)" % account.id)
            self.connection.commit()
            sum = 10000

            data=templ.render_unicode(account=account, tarif=tarif, transaction_id=tr_id.id, sum=unicode(self.lineEdit_summ.text()), document = unicode(self.lineEdit_document.text()), created=datetime.datetime.now().strftime(strftimeFormat))
            
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
    

        
class antiMungeValidator(Pyro.protocol.DefaultConnValidator):
    def __init__(self):
        Pyro.protocol.DefaultConnValidator.__init__(self)

    def createAuthToken(self, authid, challenge, peeraddr, URI, daemon):

        return authid

    def mungeIdent(self, ident):
        return ident
      

def login():
    child = ConnectDialog()
    while True:

        if child.exec_() == 1:
            waitchild = ConnectionWaiting()
            waitchild.show()
            try:
                connection = Pyro.core.getProxyForURI("PYROLOC://%s:7766/rpc" % unicode(child.address))
                password = unicode(child.password.toHex())
                #f = open('tmp', 'wb')
                #f.write(child.password.toHex())
                connection._setNewConnectionValidator(antiMungeValidator())
                connection._setIdentification("%s:%s:1" % (str(child.name), str(child.password.toHex())))
                connection.test()
                waitchild.hide()
                return connection

            except Exception, e:
                #print "login connection error"
                waitchild.hide()
                if isinstance(e, Pyro.errors.ConnectionDeniedError):
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
    connection.commit()
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


        

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
strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
tr_id=0

#sys.stderr=sys.stdout
class MainWindow(QtGui.QMainWindow):
    def __init__(self, connection):
        super(MainWindow, self).__init__()
        self.connection = connection
        self.resize(912, 539)
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
        self.pushButton = QtGui.QPushButton(self.groupBox_filter)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 10, 1, 1)
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
        self.gridLayout_4.addWidget(self.groupBox_filter, 0, 0, 1, 3)
        
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget=tableFormat(self.tableWidget)

        self.gridLayout_4.addWidget(self.tableWidget, 2, 0, 1, 3)
        self.groupBox_pay = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_pay.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_pay.setObjectName("groupBox_pay")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_pay)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_sum = QtGui.QLabel(self.groupBox_pay)
        self.label_sum.setObjectName("label_sum")
        self.gridLayout_2.addWidget(self.label_sum, 0, 0, 1, 1)
        self.lineEdit_sum = QtGui.QLineEdit(self.groupBox_pay)
        self.lineEdit_sum.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_sum.setObjectName("lineEdit_sum")
        self.gridLayout_2.addWidget(self.lineEdit_sum, 0, 1, 1, 1)
        self.pushButton_pay = QtGui.QPushButton(self.groupBox_pay)
        self.pushButton_pay.setObjectName("pushButton_pay")
        self.gridLayout_2.addWidget(self.pushButton_pay, 0, 2, 1, 1)
        self.pushButton_print = QtGui.QPushButton(self.groupBox_pay)
        self.pushButton_print.setObjectName("pushButton_print")
        self.pushButton_print.setHidden(True)
        self.gridLayout_2.addWidget(self.pushButton_print, 0, 3, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_pay, 3, 1, 1, 1)
        self.groupBox_tariffs = QtGui.QGroupBox(self.centralwidget)
        self.groupBox_tariffs.setMinimumSize(QtCore.QSize(450, 0))
        self.groupBox_tariffs.setMaximumSize(QtCore.QSize(16777215, 16777215))
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
        self.gridLayout_4.addWidget(self.groupBox_tariffs, 3, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        #self.fixtures()
        #self.connect(self.comboBox_account, QtCore.SIGNAL("currentIndexChanged(int)"), self.refresh)
        self.connect(self.pushButton_pay, QtCore.SIGNAL("clicked()"), self.pay)
        bhdr = HeaderUtil.getBinaryHeader("cashier_frame_header")
        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        self.connect(self.pushButton, QtCore.SIGNAL("clicked()"), self.refreshTable)
        self.connect(self.pushButton_change_tariff, QtCore.SIGNAL("clicked()"), self.createAccountTarif)
        self.connect(self.pushButton_print, QtCore.SIGNAL("clicked()"), self.cheque_print)
        HeaderUtil.nullifySaved("cashier_frame_header")
        #print "empty=", bhdr.isEmpty()
        if not bhdr.isEmpty():
            HeaderUtil.setBinaryHeader("cashier_frame_header", bhdr)
            HeaderUtil.getHeader("cashier_frame_header", self.tableWidget)
        #HeaderUtil.getHeader("account_frame_header", self.tableWidget)
        self.setTabOrder(self.lineEdit_fullname, self.lineEdit_username)
        self.setTabOrder(self.lineEdit_username, self.lineEdit_city)
        self.setTabOrder(self.lineEdit_city, self.lineEdit_street)
        self.setTabOrder(self.lineEdit_street, self.lineEdit_house)
        self.setTabOrder(self.lineEdit_house, self.lineEdit_bulk)
        self.setTabOrder(self.lineEdit_bulk, self.lineEdit_room)
        self.setTabOrder(self.lineEdit_room, self.pushButton)
        self.setTabOrder(self.pushButton, self.comboBox_tariff)
        self.setTabOrder(self.comboBox_tariff, self.pushButton_change_tariff)
        self.setTabOrder(self.pushButton_change_tariff, self.lineEdit_sum)
        self.setTabOrder(self.lineEdit_sum, self.pushButton_pay)
        self.setTabOrder(self.pushButton_pay, self.pushButton_print)
        self.setTabOrder(self.pushButton_print, self.tableWidget)
        self.restoreWindow()
        self.refreshTariffs()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Интерфейс кассира", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_filter.setTitle(QtGui.QApplication.translate("MainWindow", "Фильтр", None, QtGui.QApplication.UnicodeUTF8))
        self.label_fullname.setText(QtGui.QApplication.translate("MainWindow", "ФИО", None, QtGui.QApplication.UnicodeUTF8))
        self.label_username.setText(QtGui.QApplication.translate("MainWindow", "Username", None, QtGui.QApplication.UnicodeUTF8))
        self.label_city.setText(QtGui.QApplication.translate("MainWindow", "Город", None, QtGui.QApplication.UnicodeUTF8))
        self.label_street.setText(QtGui.QApplication.translate("MainWindow", "Улица", None, QtGui.QApplication.UnicodeUTF8))
        self.label_house.setText(QtGui.QApplication.translate("MainWindow", "Дом", None, QtGui.QApplication.UnicodeUTF8))
        self.label_room.setText(QtGui.QApplication.translate("MainWindow", "Квартира", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bulk.setText(QtGui.QApplication.translate("MainWindow", "Корпус", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "Показать", None, QtGui.QApplication.UnicodeUTF8))

        columns=['#', u"Username", u'ФИО', u'Тарифный план', u'Баланс', u'Кредит', u'Город', u'Улица', u'д.', u'к.', u'кв.']
        makeHeaders(columns, self.tableWidget)
         
        self.groupBox_pay.setTitle(QtGui.QApplication.translate("MainWindow", "Зачислить", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sum.setText(QtGui.QApplication.translate("MainWindow", "Сумма", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_pay.setText(QtGui.QApplication.translate("MainWindow", "Зачислить", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_print.setText(QtGui.QApplication.translate("MainWindow", "Печать чека", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_tariffs.setTitle(QtGui.QApplication.translate("MainWindow", "Перевести на другой тарифный план", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_change_tariff.setText(QtGui.QApplication.translate("MainWindow", "Перевести", None, QtGui.QApplication.UnicodeUTF8))

    def refreshTariffs(self):
        #accounts = self.connection.get_models("billservice_account")
        tariffs = self.connection.get_models("billservice_tariff")
        self.connection.commit()
        i=0
        for tariff in tariffs:
            self.comboBox_tariff.addItem("%s" % tariff.name)
            self.comboBox_tariff.setItemData(i, QtCore.QVariant(tariff.id))
            i+=1
        #self.refresh()
            
    def refresh(self):
        selected_id = unicode(self.comboBox_account.itemData(self.comboBox_account.currentIndex()).toInt()[0])
        #print "id=", selected_id, self.comboBox_account.currentIndex()
        account = self.connection.get_model(selected_id, "billservice_account")
        self.lineEdit_balance.setText(unicode(account.ballance))
        self.lineEdit_label.setText(unicode(account.credit))
    
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
            self.addrow(account.city, i, 6, enabled=account.status)
            self.addrow(account.street, i, 7, enabled=account.status)
            self.addrow(account.house, i, 8, enabled=account.status)
            self.addrow(account.house_bulk, i, 9, enabled=account.status)
            self.addrow(account.room, i, 10, enabled=account.status)

            i+=1


    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())      
        
    def pay(self):
        if self.getSelectedId() and QtGui.QMessageBox.question(self, u"Произвести платёж?" , u"Вы уверены, что хотите произвести платёж?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            account = self.getSelectedId()
            global tr_id
            tr_id = self.connection.pay(unicode(account), float(unicode(self.lineEdit_sum.text())), unicode(u"Платёж проведён кассиром"))

            if tr_id!=False:
                QtGui.QMessageBox.information(self, unicode(u"Ок"), unicode(u"Платёж произведён успешно."))
                if QtGui.QMessageBox.question(self, u"Печатать чек?" , u"Напечатать чек?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
                    self.cheque_print()
                
                self.lineEdit_sum.setText("")
                self.refreshTable()
            else:
                QtGui.QMessageBox.critical(self, unicode(u"Ошибка"), unicode(u"Возникла неизвестаня ошибка. Обратитесь к администратору."))
            

    def createAccountTarif(self):
        account_id = self.getSelectedId()
        tarif_id = unicode(self.comboBox_tariff.itemData(self.comboBox_tariff.currentIndex()).toInt()[0])
        if account_id and tarif_id and QtGui.QMessageBox.question(self, u"Произвести перевод пользователя на нвоый тарифный план?" , u"Вы уверены, что хотите перевести пользователя на выбранный тарифный план?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            datetime = self.dateTime.dateTime().toPyDateTime()
            self.connection.createAccountTarif(account_id, tarif_id, datetime)
            self.connection.commit()
            self.refreshTable()
        

    def cheque_print(self):
        account_id = self.getSelectedId()
        if account_id:
            template = self.connection.get('SELECT body FROM billservice_template WHERE type_id=5;')
            templ = Template(unicode(template.body), input_encoding='utf-8')
            account = self.connection.get("SELECT * FROM billservice_account WHERE id=%s LIMIT 1;" % account_id)

            tarif = self.connection.get("SELECT name FROM billservice_tariff WHERE id=get_tarif(%s);" % account.id)
            self.connection.commit()
            #sum = 10000

            data=templ.render_unicode(account=account, tarif=tarif, transaction_id=tr_id.id, sum=unicode(self.lineEdit_sum.text()), document = u"Платёж в кассу", created=datetime.datetime.now().strftime(strftimeFormat))

            file= open('templates/tmp/temp.html', 'wb')
            file.write(data.encode("utf-8", 'replace'))
            file.flush()
            a=CardPreviewDialog(url="templates/tmp/temp.html")
            a.exec_()
            
    def restoreWindow(self):
        #print 'restore geometry'
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        val=settings.value("window-geometry-%s" % unicode(self.objectName()), QtCore.QVariant(QtCore.QByteArray())).toByteArray()
        #print val
        self.restoreGeometry(val)
        
    def closeEvent(self, event):
        #self.thread.terminate()
        #print "Close Window"
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        settings.setValue("window-geometry-%s" % unicode(self.objectName()), QtCore.QVariant(self.saveGeometry()))
        event.accept()

    def saveHeader(self, *args):
        #if self.tableWidget.rowCount():
        HeaderUtil.saveHeader("cashier_frame_header", self.tableWidget)
        
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
                connection._setIdentification("%s:%s" % (str(child.name), str(child.password.toHex())))
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
    try:
        global mainwindow
        mainwindow = MainWindow(connection=connection)
        mainwindow.show()
        app.setStyleSheet(open("./cassa_style.qss","r").read())
        sys.exit(app.exec_())
        connection.commit()
    except Exception, ex:
        print "main-----------"
        print ex


        
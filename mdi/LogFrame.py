#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

from ebsWindow import ebsTableWindow
from helpers import tableFormat
import datetime, calendar
from db import Object as Object
from helpers import makeHeaders
from helpers import dateDelim
from helpers import HeaderUtil

class MessageDialog(QtGui.QDialog):
    def __init__(self, accounts=[], model=None,connection=None):
        super(MessageDialog, self).__init__()
        self.accounts = accounts
        self.model = model
        self.connection = connection
        self.setObjectName("MessageDialog")
        self.resize(716, 287)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(0, 9, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.textEdit = QtGui.QTextEdit(self)
        self.textEdit.setAutoFormatting(QtGui.QTextEdit.AutoNone)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 1, 1, 1)
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.checkBox_public = QtGui.QCheckBox(self.groupBox)
        self.checkBox_public.setObjectName("checkBox_public")
        self.gridLayout_2.addWidget(self.checkBox_public, 0, 1, 1, 1)
        self.checkBox_private = QtGui.QCheckBox(self.groupBox)
        self.checkBox_private.setObjectName("checkBox_private")
        self.gridLayout_2.addWidget(self.checkBox_private, 1, 1, 1, 1)
        self.checkBox_agent = QtGui.QCheckBox(self.groupBox)
        self.checkBox_agent.setObjectName("checkBox_agent")
        self.gridLayout_2.addWidget(self.checkBox_agent, 2, 1, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.spinBox = QtGui.QSpinBox(self.groupBox_2)
        self.spinBox.setMaximum(99999999)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout_3.addWidget(self.spinBox, 0, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_2, 0, 2, 3, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 1, 1, 1)
        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 0, 0, 2, 1)


        self.retranslateUi()
        self.fixtures()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Сообщение", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Параметры сообщения", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_public.setText(QtGui.QApplication.translate("Dialog", "Опубликовать в публичной части веб-кабинета(всем)", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_private.setText(QtGui.QApplication.translate("Dialog", "Опубликовать в приватной части веб-кабинета", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_agent.setText(QtGui.QApplication.translate("Dialog", "Отправить через EBS Agent", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Dialog", "Параметры отображения", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Срок жизни(минут)", None, QtGui.QApplication.UnicodeUTF8))
        
        
    def fixtures(self):
        if self.model:
            self.textEdit.setPlainText(self.model.body)
            #print self.model.public
            self.checkBox_public.setChecked(self.model.public)
            self.checkBox_private.setChecked(self.model.private)
            self.checkBox_agent.setChecked(self.model.agent)
            self.buttonBox.setDisabled(True)
        if self.accounts:
            accounts = self.connection.sql("SELECT username FROM billservice_account WHERE id in %s ORDER BY username ASC" % str(self.accounts).replace("[","(").replace("]",")"))
            self.connection.commit()
            for account in accounts:
                item = QtGui.QListWidgetItem(unicode(account.username))
                self.listWidget.addItem(item)
        elif self.model:
            accounts = self.connection.sql("SELECT username FROM billservice_account WHERE id in (SELECT account_id FROM billservice_accountviewednews WHERE news_id=%s)" % self.model.id)
            self.connection.commit()
            for account in accounts:
                item = QtGui.QListWidgetItem(unicode(account.username))
                self.listWidget.addItem(item)
        
            
    def accept(self):
        body = self.textEdit.toPlainText()
        #print body
        
        if not body:
            QtGui.QDialog.accept(self)
            return

        if self.checkBox_agent.isChecked()==False and self.checkBox_public.isChecked()==False and self.checkBox_private.isChecked()==False:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Выберите хотя бы один способ получения сообщения абонентами."))
            return
        
        if self.model:
            news_model = self.model
        else:
            news_model = Object()
            
        news_model.body = unicode(body)
        if self.spinBox.value():
            news_model.age = datetime.datetime.now()+datetime.timedelta(minutes=self.spinBox.value())
        news_model.created = "now()"
        if self.checkBox_public.isChecked()==True or (self.accounts and (self.checkBox_public.isChecked() or self.checkBox_private.isChecked())):
            news_model.id = self.connection.save(news_model, "billservice_news")
            
        if self.checkBox_public.isChecked()==True:
            news_model.public = True
            self.connection.save(news_model, "billservice_news")
            
        if not self.model and self.accounts and (self.checkBox_private.isChecked() or self.checkBox_agent.isChecked()):
            if self.checkBox_private.isChecked()==True: 
                news_model.private = True
            if self.checkBox_agent.isChecked()==True:
                news_model.agent = True
            self.connection.save(news_model, "billservice_news")
            if self.model:
                QtGui.QDialog.accept(self)
            account_model = Object()
            account_model.news_id = news_model.id
            account_model.viewed = False
            for account in self.accounts:
                account_model.account_id = account
                self.connection.save(account_model, "billservice_accountviewednews")
                self.connection.commit()
        elif not self.accounts and (self.checkBox_private.isChecked() or self.checkBox_agent.isChecked()):
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Это сообщение будет помечено только как публичное. Для посылки приватных сообщений воспользуйтесь этой опцией из окна Пользователи и тарифы"))
        QtGui.QDialog.accept(self)




class LogViewEbs(ebsTableWindow):
    def __init__(self, connection):
        self.connection = connection
        columns=['Id', u'Дата', u'Пользователь', u'Сообщение']
        initargs = {"setname":"messages_frame", "objname":"LogViewEbs", "winsize":(0,0,827,476), "wintitle":"Лог событий", "tablecolumns":columns, "tablesize":(0,0,821,401)}
        super(LogViewEbs, self).__init__(connection, initargs)
        
    def ebsInterInit(self, initargs):

        self.systemusers = {}
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
            self.date_start.setDateTime(settings.value("logview_date_start", QtCore.QVariant(QtCore.QDateTime(2000,1,1,0,0))).toDateTime())
            self.date_end.setDateTime(settings.value("logview_date_end", QtCore.QVariant(QtCore.QDateTime(2000,1,1,0,0))).toDateTime())
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



        self.label_systemuser = QtGui.QLabel(self)
        self.label_systemuser.setMargin(10)
           
        self.comboBox_systemuser = QtGui.QComboBox(self)
        
        
        self.go_pushButton = QtGui.QPushButton(self)
        self.go_pushButton.setGeometry(QtCore.QRect(590,40,101,25))
        self.go_pushButton.setObjectName("go_pushButton")        
        #self.system_transactions_checkbox = QtGui.QCheckBox(self)
        #self.system_transactions_checkbox.setObjectName("system_transactions_checkbox")

        self.toolBar = QtGui.QToolBar(self)      
        
        
        self.toolBar.addWidget(self.label_systemuser)
        self.toolBar.addWidget(self.comboBox_systemuser)
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
        self.fixtures()
        #self.tableWidget
        
    def ebsPostInit(self, initargs):
        #self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_message)
        self.connect(self.tableWidget, QtCore.SIGNAL("itemSelectionChanged ()"), self.showMessage)

        self.connect(self.go_pushButton, QtCore.SIGNAL("clicked()"), self.refresh)
        actList=[]
        objDict = {}
        
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        
        self.plainTextEdit = QtGui.QPlainTextEdit(self)
        
        self.gridLayout.addWidget(self.tableWidget,1,0,1,1)
        self.gridLayout.addWidget(self.plainTextEdit,2,0,1,1)
        
        self.setCentralWidget(self.centralwidget)
        
        self.actionCreator(actList, objDict)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.delNodeLocalAction()
        
        
    def retranslateUI(self, initargs):
        super(LogViewEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.date_start_label.setText(QtGui.QApplication.translate("Dialog", "С", None, QtGui.QApplication.UnicodeUTF8))
        self.date_end_label.setText(QtGui.QApplication.translate("Dialog", "По", None, QtGui.QApplication.UnicodeUTF8))
        self.go_pushButton.setText(QtGui.QApplication.translate("Dialog", "Показать", None, QtGui.QApplication.UnicodeUTF8))
        self.date_end.setDisplayFormat(QtGui.QApplication.translate("Dialog", self.datetimeFormat, None, QtGui.QApplication.UnicodeUTF8))
        self.date_start.setDisplayFormat(QtGui.QApplication.translate("Dialog", self.datetimeFormat, None, QtGui.QApplication.UnicodeUTF8))
        self.label_systemuser.setText(QtGui.QApplication.translate("Dialog", "Пользователь", None, QtGui.QApplication.UnicodeUTF8))
        
    def add_message(self):
        child=MessageDialog(connection=self.connection)
        child.exec_()
        #self.refresh()

    def showMessage(self):
        
        self.plainTextEdit.setPlainText(unicode(self.tableWidget.item(self.tableWidget.currentRow(),3).text()))
        

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/sp.png"))
        self.tableWidget.setItem(x,y,headerItem)

    def fixtures(self):
        systemusers = self.connection.get_models("billservice_systemuser")
        self.connection.commit()
         
        self.comboBox_systemuser.addItem(u"--Все--")
        self.comboBox_systemuser.setItemData(0, QtCore.QVariant(0))
        i=1
        for systemuser in systemusers:
            self.systemusers[systemuser.id] = systemuser.username
            self.comboBox_systemuser.addItem(systemuser.username)
            self.comboBox_systemuser.setItemData(i, QtCore.QVariant(systemuser.id))
            i+=1
            
    def refresh(self):
        #self.tableWidget.setSortingEnabled(False)
        self.statusBar().showMessage(u"Идёт получение данных")
        systemuser_id = self.comboBox_systemuser.itemData(self.comboBox_systemuser.currentIndex()).toInt()[0]
        start_date = self.date_start.dateTime().toPyDateTime()
        end_date = self.date_end.dateTime().toPyDateTime()
        messages = self.connection.get_log_messages(systemuser_id=systemuser_id, start_date=start_date, end_date=end_date)
        #print self.connection
        self.connection.commit()
        self.tableWidget.setRowCount(len(messages))
        #.values('id','user', 'username', 'ballance', 'credit', 'firstname','lastname', 'vpn_ip_address', 'ipn_ip_address', 'suspended', 'status')[0:cnt]
        i=0
        for message in messages:
            #print message.systemuser_id
            self.addrow(message.id, i,0)
            self.addrow(message.created.strftime(self.strftimeFormat), i,1)
            self.addrow(self.systemusers.get(message.systemuser_id,""), i,2)
            self.addrow(message.text, i,3)
            #self.addrow(message.public, i,2)
            #self.addrow(message.private, i,3)
            #self.addrow(message.agent, i,4)        
            #self.addrow(message.body[0:100], i,5)         
            #self.addrow(period.length, i,5)
            #self.tableWidget.setRowHeight(i, 17)
            #self.tableWidget.setColumnHidden(0, True)
            #self.tableWidget.setRowHeight(i, 14)
            i+=1
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader(self.setname, self.tableWidget)
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue("logview_date_start", QtCore.QVariant(self.date_start.dateTime()))
            settings.setValue("logview_date_end", QtCore.QVariant(self.date_end.dateTime()))
        except Exception, ex:
            print "Transactions settings save error: ", ex
        self.statusBar().showMessage(u"Готово")
        
    def delNodeLocalAction(self):
        #super(LogViewEbs, self).delNodeLocalAction([self.delAction])
        pass


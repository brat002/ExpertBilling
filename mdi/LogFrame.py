#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

from ebsWindow import ebsTableWindow
from helpers import tableFormat
import datetime, calendar
from db import Object as Object
from helpers import makeHeaders
from helpers import dateDelim
from helpers import HeaderUtil
from customwidget import CustomDateTimeWidget





class LogViewEbs(ebsTableWindow):
    def __init__(self, connection):
        self.connection = connection
        columns=['Id', u'Дата', u"Действие",  u'Пользователь', u'Сообщение']
        initargs = {"setname":"messages_frame", "objname":"LogViewEbs", "winsize":(0,0,827,476), "wintitle":"Лог событий", "tablecolumns":columns, "tablesize":(0,0,821,401)}
        super(LogViewEbs, self).__init__(connection, initargs)
        
    def ebsInterInit(self, initargs):

        self.systemusers = {}
        dt_now = datetime.datetime.now()
        
        self.date_start = CustomDateTimeWidget()
        #self.date_start.setGeometry(QtCore.QRect(420,9,161,20))
        #self.date_start.setCalendarPopup(True)
        self.date_start.setObjectName("date_start")
        #self.date_start.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)

        self.date_end = CustomDateTimeWidget()
        #self.date_end.setGeometry(QtCore.QRect(420,42,161,20))
        self.date_end.setDate(QtCore.QDate(dt_now.year, dt_now.month, dt_now.day))
        #self.date_end.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        #self.date_end.setCalendarPopup(True)
        self.date_end.setObjectName("date_end")
        #self.date_end.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        
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
        
        self.plainTextEdit.setPlainText(unicode(self.tableWidget.item(self.tableWidget.currentRow(),4).text()))
        

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(unicode(value))
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/sp.png"))
        self.tableWidget.setItem(x,y,headerItem)

    def fixtures(self):
        systemusers = self.connection.get_systemusers( fields=['id', 'username'])
        self.connection.commit()
         
        self.comboBox_systemuser.addItem(u"--Все--")
        self.comboBox_systemuser.setItemData(0, QtCore.QVariant(None))
        i=1
        for systemuser in systemusers:
            self.systemusers[systemuser.id] = systemuser.username
            self.comboBox_systemuser.addItem(systemuser.username)
            self.comboBox_systemuser.setItemData(i, QtCore.QVariant(systemuser.id))
            i+=1
            
    def refresh(self):
        #self.tableWidget.setSortingEnabled(False)
        self.statusBar().showMessage(u"Идёт получение данных")
        systemuser_id = self.comboBox_systemuser.itemData(self.comboBox_systemuser.currentIndex()).toInt()[0] or None
        start_date = self.date_start.currentDate()
        end_date = self.date_end.currentDate()
        messages = self.connection.get_log_messages(systemuser_id=systemuser_id, start_date=start_date, end_date=end_date)
        #print self.connection
        self.connection.commit()
        self.tableWidget.setRowCount(len(messages))
        #.values('id','user', 'username', 'ballance', 'credit', 'firstname','lastname', 'vpn_ip_address', 'ipn_ip_address', 'suspended', 'status')[0:cnt]
        i=0
        for message in messages:
            #print message.systemuser_id
            self.addrow(message.id, i,0)
            self.addrow(message.timestamp.strftime(self.strftimeFormat), i,1)
            self.addrow(message.action__name, i,2)
            self.addrow(message.user__username, i,3)
            self.addrow(message.serialized_data, i,4)
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


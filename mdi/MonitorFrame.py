#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

#from nas.models import TrafficClass, TrafficNode
from helpers import tableFormat
from helpers import Object as Object
from helpers import makeHeaders

class MonitorFrame(QtGui.QMainWindow):
    def __init__(self, connection):
        super(MonitorFrame, self).__init__()
        self.connection = connection
        self.setObjectName("MainWindow")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,1102,593).size()).expandedTo(self.minimumSizeHint()))



        self.tableWidget = QtGui.QTableWidget()
        self.tableWidget.setGeometry(QtCore.QRect(0,0,801,541))
        self.tableWidget = tableFormat(self.tableWidget)
        self.setCentralWidget(self.tableWidget)
        
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        self.userCombobox = QtGui.QComboBox()
        self.userCombobox.setGeometry(QtCore.QRect(100,12,201,20))
        self.user_label = QtGui.QLabel(u" Пользователь  ")
        self.allTimeCheckbox = QtGui.QCheckBox(u"Все сессии пользователя")
        
        self.menubar = QtGui.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0,0,802,21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar()
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        
        self.pushbutton = QtGui.QPushButton()
        self.pushbutton.setText(u"Обновить")

        self.toolBar = QtGui.QToolBar()
        self.toolBar.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.toolBar.setMovable(False)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.toolBar.setFloatable(False)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)

        self.actionResetSession = QtGui.QAction(self)
        self.actionResetSession.setIcon(QtGui.QIcon("images/del.png"))
        self.actionResetSession.setObjectName("actionResetSession")

        self.actionGoToUser = QtGui.QAction(self)
        self.actionGoToUser.setIcon(QtGui.QIcon("images/accounts.png"))

                
        self.tableWidget.addAction(self.actionResetSession)
        self.tableWidget.addAction(self.actionGoToUser)

        
        self.toolBar.addAction(self.actionResetSession)

        self.toolBar.addWidget(self.user_label)
        self.toolBar.addWidget(self.userCombobox)
        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.allTimeCheckbox)
        self.toolBar.addWidget(self.pushbutton)

        QtCore.QObject.connect(self.pushbutton, QtCore.SIGNAL("clicked()"), self.fixtures)
        
        self.retranslateUi()
        self.fixtures()
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Монитор активности", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()

        columns = [u'Id', u'Аккаунт', u'IP', u'Сервер доступа', u'Способ доступа', u'Тарифный план', u'Начало', u'Передано байт', u'Принято байт', u'Длительность', u'Статус']
        makeHeaders(columns, self.tableWidget)
        
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionResetSession.setText(QtGui.QApplication.translate("MainWindow", "Сбросить сессию", None, QtGui.QApplication.UnicodeUTF8))
        self.actionGoToUser.setText(QtGui.QApplication.translate("MainWindow", "Перейти к пользователю", None, QtGui.QApplication.UnicodeUTF8))

    def addrow(self, widget, value, x, y):
        if value==None:
            value=''
            
        if widget.item(x,y):
            widget.item(x,y).setText(unicode(value))
        else:
            item_type = QtGui.QTableWidgetItem()
            item_type.setText(unicode(value))
            widget.setItem(x, y, item_type)
        
    
    def fixtures(self):
        
        self.tableWidget.clearContents()
        
        if self.allTimeCheckbox.checkState()==2:
            sessions = self.connection.sql("""SELECT *,billservice_account.username as username, nas_nas.name as nas_name  FROM radius_activesession
                                              JOIN billservice_account ON billservice_account.id=radius_activesession.account_id
                                              JOIN nas_nas ON nas_nas.ipaddress = radius_activesession.nas_id
                                
                                             """)
        elif self.allTimeCheckbox.checkState()==0:
            sessions = self.connection.sql("""SELECT *,billservice_account.username as username, nas_nas.name as nas_name  FROM radius_activesession
                                              JOIN billservice_account ON billservice_account.id=radius_activesession.account_id
                                              JOIN nas_nas ON nas_nas.ipaddress = radius_activesession.nas_id
                                              WHERE radius_activesession.session_status='ACTIVE'"""
                                              )
        i=0

        
        self.tableWidget.setRowCount(len(sessions))
        
        for session in sessions:
            print i
            self.addrow(self.tableWidget, session.id, i, 0)
            self.addrow(self.tableWidget, session.username, i, 1)
            self.addrow(self.tableWidget, session.caller_id, i, 2)
            self.addrow(self.tableWidget, session.nas_name, i, 3)
            self.addrow(self.tableWidget, session.framed_protocol, i, 4)
            self.addrow(self.tableWidget, session.date_start.strftime("%Y-%m-%d %H:%M:%S"), i, 6)
            self.addrow(self.tableWidget, session.bytes_out, i, 7)
            self.addrow(self.tableWidget, session.bytes_in, i, 8)
            self.addrow(self.tableWidget, session.session_time, i, 9)
            self.addrow(self.tableWidget, session.session_status, i, 10)
            self.tableWidget.setRowHeight(i, 14)
            i+=1
            
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setColumnHidden(0, True)
        #self.tableWidget.setSortingEnabled(True)
            
        
#-*-coding=utf-8-*-

import os, sys
from PyQt4 import QtCore, QtGui

sys.path.append('d:/projects/mikrobill/webadmin')
sys.path.append('d:/projects/mikrobill/webadmin/mikrobill')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mikrobill.settings'

from radius.models import ActiveSession
#from nas.models import TrafficClass, TrafficNode


class MonitorFrame(QtGui.QMainWindow):
    def __init__(self):
        super(MonitorFrame, self).__init__()
        
        self.setObjectName("MainWindow")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,1102,593).size()).expandedTo(self.minimumSizeHint()))



        self.tableWidget = QtGui.QTableWidget()
        self.tableWidget.setGeometry(QtCore.QRect(0,0,801,541))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setFrameShape(QtGui.QFrame.Panel)
        self.tableWidget.setFrameShadow(QtGui.QFrame.Sunken)
        self.tableWidget.setLineWidth(1)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableWidget.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tableWidget.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QtGui.QTableWidget.SelectRows)
        self.tableWidget.setSelectionMode(QtGui.QTableWidget.SingleSelection)        
        hh = self.tableWidget.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setHighlightSections(False)
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
        self.tableWidget.setColumnCount(11)
        self.tableWidget.setRowCount(0)

        headerItem0 = QtGui.QTableWidgetItem()
        headerItem0.setText(QtGui.QApplication.translate("MainWindow", "Id", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(0,headerItem0)
        
        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("MainWindow", "Аккаунт", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(1,headerItem1)

        headerItem21 = QtGui.QTableWidgetItem()
        headerItem21.setText(QtGui.QApplication.translate("MainWindow", "Адрес пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(2,headerItem21)
        
        headerItem2 = QtGui.QTableWidgetItem()
        headerItem2.setText(QtGui.QApplication.translate("MainWindow", "NAS", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(3,headerItem2)

        headerItem3 = QtGui.QTableWidgetItem()
        headerItem3.setText(QtGui.QApplication.translate("MainWindow", "Протокол", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(4,headerItem3)

        headerItem4 = QtGui.QTableWidgetItem()
        headerItem4.setText(QtGui.QApplication.translate("MainWindow", "ТП", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(5,headerItem4)

        headerItem6 = QtGui.QTableWidgetItem()
        headerItem6.setText(QtGui.QApplication.translate("MainWindow", "Дата начала", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(6,headerItem6)

        headerItem7 = QtGui.QTableWidgetItem()
        headerItem7.setText(QtGui.QApplication.translate("MainWindow", "Передано b", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(7,headerItem7)

        headerItem8 = QtGui.QTableWidgetItem()
        headerItem8.setText(QtGui.QApplication.translate("MainWindow", "Принято b", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(8,headerItem8)
        
        headerItem9 = QtGui.QTableWidgetItem()
        headerItem9.setText(QtGui.QApplication.translate("MainWindow", "Длительность", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(9,headerItem9)

       
        headerItem11 = QtGui.QTableWidgetItem()
        headerItem11.setText(QtGui.QApplication.translate("MainWindow", "Статус", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setHorizontalHeaderItem(10,headerItem11)
        
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
            sessions = ActiveSession.objects.all()
        elif self.allTimeCheckbox.checkState()==0:
            sessions = ActiveSession.objects.filter(session_status="ACTIVE")
        i=0

        
        self.tableWidget.setRowCount(sessions.count())
        
        for session in sessions:
            print i
            self.addrow(self.tableWidget, session.id, i, 0)
            self.addrow(self.tableWidget, session.account.username, i, 1)
            self.addrow(self.tableWidget, session.caller_id, i, 2)
            self.addrow(self.tableWidget, session.nas_id, i, 3)
            self.addrow(self.tableWidget, session.framed_protocol, i, 4)
            self.addrow(self.tableWidget, session.date_start.strftime("%Y-%m-%d %H:%M:%S"), i, 6)
            self.addrow(self.tableWidget, session.bytes_out, i, 7)
            self.addrow(self.tableWidget, session.bytes_in, i, 8)
            self.addrow(self.tableWidget, session.session_time, i, 9)
            self.addrow(self.tableWidget, session.session_status, i, 10)
            self.tableWidget.setRowHeight(i, 17)
            i+=1
            
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setColumnHidden(0, True)
        #self.tableWidget.setSortingEnabled(True)
            
        
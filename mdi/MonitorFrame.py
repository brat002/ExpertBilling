#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

from ebsWindow import ebsTableWindow
from helpers import tableFormat
from db import Object as Object
from helpers import makeHeaders
from helpers import dateDelim
from helpers import HeaderUtil
from helpers import humanable_bytes
from helpers import Worker
from helpers import prntime
import time


class MonitorEbs(ebsTableWindow):
    def __init__(self, connection):
        columns=[u'#', u'Аккаунт', u'IPN IP', 'VPN IP', u'Сервер доступа', u'Способ доступа', u'Начало', u'Конец', u'Передано', u'Принято', u'Длительность, с', u'Статус']
        initargs = {"setname":"monitor_frame_header", "objname":"MonitorEbsMDI", "winsize":(0,0,1102,593), "wintitle":"Монитор активности", "tablecolumns":columns, "tablesize":(0,0,801,541)}
        super(MonitorEbs, self).__init__(connection, initargs)
        
    def ebsPreInit(self, initargs):
        self.thread = Worker()
        self.selected_user=None
        
    def ebsInterInit(self, initargs):
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        self.userCombobox = QtGui.QComboBox()
        self.userCombobox.setGeometry(QtCore.QRect(100,12,201,20))
        self.user_label = QtGui.QLabel(u" Пользователь  ")
        self.allTimeCheckbox = QtGui.QCheckBox(u"Включая завершённые")
        
        self.checkBoxAutoRefresh = QtGui.QCheckBox(u"Автоматически обновлять")
        
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
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        
        self.toolBar.addWidget(self.user_label)
        self.toolBar.addWidget(self.userCombobox)
        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.allTimeCheckbox)
        self.toolBar.addWidget(self.checkBoxAutoRefresh)
        self.toolBar.addWidget(self.pushbutton)
        
        QtCore.QObject.connect(self.pushbutton, QtCore.SIGNAL("clicked()"), self.fixtures)        
        QtCore.QObject.connect(self.checkBoxAutoRefresh, QtCore.SIGNAL("stateChanged(int)"), self.autorefresh_state)
        self.connect(self.thread, QtCore.SIGNAL("refresh()"), self.fixtures)
        QtCore.QObject.connect(self.userCombobox, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.fixtures)
    
    def ebsPostInit(self, initargs):
        actList=[("actionResetSession", "Сбросить сессию", "images/del.png", self.reset_action)]
        objDict = {self.tableWidget:["actionResetSession"]}
        self.actionCreator(actList, objDict)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
    def retranslateUI(self, initargs):
        super(MonitorEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
    def autorefresh_state(self):
        """
        Метод, стартующий трэд, эмитирующий в родительское окно сигнал refresh()
        """
        if self.checkBoxAutoRefresh.checkState()==2:
            self.thread.go(interval=25)
        else:
            self.thread.terminate()
            
    def closeEvent(self, event):
        """
        Terminate thread
        """
        self.thread.terminate()
        event.accept()
            
    def addrow(self, widget, value, x, y, color=False):
        
        item_type = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        if y==0:
            text, item_type.sessionid = value
        else:
            text=value
            
        if widget.item(x,y):
            widget.item(x,y).setText(unicode(text))
        else:
            item_type.setText(unicode(text))
            widget.setItem(x, y, item_type)
        if y==1:
            item_type.setIcon(QtGui.QIcon("images/user.png"))
        

            
        if color:
            if value=='ACTIVE':
                item_type.setBackgroundColor(QtGui.QColor('green'))
                item_type.setTextColor(QtGui.QColor('#ffffff'))
            elif value=='ACK':
                item_type.setBackgroundColor(QtGui.QColor('#4d4d4d'))
                item_type.setTextColor(QtGui.QColor('#ffffff'))
            elif value=='NACK':
                item_type.setBackgroundColor(QtGui.QColor('#e8ff6a'))
                item_type.setTextColor(QtGui.QColor('#000000'))
        
    def reset_action(self):
        sessionid = unicode(self.tableWidget.item(self.tableWidget.currentRow(), 0).sessionid)
        self.connection.pod(session=sessionid)
        d = Object()
        d.id = unicode(self.tableWidget.item(self.tableWidget.currentRow(), 0).id)
        d.sessionid = sessionid
        d.session_status='ACK'
        self.connection.save(d, "radius_activesession")
        self.connection.commit()
        self.fixtures()
        
    def fixtures(self, user=None):
        
        self.tableWidget.clearContents()
        self.tableWidget.setSortingEnabled(False)
        if self.allTimeCheckbox.checkState()==2:
            sql="""SELECT *,billservice_account.username as username, nas_nas.name as nas_name  FROM radius_activesession
            
                  JOIN billservice_account ON billservice_account.id=radius_activesession.account_id
                  JOIN nas_nas ON nas_nas.ipaddress = radius_activesession.nas_id WHERE billservice_account.id>0    
                 """
        elif self.allTimeCheckbox.checkState()==0:
            sql="""SELECT *,billservice_account.username as username, nas_nas.name as nas_name  FROM radius_activesession
                  JOIN billservice_account ON billservice_account.id=radius_activesession.account_id
                  JOIN nas_nas ON nas_nas.ipaddress = radius_activesession.nas_id
                  WHERE radius_activesession.session_status='ACTIVE'"""
        
        if user==None:
            user=unicode(self.userCombobox.currentText())                                      
        
        if user!="---":
            sql+=" AND billservice_account.username='%s'" % unicode(user)
          
        sessions = self.connection.sql(sql)  
        self.connection.commit()
        i=0        
        self.tableWidget.setRowCount(len(sessions))        
        for session in sessions:
            if session.date_end==None:
                date_end=""
            else:
                date_end = session.date_end.strftime(self.strftimeFormat)
                
            self.addrow(self.tableWidget, (i, session.sessionid), i, 0)
            self.addrow(self.tableWidget, session.username, i, 1)
            self.addrow(self.tableWidget, session.caller_id, i, 2)
            self.addrow(self.tableWidget, session.framed_ip_address, i, 3)
            self.addrow(self.tableWidget, session.nas_name, i, 4)
            self.addrow(self.tableWidget, session.framed_protocol, i, 5)
            self.addrow(self.tableWidget, session.date_start.strftime(self.strftimeFormat), i, 6)
            self.addrow(self.tableWidget, date_end, i, 7)
            self.addrow(self.tableWidget, humanable_bytes(session.bytes_out), i, 8)
            self.addrow(self.tableWidget, humanable_bytes(session.bytes_in), i, 9)
            self.addrow(self.tableWidget, prntime(session.session_time), i, 10)
            self.addrow(self.tableWidget, session.session_status, i, 11, color=True)
            i+=1
        if self.firsttime and sessions and HeaderUtil.getBinaryHeader("monitor_frame_header").isEmpty():
            self.tableWidget.resizeColumnsToContents()
            self.firsttime = False
        else:
            if sessions:
                HeaderUtil.getHeader("monitor_frame_header", self.tableWidget)
        
        self.tableWidget.setColumnHidden(0, False)
        #self.tableWidget.setSortingEnabled(True)

        
    def refresh_users(self):
        if self.selected_user is None:
            self.userCombobox.addItem('---')
            users = self.connection.get_models("billservice_account")
            self.connection.commit()
            if users==None:
                users=[]
            for user in users:
                self.userCombobox.addItem(unicode(user.username))
                
    def refresh(self):
        self.fixtures()
        self.refresh_users()
        
       
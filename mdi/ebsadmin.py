#-*- coding=utf-8 -*-

#global connection
import sys, traceback, os
sys.path.append(os.path.abspath('../'))
from PyQt4 import QtCore, QtGui
#sys.stdout=sys.stderr=None
#import socket
#socket.setdefaulttimeout(None)
from helpers import Object as Object
from helpers import connlogin
#===============================================================================
# import Pyro.core
# import Pyro.util
# import Pyro.protocol
# import Pyro.constants
# import Pyro.errors
# import Pyro.configuration
import threading
# import Pyro
#===============================================================================
#import psyco
#psyco.log()
#psyco.profile()
#psyco.full()

from rpc2 import rpc_protocol, client_networking

DEFAULT_PORT = 7771
LOG_LEVEL    = 0
ROLE = 0

class PrintLogger(object):
    def __getattr__(self, name):
        return self.lprint
    
    def lprint(self, *args):
        if len(args) == 1:
            print 'LOGGER: ', args[0]
        elif len(args) == 2:
            print 'LOGGER: ', args[0] % args[1]


import isdlogger

import mdi_rc

from AccountFrame import AccountsMdiEbs as AccountsMdiChild
from NasFrame import NasEbs
from SettlementPeriodFrame import SettlementPeriodEbs as SettlementPeriodChild
from TimePeriodFrame import TimePeriodChildEbs as TimePeriodChild
from ClassFrame import ClassChildEbs as ClassChild
from MonitorFrame import MonitorEbs as MonitorFrame
from PoolFrame import PoolEbs as PoolFrame
from SystemUser import SystemEbs
from CustomForms import ConnectDialog, ConnectionWaiting, OperatorDialog
from Reports import NetFlowReportEbs as NetFlowReport, StatReport , LogViewWindow, SimpleReportEbs
from CardsFrame import CardsChildEbs as CardsChild
from DealerFrame import DealerMdiEbs as DealerMdiChild
from CustomForms import TemplatesWindow, SqlDialog
from TPChangeRules import TPRulesEbs
from AddonServiceFrame import AddonServiceEbs
from MessagesFrame import MessagesEbs
from LogFrame import LogViewEbs
from AddressFrame import AddressEbs

_reportsdict = [['Статистика по группам',[['report3_users.xml', ['groups'], 'Общий трафик']]],\
                ['Глобальная статистика',[['report3_users.xml', ['gstat_globals'], 'Общий трафик'],['report3_users.xml', ['gstat_multi'], 'Трафик с выбором классов'], ['report3_pie.xml', ['pie_gmulti'], 'Пирог']]],\
                ['Другие отчёты',[['report3_sess.xml', ['sessions'], 'Сессии пользователей'], ['report3_tr.xml', ['trans_crd'], 'Динамика прибыли']]]]

#разделитель для дат по умолчанию
dateDelim = "."


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.workspace = QtGui.QWorkspace()

        self.setCentralWidget(self.workspace)

        self.connect(self.workspace, QtCore.SIGNAL("windowActivated(QWidget *)"), self.updateMenus)
        self.windowMapper = QtCore.QSignalMapper(self)
        self.connect(self.windowMapper, QtCore.SIGNAL("mapped(QWidget *)"),
                     self.workspace, QtCore.SLOT("setActiveWindow(QWidget *)"))

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        #self.setWindowTitle(u"Expert Billing Client 1.2.1")

    def closeEvent(self, event):
        self.workspace.closeAllWindows()
        if self.activeMdiChild():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

    @connlogin
    def newFile(self):
        self.workspace.windowList()
        

        child =  AccountsMdiChild(connection=connection, parent=self)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)        
        child.show()
    

    @connlogin
    def templates(self):
        self.workspace.windowList()  

        child =  TemplatesWindow(connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)
        
        child.show()
 
    @connlogin
    def messages(self):
        self.workspace.windowList()  

        child =  MessagesEbs(connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)
        
        child.show()


    @connlogin
    def pool(self):
        self.workspace.windowList()  

        child =  PoolFrame(connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)
        
        child.show()
               


    @connlogin
    def dealers(self):
        self.workspace.windowList()
        child =  DealerMdiChild(parent=self, connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )

        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)        
        child.show()        

    @connlogin
    def netflowreport(self):
        self.workspace.windowList()
        child =  NetFlowReport(parent=self, connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )

        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)        
        child.show()    
        
    @connlogin
    def open(self):
        child = NasEbs(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return            
        self.workspace.addWindow(child)
        child.show()
        #return child

    @connlogin
    def save(self):
        child=SettlementPeriodChild(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return            
        self.workspace.addWindow(child)
        child.show()


    @connlogin
    def saveAs(self):

        child = SystemEbs(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return            
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def tpchangerules(self):
        child = TPRulesEbs(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return            
        self.workspace.addWindow(child)
        child.show()       
               
    
    @connlogin
    def cut(self):
        child=TimePeriodChild(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
            
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def copy(self):
        child=ClassChild(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
            
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def paste(self):
        child = MonitorFrame(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def addonservice(self):
        child = AddonServiceEbs(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()


    @connlogin
    def adminsLogViewWindow(self):
        child = LogViewEbs(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()
            
    
    @connlogin
    def logview(self):
        child = LogViewWindow(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def addressview(self):
        child = AddressEbs(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()
    
    #@connlogin
    def about(self):
        QtGui.QDesktopServices().openUrl(QtCore.QUrl('http://wiki.expertbilling.ru/')) 
        #QtGui.QMessageBox.about(self, u"О программе",
        #                        u"Expert Billing Client<br>Интерфейс конфигурирования.<br>Версия 0.2")
    #@connlogin
    def to_forum(self):
        QtGui.QDesktopServices().openUrl(QtCore.QUrl('http://forum.expertbilling.ru/')) 
        #QtGui.QMessageBox.about(self, u"О программе",
        #     
        
    @connlogin
    def aboutOperator(self):
        child = OperatorDialog(connection=connection)
        child.exec_()
        
    @connlogin
    def sqlDialog(self):
        child = SqlDialog(connection=connection)
        child.exec_()
        
    @connlogin
    def cardsFrame(self):
        child = CardsChild(connection = connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def radiuslog_report(self):
        child = SimpleReportEbs(connection = connection, report_type='radius_authlog')
        self.workspace.addWindow(child)
        child.show()
        
        

    def relogin(self):
        global connection
        connection = login()
        global mainwindow
        mainwindow.setWindowTitle("ExpertBilling administrator interface #%s - %s" % (username, server_ip)) 
        

    def updateMenus(self):
        hasMdiChild = (self.activeMdiChild() is not None)
        #self.saveAct.setEnabled(hasMdiChild)
        #self.sysadmAct.setEnabled(hasMdiChild)
        #self.pasteAct.setEnabled(True)
        self.closeAct.setEnabled(hasMdiChild)
        self.closeAllAct.setEnabled(hasMdiChild)
        self.tileAct.setEnabled(hasMdiChild)
        self.cascadeAct.setEnabled(hasMdiChild)
        self.arrangeAct.setEnabled(hasMdiChild)
        self.nextAct.setEnabled(hasMdiChild)
        self.previousAct.setEnabled(hasMdiChild)
        self.separatorAct.setVisible(hasMdiChild)


    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addAction(self.arrangeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        windows = self.workspace.windowList()
        self.separatorAct.setVisible(len(windows) != 0)

        i = 0

        for child in windows:
            i += 1
            action = self.windowMenu.addAction(child.windowTitle())
            action.setCheckable(True)
            action.setChecked(child == self.activeMdiChild())
            self.connect(action, QtCore.SIGNAL("triggered()"),
                         self.windowMapper, QtCore.SLOT("map()"))
            self.windowMapper.setMapping(action, child)


       
    def createActions(self):
        self.newAct = QtGui.QAction(QtGui.QIcon("images/accounts.png"),
                                    u"&Пользователи и тарифы", self)
        #self.newAct.setShortcut(self.tr("Ctrl+A"))
        self.newAct.setStatusTip(u"Пользователи и тарифы")
        self.connect(self.newAct, QtCore.SIGNAL("triggered()"), self.newFile)

        self.dealerAct = QtGui.QAction(QtGui.QIcon("images/dealer.png"),
                                    u"&Дилеры", self)
        #self.dealerAct.setShortcut(self.tr("Ctrl+D"))
        self.dealerAct.setStatusTip(u"Дилеры")
        self.connect(self.dealerAct, QtCore.SIGNAL("triggered()"), self.dealers)
        
        self.netflowAct = QtGui.QAction(QtGui.QIcon("images/nfstat.png"),
                                    u"&NetFlow статистика", self)
        #self.dealerAct.setShortcut(self.tr("Ctrl+D"))
        self.netflowAct.setStatusTip(u"NetFlow статистика")
        self.connect(self.netflowAct, QtCore.SIGNAL("triggered()"), self.netflowreport)
                
        self.nasAct = QtGui.QAction(QtGui.QIcon("images/nas.png"), u"&Серверы доступа", self)
        
        #self.nasAct.setShortcut(self.tr("Ctrl+N"))
        self.nasAct.setStatusTip(u'Серверы доступа')
        self.connect(self.nasAct, QtCore.SIGNAL("triggered()"), self.open)
        
       

        self.settlementPeriodAct = QtGui.QAction(QtGui.QIcon("images/sp.png"), u'Расчётные периоды', self)
        self.settlementPeriodAct.setStatusTip(u"Расчётные периоды")
        self.connect(self.settlementPeriodAct, QtCore.SIGNAL("triggered()"), self.save)



        self.adminLogViewAct = QtGui.QAction(QtGui.QIcon("images/add.png"), u'Лог действий', self)
        self.adminLogViewAct.setStatusTip(u"Лог действий")
        self.connect(self.adminLogViewAct, QtCore.SIGNAL("triggered()"), self.adminsLogViewWindow)
        

        self.addressViewAct = QtGui.QAction(QtGui.QIcon("images/house.png"), u'Адреса домов', self)
        self.addressViewAct.setStatusTip(u"Адреса")
        self.connect(self.addressViewAct, QtCore.SIGNAL("triggered()"), self.addressview)
        
                
        self.sysadmAct = QtGui.QAction(QtGui.QIcon("images/system_administrators.png"),u'Администраторы и работники', self)
        self.sysadmAct.setStatusTip(u"Администраторы и работники")
        self.connect(self.sysadmAct, QtCore.SIGNAL("triggered()"), self.saveAs)

        self.poolAct = QtGui.QAction(QtGui.QIcon("images/ipv4.png"),u'IP пулы', self)
        self.poolAct.setStatusTip(u"Пулы IP адресов")
        self.connect(self.poolAct, QtCore.SIGNAL("triggered()"), self.pool)


        self.exitAct = QtGui.QAction(u"Выход", self)
        self.exitAct.setShortcut(self.tr("Ctrl+Q"))
        self.exitAct.setStatusTip(u"Выход из программы")
        self.connect(self.exitAct, QtCore.SIGNAL("triggered()"), self.close)
        
        
        self.timePeriodAct = QtGui.QAction(QtGui.QIcon("images/tp.png"),
                                    u'Периоды тарификации', self)

        self.timePeriodAct.setStatusTip(u"Периоды тарификации")
        self.connect(self.timePeriodAct, QtCore.SIGNAL("triggered()"), self.cut)

        self.messagesAct = QtGui.QAction(QtGui.QIcon("images/messages.png"),
                                    u'Сообщения абонентам', self)

        self.messagesAct.setStatusTip(u"Сообщениия")
        self.connect(self.messagesAct, QtCore.SIGNAL("triggered()"), self.messages)


        self.sqlDialogAct = QtGui.QAction(QtGui.QIcon("images/sql.png"),u'SQL Консоль', self)

        self.sqlDialogAct.setShortcut(self.tr("Ctrl+Y"))
        self.connect(self.sqlDialogAct, QtCore.SIGNAL("triggered()"), self.sqlDialog)


        self.tclassesAct = QtGui.QAction(QtGui.QIcon("images/tc.png"),
                                     u"Классы трафика", self)
        #self.tclassesAct.setShortcut(self.tr("Ctrl+C"))
        self.tclassesAct.setStatusTip(u"Классы трафика")
        self.connect(self.tclassesAct, QtCore.SIGNAL("triggered()"), self.copy)

        self.sessionsMonAct = QtGui.QAction(QtGui.QIcon("images/monitor.png"),
                                      u"Монитор сессий", self)
        
        #self.sessionsMonAct.setShortcut(self.tr("Ctrl+M"))
        self.sessionsMonAct.setStatusTip(u"Монитор сессий")

        self.connect(self.sessionsMonAct, QtCore.SIGNAL("triggered()"), self.paste)

        self.cardsAct = QtGui.QAction(QtGui.QIcon("images/cards.png"),
                                      u"Карточная система", self)
        #self.reportPropertiesAct.setShortcut(self.tr("Ctrl+V"))
        self.cardsAct.setStatusTip(u"Карточная система")

        self.connect(self.cardsAct, QtCore.SIGNAL("triggered()"), self.cardsFrame)

        self.radiuslogReportAct=QtGui.QAction(QtGui.QIcon("images/easytag.png"), u"История RADIUS авторизаций", self)

        self.radiuslogReportAct.setStatusTip(u"История RADIUS авторизаций пользователей")

        self.connect(self.radiuslogReportAct, QtCore.SIGNAL("triggered()"), self.radiuslog_report)

        self.reloginAct = QtGui.QAction(QtGui.QIcon("images/refresh_connection.png"),self.tr("&Reconnect"), self)
        self.reloginAct.setStatusTip(self.tr("Reconnect"))
        self.connect(self.reloginAct, QtCore.SIGNAL("triggered()"), self.relogin)

        self.templatesAct = QtGui.QAction(QtGui.QIcon("images/templates.png"),u"Шаблоны документов", self)
        #self.reloginAct.setStatusTip(self.tr("Reconnect"))
        self.connect(self.templatesAct, QtCore.SIGNAL("triggered()"), self.templates)


        self.tpchangeAct = QtGui.QAction(QtGui.QIcon("images/tarif_change.png"),u"Правила смены тарифов", self)
        #self.reloginAct.setStatusTip(self.tr("Reconnect"))
        self.connect(self.tpchangeAct, QtCore.SIGNAL("triggered()"), self.tpchangerules)

        self.addonserviceAct = QtGui.QAction(QtGui.QIcon("images/turboicon.png"),u"Подключаемые услуги", self)
        #self.reloginAct.setStatusTip(self.tr("Reconnect"))
        self.connect(self.addonserviceAct, QtCore.SIGNAL("triggered()"), self.addonservice)
 
        self.logViewAct = QtGui.QAction(QtGui.QIcon("images/logs.png"), u"Просмотр логов", self)
        #self.reloginAct.setStatusTip(self.tr("Reconnect"))
        self.connect(self.logViewAct, QtCore.SIGNAL("triggered()"), self.logview)       
        
        
        self.reportActs = []
        i = 0
        
        for branch in _reportsdict:
            j=0
            self.reportActs.append([branch[0],[]])
            for leaf in branch[1]:
                rAct = QtGui.QAction(self.trUtf8(leaf[2]), self)
                rAct.setStatusTip(u"Отчёт")
                rAct.setData(QtCore.QVariant('_'.join((str(i), str(j)))))
                self.connect(rAct, QtCore.SIGNAL("triggered()"), self.reportsMenu)
                self.reportActs[-1][1].append(rAct)
                j+=1
            i += 1

        self.closeAct = QtGui.QAction(self.tr("Cl&ose"), self)
        self.closeAct.setShortcut(self.tr("Ctrl+F4"))
        self.closeAct.setStatusTip(self.tr("Close the active window"))
        self.connect(self.closeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.closeActiveWindow)

        self.closeAllAct = QtGui.QAction(self.tr("Close &All"), self)
        self.closeAllAct.setStatusTip(self.tr("Close all the windows"))
        self.connect(self.closeAllAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.closeAllWindows)

        self.tileAct = QtGui.QAction(self.tr("&Tile"), self)
        self.tileAct.setStatusTip(self.tr("Tile the windows"))
        self.connect(self.tileAct, QtCore.SIGNAL("triggered()"), self.workspace.tile)

        self.cascadeAct = QtGui.QAction(self.tr("&Cascade"), self)
        self.cascadeAct.setStatusTip(self.tr("Cascade the windows"))
        self.connect(self.cascadeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.cascade)

        self.arrangeAct = QtGui.QAction(self.tr("Arrange &icons"), self)
        self.arrangeAct.setStatusTip(self.tr("Arrange the icons"))
        self.connect(self.arrangeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.arrangeIcons)

        self.nextAct = QtGui.QAction(self.tr("Ne&xt"), self)
        self.nextAct.setShortcut(self.tr("Ctrl+F6"))
        self.nextAct.setStatusTip(self.tr("Move the focus to the next window"))
        self.connect(self.nextAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.activateNextWindow)

        self.previousAct = QtGui.QAction(self.tr("Pre&vious"), self)
        self.previousAct.setShortcut(self.tr("Ctrl+Shift+F6"))
        self.previousAct.setStatusTip(self.tr("Move the focus to the previous "
                                              "window"))
        self.connect(self.previousAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.activatePreviousWindow)

        self.separatorAct = QtGui.QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = QtGui.QAction(u"&Документация", self)
        self.aboutAct.setStatusTip(u"Перейти на страницу документации")
        self.connect(self.aboutAct, QtCore.SIGNAL("triggered()"), self.about)
      
        self.forumAct = QtGui.QAction(u"&Форум проекта", self)
        self.forumAct.setStatusTip(u"Перейти на форум")
        self.connect(self.forumAct, QtCore.SIGNAL("triggered()"), self.to_forum)
        
        self.aboutOperAct = QtGui.QAction(u"Информация о провайдере", self)
        self.aboutOperAct.setStatusTip(self.tr("Show the operator info"))
        self.connect(self.aboutOperAct, QtCore.SIGNAL("triggered()"), self.aboutOperator)

        self.aboutQtAct = QtGui.QAction(self.tr("About &Qt"), self)
        self.aboutQtAct.setStatusTip(self.tr("Show the Qt library's About box"))
        self.connect(self.aboutQtAct, QtCore.SIGNAL("triggered()"),
                     QtGui.qApp, QtCore.SLOT("aboutQt()"))



    def createMenus(self):
        self.mainMenu = self.menuBar().addMenu(u"&Главное меню")
        self.mainMenu.addAction(self.newAct)
        
        #self.mainMenu.addAction(self.settlementPeriodAct)
        
        #self.editMenu = self.menuBar().addMenu(self.tr("&Edit"))
        #self.mainMenu.addAction(self.timePeriodAct)
        self.mainMenu.addSeparator()
        self.mainMenu.addAction(self.tpchangeAct)
        
        self.mainMenu.addAction(self.sessionsMonAct)
        
        #self.mainMenu.addAction(self.poolAct)
        self.mainMenu.addSeparator()
        #self.mainMenu.addAction(self.addressViewAct)
        #self.mainMenu.addSeparator()
        #self.mainMenu.addAction(self.sysadmAct)
        self.mainMenu.addAction(self.dealerAct)
        self.mainMenu.addSeparator()
        #self.mainMenu.addAction(self.templatesAct)

        #self.mainMenu.addSeparator()
        #self.mainMenu.addAction(self.addonserviceAct)
        self.mainMenu.addSeparator()
        self.mainMenu.addAction(self.messagesAct)
        self.mainMenu.addSeparator()
        self.mainMenu.addAction(self.logViewAct)
        
        self.mainMenu.addSeparator()
        
        self.mainMenu.addAction(self.adminLogViewAct)
        self.mainMenu.addSeparator()
        self.mainMenu.addAction(self.sqlDialogAct)
        self.mainMenu.addSeparator()
        self.mainMenu.addAction(self.reloginAct)
        self.mainMenu.addSeparator()
        self.mainMenu.addAction(self.exitAct)

        self.settingsMenu = self.menuBar().addMenu(u"&Справочники")
        self.settingsMenu.addAction(self.nasAct)
        self.settingsMenu.addAction(self.addonserviceAct)
        self.settingsMenu.addAction(self.settlementPeriodAct)
        self.settingsMenu.addAction(self.timePeriodAct)
        self.settingsMenu.addAction(self.tclassesAct)
        self.settingsMenu.addAction(self.poolAct)
        self.settingsMenu.addAction(self.addressViewAct)
        self.settingsMenu.addAction(self.sysadmAct)
        self.settingsMenu.addAction(self.templatesAct)
        self.settingsMenu.addAction(self.aboutOperAct)
        
        
        self.windowMenu = self.menuBar().addMenu(u"&Окна")
        self.connect(self.windowMenu, QtCore.SIGNAL("aboutToShow()"),
                     self.updateWindowMenu)
        self.reportsMenu = self.menuBar().addMenu(u"&Отчёты")
        
        for menuName, branch in self.reportActs:
            branchMenu = self.reportsMenu.addMenu(self.trUtf8(menuName))
            for leaf in branch:
                branchMenu.addAction(leaf)
        
        self.reportsMenu.addAction(self.netflowAct)
        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu(u"&Справка")
        
        #self.helpMenu.addAction(self.aboutOperAct)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.forumAct)
        #self.helpMenu.addAction(self.aboutQtAct)

    @connlogin
    def reportsMenu(self):
        #print self.sender().data().toInt()
        i,j = [int(vstr) for vstr in str(self.sender().data().toString()).split('_')]
        child=StatReport(connection=connection, chartinfo=_reportsdict[i][1][j])
        self.workspace.addWindow(child)
        child.show()

    def createToolBars(self):
        self.fileToolBar = QtGui.QToolBar(self)
        self.fileToolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.nasAct)
        #self.fileToolBar.addAction(self.openAct)
        #self.fileToolBar.addAction(self.settlementPeriodAct)
        self.fileToolBar.setMovable(False)
        self.fileToolBar.setFloatable(False)

        self.fileToolBar.setAllowedAreas(QtCore.Qt.TopToolBarArea)
        self.fileToolBar.setIconSize(QtCore.QSize(24,24))

        self.fileToolBar.addAction(self.timePeriodAct)
        self.fileToolBar.addAction(self.tclassesAct)
        self.fileToolBar.addAction(self.sessionsMonAct)
        self.fileToolBar.addAction(self.cardsAct)
        self.fileToolBar.addAction(self.radiuslogReportAct)

        self.addToolBar(QtCore.Qt.TopToolBarArea,self.fileToolBar)

    def createStatusBar(self):
        self.statusBar().showMessage(self.tr("Ready"))

    def readSettings(self):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        pos = settings.value("pos", QtCore.QVariant(QtCore.QPoint(200, 200))).toPoint()
        size = settings.value("size", QtCore.QVariant(QtCore.QSize(400, 400))).toSize()
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        settings.setValue("pos", QtCore.QVariant(self.pos()))
        settings.setValue("size", QtCore.QVariant(self.size()))

    def activeMdiChild(self):
        return self.workspace.activeWindow()

    def findMdiChild(self, fileName):
        canonicalFilePath = QtCore.QFileInfo(fileName).canonicalFilePath()

        for window in self.workspace.windowList():
            if window.currentFile() == canonicalFilePath:
                return window
        return None
    
class Executor(Object):
    def __init__(self):
        pass
    def execute(self, execcmd):
        inQueue.append(execcmd)
        #use locks etc
        return outQueue.pop()
    
class rpcDispatcher(threading.Thread):
    
    def __init__(self):
        pass
    
    def run(self):
        pass

#===============================================================================
# class antiMungeValidator(Pyro.protocol.DefaultConnValidator):
#    def __init__(self):
#        Pyro.protocol.DefaultConnValidator.__init__(self)
#    def createAuthToken(self, authid, challenge, peeraddr, URI, daemon):
#        return authid
#    def mungeIdent(self, ident):
#        return ident
#===============================================================================
      

def login():
    child = ConnectDialog()
    while True:

        if child.exec_()==1:
            #waitchild = ConnectionWaiting()
            #waitchild.show()
            global splash, username, server_ip
            pixmap = QtGui.QPixmap("splash.png")
            #splash = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
            splash = QtGui.QSplashScreen(pixmap)
            splash.setMask(pixmap.mask()) # this is usefull if the splashscreen is not a regular ractangle...
            splash.show()
            splash.showMessage(u'Starting...', QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom,QtCore.Qt.yellow)
            # make sure Qt really display the splash screen
            global app
            app.processEvents()
            try:
                
                #logger  = PrintLogger()
                try:
                    os.mkdir('log')
                except:
                    pass
                logger = isdlogger.isdlogger('logging', loglevel=LOG_LEVEL, ident='mdi', filename='log/mdi_log')
                rpc_protocol.install_logger(logger)
                client_networking.install_logger(logger)
                
                authenticator = rpc_protocol.MD5_Authenticator('client', 'AUTH')
                protocol = rpc_protocol.RPCProtocol(authenticator)
                connection = rpc_protocol.BasicClientConnection(protocol)
                connection.notifier = lambda x: QtGui.QMessageBox.warning(None, unicode(u"Exception"), unicode(x))
                if ':' in child.address:
                    host, port = str(child.address).split(':')
                else:
                    host, port = str(child.address), DEFAULT_PORT
                transport = client_networking.BlockingTcpClient(host, port)
                transport.connect()
                connection.registerConsumer_(transport)
                auth_result = connection.authenticate(str(child.name), str(child.password), ROLE)
                if not auth_result or not connection.protocol._check_status():
                    raise Exception('Status = False!')
                username = str(child.name)
                server_ip = unicode(child.address)
                #connection._setIdentification("%s:%s:0" % (str(child.name), str(child.password.toHex())))
                #connection.test()
                #waitchild.hide()
                return connection

            except Exception, e:
                print repr(e), traceback.format_exc()
                if not isinstance(e, client_networking.TCPException):
                    QtGui.QMessageBox.warning(None, unicode(u"Ошибка"), unicode(u"Отказано в авторизации."))
                else:
                    QtGui.QMessageBox.warning(None, unicode(u"Ошибка"), unicode(u"Невозможно подключиться к серверу."))
            #splash.hide()
            #del waitchild
        else:
            #splash.hide()
            return None

if __name__ == "__main__":
    global app
    app = QtGui.QApplication(sys.argv)
    #translator = QtCore.QTranslator(app)
    #translator.load('ebsadmin_en')
    #app.installTranslator(translator)
    global connection, username, server_ip
    connection = login() 
       
    if connection is None:
        sys.exit()
    #connection.commit()
    
    connection.server_ip = server_ip
    try:
        global mainwindow
        mainwindow = MainWindow()
        
        splash.finish(mainwindow) 
        mainwindow.show()
        mainwindow.setWindowTitle("ExpertBilling administrator interface v.1.4.2003-dev #%s - %s" % (username, server_ip))  
        #app.setStyle("cleanlooks")
        mainwindow.setWindowIcon(QtGui.QIcon("images/icon.png"))
        app.setStyleSheet(open("./style.qss","r").read())
        sys.exit(app.exec_())
        connection.commit()
    except Exception, ex:
        print "main-----------"
        print repr(ex)
        print traceback.format_exc()


    #QtGui.QStyle.SH_Table_GridLineColor


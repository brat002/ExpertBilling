from PyQt4 import QtCore, QtGui

from helpers import tableFormat
from helpers import Object as Object
from helpers import makeHeaders
from helpers import HeaderUtil, SplitterUtil
from helpers import dateDelim
from helpers import setFirstActive

class ebsTableWindow(QtGui.QMainWindow):
    sequenceNumber = 1
    def __init__(self, connection, initargs):
        #print initargs
        self.setname = initargs["setname"]
        bhdr = HeaderUtil.getBinaryHeader(self.setname)
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        self.datetimeFormat = "dd" + dateDelim + "MM" + dateDelim + "yyyy hh:mm:ss"
        self.ebsPreInit(initargs)
        super(ebsTableWindow, self).__init__()
        self.setObjectName(initargs["objname"])
        self.connection = connection
        self.resize(QtCore.QSize(QtCore.QRect(*initargs["winsize"]).size()).expandedTo(self.minimumSizeHint()))
        self.tableWidget = QtGui.QTableWidget()
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setTextElideMode(QtCore.Qt.ElideNone)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        if initargs.has_key("tablesize"):
            self.tableWidget.setGeometry(QtCore.QRect(*initargs["tablesize"]))
        self.setCentralWidget(self.tableWidget)
        self.tableWidget = tableFormat(self.tableWidget)
        
        self.ebsInterInit(initargs) 
        
        self.retranslateUI(initargs)
        HeaderUtil.nullifySaved(self.setname)
        
        self.firsttime = True
        self.refresh()
        
        
        if not bhdr.isEmpty():
            HeaderUtil.setBinaryHeader(self.setname, bhdr)
            HeaderUtil.getHeader(self.setname, self.tableWidget)
        else: self.firsttime = False
        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        
        self.ebsPostInit(initargs)
        
    def retranslateUI(self, initargs):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", initargs["wintitle"], None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()

        columns = initargs["tablecolumns"]
        makeHeaders(columns, self.tableWidget)
        self.restoreWindow()
    
    def ebsRetranslateUi(self, initargs):
        pass
    
    def ebsPreInit(self, initargs):
        pass
    
    def ebsInterInit(self, initargs):
        pass
    
    def ebsPostInit(self, initargs):
        pass
            
    def refresh(self):
        pass
    def getSelectedId(self):
        try:
            return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())
        except Exception,e:
            print e
            return -1
    #list example: [(name, title, iconpath, function)]
    #dict example: {objname:[actname, {"separator"}]
    def actionCreator(self, aList, objDict):
        aDict = {}
        for atuple in aList:
            try:
                setattr(self, atuple[0], QtGui.QAction(self))
                newAct = getattr(self, atuple[0])
                newAct.setIcon(QtGui.QIcon(atuple[2]))
                self.connect(newAct, QtCore.SIGNAL("triggered()"), atuple[3])
                newAct.setText(QtGui.QApplication.translate("MainWindow", atuple[1], None, QtGui.QApplication.UnicodeUTF8)) 
                aDict[atuple[0]] = newAct
            except Exception, ex:
                print "ebsWindow.actionCreator create error: ", repr(ex)
                
        for wObj in objDict.iterkeys():
            for actname in objDict[wObj]:
                try:
                    if actname == "separator":
                        wObj.addSeparator()
                    else:
                        wObj.addAction(aDict[actname])
                except Exception, ex:
                    print "ebsWindow.actionCreator addaction error: ", repr(ex)
    
    def saveHeader(self, *args):
        if self.tableWidget.rowCount():
            HeaderUtil.saveHeader(self.setname, self.tableWidget)
            
    def delNodeLocalAction(self, actList):
        if self.tableWidget.currentRow()==-1:
            for actObj in actList:
                actObj.setDisabled(True)
        else:
            for actObj in actList:
                actObj.setDisabled(False)
    
    def restoreWindow(self):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        val=settings.value("window-geometry-%s" % unicode(self.objectName()), QtCore.QVariant(QtCore.QByteArray())).toByteArray()
        self.restoreGeometry(val)
        
    def closeEvent(self, event):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        settings.setValue("window-geometry-%s" % unicode(self.objectName()), QtCore.QVariant(self.saveGeometry()))
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()    
                     
class ebsTabs_n_TablesWindow(QtGui.QMainWindow):
    sequenceNumber = 1
    def __init__(self, connection, initargs, tabargs):
        #print initargs
        self.setname = initargs["setname"]
        bhdrs = []
        for tabnum in range(len(tabargs)):
            bhdrs.append(HeaderUtil.getBinaryHeader(self.setname + '_tab_' + str(tabnum)))
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        self.datetimeFormat = "dd" + dateDelim + "MM" + dateDelim + "yyyy hh:mm:ss"
        self.ebsPreInit(initargs, tabargs)
        super(ebsTabs_n_TablesWindow, self).__init__()
        self.setObjectName(initargs["objname"])
        self.connection = connection
        self.resize(QtCore.QSize(QtCore.QRect(*initargs["winsize"]).size()).expandedTo(self.minimumSizeHint()))
        
        self.centralwidget = QtGui.QWidget()
        self.centralwidget.setObjectName("centralwidget")

        self.gridlayout = QtGui.QGridLayout(self.centralwidget)
        self.gridlayout.setObjectName("gridlayout")

        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        
        #self.tabs = []
        self.tables = []
        for tabinf in tabargs:
            setattr(self, tabinf[0], QtGui.QWidget())
            newTab =  getattr(self, tabinf[0])
            newTab.setObjectName(tabinf[0])
            setattr(self, tabinf[0]+ "_gridLayout", QtGui.QGridLayout(newTab))
            newGL = getattr(self, tabinf[0] + "_gridLayout")
            setattr(self, tabinf[0]+ "_tableWidget", QtGui.QTableWidget(newTab))
            newTW = getattr(self, tabinf[0] + "_tableWidget")
            newTW = tableFormat(newTW)
            newGL.addWidget(newTW, 0, 0, 1, 1)
            self.tabWidget.addTab(newTab, "")
            self.tables.append(newTW)
            
        self.setCentralWidget(self.centralwidget)
        self.gridlayout.addWidget(self.tabWidget,0,0,1,1)
        
        
        self.ebsInterInit(initargs, tabargs) 
        
        self.retranslateUI(initargs, tabargs)
        for tabnum in range(len(tabargs)):
            HeaderUtil.nullifySaved(self.setname + '_tab_' + str(tabnum))
        

        self.refresh_()
        
        for tabnum in range(len(tabargs)):
            if not bhdrs[tabnum].isEmpty():
                HeaderUtil.setBinaryHeader(self.setname + '_tab_' + str(tabnum), bhdrs[tabnum])
                HeaderUtil.getHeader(self.setname + '_tab_' + str(tabnum), self.tables[tabnum])
                
            tableHeader = self.tables[tabnum].horizontalHeader()
            self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
            self.tables[tabnum].setTextElideMode(QtCore.Qt.ElideNone)
            self.tables[tabnum].setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            
        
        self.ebsPostInit(initargs, tabargs)
        
        
    def retranslateUI(self, initargs, tabargs):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", initargs["wintitle"], None, QtGui.QApplication.UnicodeUTF8))
        
        for i in range(len(tabargs)):   
            self.tabWidget.setTabText(i, QtGui.QApplication.translate("MainWindow", tabargs[i][2], None, QtGui.QApplication.UnicodeUTF8))
            columns = tabargs[i][1]
            self.tables[i].clear()
            makeHeaders(columns, self.tables[i])
            self.restoreWindow()
    
    def ebsRetranslateUi(self, initargs, tabargs):
        pass
    
    def ebsPreInit(self, initargs, tabargs):
        pass
    
    def ebsInterInit(self, initargs, tabargs):
        pass
    
    def ebsPostInit(self, initargs, tabargs):
        pass
            
    def refresh_(self):
        pass
    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())
    
    #list example: [(name, title, iconpath, function)]
    #dict example: {objname:[actname, {"separator"}]
    def actionCreator(self, aList, objDict):
        aDict = {}
        for atuple in aList:
            try:
                setattr(self, atuple[0], QtGui.QAction(self))
                newAct = getattr(self, atuple[0])
                newAct.setIcon(QtGui.QIcon(atuple[2]))
                self.connect(newAct, QtCore.SIGNAL("triggered()"), atuple[3])
                newAct.setText(QtGui.QApplication.translate("MainWindow", atuple[1], None, QtGui.QApplication.UnicodeUTF8)) 
                aDict[atuple[0]] = newAct
            except Exception, ex:
                print "ebsWindow.actionCreator create error: ", repr(ex)
                
        for wObj in objDict.iterkeys():
            for actname in objDict[wObj]:
                try:
                    if actname == "separator":
                        wObj.addSeparator()
                    else:
                        wObj.addAction(aDict[actname])
                except Exception, ex:
                    print "ebsWindow.actionCreator addaction error: ", repr(ex)
    
    def saveHeader(self, *args):
        tIndex = int(self.tabWidget.currentIndex())
        tableWidget = self.tables[tIndex]
        if tableWidget.rowCount():
            HeaderUtil.saveHeader(self.setname + '_tab_' + str(tIndex), tableWidget)
            
    def delNodeLocalAction(self, actList):
        if self.tableWidget.currentRow()==-1:
            for actObj in actList:
                actObj.setDisabled(True)
        else:
            for actObj in actList:
                actObj.setDisabled(False)
    
    def restoreWindow(self):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        val=settings.value("window-geometry-%s" % unicode(self.objectName()), QtCore.QVariant(QtCore.QByteArray())).toByteArray()
        self.restoreGeometry(val)
        
    def closeEvent(self, event):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        settings.setValue("window-geometry-%s" % unicode(self.objectName()), QtCore.QVariant(self.saveGeometry()))
        event.accept()
 
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
                   
                
class ebsTable_n_TreeWindow(QtGui.QMainWindow):
    sequenceNumber = 1
    def __init__(self, connection, initargs):
        #print initargs
        self.setname = initargs["setname"] + "_table"
        self.splname = initargs["setname"] + "_splitter"
        bhdr = HeaderUtil.getBinaryHeader(self.setname)
        bspltr = SplitterUtil.getBinarySplitter(self.splname)
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        self.datetimeFormat = "dd" + dateDelim + "MM" + dateDelim + "yyyy hh:mm:ss"
        #------------
        self.ebsPreInit(initargs)
        #------------
        super(ebsTable_n_TreeWindow, self).__init__()
        self.setObjectName(initargs["objname"])
        self.connection = connection
        self.resize(QtCore.QSize(QtCore.QRect(*initargs["winsize"]).size()).expandedTo(self.minimumSizeHint()))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        #self.centralwidget = QtGui.QWidget(self)
        
        self.centralwidget = QtGui.QWidget(self)
        
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(*initargs["spltsize"]))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        
        self.treeWidget = QtGui.QTreeWidget(self.splitter)
        
        self.tableWidget = QtGui.QTableWidget(self.splitter)
        self.tableWidget.setObjectName("tableWidget")
        
        self.tableWidget.setTextElideMode(QtCore.Qt.ElideNone)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            
        if initargs.has_key("tablesize"):
            self.tableWidget.setGeometry(QtCore.QRect(*initargs["tablesize"]))
        #self.setCentralWidget(self.tableWidget)
        self.tableWidget = tableFormat(self.tableWidget)
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        
        tree_header = self.treeWidget.headerItem()
        hght = self.tableWidget.horizontalHeader().maximumHeight()
        sz = QtCore.QSize()
        sz.setHeight(hght)
        tree_header.setSizeHint(0,sz)
        tree_header.setText(0,QtGui.QApplication.translate("MainWindow", initargs["treeheader"], None, QtGui.QApplication.UnicodeUTF8))
        wwidth =  self.width()
        
        self.setCentralWidget(self.splitter)
        self.splitter.setSizes([wwidth / 5, wwidth - (wwidth / 5)])
        
        if initargs.has_key("menubarsize"):
            self.menubar = QtGui.QMenuBar(self)
            self.menubar.setGeometry(QtCore.QRect(*initargs["menubarsize"]))
            self.menubar.setObjectName("menubar")
            self.setMenuBar(self.menubar)
            
        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)
        if initargs.has_key("tbiconsize"):
            self.toolBar.setIconSize(QtCore.QSize(*initargs["tbiconsize"]))
        
        #---------
        self.ebsInterInit(initargs) 
        #---------
        self.connectTree()
        #---------
        self.retranslateUI(initargs)
        #---------
        
        HeaderUtil.nullifySaved(self.setname)
        SplitterUtil.nullifySaved(self.splname)
        
        self.firsttime = True
        
        self.refreshTree()
        self.refresh_()
        
        try:
            setFirstActive(self.treeWidget)
            if not bhdr.isEmpty():
                HeaderUtil.setBinaryHeader(self.setname, bhdr)
                HeaderUtil.getHeader(self.setname, self.tableWidget)
            else: self.firsttime = False
            if not bspltr.isEmpty():
                SplitterUtil.setBinarySplitter(self.splname, bspltr)
                SplitterUtil.getSplitter(self.splname, self.splitter)                
        except Exception, ex:
            print "Error in setting first element active: ", repr(ex)
        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        self.connect(self.splitter, QtCore.SIGNAL("splitterMoved(int,int)"), self.saveSplitter)
        
        self.ebsPostInit(initargs)
        
    def retranslateUI(self, initargs):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", initargs["wintitle"], None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()

        columns = initargs["tablecolumns"]
        makeHeaders(columns, self.tableWidget)
        self.restoreWindow()
    
    def ebsRetranslateUi(self, initargs):
        pass
    
    def ebsPreInit(self, initargs):
        pass
    
    def ebsInterInit(self, initargs):
        pass
    
    def ebsPostInit(self, initargs):
        pass
            
    def refresh_(self):
        pass
    def refreshTree(self):
        pass
    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())
    def getTreeId(self):
        return self.treeWidget.currentItem().id
    
    #list example: [(name, title, iconpath, function)]
    #dict example: {objname:[actname, {"separator"}]
    def actionCreator(self, aList, objDict):
        aDict = {}
        for atuple in aList:
            try:
                setattr(self, atuple[0], QtGui.QAction(self))
                newAct = getattr(self, atuple[0])
                if atuple[2]:
                    newAct.setIcon(QtGui.QIcon(atuple[2]))
                self.connect(newAct, QtCore.SIGNAL("triggered()"), atuple[3])
                newAct.setText(QtGui.QApplication.translate("MainWindow", atuple[1], None, QtGui.QApplication.UnicodeUTF8)) 
                aDict[atuple[0]] = newAct
            except Exception, ex:
                print "ebsWindow.actionCreator create error: ", repr(ex)
                
        for wObj in objDict.iterkeys():
            for actname in objDict[wObj]:
                try:
                    if actname == "separator":
                        wObj.addSeparator()
                    else:
                        wObj.addAction(aDict[actname])
                except Exception, ex:
                    print "ebsWindow.actionCreator addaction error: ", repr(ex)
    
    def saveHeader(self, *args):
        if self.tableWidget.rowCount():
            HeaderUtil.saveHeader(self.setname, self.tableWidget)
            
    def saveSplitter(self, *args):
        SplitterUtil.saveSplitter(self.splname, self.splitter)
            
    def delNodeLocalAction(self, actList):
        if self.tableWidget.currentRow()==-1:
            for actObj in actList:
                actObj.setDisabled(True)
        else:
            for actObj in actList:
                actObj.setDisabled(False)
                
    def addNodeLocalAction(self, actList):
        if self.treeWidget.currentItem() is None:
            for actObj in actList:
                actObj.setDisabled(True)
        else:
            for actObj in actList:
                actObj.setDisabled(False)
    
    def restoreWindow(self):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        val=settings.value("window-geometry-%s" % unicode(self.objectName()), QtCore.QVariant(QtCore.QByteArray())).toByteArray()
        self.restoreGeometry(val)
        
    def closeEvent(self, event):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        settings.setValue("window-geometry-%s" % unicode(self.objectName()), QtCore.QVariant(self.saveGeometry()))
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
    def editRow(self):
        pass
    def connectTree(self):
        self.connect(self.treeWidget, QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"), self.editRow)
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.refresh_)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.addNodeLocalAction)

        self.connect(self.treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.refresh_)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.addNodeLocalAction)        
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.refresh_)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.addNodeLocalAction)    
           
    def disconnectTree(self):
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"), self.editRow)
        
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.refresh_)
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.addNodeLocalAction)

        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.refresh_)
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.addNodeLocalAction)        
        
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.refresh_)
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.addNodeLocalAction)    

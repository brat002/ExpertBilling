#-*-coding=utf-8*-

from PyQt4 import QtCore, QtGui

from helpers import tableFormat
from helpers import Object as Object
from helpers import makeHeaders
from helpers import HeaderUtil, SplitterUtil
from helpers import dateDelim
from helpers import setFirstActive
import math

class Overlay(QtGui.QWidget):

    def __init__(self, parent = None):
    
        QtGui.QWidget.__init__(self, parent)
        palette = QtGui.QPalette(self.palette())
        palette.setColor(palette.Background, QtCore.Qt.transparent)
        self.setPalette(palette)
    
    def paintEvent(self, event):
    
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(event.rect(), QtGui.QBrush(QtGui.QColor(255, 255, 255, 127)))
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        
        for i in range(6):
            if (self.counter / 5) % 6 == i:
                painter.setBrush(QtGui.QBrush(QtGui.QColor(127 + (self.counter % 5)*32, 127, 127)))
            else:
                painter.setBrush(QtGui.QBrush(QtGui.QColor(127, 127, 127)))
            painter.drawEllipse(
                self.width()/2 + 30 * math.cos(2 * math.pi * i / 6.0) - 10,
                self.height()/2 + 30 * math.sin(2 * math.pi * i / 6.0) - 10,
                20, 20)
        
        painter.end()
    
    def showEvent(self, event):
    
        self.timer = self.startTimer(50)
        self.counter = 0
    
    def timerEvent(self, event):
    
        self.counter += 1
        self.update()
        if self.counter == 60:
            self.killTimer(self.timer)
            self.hide()
            
class ebsTableWindow(QtGui.QMainWindow):
    sequenceNumber = 1
    def __init__(self, connection, initargs, parent=None):
        #print initargs
        self.setname = initargs["setname"]
        bhdr = HeaderUtil.getBinaryHeader(self.setname)
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        self.datetimeFormat = "dd" + dateDelim + "MM" + dateDelim + "yyyy hh:mm:ss"
        self.ebsPreInit(initargs)
        super(ebsTableWindow, self).__init__(parent)
        self.setObjectName(initargs["objname"])
        self.connection = connection
        self.resize(QtCore.QSize(QtCore.QRect(*initargs["winsize"]).size()).expandedTo(self.minimumSizeHint()))
        if initargs.has_key("centralwidget") and initargs["centralwidget"]:            
            self.centralwidget = QtGui.QWidget(self)        
            self.tableWidget = QtGui.QTableWidget(self.centralwidget)
            self.setCentralWidget(self.centralwidget)
        else:
            self.tableWidget = QtGui.QTableWidget(self)
            self.setCentralWidget(self.tableWidget)
        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setTextElideMode(QtCore.Qt.ElideNone)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        if initargs.has_key("tablesize"):
            self.tableWidget.setGeometry(QtCore.QRect(*initargs["tablesize"]))
        #self.setCentralWidget(self.tableWidget)
        self.tableWidget = tableFormat(self.tableWidget)
        
        self.ebsInterInit(initargs) 
        
        
        self.retranslateUI(initargs)
        HeaderUtil.nullifySaved(self.setname)
        
        self.firsttime = True
        self.overlay = Overlay(self.centralWidget())
        self.overlay.hide()
        self.refresh()
        
        
        
        
        if not bhdr.isEmpty():
            HeaderUtil.setBinaryHeader(self.setname, bhdr)
            HeaderUtil.getHeader(self.setname, self.tableWidget)
        else: self.firsttime = False
        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        #self.connect(tableHeader, QtCore.SIGNAL("geometriesChanged()"), self.saveHeader)
        #self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.optpr2)
        #self.connect(tableHeader, QtCore.SIGNAL("sectionAutoResize (int,QHeaderView::ResizeMode)"), self.optpr3)
        
        self.createFindToolbar()
        #self.connect(self.lineEdit_search_text, QtCore.SIGNAL("textEdited (const QString&)"), self.tableFind)
        self.connect(self.pushButton_find, QtCore.SIGNAL("clicked()"), self.tableFind)
        self.connect(self.pushButton_export, QtCore.SIGNAL("clicked()"), self.exportToCSV)

        
        self.ebsPostInit(initargs)
        #self.overlay.show()

    def retranslateUI(self, initargs):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", initargs["wintitle"], None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()

        columns = initargs["tablecolumns"]
        makeHeaders(columns, self.tableWidget)
        self.restoreWindow()
    
    def createFindToolbar(self):
        self.toolBar_find = QtGui.QToolBar(self)
        self.toolBar_find.setMovable(True)
        self.toolBar_find.setFloatable(True)
        self.label_search_text = QtGui.QLabel(self)
        self.label_search_text.setText(u'Поиск:')
        self.lineEdit_search_text = QtGui.QLineEdit(self)
        self.lineEdit_search_text.setMaximumHeight(20)
        self.lineEdit_search_text.setContentsMargins(0,0,0,0)
        
        self.pushButton_find = QtGui.QToolButton(self)
        self.pushButton_find.setIcon(QtGui.QIcon("images/search.png"))
        self.pushButton_find.setMaximumHeight(20)
        self.toolBar_find.addWidget(self.label_search_text)
        self.toolBar_find.addWidget(self.lineEdit_search_text)
        self.toolBar_find.addWidget(self.pushButton_find)

        self.pushButton_export = QtGui.QToolButton(self)
        self.pushButton_export.setIcon(QtGui.QIcon("images/fileexport.png"))
        self.pushButton_export.setMaximumHeight(20)
        
        self.toolBar_find.addWidget(self.pushButton_export)
        
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar_find)
        self.insertToolBarBreak(self.toolBar_find)
        
    def export_action(self):
        pass
    
    def tableFind(self):
        self.tableWidget.clearSelection()
        for y in xrange(self.tableWidget.rowCount()):
            for x in xrange(self.tableWidget.columnCount()):
                #print "check"
                if unicode((self.tableWidget.item(y,x) and self.tableWidget.item(y,x).text()) or '').lower().rfind(unicode(self.lineEdit_search_text.text()).lower())>-1 and unicode(self.lineEdit_search_text.text()).lower():
                    self.tableWidget.scrollToItem(self.tableWidget.item(y,x))
                    self.tableWidget.setItemSelected(self.tableWidget.item(y,x), True)
                    #print "finded!"
                    #break
            
    def exportToCSV(self):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        val=settings.value("exportcsv-%s" % unicode(self.objectName()), QtCore.QVariant('')).toString()

        

        fileName = str(QtGui.QFileDialog.getSaveFileName(self, u"Экспорт CSV", val, "CSV Files (*.csv)")).decode('mbcs')
        if fileName=="":
            return
        settings.setValue("exportcsv-%s" % unicode(self.objectName()), QtCore.QVariant(fileName))
        
        try:
            
            f = open(fileName, "w")
            column_count = self.tableWidget.columnCount()

            for x in xrange(column_count):
                try:
                    f.write(self.tableWidget.horizontalHeaderItem(x).text().toLocal8Bit())
                except Exception, e:
                    print e
                    f.write("")
                finally:
                    f.write(";")
            f.write("\n")   
            for x in xrange(self.tableWidget.rowCount()):
                for i in xrange(column_count):
                    try:
                        f.write(self.tableWidget.item(x, i).text().toLocal8Bit())
                    except Exception, e:
                        print e
                        f.write("")
                    finally:
                        f.write(";")
                f.write("\n")
            f.close()
            QtGui.QMessageBox.information(self, u"Файл успешно сохранён", unicode(u"Операция произведена успешно."))
        except Exception, e:
            
            QtGui.QMessageBox.warning(self, u"Ошибка‹", unicode(u"Ошибка при сохранении."))
            raise e
            
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
            return 0
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
        if (self.tableWidget.currentRow()==-1) and (len(self.tableWidget.selectedIndexes()) == 0):
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
        self.saveHeader()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()    
        if event.key() == QtCore.Qt.Key_Return and self.lineEdit_search_text.hasFocus()==True:
            self.tableFind()

    def resizeEvent(self, event):
    
        self.overlay.resize(event.size())
        event.accept()
          
            
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
            self.tables[tabnum].setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            
        
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
        if event.key() == QtCore.Qt.Key_Return and self.lineEdit_search_text.hasFocus()==True:
            self.tableFind()
                
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
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            
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
        
        self.toolBar2 = QtGui.QToolBar(self)
        self.toolBar2.setMovable(False)
        self.toolBar2.setFloatable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar2)
        if initargs.has_key("tbiconsize"):
            self.toolBar.setIconSize(QtCore.QSize(*initargs["tbiconsize"]))
            self.toolBar2.setIconSize(QtCore.QSize(*initargs["tbiconsize"]))
        
        self.insertToolBarBreak(self.toolBar2)
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
        
        #self.refreshTree()
        #self.refresh_()
        
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
        self.createFindToolbar()
        #self.connect(self.lineEdit_search_text, QtCore.SIGNAL("textEdited (const QString&)"), self.tableFind)
        self.connect(self.pushButton_find, QtCore.SIGNAL("clicked()"), self.tableFind)
        self.connect(self.pushButton_export, QtCore.SIGNAL("clicked()"), self.exportToCSV)

        self.ebsPostInit(initargs)
        
    def retranslateUI(self, initargs):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", initargs["wintitle"], None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.clear()

        columns = initargs["tablecolumns"]
        makeHeaders(columns, self.tableWidget)
        self.restoreWindow()
    
    def ebsRetranslateUi(self, initargs):
        pass
    

    def createFindToolbar(self):
        self.toolBar_find = QtGui.QToolBar(self)
        self.toolBar_find.setMovable(False)
        self.toolBar_find.setFloatable(False)
        self.label_search_text = QtGui.QLabel(self)
        self.label_search_text.setText(u'Поиск:')        
        self.lineEdit_search_text = QtGui.QLineEdit(self)
        self.lineEdit_search_text.setMaximumHeight(20)
        self.lineEdit_search_text.setContentsMargins(0,0,0,0)
        self.pushButton_find = QtGui.QToolButton(self)
        self.pushButton_find.setIcon(QtGui.QIcon("images/search.png"))
        self.pushButton_find.setMaximumHeight(20)
        self.toolBar_find.addWidget(self.label_search_text)
        self.toolBar_find.addWidget(self.lineEdit_search_text)
        self.toolBar_find.addWidget(self.pushButton_find)

        self.pushButton_export = QtGui.QToolButton(self)
        self.pushButton_export.setIcon(QtGui.QIcon("images/fileexport.png"))
        self.pushButton_export.setMaximumHeight(20)
        
        self.toolBar_find.addWidget(self.pushButton_export)
        
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar_find)
        self.insertToolBarBreak(self.toolBar_find)
        
    def tableFind(self):
        self.tableWidget.clearSelection()
        for y in xrange(self.tableWidget.rowCount()):
            for x in xrange(self.tableWidget.columnCount()):
                #print "check"
                try:
                    if unicode(self.tableWidget.item(y,x).text()).lower().rfind(unicode(self.lineEdit_search_text.text()).lower())>-1:
                        self.tableWidget.scrollToItem(self.tableWidget.item(y,x))
                        self.tableWidget.setItemSelected(self.tableWidget.item(y,x), True)
                except:
                    pass
                    #print "finded!"
                    #break

    def exportToCSV(self):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        val=settings.value("exportcsv-%s" % unicode(self.objectName()), QtCore.QVariant('')).toString()

        

        fileName = str(QtGui.QFileDialog.getSaveFileName(self, u"Экспорт CSV", val, "CSV Files (*.csv)")).decode('mbcs')
        if fileName=="":
            return
        settings.setValue("exportcsv-%s" % unicode(self.objectName()), QtCore.QVariant(fileName))
        try:
            
            f = open(fileName, "w")
            column_count = self.tableWidget.columnCount()

            for x in xrange(column_count):
                try:
                    f.write(self.tableWidget.horizontalHeaderItem(x).text().toLocal8Bit())
                    
                except Exception, e:
                    print e
                    f.write("")
                finally:
                    f.write(";")
            f.write("\n")
            for x in xrange(self.tableWidget.rowCount()):
                for i in xrange(column_count):
                    try:
                        f.write(self.tableWidget.item(x, i).text().toLocal8Bit())

                    except Exception, e:
                        print e
                        f.write("")
                    finally:
                        f.write(";")
                f.write("\n")
            f.close()
            QtGui.QMessageBox.information(self, u"Файл успешно сохранён", unicode(u"Операция произведена успешно."))
        except Exception, e:
            print e
            QtGui.QMessageBox.warning(self, u"Ошибка‹", unicode(u"Ошибка при сохранении."))
            
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
        try:
            return self.treeWidget.currentItem().id
        except:
            return 0
    
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
        realm = self.getTreeId()
        if self.tableWidget.rowCount():
            HeaderUtil.saveHeader("%s%s" % (self.setname,realm<0), self.tableWidget)
            
    def saveSplitter(self, *args):
        SplitterUtil.saveSplitter(self.splname, self.splitter)
            
    def delNodeLocalAction(self, actList):
        disable = False
        
        rows = 0
        for r in self.tableWidget.selectedRanges():
            rows += r.rowCount() 
        #if rows>1:
        #    disable=True
                
        if self.tableWidget.currentRow()==-1 or disable==True:
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
        #print "key pressed"
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        #print event.key()
        if event.key() == QtCore.Qt.Key_Return and self.lineEdit_search_text.hasFocus()==True:
            self.tableFind()
            
    def editRow(self):
        pass
    def editTarif(self):
        pass
    
    def connectTree(self):
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"), self.editTarif)
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.refresh_)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.addNodeLocalAction)

        self.connect(self.treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.refresh_)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.addNodeLocalAction)        
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.refresh_)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.addNodeLocalAction)    
           
    def disconnectTree(self):
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"), self.editTarif)
        
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.refresh_)
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.addNodeLocalAction)

        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.refresh_)
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.addNodeLocalAction)        
        
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.refresh_)
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.addNodeLocalAction)    


class ebsTableView_n_TreeWindow(QtGui.QMainWindow):
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
        super(ebsTableView_n_TreeWindow, self).__init__()
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
        
        self.tableWidget = QtGui.QTableView(self.splitter)
        self.tableWidget.setObjectName("tableWidget")
        
        self.tableWidget.setTextElideMode(QtCore.Qt.ElideNone)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            
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
        
        self.toolBar2 = QtGui.QToolBar(self)
        self.toolBar2.setMovable(False)
        self.toolBar2.setFloatable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar2)
        if initargs.has_key("tbiconsize"):
            self.toolBar.setIconSize(QtCore.QSize(*initargs["tbiconsize"]))
            self.toolBar2.setIconSize(QtCore.QSize(*initargs["tbiconsize"]))
        
        self.insertToolBarBreak(self.toolBar2)
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
        
        #self.refreshTree()
        #self.refresh_()
        
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
        self.createFindToolbar()
        #self.connect(self.lineEdit_search_text, QtCore.SIGNAL("textEdited (const QString&)"), self.tableFind)
        self.connect(self.pushButton_find, QtCore.SIGNAL("clicked()"), self.tableFind)
        self.connect(self.pushButton_export, QtCore.SIGNAL("clicked()"), self.exportToCSV)

        self.ebsPostInit(initargs)
        
    def retranslateUI(self, initargs):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", initargs["wintitle"], None, QtGui.QApplication.UnicodeUTF8))
        #self.tableWidget.clear()

        columns = initargs["tablecolumns"]
        #makeHeaders(columns, self.tableWidget)
        self.restoreWindow()
    
    def ebsRetranslateUi(self, initargs):
        pass
    

    def createFindToolbar(self):
        self.toolBar_find = QtGui.QToolBar(self)
        self.toolBar_find.setMovable(False)
        self.toolBar_find.setFloatable(False)
        self.label_search_text = QtGui.QLabel(self)
        self.label_search_text.setText(u'Поиск:')        
        self.lineEdit_search_text = QtGui.QLineEdit(self)
        self.lineEdit_search_text.setMaximumHeight(20)
        self.lineEdit_search_text.setContentsMargins(0,0,0,0)
        self.pushButton_find = QtGui.QToolButton(self)
        self.pushButton_find.setIcon(QtGui.QIcon("images/search.png"))
        self.pushButton_find.setMaximumHeight(20)
        self.toolBar_find.addWidget(self.label_search_text)
        self.toolBar_find.addWidget(self.lineEdit_search_text)
        self.toolBar_find.addWidget(self.pushButton_find)

        self.pushButton_export = QtGui.QToolButton(self)
        self.pushButton_export.setIcon(QtGui.QIcon("images/fileexport.png"))
        self.pushButton_export.setMaximumHeight(20)
        
        self.toolBar_find.addWidget(self.pushButton_export)
        
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar_find)
        self.insertToolBarBreak(self.toolBar_find)
        
    def tableFind(self):
        self.tableWidget.clearSelection()
        model = self.tableWidget.model()
        searched_text = unicode(self.lineEdit_search_text.text()).lower()
        
        for column in xrange(self.tableWidget.model().columnCount(self)):
            for row in xrange(self.tableWidget.model().rowCount(self)):
                try:
                    
                    index = self.tableWidget.model().index(row, column)
                    data = unicode(model.data(index, QtCore.Qt.DisplayRole).toString()).lower()
                    if data and data.rfind(searched_text)!=-1:
                        self.tableWidget.scrollTo(index)
                        self.tableWidget.selectRow(row)
                        #return
                except Exception, e:
                    print e
                    pass
                #print "finded!"
                #break

    def exportToCSV(self):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        val=settings.value("exportcsv-%s" % unicode(self.objectName()), QtCore.QVariant('')).toString()

        

        fileName = str(QtGui.QFileDialog.getSaveFileName(self, u"Экспорт CSV", val, "CSV Files (*.csv)")).decode('mbcs')
        if fileName=="":
            return
        settings.setValue("exportcsv-%s" % unicode(self.objectName()), QtCore.QVariant(fileName))
        try:
            
            f = open(fileName, "w")
            column_count = self.tableWidget.columnCount()

            for x in xrange(column_count):
                try:
                    f.write(self.tableWidget.horizontalHeaderItem(x).text().toLocal8Bit())
                    
                except Exception, e:
                    print e
                    f.write("")
                finally:
                    f.write(";")
            f.write("\n")
            for x in xrange(self.tableWidget.rowCount()):
                for i in xrange(column_count):
                    try:
                        f.write(self.tableWidget.item(x, i).text().toLocal8Bit())

                    except Exception, e:
                        print e
                        f.write("")
                    finally:
                        f.write(";")
                f.write("\n")
            f.close()
            QtGui.QMessageBox.information(self, u"Файл успешно сохранён", unicode(u"Операция произведена успешно."))
        except Exception, e:
            print e
            QtGui.QMessageBox.warning(self, u"Ошибка‹", unicode(u"Ошибка при сохранении."))
            
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
        try:
            return self.treeWidget.currentItem().id
        except:
            return 0
    
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
        realm = self.getTreeId()

        HeaderUtil.saveHeader("%s%s" % (self.setname,realm<0), self.tableWidget)
            
    def saveSplitter(self, *args):
        SplitterUtil.saveSplitter(self.splname, self.splitter)
            
    def delNodeLocalAction(self, actList):
        disable = False
        
        rows = 0
        for r in self.tableWidget.selectedIndexes():
            rows += r.rowCount() 
        #if rows>1:
        #    disable=True
                
        if self.tableWidget.currentIndex().row==-1 or disable==True:
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
        #print "key pressed"
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        #print event.key()
        if event.key() == QtCore.Qt.Key_Return and self.lineEdit_search_text.hasFocus()==True:
            self.tableFind()
            
    def editRow(self):
        pass
    def editTarif(self):
        pass
    
    def connectTree(self):
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"), self.editTarif)
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.refresh_)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.addNodeLocalAction)

        self.connect(self.treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.refresh_)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.addNodeLocalAction)        
        
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.refresh_)
        self.connect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.addNodeLocalAction)    
           
    def disconnectTree(self):
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemDoubleClicked (QTreeWidgetItem *,int)"), self.editTarif)
        
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.refresh_)
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem *,int)"), self.addNodeLocalAction)

        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.refresh_)
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemActivated(QTreeWidgetItem *,int)"), self.addNodeLocalAction)        
        
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.refresh_)
        self.disconnect(self.treeWidget, QtCore.SIGNAL("itemSelectionChanged()"), self.addNodeLocalAction)    
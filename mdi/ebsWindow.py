from PyQt4 import QtCore, QtGui

from helpers import tableFormat
from helpers import Object as Object
from helpers import makeHeaders
from helpers import HeaderUtil
from helpers import dateDelim

class ebsTableWindow(QtGui.QMainWindow):
    sequenceNumber = 1
    def __init__(self, connection, initargs):
        #print initargs
        self.setname = initargs["setname"]
        bhdr = HeaderUtil.getBinaryHeader(self.setname)
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        self.ebsPreInit(initargs)
        super(ebsTableWindow, self).__init__()
        self.setObjectName(initargs["objname"])
        self.connection = connection
        self.resize(QtCore.QSize(QtCore.QRect(*initargs["winsize"]).size()).expandedTo(self.minimumSizeHint()))
        self.tableWidget = QtGui.QTableWidget()
        self.tableWidget.setObjectName("tableWidget")
        if initargs.has_key("tablesize"):
            self.tableWidget.setGeometry(QtCore.QRect(*initargs["tablesize"]))
        self.setCentralWidget(self.tableWidget)
        
        
        self.ebsInterInit(initargs)
        
        
        self.retranslateUI(initargs)
        HeaderUtil.nullifySaved(self.setname)
        self.tableWidget = tableFormat(self.tableWidget)
        self.refresh()
        self.firsttime = True
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
    
    def ebsRetranslateUi(self, initargs):
        pass
    
    def ebsPreInit(self, initargs):
        pass
    
    def ebsInterInit(self, initargs):
        pass
    
    def ebsPostInit(self, initargs):
        pass
    
    def retranslateUi(self):
        pass
    
    def addrow(self):
        pass
            
    def refresh(self):
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
        if self.tableWidget.rowCount():
            HeaderUtil.saveHeader(self.setname, self.tableWidget)
            
    def delNodeLocalAction(self, actList):
        if self.tableWidget.currentRow()==-1:
            for actObj in actList:
                actObj.setDisabled(True)
        else:
            for actObj in actList:
                actObj.setDisabled(True)
    

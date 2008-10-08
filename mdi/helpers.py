#-*-encoding:utf-8-*-

from PyQt4 import QtGui, QtCore, QtSql
from types import InstanceType, StringType, UnicodeType
import Pyro.errors
import datetime
import os
import time
dateDelim = "."
connectDBName = "exbillusers"
tableHeight = 17

def tableFormat(table):
    #setTableHeight(table)
    #table.verticalHeader().setDefaultSectionSize(table.fontMetrics().height()+3)
    table.verticalHeader().setDefaultSectionSize(tableHeight)
    table.setFrameShape(QtGui.QFrame.Panel)
    table.setFrameShadow(QtGui.QFrame.Sunken)
    #table.setAlternatingRowColors(True)
    table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
    table.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
    table.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
    table.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
    #table.setGridStyle(QtCore.Qt.DotLine)
    table.setSortingEnabled(False)
    table.setEditTriggers(QtGui.QTableWidget.NoEditTriggers)
    table.verticalHeader().setHidden(True)
    table.setColumnHidden(0, True)
    hh = table.horizontalHeader()
    hh.setMaximumHeight(17)
    hh.setStretchLastSection(True)
    hh.setHighlightSections(False)
    hh.setClickable(True)
    hh.setMovable(False)
    hh.ResizeMode(QtGui.QHeaderView.Stretch)
    
    return table

def createHeader(text):
    headerItem = QtGui.QTableWidgetItem()
    headerItem.setTextAlignment(QtCore.Qt.AlignVCenter)
    headerItem.setText(text)
    return headerItem
  
def makeHeaders(columns, table):
    
    table.setColumnCount(len(columns))
    
    i=0
    for header in map(createHeader, columns):
        table.setHorizontalHeaderItem(i, header)
        i+=1

        
def connlogin(func):
    def relogfunc(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except Pyro.errors.ConnectionClosedError, cce:
            print cce
            QtGui.QMessageBox.warning(args[0], u"Внимание", unicode(u"Потеря связи."))
        except Pyro.errors.ConnectionDeniedError, cde:
            print cde
            QtGui.QMessageBox.warning(args[0], u"Внимание", unicode(u"Действие не авторизовано."))
    return relogfunc

def setFirstActive(listWidget):
    try:
        if isinstance(listWidget, QtGui.QTreeWidget):
            listWidget.setCurrentItem(listWidget.topLevelItem(0))
        elif listWidget.rowCount > 0:
            listWidget.setCurrentItem(listWidget.item(0, 0))
    except Exception, ex:
        print ex
        
def setTableHeight(tableWidget):
    try:
        height = tableWidget.fontMetrics().height()
        tableWidget.verticalHeader().setDefaultSectionSize(height+3)
    except Exception, ex:
        print "Error in setTableHeight: ", ex

class HeaderUtil(object):
    @staticmethod
    def nullifySaved(name):
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue(name, QtCore.QVariant(QtCore.QByteArray()))
        except Exception, ex:
            print "HeaderUtil settings nullify error: ", ex
            
    @staticmethod
    def saveHeader(name, table):
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue(name, QtCore.QVariant(table.horizontalHeader().saveState()))
            #print "save header"
        except Exception, ex:
            print "HeaderUtil settings save error: ", ex
            
    @staticmethod
    def setBinaryHeader(name, bhdr):
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue(name, QtCore.QVariant(bhdr))
        except Exception, ex:
            print "HeaderUtil settings save error: ", ex
            
    @staticmethod
    def getBinaryHeader(name):
        bhdr = QtCore.QByteArray()
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            bhdr =  settings.value(name, QtCore.QVariant(QtCore.QByteArray())).toByteArray()
        except Exception, ex:
            print "Frame settings error: ", ex
        return bhdr
    
    @staticmethod
    def getHeader(name, table):
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            headerState = settings.value(name, QtCore.QVariant(QtCore.QByteArray())).toByteArray()
            if not headerState.isEmpty():
                table.horizontalHeader().restoreState(headerState)
            else:
                table.resizeColumnsToContents()
        except Exception, ex:
            print "Frame settings error: ", ex
            table.resizeColumnsToContents()
            
class SplitterUtil(object):
    @staticmethod
    def nullifySaved(name):
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue(name, QtCore.QVariant(QtCore.QByteArray()))
        except Exception, ex:
            print "SplitterUtil settings nullify error: ", ex
            
    @staticmethod
    def saveSplitter(name, splitter):
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue(name, QtCore.QVariant(splitter.saveState()))
            #print "save header"
        except Exception, ex:
            print "SplitterUtil settings save error: ", ex
            
    @staticmethod
    def setBinarySplitter(name, bspltr):
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue(name, QtCore.QVariant(bspltr))
        except Exception, ex:
            print "HeaderUtil settings save error: ", ex
            
    @staticmethod
    def getBinarySplitter(name):
        bspltr = QtCore.QByteArray()
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            bspltr =  settings.value(name, QtCore.QVariant(QtCore.QByteArray())).toByteArray()
        except Exception, ex:
            print "Frame settings error: ", ex
        return bspltr
    
    @staticmethod
    def getSplitter(name, splitter):
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            splitterState = settings.value(name, QtCore.QVariant(QtCore.QByteArray())).toByteArray()
            if not splitterState.isEmpty():
                splitter.restoreState(splitterState)
            else:
                wwidth = splitter.parent().width()
                splitter.setSizes([wwidth / 5, wwidth - (wwidth / 5)])
        except Exception, ex:
            print "Frame settings error: ", ex
            wwidth = splitter.parent().width()
            splitter.setSizes([wwidth / 5, wwidth - (wwidth / 5)])
            

def format_update (x,y):
    if y!='Null' and y!='None':
        if type(y)==StringType or type(y)==UnicodeType:
            y=y.replace("\\", r"\\").replace(r"'", r"\'").replace(r'"', r'\"')
            print y
        return "%s='%s'" % (x,y)
    else:
        return "%s=%s" % (x,'Null')

def format_insert(y):
    if y=='None' or y == 'Null':
        return y
    elif type(y)==StringType or type(y)==UnicodeType:
        return y.replace("\\", r"\\").replace(r"'", r"\'").replace(r'"', r'\"')
    else:
        return y
        

class Object(object):
    def __init__(self, result=[], *args, **kwargs):
        for key in result:
            setattr(self, key, result[key])
        """
        if result[key]!=None:
            setattr(self, key, result[key])
        else:
            setattr(self, key, 'Null')
        """


        for key in kwargs:
            setattr(self, key, kwargs[key])  
        
        #print dir(self)          
            
         
    def save(self, table):
        
        
        fields=[]
        for field in self.__dict__:
            if type(field)!=InstanceType:
                # and self.__dict__[field]!=None
                fields.append(field)
        try:
            self.__dict__['id']
            sql=u"UPDATE %s SET %s WHERE id=%d;" % (table, " , ".join([format_update(x, unicode(self.__dict__[x])) for x in fields ]), self.__dict__['id'])
        except:
            sql=u"INSERT INTO %s (%s) VALUES('%s') RETURNING id;" % (table, ",".join([x for x in fields]), ("%s" % "','".join([format_insert(unicode(self.__dict__[x])) for x in fields ]).replace("'None'", 'Null')))
        return sql
    
    def get(self, table):
        return "SELECT * FROM %s WHERE id=%d" % (table, int(self.id))
    
    def __call__(self):
        return self.id
    
    def hasattr(self, attr):
        if attr in self.__dict__:
            return True
        return False
    
    def isnull(self, attr):
        if self.hasattr(attr):
            if self.__dict__[attr]!=None:
                return False
            
        return True
    

        

    

class sqliteDbAccess(object):
    def __init__(self, dbname, dbtype=''):
        '''
    #self.filestat codes for 'system' type:
    
    1: HOME
    2: HOME created
    3: dbname
    4: dbname created
            
        '''
        #self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        if dbtype == 'system':
            if os.name == "nt":
                if os.environ.has_key('USERPROFILE'):
                    if os.path.exists(os.environ['USERPROFILE'] + '\\' + dbname):
                        self.dbfile = os.environ['USERPROFILE'] + '\\' + dbname
                        self.filestat = 1
                    elif os.path.exists(dbname):
                        self.dbfile = dbname
                        self.filestat = 3
                    else:
                        self.dbfile = os.environ['USERPROFILE'] + '\\' + dbname
                        self.filestat = 2
                elif os.path.exists(dbname):
                    self.dbfile = dbname
                    self.filestat = 3
                else:
                    self.dbfile = dbname
                    self.filestat = 4
            else:
                if os.environ.has_key('HOME'):
                    if os.path.exists(os.environ['HOME'] + '/' + dbname):
                        self.dbfile = os.environ['HOME'] + '/' + dbname
                        self.filestat = 1
                    elif os.path.exists(dbname):
                        self.dbfile = dbname
                        self.filestat = 3
                    else:
                        self.dbfile = os.environ['HOME'] + '/' + dbname
                        self.filestat = 2
                elif os.path.exists(dbname):
                    self.dbfile = dbname
                    self.filestat = 3
                else:
                    self.dbfile = dbname
                    self.filestat = 4

        else:
            self.dbfile = dbname
            self.filestat = 1
            
        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(self.dbfile)
            
    def action(self, qstr, type, vartuple=None):
        if vartuple:
            qstr = qstr % vartuple   

        if not self.db.open():
            raise Exception("QSQLITE DATABASE CONNECTION ERROR: " + self.dbfile)
        
        qquery = QtSql.QSqlQuery(qstr)
        
        if not qquery.isActive():
            raise Exception("QSQLITE DATABASE QUERY EXECUTE ERROR: " + qstr)
        
        if type == 'select':
            res = []
            while (qquery.next()):
                res.append(qquery.record())
            return res
        
        return qquery.numRowsAffected()
    
    def select(self, qstr, vartuple=None):        
        return self.action(qstr, 'select', vartuple)
    
    def insert(self, qstr, vartuple=None):        
        return self.action(qstr, 'insert', vartuple)
    
    def delete(self, qstr, vartuple=None):        
        return self.action(qstr, 'delete', vartuple)
    
    def update(self, qstr, vartuple=None):        
        return self.action(qstr, 'update', vartuple)
    
    def getTableModel(self, table):
        self.db.open()
        tModel = QtSql.QSqlTableModel(None, self.db)
        tModel.setTable(table)
        
        return tModel
        
            
def transaction(account_id, type_id, approved, description, summ, bill):
    
    o = Object()
    o.account_id = account_id
    o.type_id = type_id
    o.approved = approved
    o.description = description
    o.summ = summ
    o.bill = bill
    #o.tarif_id=1
    o.created = datetime.datetime.now()
    
    sql = "UPDATE billservice_account SET ballance = ballance - %d WHERE id = %d;" % (summ, account_id)
    sql += o.save("billservice_transaction")
    
     
    return sql 

    
def humanable_bytes(a):
    """
    Функция для удобного человеку предоставления обхёма трафика
    """
    if a is not None:
        try:
            a=float(a)
            #res = a/1024
            if a>1024 and a<(1024*1000):
                return u"%.5s KB" % unicode(a/(1024))
            elif a>=(1024*1000) and a<=(1024*1000*1000):
                return u"%.5s МB" % unicode(a/(1024*1000))
            elif a>(1024*1000*1000):
                return u"%.5s GB" % unicode(a/(1024*1000*1000))
            elif a<1024:
                return u"%s B" % unicode(int(a)) 
        except Exception, e:
            print e
    
    return 0
    
class Worker(QtCore.QThread):
    """
    Timer Class
    import time
    def __init__(self, connection):
        super(MonitorFrame, self).__init__()
        self.thread = Worker()
        self.connect(self.thread, QtCore.SIGNAL("refresh()"), self.fixtures)
        self.thread.go(interval=10)
    """
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
    
    def __del__(self):
    
        self.exiting = True
        self.wait()

    def go(self, interval=60):
        self.interval=interval
        self.start()

    def run(self):
        
        while True:
            
            
            time.sleep(self.interval)
            print "emit"
            self.emit(QtCore.SIGNAL("refresh()"))
                    

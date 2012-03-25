#-*-encoding:utf-8-*-

from PyQt4 import QtGui, QtCore, QtSql
from types import InstanceType, StringType, UnicodeType
#import Pyro.errors
from re import escape
import datetime
import os, sys
sys.path.append(os.path.abspath('../'))
import time
import string
import traceback
import IPy
from dateutil.relativedelta import relativedelta
dateDelim = "."
connectDBName = "exbillusers"
tableHeight = 17

class GenericThread(QtCore.QThread):
    def __init__(self, connection, sql):
        QtCore.QThread.__init__(self)
        self.connection=connection
        self.sql=sql

    def __del__(self):
      self.wait()

    def run(self):
        print "send request"
        data=self.connection.sql(self.sql)
        print "get response"
        self.emit(QtCore.SIGNAL("refresh(QVariant)"), data)
        #self.terminate()
        
class AccountsRefreshThread(QtCore.QThread):
    def __init__(self, connection, tarif_id):
        QtCore.QThread.__init__(self)
        self.connection=connection
        self.tarif_id=tarif_id

    def __del__(self):
      self.wait()

    def run(self):
        print "send request"
        data= self.connection.get_accounts_for_tarif(self.tarif_id)
        print "get response"
        self.emit(QtCore.SIGNAL("accountsRefresh(QVariant)"), data)
        self.terminate()
        
class AccountsFilterThread(QtCore.QThread):
    def __init__(self, connection, sql):
        QtCore.QThread.__init__(self)
        self.connection=connection
        self.sql=sql

    def __del__(self):
      self.wait()

    def run(self):
        print "send request"
        data=self.connection.get_accounts_for_tilter(self.sql)
        print "get response"
        self.emit(QtCore.SIGNAL("accountsRefresh(QVariant)"), data)
        self.terminate()
         
def settlement_period_info(time_start, repeat_after='', repeat_after_seconds=0,  now=None, prev = False):
    """
        Функция возвращает дату начала и дату конца текущего периода
        @param time_start: время начала расчётного периода
        @param repeat_after: период повторения в константах
        @param repeat_after_seconds: период повторения в секундах
        @param now: текущая дата
        @param prev: получить данные о прошлом расчётном периоде     
    """

    #print time_start, repeat_after, repeat_after_seconds,  now

    if not now:
        now=datetime.datetime.now()
    #time_start=time_start.replace(tzinfo='UTC')
    #print "repeat_after_seconds=",repeat_after_seconds
    if repeat_after_seconds>0:
        #print 1
        delta_days = (now - time_start) if not prev else (now-datetime.timedelta(seconds=repeat_after_seconds) - time_start)
        length=repeat_after_seconds
        if repeat_after!='DONT_REPEAT':
            #Когда будет начало в текущем периоде.
            nums,ost= divmod(delta_days.days*86400+delta_days.seconds, length)
            tnc=now-datetime.timedelta(seconds=ost)
            #Когда это закончится
            tkc=tnc+datetime.timedelta(seconds=length)
            return (tnc, tkc, length)
        else:
            return (time_start,time_start+datetime.timedelta(seconds=repeat_after_seconds), repeat_after_seconds)
    elif repeat_after=='DAY':
        delta_days = (now - time_start) if not prev else (now-datetime.timedelta(seconds=86400) - time_start)
        length=86400
        #Когда будет начало в текущем периоде.
        nums,ost= divmod(delta_days.days*86400+delta_days.seconds, length)
        tnc=now-datetime.timedelta(seconds=ost)
        #Когда это закончится
        tkc=tnc+datetime.timedelta(seconds=length)
        return (tnc, tkc, length)

    elif repeat_after=='WEEK':
        delta_days = (now - time_start) if not prev else (now-datetime.timedelta(seconds=604800) - time_start)
        length=604800
        #Когда будет начало в текущем периоде.
        nums,ost= divmod(delta_days.days*86400+delta_days.seconds, length)
        tnc=time_start+relativedelta(weeks=nums)
        tkc=tnc+relativedelta(weeks=1)

        return (tnc, tkc, length)
    elif repeat_after=='MONTH':
        rdelta = relativedelta(now, time_start) if not prev else relativedelta(now-relativedelta(months=1),time_start)
        tnc=time_start+relativedelta(months=rdelta.months, years = rdelta.years)
        tkc=tnc+relativedelta(months=1)
        delta=tkc-tnc

        return (tnc, tkc, delta.days*86400+delta.seconds)
    elif repeat_after=='YEAR':
        #Февраль!
        #To-DO: Добавить проверку на prev 
        tnc=time_start+relativedelta(years=relativedelta(now, time_start).years)

        tkc=tnc+relativedelta(years=1)
        delta=tkc-tnc
        return (tnc, tkc, delta.days*86400+delta.seconds)
    
def tableFormat(table, no_vsection_size=False):
    #setTableHeight(table)
    #table.verticalHeader().setDefaultSectionSize(table.fontMetrics().height()+3)
    if no_vsection_size==False:
        table.verticalHeader().setDefaultSectionSize(tableHeight)
    table.setFrameShape(QtGui.QFrame.Panel)
    table.setFrameShadow(QtGui.QFrame.Sunken)
    table.setAlternatingRowColors(False)
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
    hh.setStretchLastSection(False)
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
        except Exception, cce:
            print repr(cce)
            QtGui.QMessageBox.warning(args[0], u"Внимание", unicode(u"%s." % repr(cce)))
        '''
        except Pyro.errors.ConnectionDeniedError, cde:
            print repr(cde)
            QtGui.QMessageBox.warning(args[0], u"Внимание", unicode(u"Действие не авторизовано."))
        '''
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
def card_template_parser(command_string='', command_dict={}):
    
    import re
    if len(command_string) == 0 or len(command_dict) == 0:
        return ''
    pattern = re.compile('\$\w+?\$')
    match = pattern.finditer(command_string)
    if match is None:
        return ''
    params = [m.group()[1:-1] for m in match]
    i = 0
    for p in params :
        if p in command_dict.keys() :
            s = re.compile( '\$%s\$' % p)
            command_string = s.sub(str(command_dict[p]),command_string)
            i +=1
            
    return (command_string, i)

#TODO:exceptions
def write_cards(template_fname, pattern_dicts, strict=True, adddicts=[]):
    if not os.path.exists(template_fname):
        raise Exception("Template file doesn't exist!")
    tmpl_basename = os.path.basename(template_fname)
    #tmpl_dirname = os.pa
    f = open(template_fname, "rb")
    template_str = f.read()
    f.close()
    ext_str = ''
    if template_fname[-4] == '.':
        ext_str = template_fname[-4:]
    elif template_fname[-5] == '.':
        ext_str = template_fname[-5:]
    i = 0
    fnames = []
    for pdict in pattern_dicts:
        if adddicts:
            for addct in adddicts:
                pdict.update(addct)
        write_tstr, cnt = card_template_parser(template_str, pdict)
        if strict and (cnt != len(pdict)):
            print "Template %s was not fully parsed with dictionary %s and was discarded!" % (tmpl_basename, str(pdict))
            continue
        fname = template_fname + "_printandum_#" +str(i) +"__" + str(time.time()) + ext_str
        f = open(fname, "wb")
        f.write(write_tstr)
        f.close()
        fnames.append(fname)
        i += 1
    return (fnames, i)
    
    
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
            #print "save header", name
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
            y=escape(y)
            #print y
        return "%s='%s'" % (x,y)
    else:
        return "%s=%s" % (x,'Null')

def format_insert(y):
    if y=='None' or y == 'Null':
        return y
    elif type(y)==StringType or type(y)==UnicodeType:
        return escape(y)
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
                    if os.path.exists(''.join((os.environ['USERPROFILE'], '\\', dbname))):
                        self.dbfile = ''.join((os.environ['USERPROFILE'], '\\', dbname))
                        self.dbfile = self.dbfile.decode('mbcs')
                        self.filestat = 1
                    elif os.path.exists(dbname):
                        self.dbfile = dbname
                        self.filestat = 3
                    else:
                        self.dbfile = ''.join((os.environ['USERPROFILE'], '\\', dbname))
                        self.dbfile = self.dbfile.decode('mbcs')
                        self.filestat = 2
                elif os.path.exists(dbname):
                    self.dbfile = dbname
                    self.filestat = 3
                else:
                    self.dbfile = dbname
                    self.filestat = 4
            else:
                if os.environ.has_key('HOME'):
                    if os.path.exists(''.join((os.environ['HOME'], '/', dbname))):
                        self.dbfile = ''.join((os.environ['HOME'], '/', dbname))
                        self.filestat = 1
                    elif os.path.exists(dbname):
                        self.dbfile = dbname
                        self.filestat = 3
                    else:
                        self.dbfile = ''.join((os.environ['HOME'], '/', dbname))
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
        #import sys 
        #print >>sys.stderr, "dbpath=", self.dbfile
        #print unicode(self.dbfile).encode('raw-unicode-escape')
        self.db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        #try:
        #print self.dbfile
        #self.dbfile = QtCore.QString(self.dbfile)
        self.db.setDatabaseName(self.dbfile)
        #except:
            #self.db.setDatabaseName(u"c:\%s" % connectDBName)
            
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
    
    #sql = "UPDATE billservice_account SET ballance = ballance - %d WHERE id = %d;" % (summ, account_id)
    sql = o.save("billservice_transaction")
    
     
    return sql 

    
def humanable_bytes(a):
    """
    Функция для удобного человеку предоставления объёма трафика
    """
    if a is not None:
        try:
            a=float(a)
            #res = a/1024
            if a>1024 and a<(1048576):
                return u"%.5s KB" % unicode(a/(1024))
            elif a>=(1048576) and a<=(1024*1024*1024):
                return u"%.5s МB" % unicode(a/(1048576))
            elif a>(1024*1024*1024):
                return u"%.5s GB" % unicode(a/(1024*1024*1024))
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

    def stop(self):
    
        self.exiting = True
        self.wait()


    def go(self, interval=60):
        self.interval=interval
        self.start()

    def run(self):
        
        while not self.exiting:
            
            
            
            print "emit"
            self.emit(QtCore.SIGNAL("refresh()"))
            time.sleep(self.interval)
                    

def prntime(s):
    """
    Функция возвращает длительность времени в удобном для человека виде 
    """
    if s==None:
        return ""
    m,s=divmod(s,60)
    h,m=divmod(m,60)
    if h==0 and m==0:
        return u"%sс" % s
    elif h==0 and m!=0:
        return u"%sм %sс" % (m,s,)
    else:
        return u"%sч %sм %sс" % (h,m,s)
    
def convert_values(value):
    if str(value).endswith('k'):
        return str(int(str(value)[0:-1])*1000)
    elif str(value).endswith('M'):
        return str(int(str(value)[0:-1])*1000*1000)
    else:
        return str(value)
                
def get_decimals_speeds(params):
    #print "before", params
    i = 0
    for param in params:
        #values = map(convert_values, str(params[param]).split('/'))
        values = map(convert_values, str(param).split('/'))
        #print values
        params[i] ='/'.join(values)
        i += 1
    #print 'after', params
    return params

def split_speed(speed):
    if speed=='':
        return "",""
    return speed.split("/")

def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).
    """

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            #print el
            if el=='':
                result.append(el)
            else:
                result.append(int(el))
    return result

def check_speed(speed):
    #print speed
    speed = flatten(map(split_speed,get_decimals_speeds(speed)))
    #print speed
    if speed[2]==speed[3]==speed[4]==speed[5]==speed[6]==speed[7] in ('', 0) and ((speed[0]>=speed[9] and speed[1]>=speed[10]) or speed[9] in ('', 0) or speed[10] in ('', 0)):
        return True
    else:
        return speed[0]>=speed[9] and speed[1]>=speed[10] and \
        speed[2]>=speed[0] and speed[3]>=speed[1] and \
        ((speed[4]>=speed[9] and speed[5]>=speed[10]) and speed[2] not in ('', 0) and speed[3] not in ('', 0) and speed[6] not in ('', 0) and speed[7] not in ('', 0)) and speed[4]<=speed[2] and speed[5]<=speed[3] and speed[4]<=speed[0] and speed[5]<=speed[1]
    return False

def transip (ipstr):
    hv = hex (string.atol (ipstr))[2:-1]
    p1 = string.atoi (hv[-2:]  , 16)
    p2 = string.atoi (hv[-4:-2], 16)
    p3 = string.atoi (hv[-6:-4], 16)
    p4 = string.atoi (hv[:-6]  , 16)
    return `p4`+'.'+`p3`+'.'+`p2`+'.'+`p1`


def get_type(nas_id, tarif_id):
    if tarif_id and not nas_id:
        return u"HotSpot"
    if tarif_id and nas_id:
        return u"Карта доступа"
    if not tarif_id and not nas_id:
        return u"Карта предоплаты"
            
            
def get_free_addreses_from_pool(connection, pool_id, count=-1, only_from_pool=True, default_ip=''):
    d = connection.get_ips_from_ippool(pool_id)
    if not d.status: return []
    return d.records
        

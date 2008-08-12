#-*-encoding:utf-8-*-

from PyQt4 import QtGui, QtCore
from types import InstanceType, StringType, UnicodeType
import datetime

dateDelim = "."

def tableFormat(table):        
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
            
def format_update (x,y):
    if y!='Null':
        if type(y)==StringType or type(y)==UnicodeType:
            y=y.replace("\\", r"\\").replace(r"'", r"\'").replace(r'"', r'\"')
            print y
        return "%s='%s'" % (x,y)
    else:
        return "%s=%s" % (x,y)

def format_insert(y):
    if y=='Null':
        return y
    elif type(y)==StringType or type(y)==UnicodeType:
        return y.replace("\\", r"\\").replace(r"'", r"\'").replace(r'"', r'\"')
    else:
        return y
        

class Object(object):
    def __init__(self, result=[], *args, **kwargs):
        for key in result:
            if result[key]!=None:
                setattr(self, key, result[key])
            else:
                setattr(self, key, 'Null')      
            
         
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
            sql=u"INSERT INTO %s (%s) VALUES('%s') RETURNING id;" % (table, ",".join([x for x in fields]), ("%s" % "','".join([format_insert(unicode(self.__dict__[x])) for x in fields ]).replace("'Null'", 'Null')))
        
        return sql
    
    def get(self, table):
        return "SELECT * FROM %s WHERE id=%d" % (table, int(self.id))
    
    def __call__(self):
        return self.id
    

def transaction(account_id, type_id, approved, description, summ, bill):
    
    o = Object()
    o.account_id = account_id
    o.type_id = type_id
    o.approved = approved
    o.description = description
    o.summ = summ
    o.bill = bill
    o.created = datetime.datetime.now()
    
    sql = o.save("billservice_transaction")
    sql += "UPDATE billservice_account SET ballance = ballance - %d WHERE id = %d;" % (summ, account_id)
     
    return sql 

    
    
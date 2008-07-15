#-*-encoding:utf-8-*-

from PyQt4 import QtGui     
from types import InstanceType
   


def tableFormat(table):        
    table.setFrameShape(QtGui.QFrame.Panel)
    table.setFrameShadow(QtGui.QFrame.Sunken)
    table.setAlternatingRowColors(True)
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
    #hh.setVerticalSize(10)
    hh.setStretchLastSection(True)
    hh.setHighlightSections(False)
    hh.setClickable(False)
    hh.setMovable(False)
    hh.ResizeMode(QtGui.QHeaderView.Stretch)
    return table

  

def format_update (x,y):
    if y!='Null':
        return "%s='%s'" % (x,y)
    else:
        return "%s=%s" % (x,y)

def format_insert(y):
    if y=='Null':
        return 

class Object(object):
    def __init__(self, result=[], *args, **kwargs):
        for key in result:
            if result[key]!=None:
                setattr(self, key, result[key])


        for key in kwargs:
            setattr(self, key, kwargs[key])  
        
        print dir(self)          
            
         
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
            sql=u"INSERT INTO %s (%s) VALUES('%s') RETURNING id;" % (table, ",".join([x for x in fields]), ("%s" % "','".join([unicode(self.__dict__[x]) for x in fields ]).replace("'Null'", 'Null')))
        
        return sql
    
    def get(self, table):
        return "SELECT * FROM %s WHERE id=%d" % (table, int(self.id))
    
    def __call__(self):
        return self.id
    

    
    
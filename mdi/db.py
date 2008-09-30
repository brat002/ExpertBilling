#-*-coding=utf-8-*-
"""
Database wrapper for mikrobill
"""
#Post
import psycopg2, datetime
from types import InstanceType, StringType, UnicodeType
import os

def format_update (x,y):
    #print 'y', y, type(y)
    #print x,y, type(y), y=='None'
    if y!=u'Null' and y!=u'None':
        if type(y)==StringType or type(y)==UnicodeType:
            print True
            y=y.replace('\'', '\\\'').replace('"', '\"').replace("\\","\\\\")
            #print 'y', y
        return "%s='%s'" % (x,y)
    else:
        return "%s=%s" % (x,'Null')

def format_insert(y):
    if y==u'Null' or y ==u'None':
        return 'Null'
    elif type(y)==StringType or type(y)==UnicodeType:
        #print True
        return y.replace('\'', '\\\'').replace('"', '\"').replace("\\","\\\\")
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
    
#-*-coding=utf-8-*-
"""
Database wrapper for mikrobill
"""
#Post
import  datetime
import os
from re import escape
from types import InstanceType, StringType, UnicodeType
def format_update (x,y):
    #print 'y', y, type(y)
    if y!=u'Null' and y!=u'None':
        if type(y)==StringType or type(y)==UnicodeType:
            #print True
            y=escape(y)
            #print 'y', y
        return "%s='%s'" % (x,y)
    else:
        return "%s=%s" % (x,'Null')

def format_insert(y):
    if y==u'Null' or y ==u'None':
        return 'Null'
    elif type(y)==StringType or type(y)==UnicodeType:
        #print True
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
                if self.__dict__[field]=='now()':
                    self.__dict__[field] = datetime.datetime.now()
                fields.append(field)
        try:
            self.__dict__['id']
            sql=u"UPDATE %s SET %s WHERE id=%d RETURNING id;" % (table, " , ".join([format_update(x, unicode(self.__dict__[x])) for x in fields ]), self.__dict__['id'])
        except:
            sql=u"INSERT INTO %s (%s) VALUES('%s') RETURNING id;" % (table, ",".join([x for x in fields]), ("%s" % "','".join([format_insert(unicode(self.__dict__[x])) for x in fields ])))
            sql = sql.replace("'None'", 'Null')
            sql = sql.replace("'Null'", 'Null')
        return sql

    def get(self, table):
        return "SELECT * FROM %s WHERE id=%d" % (table, int(self.id))

    def delete(self, table):
        fields=[]
        for field in self.__dict__:
            if type(field)!=InstanceType:
                # and self.__dict__[field]!=None
                fields.append(field)
        
        sql = u"DELETE FROM %s WHERE %s" % (table, " AND ".join([format_update(x, unicode(self.__dict__[x])) for x in fields ]))
        
        return sql
    
    def __call__(self):
        return self.id

    def hasattr(self, attr):
        if attr in self.__dict__:
            return True
        return False

    def isnull(self, attr):
        if self.hasattr(attr):
            if self.__dict__[attr]!=None and self.__dict__[attr]!='Null':
                return False

        return True
        return self.id
    
    def __repr__(self):
        return repr(self.__dict__)
    
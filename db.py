#-*-coding=utf-8-*-
"""
Database wrapper for mikrobill
"""
#Post
import psycopg2

#Primitives

class Nas:
    def __init__(self, name='', ipaddress='', secret=''):
        self.name=name
        self.ipaddress=ipaddress
        self.secret=secret
        
class postgreinterface:

    def __init__(self, host, db, user, password):
        self.host=host
        self.db=db
        self.user=user
        self.password=password
        try:
            self.conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % self.db, self.user, self.host, self.password);
        except:
            print "I am unable to connect to the database"

        self.cur = self.conn.cursor()

    def do_sql(self, sql):
        return self.cur.execute(sql)
    
    def get_nas(self,nasip):
    
        result=self.do_sql("SELECT name, ipaddress, secret FROM %s WHERE ipaddress='%s'" % self.db, nasip)
        nas=Nas(name=result[0], ipaddress=result[1], secret=result[2])
        return nas

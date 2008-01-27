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

def get_nas_by_ip(cursor, ip):
    cursor.execute("""SELECT id, secret from nas_nas WHERE ipaddress='%s'""" % ip)
    return cursor

def get_account_data_by_username(cursor, username):
    cursor.execute("""SELECT bsa.username, bsa.password, bsa.ipaddress, (SELECT bat.tarif_id FROM billservice_accounttarif as bat WHERE bat.datetime<now() and bat.account_id=bsa.id ORDER BY datetime DESC LIMIT 1) as tarif_id, status, banned, ballance FROM billservice_account as bsa WHERE username='%s'""" % username)
    return cursor

def get_nas_id_by_tarif_id(cursor, tarif_id):
    cursor.execute("""SELECT id from nas_nas WHERE id=(SELECT nas_id FROM billservice_accessparameters_nas WHERE accessparameters_id=(SELECT access_type_id FROM billservice_tariff WHERE id=%s))""" % tarif_id)
    return cursor

def time_periods_by_tarif_id(cursor, tarif_id):
    cursor.execute("""SELECT id, name, time_start::timestamp without time zone, length, repeat_after FROM billservice_timeperiodnode WHERE id=(SELECT  timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id=(SELECT access_time_id FROM billservice_tariff WHERE id='%s'))""" % tarif_id)
    return cursor

#-*-coding=utf-8-*-
"""
Database wrapper for mikrobill
"""
#Post
import psycopg2, datetime

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
    cursor.execute("""SELECT bsa.username, bsa.password, bsa.ipaddress, (SELECT bat.tarif_id FROM billservice_accounttarif as bat WHERE bat.datetime<now() and bat.account_id=bsa.id ORDER BY datetime DESC LIMIT 1) as tarif_id, status, banned, (ballance+credit) as ballance FROM billservice_account as bsa WHERE username='%s'""" % username)
    return cursor

def get_nas_id_by_tarif_id(cursor, tarif_id):
    cursor.execute("""SELECT id from nas_nas WHERE id=(SELECT nas_id FROM billservice_accessparameters_nas WHERE accessparameters_id=(SELECT access_type_id FROM billservice_tariff WHERE id=%s))""" % tarif_id)
    return cursor

def time_periods_by_tarif_id(cursor, tarif_id):
    cursor.execute("""SELECT id, name, time_start::timestamp without time zone, length, repeat_after FROM billservice_timeperiodnode WHERE id=(SELECT  timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id=(SELECT access_time_id FROM billservice_tariff WHERE id='%s'))""" % tarif_id)
    return cursor

def transaction(cursor, account, approved, tarif, summ, description, created=None):
    if not created:
        created=datetime.datetime.now()
        
    cursor.execute("""
    INSERT INTO billservice_transaction(
    account_id, approved, tarif_id, summ, description, created)
    VALUES (%s, %s, %s, %s, %s, %s);
    """,(account, approved, tarif , summ, description, created))
    cursor.execute("""
    UPDATE billservice_account
    SET ballance=ballance-%s WHERE id=%s""" % (summ, account))
    
    cursor.execute("""
    SELECT id
    FROM billservice_transaction
    WHERE
    account_id=%s
    AND tarif_id=%s
    AND created='%s'""" % (account,tarif, created))
    
    return cursor.fetchone()[0]

def ps_history(cursor, ps_id, transaction, created=None):
    if not created:
        created=datetime.datetime.now()
    cursor.execute("""
       INSERT INTO billservice_periodicalservicehistory(service_id, transaction_id, datetime) VALUES (%s, %s, %s);
       """, (ps_id, transaction, created))

def get_last_checkout(cursor, ps_id, tarif, account):
    cursor.execute("""
    SELECT psh.datetime::timestamp without time zone FROM billservice_periodicalservicehistory as psh
    JOIN billservice_transaction as t ON t.id=psh.transaction_id
    WHERE psh.service_id='%s' AND t.tarif_id='%s' AND t.account_id='%s' ORDER BY datetime DESC LIMIT 1
    """ % (ps_id, tarif, account))
    try:
        return cursor.fetchone()[0]
    except:
        return None
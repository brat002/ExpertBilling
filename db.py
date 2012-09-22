#-*-coding=utf-8-*-
"""
Database wrapper for mikrobill
"""
#Post
import psycopg2, datetime
from re import  escape
import os
from types import InstanceType, StringType, UnicodeType

class GpstTableException(Exception):
    pass

class TraftransTableException(Exception):
    pass

    
class dbRoutine(object):

    @staticmethod
    def execRoutine(*args, **kwargs):
        '''@args[0] - method identifier'''
        #add an opportunity to pass method name as a kwargs value
        methodName = args[0]
        #print methodName
        method = getattr(self, "db_" + methodName, None)
        if callable(method):
            try:
                args = args[1:]
                res =  method(*args, **kwargs)
                return res
            except Exception, ex:
                print "Exception upon executing dbRoutine #" + methodName + "# method: ", ex
                raise ex
        else:
            raise Exception("dbRoutine method #" + args[0] + "# does not exist!" )

    @staticmethod
    def db_delete_netflowstream_stat(*args, **kwargs):
        return cur.execute("DELETE FROM billservice_netflowstream WHERE date_start BETWEEN %s AND %s; " , ((((kwargs.has_key('start_date')) and kwargs['start_date'].isoformat(' ')) or ((not kwargs.has_key('start_date'))and '-infinity')), (((kwargs.has_key('end_date')) and kwargs['end_date'].isoformat(' ')) or ((not kwargs.has_key('end_date'))and 'infinity'))))

    @staticmethod
    def db_delete_rawnetflowstream_stat(*args, **kwargs):
        return cur.execute("DELETE FROM billservice_rawnetflowstream WHERE date_start BETWEEN %s AND %s; " , ((((kwargs.has_key('start_date')) and kwargs['start_date'].isoformat(' ')) or ((not kwargs.has_key('start_date'))and '-infinity')), (((kwargs.has_key('end_date')) and kwargs['end_date'].isoformat(' ')) or ((not kwargs.has_key('end_date'))and 'infinity'))))

#Primitives
    


def transaction(cursor, account, approved, type, summ, description, created=None, bill='', tarif='Null', accounttarif='Null'):
    #print 'new transaction'
    if not created:
        created=datetime.datetime.now()
    #UPDATE billservice_account SET ballance=ballance-%s WHERE id=%s;
    cursor.execute("""                   
                    INSERT INTO billservice_transaction(bill,
                    account_id, approved, type_id, tarif_id, accounttarif_id, summ, description, created)
                    VALUES (%s, %s, %s, %s, %s, %s, (-1)*%s, %s, %s) RETURNING id;
                    """ , (bill, account, approved, type, tarif, accounttarif, summ, description, created))

    tr_id=cursor.fetchone()
    if tr_id:
        tr_id=tr_id[0]
    return tr_id


def traffictransaction(cursor, traffictransmitservice_id, accounttarif_id, account_id, summ=0, created=None):
    if not created:
        created=datetime.datetime.now()
    try:
        cursor.execute("""INSERT INTO traftrans%s""" % created.strftime("%Y%m01")+"""(traffictransmitservice_id, accounttarif_id, account_id, summ, created) VALUES (%s, %s, %s, (-1)*%s, %s) RETURNING id;
                       """, (traffictransmitservice_id, accounttarif_id, account_id, summ, created,))
    except psycopg2.ProgrammingError, e:
        if e.pgcode=='42P01':
            raise TraftransTableException()
        else:
            raise e
        
    return cursor.fetchone()[0]
    
def timetransaction(cursor, timeaccessservice_id, accounttarif_id, account_id, session_id, summ=0, created=None):
    if not created:
        created=datetime.datetime.now()
    cursor.execute("""INSERT INTO billservice_timetransaction(timeaccessservice_id, accounttarif_id, account_id, session_id, summ, created) VALUES (%s, %s, %s, %s, (-1)*%s, %s);
                   """, (timeaccessservice_id, accounttarif_id, account_id, session_id, summ, created,))
    
def timetransaction_fn(cursor, timeaccessservice_id, accounttarif_id, account_id, summ=0, created=None, sessionid='', interrim_update=None):
    if not created:
        created=datetime.datetime.now()
    if not interrim_update: interrim_update = created
    cursor.execute("""SELECT timetransaction_insert(%s, %s, %s, (-1)*%s::decimal, %s::timestamp without time zone, %s::character varying(32), %s::timestamp without time zone);
                   """, (timeaccessservice_id, accounttarif_id, account_id, summ, created, sessionid, interrim_update))
    
def ps_history(cursor, ps_id, accounttarif, account_id, type_id, summ=0, created=None):
    if not created:
        created=datetime.datetime.now()
    cursor.execute("""
                   INSERT INTO billservice_periodicalservicehistory(service_id, accounttarif_id, account_id, type_id, summ, created) VALUES (%s, %s, %s, %s, (-1)*%s, %s);
                   """, (ps_id, accounttarif, account_id, type_id, summ, created,))
    
def addon_history(cursor, addon_id, service_type, ps_id, accounttarif, account_id, type_id, summ=0, created=None):
    if not created:
        created=datetime.datetime.now()
    cursor.execute("""
                   INSERT INTO billservice_addonservicetransaction(service_id, service_type, account_id, accountaddonservice_id, 
            accounttarif_id, summ, created, type_id) VALUES (%s, %s, %s, %s, %s, (-1)*%s, %s, %s);
                   """, (addon_id, service_type, account_id, ps_id, accounttarif, summ, created, type_id))
    
def get_last_checkout(cursor, ps_id, accounttarif, co_datetime=None):
    if co_datetime:
        cursor.execute("""
                   SELECT date_trunc('second', created) FROM billservice_periodicalservicehistory
                    WHERE service_id=%s AND accounttarif_id=%s AND created <= %s ORDER BY created DESC LIMIT 1
                    """ , (ps_id, accounttarif, co_datetime))
    else:
        cursor.execute("""
                   SELECT date_trunc('second', datetime) FROM billservice_periodicalservicelog
                    WHERE service_id=%s AND accounttarif_id=%s
                    """ , (ps_id, accounttarif,))
    try:
        return cursor.fetchone()[0]
    except:
        return None
    
def get_last_addon_checkout(cursor, ps_id, accounttarif, co_datetime=None):

    cursor.execute("""
                    SELECT date_trunc('second', created) FROM billservice_addonservicetransaction
                    WHERE accountaddonservice_id=%s ORDER BY created DESC LIMIT 1
                    """ , (ps_id,))

    try:
        return cursor.fetchone()[0]
    except:
        return None

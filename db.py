#-*-coding=utf-8-*-
"""
Database wrapper for mikrobill
"""
#Post
import psycopg2, datetime

import os
from types import InstanceType, StringType, UnicodeType

def format_update (x,y):
    #print 'y', y, type(y)
    if y!=u'Null' and y!=u'None':
        if type(y)==StringType or type(y)==UnicodeType:
            #print True
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
            sql=u"UPDATE %s SET %s WHERE id=%d RETURNING id;" % (table, " , ".join([format_update(x, unicode(self.__dict__[x])) for x in fields ]), self.__dict__['id'])
        except:
            sql=u"INSERT INTO %s (%s) VALUES('%s') RETURNING id;" % (table, ",".join([x for x in fields]), ("%s" % "','".join([format_insert(unicode(self.__dict__[x])) for x in fields ])))
            sql = sql.replace("'None'", 'Null')
            sql = sql.replace("'Null'", 'Null')
        return sql
    
    def delete(self, table):
        fields=[]
        for field in self.__dict__:
            if type(field)!=InstanceType:
                # and self.__dict__[field]!=None
                fields.append(field)
        
        sql = u"DELETE FROM %s WHERE %s" % (table, " AND ".join([format_update(x, unicode(self.__dict__[x])) for x in fields ]))
        
        return sql
        
    def get(self, fields, table):
        return "SELECT %s FROM %s WHERE id=%d" % (",".join([fields]), table, int(self.id))

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

def get_nas_by_ip(cursor, ip):

    cursor.execute("""SELECT id, secret, type, multilink from nas_nas WHERE ipaddress=%s;""" , (ip,))
    return cursor.fetchone()

def set_account_deleted(cursor, account_id):
    cursor.execute('''UPDATE billservice_account SET deleted=TRUE WHERE id=%s''' , (account_id,))
    try:
        return cursor.fetchone()[0]
    except:
        return None

def get_default_speed_parameters(cursor, tarif):
    """
    rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] [rx-rate-min[/tx-rate-min]]]]
    """
    cursor.execute("""
                   SELECT accessparameters.max_limit,
                    accessparameters.burst_limit,
                    accessparameters.burst_treshold,
                    accessparameters.burst_time,
                    accessparameters.priority,
                    accessparameters.min_limit
                    FROM billservice_accessparameters as accessparameters
                    JOIN billservice_tariff as tariff ON tariff.access_parameters_id=accessparameters.id
                    WHERE tariff.id=%s;
                    """ , (tarif,))
    return cursor.fetchone()

def get_speed_parameters(cursor, tarif):
    """
    rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] [rx-rate-min[/tx-rate-min]]]]
    """
    cursor.execute("""
                   SELECT timenode.time_start::timestamp without time zone, timenode.length, timenode.repeat_after, 
                    timespeed.max_limit,
                    timespeed.burst_limit,
                    timespeed.burst_treshold,
                    timespeed.burst_time,
                    timespeed.priority, 
                    timespeed.min_limit
                    FROM billservice_timespeed as timespeed
                    JOIN billservice_tariff as tariff ON tariff.access_parameters_id=timespeed.access_parameters_id
                    JOIN billservice_timeperiod_time_period_nodes as tp ON tp.timeperiod_id=timespeed.time_id
                    JOIN billservice_timeperiodnode as timenode ON tp.timeperiodnode_id=timenode.id
                    WHERE tariff.id=%s
                    """ , (tarif,))

    return cursor.fetchall()

def get_account_data_by_username(cursor, username, access_type, station_id, multilink, common_vpn=False):
    
    at = ''
    #print "common_vpn == False", common_vpn == False, type(common_vpn)
    if common_vpn == "False":
        at = "accessparameters.access_type='%s' AND " % access_type
    #print "at", at, common_vpn, common_vpn == False, type(common_vpn)
    ins=''

    if multilink==False:
        if len(station_id)==17:
            """
            MAC - PPPOE
            """
            ins = "and (ipn_mac_address='%s' or ipn_mac_address='')" % station_id
        else:
            """
            IP - PPTP
            """
            ins=" and (ipn_ip_address='%s' or ipn_ip_address='0.0.0.0') " % station_id

    
    #print "!!!", common_vpn, at
    
    sql=u"""
    SELECT account.username, account.password, account.nas_id, account.vpn_ip_address,
    bsat.tarif_id, accessparameters.access_type, account.status, 
    account.balance_blocked, (account.ballance+account.credit) as ballance, 
    account.disabled_by_limit, account.vpn_speed,
    tariff.active
    FROM billservice_account as account
    JOIN billservice_accounttarif as bsat ON bsat.account_id=account.id
    JOIN billservice_tariff as tariff on tariff.id=bsat.tarif_id
    JOIN billservice_accessparameters as accessparameters on accessparameters.id = tariff.access_parameters_id 
    WHERE %s bsat.datetime<now() and account.username='%s' %s AND 
    (((account.allow_vpn_null=False and account.ballance+account.credit>0) or (account.allow_vpn_null=True)) 
    AND
    ((account.allow_vpn_block=False and account.balance_blocked=False and account.disabled_by_limit=False and account.status=True) or (account.allow_vpn_null=True)))=True 
    ORDER BY bsat.datetime DESC LIMIT 1""" % (at, username, ins)
    #print sql
    cursor.execute(sql)

    return cursor.fetchone()

def get_account_data_by_username_dhcp(cursor, username):
    """
    username = mac address
    """
    
    cursor.execute("""SELECT account.nas_id, account.ipn_ip_address,account.netmask, account.ipn_mac_address,
        account.ipn_speed
        FROM billservice_account as account
        WHERE 
        (((account.allow_dhcp_null=False and account.ballance+account.credit>=0) or (account.allow_dhcp_null=True)) 
        OR 
        ((account.allow_dhcp_block=False and account.balance_blocked=False and account.disabled_by_limit=False and account.status=True) or (account.allow_dhcp_null=True)))=True 
        AND account.ipn_mac_address=%s LIMIT 1""" , (str(username),))


    return cursor.fetchone()

def time_periods_by_tarif_id(cursor, tarif_id):
    #print 'tarif_id', tarif_id
    cursor.execute("""
                   SELECT tpn.time_start::timestamp without time zone as time_start, tpn.length as length, tpn.repeat_after as repeat_after
                    FROM billservice_timeperiodnode as tpn
                    JOIN billservice_timeperiod_time_period_nodes as tpnds ON tpnds.timeperiodnode_id=tpn.id
                    JOIN billservice_accessparameters AS ap ON ap.access_time_id=tpnds.timeperiod_id
                    JOIN billservice_tariff AS bst ON bst.access_parameters_id=ap.id
                    WHERE bst.id=%s""", (int(tarif_id),))
    return cursor.fetchall()

def transaction(cursor, account, approved, type, summ, description, created=None, bill='', tarif='Null'):
    #print 'new transaction'
    if not created:
        created=datetime.datetime.now()

    cursor.execute("""
                   UPDATE billservice_account SET ballance=ballance-%s WHERE id=%s;
                    INSERT INTO billservice_transaction(bill,
                    account_id, approved, type_id, tarif_id, summ, description, created)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
                    """ , (summ, account, bill, account, approved, type, tarif , summ, description, created,))

    tr_id=cursor.fetchone()[0]
    #print tr_id

    #cursor.execute("""""" % ())

    #print "transaction_id=", cursor.fetchall()
    return tr_id

def delete_transaction(cursor, id):

    cursor.execute("""
                   DELETE FROM billservice_transaction WHERE id=%s RETURNING account_id, summ;
                   """ , (id,))

    row=cursor.fetchone()

    cursor.execute("""
                   UPDATE billservice_account
                   SET ballance=ballance+%s WHERE id=%s""" , (row['summ'], row['account_id'],))


def ps_history(cursor, ps_id, transaction, accounttarif, created=None):
    if not created:
        created=datetime.datetime.now()
    cursor.execute("""
                   INSERT INTO billservice_periodicalservicehistory(service_id, transaction_id, accounttarif_id,  datetime) VALUES (%s, %s, %s, %s);
                   """, (ps_id, transaction, accounttarif, created,))

def get_last_checkout(cursor, ps_id, accounttarif):
    cursor.execute("""
                   SELECT datetime::timestamp without time zone FROM billservice_periodicalservicehistory
                    WHERE service_id=%s AND accounttarif_id=%s ORDER BY datetime DESC LIMIT 1
                    """ , (ps_id, accounttarif,))
    try:
        return cursor.fetchone()[0]
    except:
        return None

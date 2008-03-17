#-*-coding=utf-8-*-
"""
Database wrapper for mikrobill
"""
#Post
import psycopg2, datetime

#Primitives

def get_nas_by_ip(cursor, ip):
    cursor.execute("""SELECT id, secret from nas_nas WHERE ipaddress='%s'""" % ip)
    return cursor

def get_account_data_by_username(cursor, username):
    cursor.execute(
    """SELECT bsa.username, bsa.password, bsa.ipaddress,
    bsat.tarif_id, status, (ballance+credit) as ballance, disabled_by_limit
    FROM billservice_account as bsa
    JOIN billservice_accounttarif as bsat ON bsat.account_id=bsa.id
    WHERE bsat.datetime<now() and bsa.username='%s' ORDER BY bsat.datetime DESC LIMIT 1""" % username)
    return cursor

def get_nas_id_by_tarif_id(cursor, tarif_id):
    cursor.execute("""SELECT nas_nas.id, ap.access_type from nas_nas
    JOIN billservice_accessparameters AS ap ON ap.nas_id=nas_nas.id
    JOIN billservice_tariff AS bst ON bst.access_type_id=ap.id
    WHERE bst.id='%s'""" % tarif_id)
    return cursor

def time_periods_by_tarif_id(cursor, tarif_id):
    cursor.execute("""
    SELECT tpn.id, tpn.name, tpn.time_start::timestamp without time zone, tpn.length, tpn.repeat_after
    FROM billservice_timeperiodnode as tpn
    JOIN billservice_timeperiod_time_period_nodes as tpnds ON tpnds.timeperiodnode_id=tpn.id
    JOIN billservice_accessparameters AS ap ON ap.access_time_id=tpnds.timeperiod_id
     JOIN billservice_tariff AS bst ON bst.access_type_id=ap.id
    WHERE bst.id=%s""" % tarif_id)
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
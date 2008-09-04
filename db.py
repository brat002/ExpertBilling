#-*-coding=utf-8-*-
"""
Database wrapper for mikrobill
"""
#Post
import psycopg2, datetime

#Primitives

def get_nas_by_ip(cursor, ip):
    
    cursor.execute("""SELECT id, secret, type from nas_nas WHERE ipaddress='%s';""" % ip)
    return cursor.fetchone()

def set_account_deleted(cursor, account_id):
    cursor.execute('''UPDATE billservice_account SET deleted=TRUE WHERE id=%d''' % account_id)
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
    """ % tarif)
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
    """ % tarif)

    return cursor.fetchall()

def get_account_data_by_username(cursor, username, access_type, station_id):
    
    if access_type=='PPTP':
        cursor.execute(
        """SELECT account.username, account.password, account.nas_id, account.vpn_ip_address,
        bsat.tarif_id, accessparameters.access_type, account.status, 
        account.balance_blocked, (account.ballance+account.credit) as ballance, 
        account.disabled_by_limit, account.vpn_speed,
        tariff.active
        FROM billservice_account as account
        JOIN billservice_accounttarif as bsat ON bsat.account_id=account.id
        JOIN billservice_tariff as tariff on tariff.id=bsat.tarif_id
        JOIN billservice_accessparameters as accessparameters on accessparameters.id = tariff.access_parameters_id 
        WHERE accessparameters.access_type='PPTP' and bsat.datetime<now() and account.username='%s' and (ipn_ip_address='%s' or ipn_ip_address='0.0.0.0')  ORDER BY bsat.datetime DESC LIMIT 1""" % (username, station_id))
    elif access_type=='PPPOE':
        cursor.execute(
        """SELECT account.username, account.password, account.nas_id, account.vpn_ip_address,
        bsat.tarif_id, accessparameters.access_type, account.status, 
        account.balance_blocked, (account.ballance+account.credit) as ballance, 
        account.disabled_by_limit, account.vpn_speed,
        tariff.active
        FROM billservice_account as account
        JOIN billservice_accounttarif as bsat ON bsat.account_id=account.id
        JOIN billservice_tariff as tariff on tariff.id=bsat.tarif_id
        JOIN billservice_accessparameters as accessparameters on accessparameters.id = tariff.access_parameters_id 
        WHERE accessparameters.access_type='PPPOE' and bsat.datetime<now() and account.username='%s' and (ipn_mac_address='%s' or ipn_mac_address='')  ORDER BY bsat.datetime DESC LIMIT 1""" % (username, station_id))        
    return cursor.fetchone()

def get_account_data_by_username_dhcp(cursor, username):
    cursor.execute(
    """SELECT account.nas_id, account.ipn_ip_address,account.netmask, account.ipn_mac_address,
    bsat.tarif_id,   account.ipn_speed
    FROM billservice_account as account
    JOIN billservice_accounttarif as bsat ON bsat.account_id=account.id
    JOIN billservice_tariff as tariff on tariff.id=bsat.tarif_id
    JOIN billservice_accessparameters as accessparameters on accessparameters.id = tariff.access_parameters_id 
    WHERE bsat.datetime<now() and account.ipn_mac_address='%s' ORDER BY bsat.datetime DESC LIMIT 1""" % username)
    return cursor.fetchone()

def time_periods_by_tarif_id(cursor, tarif_id):
    #print 'tarif_id', tarif_id
    cursor.execute("""
    SELECT tpn.time_start::timestamp without time zone as time_start, tpn.length as length, tpn.repeat_after as repeat_after
    FROM billservice_timeperiodnode as tpn
    JOIN billservice_timeperiod_time_period_nodes as tpnds ON tpnds.timeperiodnode_id=tpn.id
    JOIN billservice_accessparameters AS ap ON ap.access_time_id=tpnds.timeperiod_id
    JOIN billservice_tariff AS bst ON bst.access_parameters_id=ap.id
    WHERE bst.id=%s""" % tarif_id)
    return cursor.fetchall()

def transaction(cursor, account, approved, type, summ, description, created=None, bill='', tarif='Null'):
    print 'new transaction'
    if not created:
        created=datetime.datetime.now()

    cursor.execute("""
    UPDATE billservice_account SET ballance=ballance-%s WHERE id=%s;
    INSERT INTO billservice_transaction(bill,
    account_id, approved, type_id, tarif_id, summ, description, created)
    VALUES ('%s', %s, %s, '%s', %s, %s, '%s', '%s') RETURNING id;
    """ % (summ, account, bill, account, approved, type, tarif , summ, description, created))

    tr_id=cursor.fetchone()[0]
    print tr_id

    #cursor.execute("""""" % ())
    
    #print "transaction_id=", cursor.fetchall()
    return tr_id

def delete_transaction(cursor, id):

    cursor.execute("""
    DELETE FROM billservice_transaction WHERE id=%d RETURNING account_id, summ;
    """ % id)

    row=cursor.fetchone()
    
    cursor.execute("""
    UPDATE billservice_account
    SET ballance=ballance+%s WHERE id=%s""" % (row['summ'], row['account_id']))


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

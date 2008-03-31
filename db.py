#-*-coding=utf-8-*-
"""
Database wrapper for mikrobill
"""
#Post
import psycopg2, datetime

#Primitives

def get_nas_by_ip(cursor, ip):
    cursor.execute("""SELECT id, secret, type from nas_nas WHERE ipaddress='%s'""" % ip)
    return cursor.fetchone()

def get_default_speed_parameters(cursor, tarif):
    """
    rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] [rx-rate-min[/tx-rate-min]]]]
    """
    cursor.execute("""
    SELECT accessparameters.max_limit_in, accessparameters.max_limit_out,
           accessparameters.burst_limit_in, accessparameters.burst_limit_out, accessparameters.burst_treshold_in, accessparameters.burst_treshold_out,
           accessparameters.burst_time_in, accessparameters.burst_time_out,accessparameters.priority, accessparameters.min_limit_in, accessparameters.min_limit_out
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
    SELECT timenode.time_start::timestamp without time zone, timenode.length, timenode.repeat_after, timespeed.max_limit_in, timespeed.max_limit_out,
           timespeed.burst_limit_in, timespeed.burst_limit_out, timespeed.burst_treshold_in, timespeed.burst_treshold_in, timespeed.burst_time_in,timespeed.burst_time_out,
           timespeed.priority, timespeed.min_limit_in, timespeed.min_limit_out
    FROM billservice_timespeed as timespeed
    JOIN billservice_tariff as tariff ON tariff.access_parameters_id=timespeed.access_parameters_id
    JOIN billservice_timeperiodnode as timenode ON timespeed.time_id=timenode.id
    WHERE tariff.id=%s;
    """ % tarif)

    return cursor.fetchall()

def get_account_data_by_username(cursor, username):
    cursor.execute(
    """SELECT bsa.username, bsa.password, bsa.virtual_ip_address,
    bsat.tarif_id, status, (ballance+credit) as ballance, bsa.disabled_by_limit
    FROM billservice_account as bsa
    JOIN billservice_accounttarif as bsat ON bsat.account_id=bsa.id
    WHERE bsat.datetime<now() and bsa.username='%s' ORDER BY bsat.datetime DESC LIMIT 1""" % username)
    return cursor.fetchone()

def get_nas_id_by_tarif_id(cursor, tarif_id):
    cursor.execute("""SELECT nas_nas.id, ap.access_type from nas_nas
    JOIN billservice_accessparameters AS ap ON ap.nas_id=nas_nas.id
    JOIN billservice_tariff AS bst ON bst.access_parameters_id=ap.id
    WHERE bst.id='%s'""" % tarif_id)
    return cursor.fetchone()

def time_periods_by_tarif_id(cursor, tarif_id):
    cursor.execute("""
    SELECT tpn.id, tpn.name, tpn.time_start::timestamp without time zone, tpn.length, tpn.repeat_after
    FROM billservice_timeperiodnode as tpn
    JOIN billservice_timeperiod_time_period_nodes as tpnds ON tpnds.timeperiodnode_id=tpn.id
    JOIN billservice_accessparameters AS ap ON ap.access_time_id=tpnds.timeperiod_id
    JOIN billservice_tariff AS bst ON bst.access_parameters_id=ap.id
    WHERE bst.id=%s""" % tarif_id)
    return cursor.fetchall()

def transaction(cursor, account, approved, tarif, summ, description, created=None):
    if not created:
        created=datetime.datetime.now()

    f=cursor.execute(
    """
    UPDATE billservice_transaction SET summ=summ+%s
    WHERE account_id=%s and approved=%s and tarif_id=%s and description=%s and now()-created<=interval '00:10:00'
    """, (summ, account, approved, tarif, description)
    )

    if not f:
        cursor.execute("""
        INSERT INTO billservice_transaction(
        account_id, approved, tarif_id, summ, description, created)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """,(account, approved, tarif , summ, description, created))

        tr_id=cursor.fetchone()[0]
    else:
        cursor.execute(
        """
        SELECT id FROM billservice_transaction
        WHERE account_id=%s and approved=%s and tarif_id=%s and summ=%s and description='%s' ORDER BY id DESC LIMIT 1
        """ % (account, approved, tarif , summ, description)
        )
        tr_id=cursor.fetchone()[0]
    cursor.execute("""
    UPDATE billservice_account
    SET ballance=ballance-%s WHERE id=%s""" % (summ, account))

    return tr_id

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
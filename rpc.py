# -*- coding=utf-8 -*-

from __future__ import with_statement

import IPy
import hmac
import zlib
import signal
import hashlib
#import asyncore
#import socket
#socket.setdefaulttimeout(3600)
import datetime
import operator
import itertools
import traceback
import threading
import ConfigParser
import psycopg2, psycopg2.extras
import time, datetime, os, sys, gc, traceback
import Pyro
import Pyro.core, Pyro.protocol, Pyro.constants, Pyro.util

#Pyro.config.PYRO_TRACELEVEL = 3
#print dir(Pyro.config) 
#Pyro.config.PYRO_BROKEN_MSGWAITALL = 0
import isdlogger
import saver, utilites

from IPy import intToIp
from hashlib import md5
from utilites import PoD, cred, ssh_client
from decimal import Decimal
from db import Object as Object
from daemonize import daemonize
from encodings import idna, ascii
from threading import Thread, Lock
from DBUtils.PooledDB import PooledDB
#import chartprovider.bpcdplot
from chartprovider.bpcdplot import cdDrawer, bpbl
#from chartprovider.bpplotadapter import bpplotAdapter
from db import delete_transaction, get_default_speed_parameters, get_speed_parameters, dbRoutine
from db import transaction, ps_history, get_last_checkout, time_periods_by_tarif_id, set_account_deleted
from utilites import settlement_period_info, readpids, killpids, savepid, rempid, getpid, check_running, in_period
from saver import allowedUsersChecker, setAllowedUsers, graceful_loader, graceful_saver
import commands
try:    import mx.DateTime
except: print 'cannot import mx'
from classes.vars import RpcVars
from constants import rules

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

NAME = 'rpc'
DB_NAME = 'db'

class hostCheckingValidator(Pyro.protocol.DefaultConnValidator):
    def __init__(self):
        Pyro.protocol.DefaultConnValidator.__init__(self)

    def acceptIdentification(self, tcpserver, conn, hash, challenge):
        try:
            for val in tcpserver.implementations.itervalues():
                if val[1] == 'rpc':
                    serv = val[0]
                    break
                
            user, mdpass, role = hash.split(':')
            
            try:
                db_connection = serv.connection
                cur = db_connection.cursor()                
                cur.execute("SELECT host, password FROM billservice_systemuser WHERE username='%s' and (role='%s' or role='0');" % (user, role))
                host, password = cur.fetchone()
                db_connection.commit()
                cur.close()
            except Exception, ex:
                logger.error("acceptIdentification error: %s", repr(ex))
                conn.utoken = ''
                return (0,Pyro.constants.DENIED_SERVERTOOBUSY)
            
            hostOk = self.checkIP(conn.addr[0], str(host))

            if hostOk and (password == mdpass):
                #print "accepted---------------------------------"
                tmd5 = hashlib.md5(str(conn.addr[0]))
                tmd5.update(str(conn.addr[1]))
                tmd5.update(tcpserver.hostname)
                conn.utoken = tmd5.digest()
                try:
                    conn.db_connection = pool.connection()
                    conn.db_connection._con._con.set_client_encoding('UTF8')
                    conn.cur = conn.db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
                except Exception, ex:
                    logger.error("acceptIdentification create connection error: %s", repr(ex))
                    conn.utoken = ''
                    return (0,Pyro.constants.DENIED_SERVERTOOBUSY)
                return(1,0)
            else:
                conn.utoken = ''
                return (0,Pyro.constants.DENIED_SECURITY)
        except Exception, ex:
            logger.info("acceptIdentification exception: %s", repr(ex))
            conn.utoken = ''
            return (0,Pyro.constants.DENIED_SECURITY)

    def checkIP(self, ipstr, hostsstr):
        userIP = IPy.IP(ipstr)
        #allowed hosts
        hosts = hostsstr.split(', ')
        hostOk = False
        for host in hosts:
            iprange = host.split('-')
            if len(iprange) == 1:
                if iprange[0].find('/') != -1:
                    hostOk = userIP in IPy.IP(iprange[0])
                else:
                    hostOk = hostOk or (userIP == IPy.IP(iprange[0]))
            else:
                hostOk = hostOk or ((userIP >= IPy.IP(iprange[0])) and (userIP <= IPy.IP(iprange[1])))
            if hostOk:
                break
        return hostOk

    def createAuthToken(self, authid, challenge, peeraddr, URI, daemon):
        #print "createAuthToken_serv"
        # authid is what mungeIdent returned, a tuple (login, hash-of-password)
        # we return a secure auth token based on the server challenge string.
        return authid

    def mungeIdent(self, ident):
        #print "mungeIdent_serv"
        # ident is tuple (login, password), the client sets this.
        # we don't like to store plaintext passwords so store the md5 hash instead.
        return ident
    

def authentconn(func):
    def relogfunc(*args, **kwargs):
        try:
            if args[0].getLocalStorage().caller:
                caller = args[0].getLocalStorage().caller
                if args[0].getLocalStorage().caller.utoken:
                    kwargs['connection'] = caller.db_connection
                    kwargs['cur'] = caller.cur
                    res =  func(*args, **kwargs)
                    return res
                else:
                    return None
            else:
                return func(*args, **kwargs)
        except Exception, ex:
            if isinstance(ex, psycopg2.OperationalError):
                logger.error("%s : (RPC Server) database connection is down: %s \n %s", (args[0].getName(),repr(ex), traceback.format_exc()))
            else:
                #print args[0].getName() + ": exception: " + str(ex)
                logger.error("%s: (RPC server) remote execution exception: %s \n %s", (args[0].getName(),repr(ex), traceback.format_exc()))
                raise ex

    return relogfunc

class RPCServer(Thread, Pyro.core.ObjBase):

    def __init__ (self):
        Thread.__init__(self)
        Pyro.core.ObjBase.__init__(self)
        self.connection = pool.connection()
        self.connection._con._con.set_isolation_level(1)
        self.connection._con._con.set_client_encoding('UTF8')
        self.cur = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  
        self.ticket = ''
        #print Pyro.core.Log


    def run(self):
        #from Pyro.config import PYRO_COMPRESSION
        #print "compr",Pyro.config.PYRO_COMPRESSION
        Pyro.config.PYRO_COMPRESSION=True
        
        Pyro.config.PYRO_DETAILED_TRACEBACK = 1
        Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1
        Pyro.core.initServer()
        daemon=Pyro.core.Daemon()
        daemon.setTimeout(45)
        #daemon.adapter.setIdentification = setIdentification
        daemon.setNewConnectionValidator(hostCheckingValidator())
        daemon.connect(self,"rpc")
        daemon.requestLoop()


    @authentconn
    def testCredentials(self, host, login, password, cur=None, connection=None):
        try:
            #print host, login, password
            a=ssh_client(host, login, password, '')
        except Exception, e:
            logger.error("Can not test credentials for nas %s %s", (host, e))
            return False
        return True

    @authentconn
    def configureNAS(self, id, pptp_enable,auth_types_pap, auth_types_chap, auth_types_mschap2, pptp_ip, radius_enable, radius_server_ip,interim_update, configure_smtp, configure_gateway,protect_malicious_trafic, cur=None, connection=None):
        cur.execute("SELECT ipaddress, login, password, secret FROM nas_nas WHERE id=%s" % id)
        row = cur.fetchone()
        connection.commit()
        #print row
        confstring = ''
        #print 1
        if pptp_enable:
            auth_types=''
            #print 2
            if auth_types_pap==auth_types_chap==auth_types_mschap2:
                #print 3
                auth_types="pap, chap, mschap2"
            else:    
                if auth_types_pap==True:
                    auth_types='pap'
                    
                if auth_types_chap==True and auth_types_pap==True:
                    auth_types+=','
                    
                if auth_types_chap==True:
                    auth_types+='chap'
                    
                if auth_types_mschap2==True and (auth_types_chap==True or auth_types_pap==True):
                    auth_types+=','
                    
                if auth_types_mschap2==True:
                    auth_types+='mschap2'
                
            confstring = unicode(rules['allow_pptp'] % (pptp_ip, auth_types))
            #print 4
            #print rules['allow_pptp'] % (pptp_ip, auth_types)
            
        if radius_enable==True:
            #print rules['allow_radius'],{'interim_update': interim_update, 'secret':row['secret'], 'server_ip':radius_server_ip}
            #print rules['allow_radius'] % {'interim_update': interim_update, 'secret':row['secret'], 'server_ip':radius_server_ip}
            data = rules['allow_radius'] % (interim_update, row['secret'], radius_server_ip)
            #print data
            confstring+=unicode(data)
            #print 5
            
        if configure_smtp==True:
            confstring+=rules['smtp_protect']
            #print 6
            
        if configure_gateway==True:
            confstring+=rules['gateway']
            #print 7
        
        if protect_malicious_trafic==True:
        
            confstring+=rules['malicious_trafic']
            #print 8
        
        #print confstring
        try:
            a=ssh_client(row["ipaddress"],row["login"], row["password"], confstring)
        except Exception, e:
            logger.error("configureNAS exception %s:", repr(e))
            return False
        return True


    @authentconn
    def accountActions(self, account_id, action, cur=None, connection=None):

        if type(account_id) is not list:
            account_id=[account_id]
            
        for account in account_id:
            cur.execute("""SELECT account.id as account_id, account.username as username, account.password as password, account.ipn_ip_address as ipn_ip_address,
                             account.vpn_ip_address as vpn_ip_address, account.ipn_mac_address as  ipn_mac_address,
                             nas.login as nas_login, nas.password as nas_password, nas.ipaddress as nas_ipaddress,
                             nas.user_add_action as user_add_action, nas.user_delete_action as user_delete_action, 
                             nas.user_enable_action as user_enable_action, nas.user_disable_action as user_disable_action, ap.access_type as access_type 
                             FROM billservice_account as account
                             JOIN nas_nas as nas ON nas.id = account.nas_id
                             JOIN billservice_tariff as tarif on tarif.id = get_tarif(account.id)
                             JOIN billservice_accessparameters as ap ON ap.id=tarif.access_parameters_id
                             WHERE account.id=%s
                             """, (account,))
    
            row = cur.fetchone()
            connection.commit()
            #print "actions", row
            #print action
            if row==None:
                return False
    
            if row['ipn_ip_address']=="0.0.0.0":
                return False
    
            if action=='disable':
                command = row['user_disable_action']
            elif action=='enable':
                command = row['user_enable_action']
            elif action=='create':
                command = row['user_add_action']
            elif action =='delete':
                command = row['user_delete_action']
            #print command
    
            sended = cred(account_id=row['account_id'], account_name=row['username'], account_password=row['password'], access_type = row['access_type'],
                          account_vpn_ip=row['vpn_ip_address'], account_ipn_ip=row['ipn_ip_address'], 
                          account_mac_address=row['ipn_mac_address'], nas_ip=row['nas_ipaddress'], nas_login=row['nas_login'], 
                          nas_password=row['nas_password'], format_string=command)
 
            if action=='create' and sended==True:
                cur.execute("UPDATE billservice_account SET ipn_status=%s, ipn_added=%s WHERE id=%s", (True, True, row['account_id']))
                cur.execute("UPDATE billservice_accountipnspeed SET state=False WHERE account_id=%s", (row['account_id'],))
                
            elif action=='create' and sended==False:
                cur.execute("UPDATE billservice_account SET ipn_status=%s, ipn_added=%s WHERE id=%s", (False, False, row['account_id']))
                cur.execute("UPDATE billservice_accountipnspeed SET state=False WHERE account_id=%s", (row['account_id'],))
            
            if action =='delete'  and sended==True:
                cur.execute("UPDATE billservice_account SET ipn_status=%s, ipn_added=%s WHERE id=%s", (False, False, row['account_id']))
                cur.execute("DELETE FROM billservice_accountipnspeed WHERE account_id=%s", (row['account_id'],))
                
            elif action =='delete'  and sended==False:
                cur.execute("UPDATE billservice_account SET ipn_status=%s, ipn_added=%s WHERE id=%s", (False, False, row['account_id']))
                cur.execute("DELETE FROM billservice_accountipnspeed WHERE account_id=%s", (row['account_id'],))

            if action=='disable' and sended==True:
                cur.execute("UPDATE billservice_account SET ipn_status=%s WHERE id=%s", (False, row['account_id'],))
                
            if action=='enable' and sended==True:
                cur.execute("UPDATE billservice_account SET ipn_status=%s WHERE id=%s", (True, row['account_id'],))
        
        connection.commit()

#            if sended==False:
#                cur.execute("UPDATE billservice_account SET ipn_status=%s", (ipn_status,))
        del account_id
        del row
        del account
        return sended

        
    '''@authentconn
    def get_object(self, name, cur=None, connection=None):
        try:
            model = models.__getattribute__(name)()
        except:
            return None
        return model'''

    @authentconn
    def transaction_delete(self, ids, cur=None, connection=None):
        for i in ids:
            #print "delete %s transaction" % i
            delete_transaction(cur, int(i))
        connection.commit()

        return
    @authentconn
    def flush(self, cur=None, connection=None):
        pass
    
    @authentconn
    def get(self, sql, cur=None, connection=None):
        #print sql
        if not cur:
            cur = self.cur
        cur.execute(sql)
        #connection.commit()
        result=[]
        r=cur.fetchall()
        if len(r)>1:
            raise Exception

        if r==[]:
            return None
        return Object(r[0])

    @authentconn
    def get_list(self, sql, cur=None, connection=None):
        #print sql
        listconnection = pool.connection()
        listconnection._con._con.set_client_encoding('UTF8')
        listcur = listconnection.cursor()
        listcur.execute(sql)
        retres = listcur.fetchall()
        listconnection.commit()
        listcur.close()
        listconnection.close()
        return retres

    @authentconn
    def pay(self, account, summ, document, description, created, promise, end_promise, systemuser_id, cur=None, connection=None):
        
        transaction = Object()
        transaction.account_id=account
        transaction.type_id = "CASSA_TRANSACTION"
        transaction.approved = True
        transaction.description = description
        transaction.summ=summ*(-1)
        transaction.bill=document
        transaction.systemuser_id = systemuser_id
        transaction.created = created
        
        transaction.promise = promise
        if end_promise:
            transaction.end_promise = end_promise
        
        
        try:
            sql = transaction.save("billservice_transaction")
            #sql = "INSERT INTO billservice_transaction(account_id, type_id, approved, description, bill, summ, created) VALUES(%s,'%s', True, '', '%s',%s, '%s') RETURNING id;" % (account, "MANUAL_TRANSACTION", document, sum*(-1), datetime.datetime.now())
            cur.execute(sql)
            id=cur.fetchall()[0]
            connection.commit()
            return Object(id)
        except Exception, e:
            logger.error('pay exception: %s', repr(e))
            return False
    
    @authentconn
    def createAccountTarif(self, account, tarif, datetime, cur=None, connection=None):
        
        o = Object()
        o.account_id = account
        o.tarif_id=tarif
        o.datetime = datetime
        try:
            #sql = "UPDATE billservice_account SET ballance = ballance - %f WHERE id = %d;" % (sum*(-1), account)
            sql = o.save("billservice_accounttarif")
            
            cur.execute(sql)
            connection.commit()
            return True
        except Exception, e:
            logger.error('createAccountTarif exception: %s', repr(e))
            return False

    @authentconn
    def dbaction(self, fname, *args, **kwargs):
        return dbRoutine.execRoutine(fname, *args, **kwargs)
    
    @authentconn
    def delete(self, model, table, cur=None, connection=None):
        sql = model.delete(table)
        #print sql
        cur.execute(sql)
        #connection.commit()
        del sql
        return

    @authentconn
    def list_logfiles(self, cur=None, connection=None):
        return os.listdir('log/')
        #print sql
        #cur.execute(sql)
        #connection.commit()
        #del sql
        
    def get_tail_log(self, log_name, count=10, all_file=False):
        #a=file("log/%s", 'r')
        #strs = a.re
        if all_file:
            return commands.getstatusoutput("cat log/%s" % log_name)
        
        return commands.getstatusoutput("tail -n %s log/%s" % (count, log_name))
    
    @authentconn
    def activate_card(self, login, pin, cur=None, connection=None):
        status_ok = 1
        status_bad_userpassword = 2
        status_card_was_activated =3
        now = datetime.datetime.now()
        if login and pin:
            cur.execute("SELECT * FROM billservice_card WHERE login=%s and pin=%s and sold is not Null and disabled=False;",  (login, pin, ))
            card = cur.fetchone()
            if not card: return status_bad_userpassword
            
            if card['activated'] or card['start_date']>now or card['end_date']<now: return status_card_was_activated
            
            #if card['activated'] or card['start_date']>datetime.datetime.now() or card['end_date']<datetime.datetime.now(): return status_card_was_activated
            
            cur.execute("SELECT * FROM billservice_ippool WHERE id=(SELECT pool_id FROM billservice_ipinuse WHERE id=%s);", (card['ipinuse_id'],))
            pool = cur.fetchone()
            
            # 0 -VPN, 1 - IPN
            if pool['type']==1:
                cur.execute("""INSERT INTO billservice_account(username, "password", nas_id, ipn_ip_address, ipn_status, status, created, ipn_added, allow_webcab, allow_expresscards, assign_dhcp_null, assign_dhcp_block, allow_vpn_null, allow_vpn_block)
                VALUES(%s, %s, %s, %s, False, 1, now(), False, True, True, False, False, False, False) RETURNING id;""", (login, pin, card['nas_id'], card['ip'], ))
            else:
                cur.execute("""INSERT INTO billservice_account(username, "password", nas_id, vpn_ip_address, ipn_status, status, created, ipn_added, allow_webcab, allow_expresscards, assign_dhcp_null, assign_dhcp_block, allow_vpn_null, allow_vpn_block)
                VALUES(%s, %s, %s, %s, False, 1, now(), False, True, True, False, False, False, False) RETURNING id;""", (login, pin, card['nas_id'], card['ip'], ))
                
            account_id = cur.fetchone()['id']
    
            cur.execute("INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(%s, %s, %s);", (account_id, card['tarif_id'], now))
            
            cur.execute(u"""
            INSERT INTO billservice_transaction(bill, account_id, type_id, approved, tarif_id, summ, description, created, promise, end_promise)
            VALUES('Активация карты доступа', %s, 'ACCESS_CARD', True, %s, %s*(-1),'', %s, False, Null);
            """, (account_id, card["tarif_id"], card['nominal'], now))
    
            cur.execute("UPDATE billservice_card SET activated = %s, activated_by_id = %s WHERE id = %s;", (now, account_id, card['id']))
            connection.commit()
            return  status_ok
    
                            
        #cur.execute(sql)
        #connection.commit()
        #del sql
        return
    
    @authentconn
    def change_tarif(self, accounts, tarif, date, cur=None, connection=None):
        cur.connection.commit()
        for account in accounts:
            try:
                cur.execute("INSERT INTO billservice_accounttarif(account_id, tarif_id, datetime) VALUES(%s,%s,%s)", (account, tarif, date))
            except Exception, e:
                cur.connection.rollback()
                logger.error("Error change tarif for account %s, %s", (account, e))
                return False
        cur.connection.commit()
        return True
                
            

    @authentconn
    def activate_pay_card(self, account_id, serial, card_id, pin, cur=None, connection=None):
        status_ok = 1
        status_bad_userpassword = 2
        status_card_was_activated =3
        now = datetime.datetime.now()
        try:
            if serial and pin and card_id and account_id:
                cur.execute("SELECT * FROM billservice_card WHERE id=%s and series=%s and pin=%s and disabled=False;",  (card_id, serial, pin ))
                card = cur.fetchone()
                if not card: return "CARD_NOT_FOUND"
                
                if card["sold"] is None: return "CARD_NOT_SOLD"
                
                if card['activated']: return "CARD_ALREADY_ACTIVATED"
                
                if card['start_date']>now or card['end_date']<now: return "CARD_EXPIRED"
                                
                cur.execute(u"""
                INSERT INTO billservice_transaction(bill, account_id, type_id, approved, tarif_id, summ, description, created, promise, end_promise)
                VALUES('Активация карты оплаты', %s, 'PAY_CARD', True, %s, %s*(-1),'', %s, False, Null);
                """, (account_id, card["tarif_id"], card['nominal'], now))
        
                cur.execute("UPDATE billservice_card SET activated = %s, activated_by_id = %s WHERE id = %s;", (now, account_id, card['id']))
                connection.commit()
                logger.info("Card #%s series #%s pin #%s was activated", (card_id, serial, pin))
                return  "CARD_ACTIVATED"
        except Exception, e:
            logger.error("Error activate card %s, %s", (card_id, e))
            connection.rollback()
            return "CARD_ACTIVATION_ERROR"
                            
    
    @authentconn
    def iddelete(self, id, table, cur=None, connection=None):
        sql = u"DELETE FROM %s where id=%d" % (table, id)
        #print sql
        cur.execute(sql)
        del table
        del id
        #connection.commit()
        return

    @authentconn
    def command(self, sql, cur=None, connection=None):

        cur.execute(sql)
        #connection.commit()
        del sql
        return         

    @authentconn
    def commit(self, cur=None, connection=None):
        connection.commit()

    @authentconn
    def makeChart(self, *args, **kwargs):
        kwargs['cur']=None
        kwargs['connection']=None
        listconnection = pool.connection()
        listconnection._con._con.set_client_encoding('UTF8')
        listcur = listconnection.cursor()
        bpbl.bpplotAdapter.rCursor = listcur
        #bpplotAdapter.rCursor = listcur
        cddrawer = cdDrawer()
        imgs = cddrawer.cddraw(*args, **kwargs)
        listconnection.commit()
        listcur.close()
        listconnection.close()
        gc.collect()
        return imgs

    @authentconn
    def rollback(self, cur=None, connection=None):
        connection.rollback()

    @authentconn
    def sql(self, sql, return_response=True, pickler=False, cur=None, connection=None):
        #print self.ticket
        #print sql
        cur.execute(sql)
        #connection.commit()
        
        #print dir(connection)
        result=[]
        a=time.clock()
        if return_response:
            result = map(Object, cur.fetchall())
        #print "Query length=", time.clock()-a
        return result

    @authentconn
    def get_limites(self, account_id, cur=None, connection=None):
        limites = cur.execute("""SELECT lim.name, lim.size, lim.group_id, lim.mode, sp.time_start, sp.length, sp.length_in, sp.autostart FROM billservice_trafficlimit as lim
        JOIN billservice_settlementperiod as sp ON sp.id=lim.settlement_period_id
        WHERE lim.tarif_id=get_tarif(%s)""", (account_id,))
        limites = cur.fetchall()

        cur.execute("SELECT datetime FROM billservice_accounttarif WHERE account_id=%s and datetime<now() ORDER BY ID DESC LIMIT 1", (account_id,))
        accounttarif_date = cur.fetchone()["datetime"]
        cur.connection.commit()
        res = []
        for limit in limites:
            limit_name = limit["name"]
            limit_size = limit["size"]
            group_id = limit["group_id"]
            mode = limit["mode"] 
            time_start = limit["time_start"]
            length = limit["length"]
            length_in = limit["length_in"]
            autostart = limit["autostart"]
            #print limit_name
            #print 3
            if autostart:
                time_start = accounttarif_date
            
            settlement_period_start, settlement_period_end, delta = settlement_period_info(time_start, length_in, length)
            if settlement_period_start<accounttarif_date:
                settlement_period_start = accounttarif_date
            #если нужно считать количество трафика за последнеие N секунд, а не за рачётный период, то переопределяем значения
            

            if mode==True:
                now = datetime.datetime.now()
                settlement_period_start=now-datetime.timedelta(seconds=delta)
                settlement_period_end=now
            
            cur.connection.commit()

            #print 4
            cur.execute("""
            SELECT sum(bytes) as size FROM billservice_groupstat
            WHERE group_id=%s and account_id=%s and datetime>%s and datetime<%s
            """ , (group_id, account_id, settlement_period_start, settlement_period_end,))
            
            size=cur.fetchone()
            res.append({'settlement_period_start':settlement_period_start, 'settlement_period_end':settlement_period_end, 'limit_name': limit_name, 'limit_size':limit_size or 0, 'size':size["size"] or 0,})
            cur.connection.commit()
        
        return res


    @authentconn
    def get_prepaid_traffic(self, account_id, cur=None, connection=None):
        cur.execute("""SELECT   ppt.id, ppt.account_tarif_id, ppt.prepaid_traffic_id,  ppt.size, ppt.datetime, pp.size, (SELECT name FROM billservice_group WHERE id=pp.group_id) as group_name FROM billservice_accountprepaystrafic as ppt
                            JOIN billservice_prepaidtraffic as pp ON pp.id=ppt.prepaid_traffic_id
                            WHERE account_tarif_id=(SELECT id FROM billservice_accounttarif WHERE account_id=175 and datetime<now() ORDER BY datetime DESC LIMIT 1);""", (account_id,))

        result = map(Object, cur.fetchall())
        return result
    
    @authentconn
    def get_models(self, table='', fields = [], where={}, cur=None, connection=None):
        cur.execute("SELECT %s FROM %s WHERE %s ORDER BY id ASC;" % (",".join(fields) or "*", table, " AND ".join("%s=%s" % (wh, where[wh]) for wh in where) or 'id>0'))
        
        a=time.clock()
        result = map(Object, cur.fetchall())
        return result


    @authentconn
    def get_model(self, id, table='', fields = [], cur=None, connection=None):
        #print "SELECT %s from %s WHERE id=%s ORDER BY id ASC;" % (",".join(fields) or "*", table, id)
        sql = u"SELECT %s from %s WHERE id=%s ORDER BY id ASC;" % (",".join(fields) or "*", table, id)
        #print sql
        cur.execute(sql)
        result=[]
        result = map(Object, cur.fetchall())
        return result[0]
    
    @authentconn    
    def get_notsold_cards(self, cards, cur=None, connection=None):
        if len(cards)>0:
            crd = "(" + ",".join(cards) + ")"
        else:
            crd = "(0)" 
        
        cur.execute("SELECT * FROM billservice_card WHERE id IN %s AND sold is Null;" % crd)
        result = map(Object, cur.fetchall())
        return result
    
    @authentconn
    def get_operator(self, cur=None, connection=None):
        cur.execute("SELECT * FROM billservice_operator LIMIT 1;")
        result = map(Object,cur.fetchall())
        return result
    
    @authentconn
    def get_operator_info(self, cur=None, connection=None):
        cur.execute("SELECT operator.*, bankdata.bank as bank, bankdata.bankcode as bankcode, bankdata.rs as rs FROM billservice_operator as operator JOIN billservice_bankdata as bankdata ON bankdata.id=operator.bank_id LIMIT 1")
        result = Object(cur.fetchone())
        return result

    @authentconn
    def get_dealer_info(self, id, cur=None, connection=None):
        cur.execute("SELECT dealer.*, bankdata.bank as bank, bankdata.bankcode as bankcode, bankdata.rs as rs FROM billservice_dealer as dealer JOIN billservice_bankdata as bankdata ON bankdata.id=dealer.bank_id WHERE dealer.id=%s", (id, ))
        result = Object(cur.fetchone())
        return result


    @authentconn      
    def get_bank_for_operator(self, operator, cur=None, connection=None):
        cur.execute("SELECT * FROM billservice_bankdata WHERE id=(SELECT bank_id FROM billservice_operator WHERE id=%s)", (operator,))
        result = map(Object, cur.fetchall())
        return result[0]
    
    @authentconn      
    def get_cards_nominal(self, cur=None, connection=None):
        cur.execute("SELECT nominal FROM billservice_card GROUP BY nominal")
        result = map(Object, cur.fetchall())
        return result
    
    @authentconn 
    def get_accounts_for_tarif(self, tarif_id, cur=None, connection=None):
        cur.execute("""SELECT acc.*, (SELECT name FROM nas_nas where id = acc.nas_id) AS nas_name 
        FROM billservice_account AS acc 
        WHERE %s=get_tarif(acc.id) ORDER BY acc.username ASC;""", (tarif_id,))
        result = map(Object, cur.fetchall())
        return result

    @authentconn 
    def get_tariffs(self, cur=None, connection=None):
        cur.execute("""SELECT id, name, active, (SELECT bsap.access_type
                   FROM billservice_accessparameters AS bsap WHERE (bsap.id=tariff.access_parameters_id) ORDER BY bsap.id LIMIT 1) AS ttype FROM billservice_tariff as tariff  WHERE tariff.deleted = False ORDER BY ttype, name;""")
        result = map(Object, cur.fetchall())
        return result
    
    
    @authentconn  
    def delete_card(self, id, cur=None, connection=None):
        cur.execute("DELETE FROM billservice_card WHERE id=%s", (id,))
        return
    
    @authentconn  
    def get_next_cardseries(self, cur=None, connection=None):
        cur.execute("SELECT MAX(series) as series FROM billservice_card")
        result = cur.fetchone()['series']
        if result==None:
            result=0
        else:
            result+=1
        #print result
        return result
    
    @authentconn
    def sql_as_dict(self, sql, return_response=True, cur=None, connection=None):
        #print sql
        cur.execute(sql)
        result=[]
        a=time.clock()
        if return_response:

            result =cur.fetchall()
        #print "Query length=", time.clock()-a
        return result


    @authentconn
    def transaction(self, sql, cur=None, connection=None):
        cur.execute(sql)
        id = cur.fetchone()['id']
        return id

    @authentconn
    def save(self, model, table, cur=None, connection=None):
        #print model
        sql = model.save(table)
        #print sql

        #print sql
        #print sql
        cur.execute(sql)
        id = cur.fetchone()['id']
        return id

    @authentconn
    def test(self, cur=None, connection=None):
        pass

    @authentconn
    def add_addonservice(self, account_id, service_id, ignore_locks = False, activation_date = None, cur=None, connection=None):
        #Получаем параметры абонента
        sql = "SELECT id, ballance, balance_blocked, disabled_by_limit, status, get_tarif(id) as tarif_id,(SELECT datetime FROM billservice_accounttarif WHERE account_id=acc.id and datetime<now() ORDER BY datetime DESC LIMIT 1) as accounttarif_date FROM billservice_account as acc WHERE id=%s" %account_id
        cur.execute(sql)
        connection.commit()
        result=[]
        r=cur.fetchall()
        if len(r)>1:
            raise Exception

        if r==[]:
            return 'ACCOUNT_DOES_NOT_EXIST'
                
        account = Object(r[0]) 
        
        sql = "SELECT id FROM billservice_accountaddonservice WHERE account_id=%s and service_id=%s and (deactivated>now() or deactivated is Null)" % (account_id, service_id, )
        cur.execute(sql)
        connection.commit()
        result=[]
        r=cur.fetchall()

        if r!=[]:
            return 'SERVICE_ARE_ALREADY_ACTIVATED'
                

                
        #Получаем нужные параметры услуги
        sql = "SELECT id, allow_activation,timeperiod_id, change_speed FROM billservice_addonservice WHERE id = %s" % service_id
        cur.execute(sql)
        connection.commit()
        result=[]
        r=cur.fetchall()
        if len(r)>1:
            raise Exception

        if r==[]:
            return 'ADDON_SERVICE_DOES_NOT_EXIST'
                
        service = Object(r[0]) 

        sql = "SELECT time_start, length, repeat_after FROM billservice_timeperiodnode WHERE id IN (SELECT timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id=%s)" % service.timeperiod_id

        cur.execute(sql)
        connection.commit()

        timeperiods = map(Object, cur.fetchall())

        res = False
        for timeperiod in timeperiods:
            if res==True or in_period(timeperiod.time_start, timeperiod.length, timeperiod.repeat_after):
                res=True

        if res == False and ignore_locks==False:
            return "NOT_IN_PERIOD"

        if service.change_speed and ignore_locks==False:

            try:
                cur.execute("SELECT id FROM billservice_accountaddonservice WHERE deactivated is Null and service_id IN (SELECT id FROM billservice_addonservice WHERE change_speed=True) and account_id=%s" % account.id)

            except Exception, e:
                logger.error("Can not add addonservice for account %s, %s", (account_id, e))
            if cur.fetchall():

                return "ALERADY_HAVE_SPEED_SERVICE"

        # Проверка на возможность активации услуги при наличии блокировок
        if not ignore_locks:
            if service.allow_activation==False and (account.ballance<=0 or account.balance_blocked==True or account.disabled_by_limit==True or account.status!=1):
                return "ACCOUNT_BLOCKED"
        

        #Получаем нужные параметры услуги из тарифного плана
        sql = "SELECT id, activation_count, activation_count_period_id FROM billservice_addonservicetarif WHERE tarif_id=%s and service_id = %s" % (account.tarif_id, service_id)
        cur.execute(sql)
        connection.commit()
        result=[]
        r=cur.fetchall()
        if len(r)>1:
            raise Exception

        if r==[]:
            return 'ADDONSERVICE_TARIF_DOES_NOT_ALLOWED'

        tarif_service = Object(r[0]) 

        if tarif_service.activation_count!=0 and ignore_locks==False:

            if tarif_service.activation_count_period_id:

                sql = "SELECT time_start, length, length_in, autostart  FROM billservice_settlementperiod WHERE id = %s" % tarif_service.activation_count_period_id

                cur.execute(sql)
                connection.commit()
                result=[]
                r=cur.fetchall()
                if len(r)>1:
                    raise Exception
        
                if r==[]:
                    return None

                settlement_period = Object(r[0]) 
                if settlement_period.autostart:
                    settlement_period.time_start = account.accounttarif_date
                    
                settlement_period_start, settlement_period_end, delta = settlement_period_info(settlement_period.time_start, settlement_period.length_in, settlement_period.length)
                
                sql = "SELECT count(*) as cnt FROM billservice_accountaddonservice WHERE account_id=%s and service_id=%s and activated>'%s' and activated<'%s'" % (account.id, service.id, settlement_period_start, settlement_period_end,)
            else:
                sql = "SELECT count(*) as cnt FROM billservice_accountaddonservice WHERE account_id=%s and service_id=%s" % (account.id, service.id,)
            
            cur.execute(sql)
            connection.commit()
            result=[]
            r=cur.fetchall()
            if len(r)>1:
                raise Exception
    
            if r==[]:
                return None
                    
            activations_count = Object(r[0]) 
            if activations_count.cnt>=tarif_service.activation_count: return "TOO_MUCH_ACTIVATIONS"
            

        if activation_date:
            sql = "INSERT INTO billservice_accountaddonservice(service_id, account_id, activated) VALUES(%s,%s,'%s')" % (service.id, account.id, activation_date)
        else:
            sql = "INSERT INTO billservice_accountaddonservice(service_id, account_id, activated) VALUES(%s,%s,now())" % (service.id, account.id,)
        try:
            cur.execute(sql)
            connection.commit()
            return True
        except Exception, e:
            logger.error("Error add addonservice to account, %s", e)
            connection.rollback()
            return False
        
        
    @authentconn
    def del_addonservice(self, account_id, account_service_id, cur=None, connection=None):
 
        #Получаем нужные параметры аккаунта
        cur.connection.commit()
        cur.execute("SELECT acc.id, get_tarif(id) as tarif_id, (SELECT id FROM billservice_accounttarif WHERE account_id=acc.id and datetime<now() ORDER BY datetime DESC LIMIT 1) as accounttarif_id FROM billservice_account as acc WHERE id = %s;", (account_id,))
        
        result=[]
        r=cur.fetchall()
        cur.connection.commit()
        if len(r)>1:
            raise Exception

        if r==[]:
            return 'ACCOUNT_DOES_NOT_EXIST'
                
        account = Object(r[0]) 
        #Получаем нужные параметры услуги абонента
        sql = "SELECT id, service_id, account_id, activated, deactivated, action_status FROM billservice_accountaddonservice  WHERE id = %s" % account_service_id
        cur.execute(sql)
        connection.commit()
        result=[]
        r=cur.fetchall()
        if len(r)>1:
            raise Exception

        if r==[]:
            return 'ACCOUNT_ADDON_SERVICE_DOES_NOT_EXIST'
        accountservice = Object(r[0]) 
        #print accounservice
        #Получаем нужные параметры услуги
        sql = "SELECT id, service_type, cancel_subscription, wyte_period_id, wyte_cost FROM billservice_addonservice WHERE id = %s" % accountservice.service_id
        cur.execute(sql)
        connection.commit()
        result=[]
        r=cur.fetchall()
        if len(r)>1:
            raise Exception

        if r==[]:
            return 'ADDON_SERVICE_DOES_NOT_EXIST'
                
        service = Object(r[0]) 
        
        if service.cancel_subscription:
            
            if service.wyte_period_id:
                sql = "SELECT time_start, length, length_in, autostart  FROM billservice_settlementperiod WHERE id = %s" % service.wyte_period_id
                cur.execute(sql)
                connection.commit()
                result=[]
                r=cur.fetchall()
                if len(r)>1:
                    raise Exception
        
                if r==[]:
                    return None
                        
                settlement_period = Object(r[0]) 
                try:
                    settlement_period_start, settlement_period_end, delta = settlement_period_info(settlement_period.time_start, settlement_period.length_in, settlement_period.length)
                except Exception, e:
                    logger.error("Error cannot delete addonservice for account %s, %s", (account_id, e))
            else:
                delta = 0
            now = datetime.datetime.now()
            
            if (((now-accountservice.activated).seconds+(now-accountservice.activated).days*86400)<delta) or (service.wyte_cost and delta == 0):
                try:
                    model = Object()
                    model.account_id = account_id
                    model.type_id = 'ADDONSERVICE_WYTE_PAY'
                    model.summ = service.wyte_cost
                    model.service_id = service.id
                    model.service_type = service.service_type
                    model.created = "now()"
                    model.summ = service.wyte_cost
                    model.accounttarif_id = account.accounttarif_id
                    model.accountaddonservice_id = account_service_id
                except Exception, e:
                    logger.error("Error cannot make wyte transaction for account %s, %s", (account_id, e))
                sql = model.save("billservice_addonservicetransaction")
                cur.execute(sql)
            #Отключаем услугу

            sql = "UPDATE billservice_accountaddonservice SET deactivated=now() WHERE id=%s" % accountservice.id
            cur.execute(sql)
            connection.commit()

            return True
        else:
            return 'NO_CANCEL_SUBSCRIPTION'
        return False

        
    @authentconn
    def get_allowed_users(self, cur=None, connection=None):
        return allowedUsers()
    
    @authentconn
    def pod(self, session, cur=None, connection=None):
        #print "Start POD"
        cur.execute("""
                    SELECT nas.ipaddress as nas_ip, nas.type as nas_type, nas.name as nas_name, nas.secret as nas_secret, nas.login as nas_login, nas.password as nas_password,
                    nas.reset_action as reset_action, account.id as account_id, account.username as account_name, account.vpn_ip_address as vpn_ip_address,
                    account.ipn_ip_address as ipn_ip_address, account.ipn_mac_address as ipn_mac_address, session.framed_protocol as framed_protocol
                    FROM radius_activesession as session
                    JOIN billservice_account as account ON account.id=session.account_id
                    JOIN nas_nas as nas ON nas.id=account.nas_id
                    WHERE  session.sessionid='%s'
                    """ % session)

        row = cur.fetchone()
        connection.commit()
        return PoD(dict=dict,
            account_id=row['account_id'], 
            account_name=str(row['account_name']), 
            account_vpn_ip=row['vpn_ip_address'], 
            account_ipn_ip=row['ipn_ip_address'], 
            account_mac_address=row['ipn_mac_address'], 
            access_type=str(row['framed_protocol']), 
            nas_ip=row['nas_ip'], 
            nas_type=row['nas_type'], 
            nas_name=row['nas_name'], 
            nas_secret=row['nas_secret'], 
            nas_login=row['nas_login'], 
            nas_password=row['nas_password'], 
            session_id=str(session), 
            format_string=str(row['reset_action'])
        )


def reread_pids():
    global vars
    newpids, newpiddate = readpids(vars.piddir, vars.piddate, exclude = [vars.name + '.pid'])
    if newpids:
        with vars.pidLock:
            vars.pids    = newpids
            vars.piddate = newpiddate
        
def broadcast_SIGUSR1():
    global vars
    reread_pids()
    logger.warning("Broadcasting SIGUSR1 to known pids, except self: %s {%s/%s}", (repr(vars.pids),vars.piddir, vars.piddate)) 
    if vars.pids:
        killpids(itertools.imap(operator.itemgetter(1), vars.pids), 10)
        
    
    
def SIGTERM_handler(signum, frame):
    logger.lprint("SIGTERM recieved")
    graceful_save()
    
def SIGHUP_handler(signum, frame):
    global config
    logger.lprint("SIGHUP recieved")
    try:
        config.read("ebs_config.ini")
        logger.setNewLevel(int(config.get("rpc", "log_level")))
    except Exception, ex:
        logger.error("SIGHUP config reread error: %s", repr(ex))
    else:
        logger.lprint("SIGHUP config reread OK")
        
def SIGUSR1_handler(signum, frame):
    logger.lprint("SIGUSR1 received!")
    try:
        broadcast_SIGUSR1()
    except Exception, ex:
        logger.error("Exception diring SIGUSR1 broadcast: %s \n %s", (repr(ex), traceback.format_exc()))

def graceful_save():
    global threads, vars
    for th in threads:
        if isinstance(th, RPCServer):
            th.daemon.shutdown(disconnect=True)
    logger.lprint("About to stop gracefully.")
    pool.close()
    time.sleep(2)
    rempid(vars.piddir, vars.name)
    logger.lprint("Stopping gracefully.")
    sys.exit()
    
def main():
    global threads, vars
    threads=[]
    threads.append(RPCServer())
    for th in threads:	
        th.start()
        time.sleep(0.1)
    try:
        signal.signal(signal.SIGTERM, SIGTERM_handler)
    except: logger.lprint('NO SIGTERM!')
    
    try:
        signal.signal(signal.SIGHUP, SIGHUP_handler)
    except: logger.lprint('NO SIGHUP!')
    
    try:
        signal.signal(signal.SIGUSR1, SIGUSR1_handler)
    except: logger.lprint('NO SIGUSR1!')
    #main thread should not exit!
    #print "ebs: rpc: started"
    savepid(vars.piddir, vars.name)
    while True:
        time.sleep(300)
        
if __name__ == "__main__":
    if "-D" in sys.argv:
        pass
        #daemonize("/dev/null", "log.txt", "log.txt")
     
    config = ConfigParser.ConfigParser()    
    config.read("ebs_config.ini")
    
    try:
        vars = RpcVars()        
        vars.get_vars(config=config, name=NAME, db_name=DB_NAME)


        logger = isdlogger.pyrologger(vars.log_type, loglevel=vars.log_level, ident=vars.log_ident, filename=vars.log_file)
        utilites.log_adapt = logger.log_adapt
        saver.log_adapt    = logger.log_adapt
        logger.lprint('Ebs RPC start')
        if check_running(getpid(vars.piddir, vars.name), vars.name): raise Exception ('%s already running, exiting' % vars.name)

        maxUsers = int(config.get("rpc", "max_users"))
    

        pool = PooledDB(mincached=1, maxcached=10,
                        blocking=True, maxusage=20,
                        setsession=["SET statement_timeout = 180000000;"],
                        creator=psycopg2, dsn=vars.db_dsn)
        
        if not globals().has_key('_1i'):
            _1i = lambda: ''
        allowedUsers = setAllowedUsers(_1i(), pool.connection())               
        allowedUsers()        
        Pyro.util.Log = logger
        Pyro.core.Log = logger
        Pyro.protocol.Log = logger
        #-------------------
        print "ebs: rpc: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in rpc, exiting: ', repr(ex)
        logger.error('Exception in rpc , exiting: %s', repr(ex))

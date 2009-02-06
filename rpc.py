
import IPy
import hmac
import zlib
import signal
import hashlib
import asyncore
import isdlogger
import threading
import ConfigParser
import psycopg2, psycopg2.extras
import time, datetime, os, sys, gc, traceback
import Pyro.core, Pyro.protocol, Pyro.constants

from IPy import intToIp
from hashlib import md5
from utilites import PoD, cred, SSHClient
from decimal import Decimal
from db import Object as Object
from daemonize import daemonize
from encodings import idna, ascii
from threading import Thread, Lock
from DBUtils.PooledDB import PooledDB
from chartprovider.bpcdplot import cdDrawer
from chartprovider.bpplotadapter import bpplotAdapter
from db import delete_transaction, get_default_speed_parameters, get_speed_parameters, dbRoutine
from db import transaction, ps_history, get_last_checkout, time_periods_by_tarif_id, set_account_deleted

try:    import mx.DateTime
except: print 'cannot import mx'

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

config = ConfigParser.ConfigParser()

class hostCheckingValidator(Pyro.protocol.DefaultConnValidator):
    def __init__(self):
        Pyro.protocol.DefaultConnValidator.__init__(self)
        '''self.connection = pool.connection()
    #print dir(self.connection)
    self.connection._con._con.set_client_encoding('UTF8')
    self.cur = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)'''



    def acceptIdentification(self, tcpserver, conn, hash, challenge):
        try:
            for val in tcpserver.implementations.itervalues():
                if val[1] == 'rpc':
                    serv = val[0]
                    break
                
            '''if len(pool._connections) == maxUsers:
                logger.error("rpc max_users depleted: %s", repr(ex))
                conn.utoken = ''
                return (0,Pyro.constants.DENIED_SERVERTOOBUSY)'''
            
            user, mdpass = hash.split(':', 1)
            try:
                obj = serv.get("SELECT * FROM billservice_systemuser WHERE username='%s';" % user)
                val[0].connection.commit()
            except Exception, ex:
                logger.error("acceptIdentification error: %s", repr(ex))
                conn.utoken = ''
                return (0,Pyro.constants.DENIED_SERVERTOOBUSY)
            #print obj.id
            #print obj.host
            hostOk = self.checkIP(conn.addr[0], str(obj.host))

            if hostOk and (obj.password == mdpass):
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
                #Pyro.protocol.DefaultConnValidator.acceptIdentification(self, tcpserver, conn, hash, challenge)
                #reread runtime options
                config.read("ebs_config_runtime.ini")
                logger.setNewLevel(int(config.get("rpc", "log_level")))
                return(1,0)
            else:
                #print "DENIED-----------------"
                conn.utoken = ''
                return (0,Pyro.constants.DENIED_SECURITY)
        except Exception, ex:
            logger.info("acceptIdentification exception: %s", repr(ex))
            conn.utoken = ''
            return (0,Pyro.constants.DENIED_SECURITY)

    def checkIP(self, ipstr, hostsstr):
        #print "checkIP----"
        #user IP
        userIP = IPy.IP(ipstr)
        #allowed hosts
        hosts = hostsstr.split(', ')
        hostOk = False
        for host in hosts:
            #print host
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
                    '''if func.__name__ == "flush":
                        caller.cur.close()
                        caller.db_connection.close()
                        caller.db_connection = pool.connection()
                        caller.db_connection._con._con.set_client_encoding('UTF8')
                        caller.cur = caller.db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)'''
                    #print args
                    #print kwargs
                    
                    kwargs['connection'] = caller.db_connection
                    kwargs['cur'] = caller.cur
                    res =  func(*args, **kwargs)
                    #if func.__name__ == "commit":
                    #    caller.cur.close()
                    #    caller.db_connection.close()
                    #    caller.db_connection = pool.connection()
                    #    caller.db_connection._con._con.set_client_encoding('UTF8')
                    #    caller.cur = caller.db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                    return res
                else:
                    return None
            else:
                return func(*args, **kwargs)
        except Exception, ex:
            if isinstance(ex, psycopg2.OperationalError):
                logger.error("%s : (RPC Server) database connection is down: %s", (args[0].getName(),repr(ex)))
            else:
                #print args[0].getName() + ": exception: " + str(ex)
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
        #self._cddrawer = cdDrawer()



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
            a=SSHClient(host, 22,login, password)
            a.close()
        except Exception, e:
            print e
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
            a=SSHClient(row["ipaddress"], 22,row["login"], row["password"])
            #print configuration
            a.send_command(confstring)
            a.close()
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
                
            elif action=='create' and sended==False:
                cur.execute("UPDATE billservice_account SET ipn_status=%s, ipn_added=%s WHERE id=%s", (False, False, row['account_id']))
            
            if action =='delete'  and sended==True:
                cur.execute("UPDATE billservice_account SET ipn_status=%s, ipn_added=%s WHERE id=%s", (False, False, row['account_id']))
            elif action =='delete'  and sended==False:
                cur.execute("UPDATE billservice_account SET ipn_status=%s, ipn_added=%s WHERE id=%s", (False, False, row['account_id']))

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

        
    @authentconn
    def get_object(self, name, cur=None, connection=None):
        try:
            model = models.__getattribute__(name)()
        except:
            return None


        return model

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
    def pay(self, account, sum, document, cur=None, connection=None):
        
        o = Object()
        o.account_id = account
        o.type_id = "MANUAL_TRANSACTION"
        o.approved = True
        o.description = ""
        o.summ = sum * (-1)
        o.bill = document
        o.created = datetime.datetime.now()
        try:
            sql = o.save("billservice_transaction")
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
        cur.execute(sql)
        #connection.commit()
        del sql
        return

    @authentconn
    def iddelete(self, id, table, cur=None, connection=None):

        cur.execute("DELETE FROM %s where id=%d" % (table, id))
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
        bpplotAdapter.rCursor = listcur
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
        if pickler:
            output = open('data.pkl', 'wb')
            b=time.clock()-a

            pickle.dump(result, output)
            output.close()
            #print "Pickle length=", time.clock()-a
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
        cur.execute("SELECT %s from %s WHERE id=%s ORDER BY id ASC;" % (",".join(fields) or "*", table, id))
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
        result = Object(cur.fetchone())
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
        cur.execute("SELECT id, name, active, get_tariff_type(id) AS ttype FROM billservice_tariff ORDER BY ttype, name;")
        result = map(Object, cur.fetchall())
        return result
    
    
    @authentconn  
    def delete_card(self, id, cur=None, connection=None):
        cur.execute("DELETE FROM billservice_card WHERE sold is Null and id=%s", (id,))
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
        sql = model.save(table)
        #print sql
        cur.execute(sql)
        id = cur.fetchone()['id']
        return id

    @authentconn
    def connection_request(self, username, password, cur=None, connection=None):
        try:
            obj = self.get("SELECT * FROM billservice_systemuser WHERE username=%s",(username,))
            self.commit()
        except Exception, e:
            logger.error('connection request exception: %s', repr(e))
            return False
        #print "connection_____request"
        #print self.getProxy()
        if obj is not None and obj.password==password:
            self.create("UPDATE billservice_systemuser SET last_login=%s WHERE id=%s;" , (datetime.datetime.now(), obj.id,))
            self.commit()
            #Pyro.constants.

            return True
        else:
            return False

    @authentconn
    def test(self, cur=None, connection=None):
        pass

    @authentconn
    def get_allowed_users(self, cur=None, connection=None):
        return allowedUsers()
    
    @authentconn
    def pod(self, session, cur=None, connection=None):
        print "Start POD"
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

def SIGTERM_handler(signum, frame):
    graceful_save()

def graceful_save():
    global threads
    for th in threads:
        if isinstance(th, RPCServer):
            th.daemon.shutdown(disconnect=True)
    pool.close()
    time.sleep(2)
    sys.exit()
    
def main():
    global threads
    threads=[]
    threads.append(RPCServer())
    for th in threads:	
        th.start()
        time.sleep(0.1)
    try:
        signal.signal(signal.SIGTERM, SIGTERM_handler)
    except: logger.lprint('NO SIGTERM!')
    
    #main thread should not exit!
    while True:
        time.sleep(300)
        
if __name__ == "__main__":
    if "-D" not in sys.argv:
        daemonize("/dev/null", "log.txt", "log.txt")
     
    config.read("ebs_config.ini")
    logger = isdlogger.isdlogger(config.get("rpc", "log_type"), loglevel=int(config.get("rpc", "log_level")), ident=config.get("rpc", "log_ident"), filename=config.get("rpc", "log_file")) 
             
    maxUsers = int(config.get("rpc", "max_users"))
    logger.lprint('Ebs RPC start')
    pool = PooledDB(
        mincached=1,
        maxcached=10,
        blocking=True,
        #maxusage=20,
        setsession=["SET statement_timeout = 6000000;"],
        creator=psycopg2,
        dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"),
                                                               config.get("db", "username"),
                                                               config.get("db", "host"),
                                                               config.get("db", "password")))
    
    main()
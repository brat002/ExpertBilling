#-*-coding=utf-8-*-
import sys
from daemonize import daemonize

from auth import Auth
from time import clock
try:
    import mx.DateTime
except:
    print 'cannot import mx'
import os,datetime



import socket
import asyncore

from threading import Thread
import dictionary, packet

from utilites import in_period, create_speed_string
from db import get_account_data_by_username_dhcp,get_default_speed_parameters, get_speed_parameters, get_nas_by_ip, get_account_data_by_username, time_periods_by_tarif_id


#import settings
import psycopg2
import psycopg2.extras
import traceback
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

from DBUtils.PooledDB import PooledDB

w32Import = False
try:
    import win32api,win32process,win32con
    w32Import = True
except:
    pass

import ConfigParser







gigaword = 4294967296
account_timeaccess_cache={}
account_timeaccess_cache_count=0

def log(message):
    global debug_mode
    if debug_mode>0:
        print message
        
def show_packet(packetobject):
    b=''
    for key,value in packetobject.items():
        b+=str(packetobject._DecodeKey(key))+str(packetobject[packetobject._DecodeKey(key)][0])+"\n"
    return b
        
class AsyncUDPServer(asyncore.dispatcher):
    ac_out_buffer_size = 8096*10
    ac_in_buffer_size = 8096*10
    
    def __init__(self, host, port):
        self.outbuf = []

        asyncore.dispatcher.__init__(self)

        self.host = host
        self.port = port
        self.dbconn = None
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind( (host, port) )
        self.set_reuse_addr()

        
    def handle_read_event (self):
        try:
            data, addr = self.socket.recvfrom(4096)
        except:            
            traceback.print_exc()
            return
        self.handle_readfrom(data, addr)

    def handle_readfrom(self,data, address):
        pass

    def writable (self):
        return len(self.outbuf)

    def sendto (self, data, addr):
        self.outbuf.append((data, addr))
        self.initiate_send()

    def initiate_send(self):
        b = self.outbuf
        while len(b):
            data, addr = b[0]
            del b[0]
            try:
                result = self.socket.sendto (data, addr)
                if result != len(data):
                    self.log('Sent packet truncated to %d bytes' % result)
            except socket.error, why:
                if why[0] == EWOULDBLOCK:
                    return
                else:
                    raise socket.error, why

    def handle_error (self, *info):
        traceback.print_exc()
        log('uncaptured python exception, closing channel %s' % `self`)
        self.close()
    
    def handle_close(self):
        self.close()
        
def authNA(packet):
    return packet.ReplyPacket()

def get_accesstype(packetobject):
    """
    Returns access type name by which a user connects to the NAS
    """
    try:
        if packetobject['NAS-Port-Type'][0]=='Virtual':
            return 'PPTP'
        elif packetobject['NAS-Port-Type'][0]=='Ethernet' and packetobject.has_key('Service-Type'):
            return 'PPPOE'
        elif packetobject['NAS-Port-Type'][0]=='Ethernet' and not packetobject.has_key('Service-Type'):
            return 'DHCP'
    except:
        print show_packet(packetobject)
    return
    
class HandleBase(object):


    def auth_NA(self):
        """
        Denides access
        """
        
        self.packetobject.username=None
        self.packetobject.password=None
        # Access denided
        self.packetobject.code=3
        return self.packetobject

    # Main
    def handle(self):
        pass

class HandleNA(HandleBase):

    def __init__(self,  packetobject, dbCur):
        """
        TO-DO: Сделать проверку в методе get_nas_info на тип доступа 
        """
        self.nasip = str(packetobject['NAS-IP-Address'][0])
        self.packetobject = packetobject.CreateReply()
        self.cur = dbCur

    def handle(self):
        row=self.get_nas_info()
        self.cur.close()
        
        if row is not None:
            self.packetobject.secret = str(row[1])
            return "", self.auth_NA()
        
    def get_nas_info(self):
        row = get_nas_by_ip(self.cur, self.nasip)
        return row
        
#auth_class
class HandleAuth(HandleBase):

    def __init__(self,  packetobject, access_type, dbCur):
        self.nasip = str(packetobject['NAS-IP-Address'][0])
        self.packetobject = packetobject
        self.access_type=access_type
        self.secret = ''

        log(show_packet(packetobject))
        

        self.cur = dbCur

    def auth_NA(self):
        """
        Deny access
        """
        self.packetobject.username=None
        self.packetobject.password=None
        self.packetobject.code=3
        return self.secret, self.packetobject
    
    def create_speed(self, tarif_id, speed=''):
        result_params=speed
        if speed=='':
            defaults = get_default_speed_parameters(self.cur, tarif_id)
            speeds = get_speed_parameters(self.cur, tarif_id)
            if defaults is None:
                return "0/0"
            result=[]
            #print speeds

            for speed in speeds:
                if in_period(speed[0],speed[1],speed[2])==True:
                    #print speed
                    i=0
                    for k in xrange(0, len(speed[3:])):
                        s=speed[3+k]
                        #print s
                        if s==0:
                            res=0
                        elif s=='':
                            res=defaults[i]
                        else:
                            res=s
                        #print "res=",res
                        result.append(res)
                        i+=1
                    break
                    
            if speeds==[]:
                result=defaults
            if result==[]:
                return "0/0"
            #print result
            result_params=create_speed_string(result)
            self.speed=result_params
            #print "params=", result_params

        if self.nas_type[:8]==u'mikrotik' and result_params!='':
            self.replypacket.AddAttribute((14988,8),result_params)

    def get_nas_info(self):
        row = get_nas_by_ip(self.cur, self.nasip)
        return row

    def handle(self):
        row=self.get_nas_info()
        if row==None:
            self.cur.close()
            return '',None
        self.nas_id=str(row[0])
        self.nas_type=row[2]
        self.multilink = row[3]
        self.secret = str(row[1])
        self.replypacket=packet.Packet(secret=str(row[1]),dict=dict)

        try:
            station_id=self.packetobject['Calling-Station-Id'][0]
        except:
            station_id = ''

        row = get_account_data_by_username(self.cur, self.packetobject['User-Name'][0], self.access_type, station_id=station_id, multilink = self.multilink, common_vpn = common_vpn)

        if row==None:
            self.cur.close()

            log("Unknown User %s" % self.packetobject['User-Name'][0])
            return self.auth_NA()

        username, password, nas_id, ipaddress, tarif_id, access_type, status, balance_blocked, ballance, disabled_by_limit, speed, tarif_status = row
        #Проверка на то, указан ли сервер доступа
        if int(nas_id)!=int(self.nas_id):
            self.cur.close()
            log("Unallowed NAS for user %s" % self.packetobject['User-Name'][0])
            return self.auth_NA()


        #TimeAccess
        rows = time_periods_by_tarif_id(self.cur, tarif_id)
        allow_dial=False
        for row in rows:
            if in_period(row[0],row[1],row[2])==True:
                allow_dial=True
                break

        log("Authorization user:%s allowed_time:%s User Status:%s Balance:%s Disabled by limit:%s Balance blocked:%s Tarif Active:%s" %( self.packetobject['User-Name'][0], allow_dial, status, ballance, disabled_by_limit, balance_blocked, tarif_status))
        if self.packetobject['User-Name'][0]==username and allow_dial and tarif_status==True:
            self.replypacket.code=2
            self.replypacket.username=str(username) #Нельзя юникод
            self.replypacket.password=str(password) #Нельзя юникод
            self.replypacket.AddAttribute('Service-Type', 2)
            self.replypacket.AddAttribute('Framed-Protocol', 1)
            self.replypacket.AddAttribute('Framed-IP-Address', ipaddress)
            self.create_speed(tarif_id, speed=speed)
            #print "Setting Speed For User" , self.speed
            self.cur.close()
        else:
            self.cur.close()

            return self.auth_NA()
        return self.secret, self.replypacket

#auth_class
class HandleDHCP(HandleBase):

    def __init__(self,  packetobject, dbCur):
        self.nasip = packetobject['NAS-IP-Address'][0]
        self.packetobject = packetobject
        self.secret = ""

        log(show_packet(packetobject))

        self.cur = dbCur

    def auth_NA(self):
        """
        Deny access
        """
        self.packetobject.code=3
        return self.secret, self.packetobject
    
    def get_nas_info(self):
        row = get_nas_by_ip(self.cur, self.nasip)
        return row

            
    def handle(self):
        row=self.get_nas_info()
        if row==None:
            self.cur.close()
            return self.auth_NA()

        self.nas_id=str(row[0])
        self.nas_type=row[2]
        self.secret=str(row[1])
        
        self.replypacket=packet.Packet(secret=self.secret,dict=dict)
        row = get_account_data_by_username_dhcp(self.cur, self.packetobject['User-Name'][0])

        if row==None:
            self.cur.close()
            return self.auth_NA()

    
        nas_id, ipaddress, netmask, mac_address, speed = row

        if int(nas_id)!=int(self.nas_id):
            self.cur.close()
            return self.auth_NA()

        #print 4
        self.replypacket.code=2
        self.replypacket.AddAttribute('Framed-IP-Address', ipaddress)
        self.replypacket.AddAttribute('Framed-IP-Netmask',netmask)
        self.replypacket.AddAttribute('Session-Timeout', session_timeout)
        #self.create_speed(tarif_id, speed=speed)
        self.cur.close()
        return self.secret, self.replypacket

#acct class
class HandleAcct(HandleBase):
    """
    process account information after connection
    """

    def __init__(self, packetobject, nasip, dbCur):
        self.packetobject=packetobject
        self.nasip=packetobject['NAS-IP-Address'][0]
        self.replypacket=packetobject.CreateReply()
        self.access_type=get_accesstype(self.packetobject)
        self.cur = dbCur

    def get_bytes(self):
        if self.packetobject.has_key('Acct-Input-Gigawords') and self.packetobject['Acct-Input-Gigawords'][0]!=0:
            bytes_in=self.packetobject['Acct-Input-Octets'][0]+(self.packetobject['Acct-Input-Gigawords'][0]*gigaword)
        else:
            bytes_in=self.packetobject['Acct-Input-Octets'][0]

        if self.packetobject.has_key('Acct-Output-Gigawords') and self.packetobject['Acct-Output-Gigawords'][0]!=0:
            bytes_out=self.packetobject['Acct-Output-Octets'][0]+(self.packetobject['Acct-Output-Gigawords'][0]*gigaword)
        else:
            bytes_out=self.packetobject['Acct-Output-Octets'][0]
        return (bytes_in, bytes_out)

    def acct_NA(self):
        """
        Deny access
        """

        # Access denided
        self.replypacket.code=3
        return self.replypacket
    
    def handle(self):

        self.cur.execute("""SELECT secret from nas_nas WHERE ipaddress=%s;""", (self.nasip,))
        row = self.cur.fetchone()
        #print 1
        if row==None:
            return None
        
        self.replypacket.secret=str(row[0])
        global account_timeaccess_cache_count
        if self.packetobject['User-Name'][0] not in account_timeaccess_cache or account_timeaccess_cache[self.packetobject['User-Name'][0]][2]%10==0:
            """
            Раз в десять запросов обновлять информацию о аккаунте
            """
            log("Update Timeaccess Cache for %s" % self.packetobject['User-Name'][0])
            self.cur.execute(
            """
            SELECT account.id, tariff.time_access_service_id FROM billservice_account as account
            JOIN billservice_tariff as tariff ON tariff.id=(SELECT tarif_id FROM billservice_accounttarif where account_id=account.id and datetime<now() ORDER BY id DESC LIMIT 1)
            WHERE account.username=%s;
            """, (self.packetobject['User-Name'][0],)
            )
            row=self.cur.fetchone()
            if row==None:
                self.cur.close()
                log("Unkown User or user tarif %s" % self.packetobject['User-Name'][0])
                return self.acct_NA()
            account_id, time_access=row
            account_timeaccess_cache[self.packetobject['User-Name'][0]]=[account_id, time_access,0]
        
        account_id, time_access = account_timeaccess_cache[self.packetobject['User-Name'][0]][0:2]
        account_timeaccess_cache[self.packetobject['User-Name'][0]][2] +=1
        #account_timeaccess_cache_count+=1

        self.replypacket.code=5
        now=datetime.datetime.now()

        #print 3
        if self.packetobject['Acct-Status-Type']==['Start']:
            #Проверяем нет ли такой сессии в базе
            self.cur.execute("""
            SELECT id
            FROM radius_activesession
            WHERE account_id=%s and sessionid=%s and
            caller_id=%s and called_id=%s and nas_id=%s and framed_protocol=%s;
            """, (account_id, self.packetobject['Acct-Session-Id'][0], self.packetobject['Calling-Station-Id'][0],
                   self.packetobject['Called-Station-Id'][0], self.packetobject['NAS-IP-Address'][0],self.access_type,))

            allow_write = self.cur.fetchone()==None

            if time_access and allow_write:

                self.cur.execute(
                """
                INSERT INTO radius_session(
                account_id, sessionid, date_start,
                caller_id, called_id, framed_ip_address, nas_id, framed_protocol, checkouted_by_time, checkouted_by_trafic
                )
                VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s)
                """, (account_id, self.packetobject['Acct-Session-Id'][0], now,
                     self.packetobject['Calling-Station-Id'][0], self.packetobject['Called-Station-Id'][0], self.packetobject['Framed-IP-Address'][0],
                     self.packetobject['NAS-IP-Address'][0], self.access_type, False, False,))

            if allow_write:

                self.cur.execute(
                """
                INSERT INTO radius_activesession(
                account_id, sessionid, date_start,
                caller_id, called_id, framed_ip_address, nas_id, framed_protocol, session_status
                )
                VALUES (%s, %s,%s,%s, %s, %s, %s, %s, 'ACTIVE');
                """, (account_id, self.packetobject['Acct-Session-Id'][0], now,
                     self.packetobject['Calling-Station-Id'][0], self.packetobject['Called-Station-Id'][0], self.packetobject['Framed-IP-Address'][0],
                     self.packetobject['NAS-IP-Address'][0], self.access_type,))

        if self.packetobject['Acct-Status-Type']==['Alive']:
            bytes_in, bytes_out=self.get_bytes()
            if time_access:
                self.cur.execute(
                            """
                            INSERT INTO radius_session(
                            account_id, sessionid, interrim_update,
                            caller_id, called_id, framed_ip_address, nas_id, session_time,
                            bytes_out, bytes_in, framed_protocol, checkouted_by_time, checkouted_by_trafic)
                            VALUES ( %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s);
                            """, (account_id, self.packetobject['Acct-Session-Id'][0],
                                 now, self.packetobject['Calling-Station-Id'][0],
                                 self.packetobject['Called-Station-Id'][0], self.packetobject['Framed-IP-Address'][0],
                                 self.packetobject['NAS-IP-Address'][0],
                                 self.packetobject['Acct-Session-Time'][0],
                                 bytes_in, bytes_out, self.access_type, False, False,)
                            )
            self.cur.execute(
                        """
                        UPDATE radius_activesession
                        SET interrim_update=%s,bytes_out=%s, bytes_in=%s, session_time=%s, session_status='ACTIVE'
                        WHERE sessionid=%s and nas_id=%s;
                        """, (now, bytes_in, bytes_out, self.packetobject['Acct-Session-Time'][0], self.packetobject['Acct-Session-Id'][0], self.packetobject['NAS-IP-Address'][0],)
            )



        if self.packetobject['Acct-Status-Type']==['Stop']:
            bytes_in, bytes_out=self.get_bytes()
            if time_access:
                self.cur.execute(
                """
                INSERT INTO radius_session(
                account_id, sessionid, interrim_update, date_end,
                caller_id, called_id, framed_ip_address, nas_id, session_time,
                bytes_in, bytes_out, framed_protocol, checkouted_by_time, checkouted_by_trafic)
                VALUES ( %s, %s, %s, %s, %s,
                %s, %s, %s, %s,%s, %s, %s, %s, %s);
                """, (account_id, self.packetobject['Acct-Session-Id'][0],
                      now, now, self.packetobject['Calling-Station-Id'][0],
                      self.packetobject['Called-Station-Id'][0], self.packetobject['Framed-IP-Address'][0], 
                      self.packetobject['NAS-IP-Address'][0],
                      self.packetobject['Acct-Session-Time'][0],
                      bytes_in, bytes_out, self.access_type, False, False,)
                )

            self.cur.execute(
               """
               UPDATE radius_activesession
               SET date_end=%s, session_status='ACK'
               WHERE sessionid=%s and nas_id=%s;
               """, (now,self.packetobject['Acct-Session-Id'][0], self.packetobject['NAS-IP-Address'][0],)
               )
            del account_timeaccess_cache[self.packetobject['User-Name'][0]]

        self.cur.connection.commit()

        self.cur.close()
        
        return self.replypacket

class AsyncAuth(AsyncUDPServer):
    def __init__(self, host, port, dbconn):
        self.outbuf = []
        AsyncUDPServer.__init__(self, host, port)
        self.dbconn = dbconn


        

    def handle_readfrom(self,data, address):
        try:

            t = clock()
            returndata=''
            #data=self.request[0] # or recv(bufsize, flags)
            assert len(data)<=4096
            addrport=address
            #print "BEFORE AUTH:%.20f" % (clock()-t)
            packetobject=packet.Packet(dict=dict,packet=data)
            access_type = get_accesstype(packetobject)
            
            if access_type in ['PPTP', 'PPPOE']:
                log("Auth Type %s" % access_type)
    
                coreconnect = HandleAuth(packetobject=packetobject, access_type=access_type, dbCur=self.dbconn.cursor())
                secret, packetfromcore=coreconnect.handle()
                if packetfromcore is None: log("Unknown NAS %s" % str(packetobject['NAS-IP-Address'][0]));return
    
                authobject=Auth(packetobject=packetobject, packetfromcore=packetfromcore, secret=secret, access_type=access_type)
                log("Password check: %s" % authobject.AccessAccept)
                returndata=authobject.ReturnPacket()
                del coreconnect
                del packetfromcore
                del authobject
            elif access_type in ['DHCP'] :
                #-----
                coreconnect = HandleDHCP(packetobject=packetobject, dbCur=self.dbconn.cursor())
                secret, packetfromcore=coreconnect.handle()
                if packetfromcore is None: return
                authobject=Auth(packetobject=packetobject, packetfromcore=packetfromcore, secret = secret, access_type=access_type)
                returndata=authobject.ReturnPacket()
                del coreconnect
                del packetfromcore
                del authobject
            else:
                #-----
                returnpacket = HandleNA(packetobject, self.server.dbconn.cursor()).handle()
                if returnpacket is None: return
                returndata=authNA(returnpacket)
                 
            log("AUTH time:%.8f" % (clock()-t))
            if returndata!="":
                self.sendto(returndata,address)
                del data
                del addrport
                del packetobject
                del access_type
                del returndata
        except:
            print "bad packet"


class AsyncAcc(AsyncUDPServer):
    def __init__(self, host, port, dbconn):
        self.outbuf = []
        AsyncUDPServer.__init__(self, host, port)
        self.dbconn = dbconn

    def handle_readfrom(self,data, address):
        try:
            t = clock()
            assert len(data)<=4096
            addrport=address
            packetobject=packet.AcctPacket(dict=dict,packet=data)
    
            coreconnect = HandleAcct(packetobject=packetobject, nasip=address[0], dbCur=self.dbconn.cursor())
            packetfromcore = coreconnect.handle()
            if packetfromcore is not None: 
                returndat=packetfromcore.ReplyPacket()
                self.socket.sendto(returndat,addrport)
                del returndat
            log("ACC:%.20f" % (clock()-t))
            del packetfromcore
            del coreconnect
        except:
            print "bad acct packet"

                

class Starter(Thread):
        def __init__ (self, address, port, handler):
            self.address=address
            self.port = port
            self.handler=handler
            Thread.__init__(self)

        def run(self):
            dbconn = pool.connection()
            dbconn._con._con.set_isolation_level(0)
            dbconn._con._con.set_client_encoding('UTF8')
            server = self.handler(self.address, self.port, dbconn)


def setpriority(pid=None,priority=1):
    """ Set The Priority of a Windows Process.  Priority is a value between 0-5 where
        2 is normal priority.  Default sets the priority of the current
        python process but can take any valid process ID. """

    

    priorityclasses = [win32process.IDLE_PRIORITY_CLASS,
                       win32process.BELOW_NORMAL_PRIORITY_CLASS,
                       win32process.NORMAL_PRIORITY_CLASS,
                       win32process.ABOVE_NORMAL_PRIORITY_CLASS,
                       win32process.HIGH_PRIORITY_CLASS,
                       win32process.REALTIME_PRIORITY_CLASS]
    if pid == None:
        pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, priorityclasses[priority])

def main():


    
    server_auth = Starter("0.0.0.0", 1812, AsyncAuth)
    server_auth.start()
    

    server_acct = Starter("0.0.0.0", 1813, AsyncAcc)
    server_acct.start()
    
    while 1: 
        asyncore.poll(0.01)

import socket
if socket.gethostname() not in ['dolphinik','sserv.net','sasha', 'kenny','billing','medusa', 'Billing.NemirovOnline', 'iserver']:
    import sys
    print "Licension key error. Exit from application."
    sys.exit(1)

if __name__ == "__main__":
    if "-D" not in sys.argv:
        daemonize("/dev/null", "log.txt", "log.txt")
    config = ConfigParser.ConfigParser()
    if os.name=='nt' and w32Import:
        setpriority(priority=4)
    config.read("ebs_config.ini")        
    dict=dictionary.Dictionary("dicts/dictionary","dicts/dictionary.microsoft", 'dicts/dictionary.mikrotik')
    
    pool = PooledDB(
        mincached=3,
        maxcached=10,
        blocking=True,
        creator=psycopg2,
        dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"),
                                                               config.get("db", "username"),
                                                               config.get("db", "host"),
                                                               config.get("db", "password"))
    )


    try:
        common_vpn = config.get("radius", "common_vpn")
    except Exception, e:
        common_vpn=False

    try:
        debug_mode = int(config.get("radius", "debug_mode"))
    except Exception, e:
        debug_mode=0

    try:
        session_timeout = int(config.get("dhcp", "session_timeout"))
    except Exception, e:
        session_timeout=86400
    main()

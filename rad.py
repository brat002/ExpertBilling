#-*-coding=utf-8-*-

from auth import Auth
from time import clock
try:
    import mx.DateTime
except:
    print 'cannot import mx'
import os,datetime
from SocketServer import ThreadingUDPServer
from SocketServer import DatagramRequestHandler
from threading import Thread
import dictionary, packet

    
from utilites import in_period, create_speed_string
from db import get_account_data_by_username_dhcp,get_default_speed_parameters, get_speed_parameters, get_nas_by_ip, get_account_data_by_username, time_periods_by_tarif_id


#import settings
import psycopg2
from DBUtils.PooledDB import PooledDB

try:
    import win32api,win32process,win32con
except:
    pass

import ConfigParser





from logger import redirect_std

#redirect_std("rad", redirect=config.get("stdout", "redirect"))

global numauth, numacct

numauth=0
numacct=0
gigaword = 4294967296

def authNA(packet):
    return packet.ReplyPacket()

def get_accesstype(packetobject):
    """
    Returns access type name by which a user connects to the NAS
    """
    if packetobject['NAS-Port-Type'][0]=='Virtual':
        return 'PPTP'
    elif packetobject['NAS-Port-Type'][0]=='Ethernet' and packetobject.has_key('Service-Type'):
        return 'PPPOE'
    elif packetobject['NAS-Port-Type'][0]=='Ethernet' and not packetobject.has_key('Service-Type'):
        return 'DHCP'
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

    def __init__(self,  packetobject):
        """
        TO-DO: Сделать проверку в методе get_nas_info на тип доступа 
        """
        self.nasip = str(packetobject['NAS-IP-Address'][0])
        self.packetobject = packetobject.CreateReply()


        
        self.connection = pool.connection()
        self.connection._con._con.set_isolation_level(0)
        self.cur = self.connection.cursor()


    def handle(self):
        row=self.get_nas_info()
        self.cur.close()
        self.connection.close()
        
        if row is not None:
            self.packetobject.secret = str(row[1])
            return self.auth_NA()
        
    def get_nas_info(self):
        row = get_nas_by_ip(self.cur, self.nasip)
        return row
        
#auth_class
class HandleAuth(HandleBase):

    def __init__(self,  packetobject, access_type):
        self.nasip = str(packetobject['NAS-IP-Address'][0])
        self.packetobject = packetobject
        self.access_type=access_type
        self.secret = ''

        #for key,value in packetobject.items():
        #    print packetobject._DecodeKey(key),packetobject[packetobject._DecodeKey(key)][0]
        
        self.connection = pool.connection()
        self.connection._con._con.set_isolation_level(0)
        self.cur = self.connection.cursor()
    
    def auth_NA(self):
        """
        Denides access
        """
        self.packetobject.username=None
        self.packetobject.password=None
        # Access denided
        self.packetobject.code=3
        return self.secret, self.packetobject
    
    def create_speed(self, tarif_id, speed=''):
        result_params=speed
        if speed=='':
            defaults = get_default_speed_parameters(self.cur, tarif_id)
            speeds = get_speed_parameters(self.cur, tarif_id)
            if defaults is None:
                return None
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
            #print "params=", result_params

        if self.nas_type[:8]==u'mikrotik' and result_params!='':
            self.replypacket.AddAttribute((14988,8),result_params)

    def get_nas_info(self):
        row = get_nas_by_ip(self.cur, self.nasip)
        return row

    def handle(self):
        row=self.get_nas_info()
        #print row
        if row==None:
            self.cur.close()
            self.connection.close()
            return None

        self.nas_id=str(row[0])
        self.nas_type=row[2]
        self.multilink = row[3]
        self.secret = str(row[1])
        #print str(row[1])
        self.replypacket=packet.Packet(secret=str(row[1]),dict=dict)
        
        try:
            station_id=self.packetobject['Calling-Station-Id'][0]
        except:
            station_id = ''
        #print self.replypacket.secret
        row = get_account_data_by_username(self.cur, self.packetobject['User-Name'][0], self.access_type, station_id=station_id, multilink = self.multilink, common_vpn = common_vpn)
        #print 1, row
        
        if row==None:
            self.cur.close()
            self.connection.close()
            return self.auth_NA()
        
        #print 2
        username, password, nas_id, ipaddress, tarif_id, access_type, status, balance_blocked, ballance, disabled_by_limit, speed, tarif_status = row
        #Проверка на то, указан ли сервер доступа
        if int(nas_id)!=int(self.nas_id):
           self.cur.close()
           self.connection.close()
           #print 2
           
           return self.auth_NA()


        #TimeAccess
        rows = time_periods_by_tarif_id(self.cur, tarif_id)
        allow_dial=False
        for row in rows:
            #print row[0],row[1],u"%s" % row[2]
            if in_period(row[0],row[1],row[2])==True:
                allow_dial=True
                #print 3
                break
        print 3

        if self.packetobject['User-Name'][0]==username and allow_dial and status and  ballance>0 and not disabled_by_limit and not balance_blocked and tarif_status==True:
           #print 4
           self.replypacket.code=2
           self.replypacket.username=str(username) #Нельзя юникод
           self.replypacket.password=str(password) #Нельзя юникод
           self.replypacket.AddAttribute('Service-Type', 2)
           self.replypacket.AddAttribute('Framed-Protocol', 1)
           self.replypacket.AddAttribute('Framed-IP-Address', ipaddress)
           #self.replypacket.AddAttribute('Framed-Routing', 0)
           self.create_speed(tarif_id, speed=speed)
           self.cur.close()
           self.connection.close()
        else:
             self.cur.close()
             self.connection.close()
             #print 5
             return self.auth_NA()
        #print 5
        #data_to_send=replypacket.ReplyPacket()
        return self.secret, self.replypacket

#auth_class
class HandleDHCP(HandleBase):

    def __init__(self,  packetobject):
        self.nasip = packetobject['NAS-IP-Address'][0]
        self.packetobject = packetobject

        #for key,value in packetobject.items():
        #    print packetobject._DecodeKey(key),packetobject[packetobject._DecodeKey(key)][0]
        
        #self.access_type=get_accesstype(self.packetobject)
        
        self.connection = pool.connection()
        self.connection._con._con.set_isolation_level(0)
        self.cur = self.connection.cursor()


        row=self.get_nas_info()

        if row==None:
            self.cur.close()
            self.connection.close()
            return self.auth_NA()

        self.nas_id=str(row[0])
        self.nas_type=row[2]
        self.replypacket=packet.Packet(secret=str(row[1]),dict=dict)


    def get_nas_info(self):
        row = get_nas_by_ip(self.cur, self.nasip)
        return row

    def create_speed(self, tarif_id, speed=''):
        result_params=speed
        if speed=='':
            defaults = get_default_speed_parameters(self.cur, tarif_id)
            speeds = get_speed_parameters(self.cur, tarif_id)
            if defaults is None:
                return None
            result=[]
            i=0
            for speed in speeds:
                #print speed[0],speed[1],speed[2]
                if in_period(speed[0],speed[1],speed[2])==True:
                    for s in speed[3:]:
                        if s==0:
                            res=0
                        elif s=='':
                            res=defaults[i]
                        else:
                            res=s
                        result.append(res)
                        i+=1
            if speeds==[]:
                result=defaults
    
            result_params=create_speed_string(result)
            #print "params=", result_params

        if self.nas_type[:8]==u'mikrotik' and result_params!='':
            self.replypacket.AddAttribute((14988,8),result_params)
            
    def handle(self):

        row = get_account_data_by_username_dhcp(self.cur, self.packetobject['User-Name'][0])

        if row==None:
            self.cur.close()
            #print 1
            self.cur.close()
            self.connection.close()
            return self.auth_NA()

    
        nas_id, ipaddress, netmask, mac_address, tarif_id, speed = row

        if int(nas_id)!=int(self.nas_id):
           self.cur.close()
           self.connection.close()
           #print 2
           return self.auth_NA()

        #print 4
        self.replypacket.code=2
        self.replypacket.AddAttribute('Framed-IP-Address', ipaddress)
        #self.replypacket.AddAttribute('Framed-Routing', 0)
        self.replypacket.AddAttribute('Framed-IP-Netmask',netmask)
        self.replypacket.AddAttribute('Session-Timeout', 60*60*24)
        #self.create_speed(tarif_id, speed=speed)
        self.cur.close()
        self.connection.close()
        return self.replypacket

#acct class
class HandleAcct(HandleBase):
    """
    process account information after connection
    """

    def __init__(self, packetobject, nasip):
        self.packetobject=packetobject
        self.nasip=packetobject['NAS-IP-Address'][0]
        self.replypacket=packetobject.CreateReply()
        self.access_type=get_accesstype(self.packetobject)
        self.connection = pool.connection()
        self.connection._con._con.set_isolation_level(0)
        self.cur = self.connection.cursor()

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

        self.cur.execute("""SELECT secret from nas_nas WHERE ipaddress='%s';""" % self.nasip)
        row = self.cur.fetchone()
        #print 1
        if row==None:
            return None
        
        self.replypacket.secret=str(row[0])
        self.cur.execute(
        """
        SELECT account.id, tariff.time_access_service_id FROM billservice_account as account
        JOIN billservice_tariff as tariff ON tariff.id=(SELECT tarif_id FROM billservice_accounttarif where account_id=account.id and datetime<now() ORDER BY id DESC LIMIT 1)
        WHERE account.username='%s';
        """ % self.packetobject['User-Name'][0]
        )
        row=self.cur.fetchone()
        if row==None:
            self.cur.close()
            self.connection.close()
            return self.acct_NA()

        account_id, time_access=row


        self.replypacket.code=5
        now=datetime.datetime.now()

        #print 3
        if self.packetobject['Acct-Status-Type']==['Start']:
            #Проверяем нет ли такой сессии в базе
            self.cur.execute("""
            SELECT id
            FROM radius_activesession
            WHERE account_id=%s and sessionid='%s' and
            caller_id='%s' and called_id='%s' and nas_id='%s' and framed_protocol='%s';
            """ % (account_id, self.packetobject['Acct-Session-Id'][0], self.packetobject['Calling-Station-Id'][0],
                   self.packetobject['Called-Station-Id'][0], self.packetobject['NAS-IP-Address'][0],self.access_type))
            #print 31
            allow_write = self.cur.fetchone()==None
            #allow_write=True
            #print 32
            #allow_write=True
            if time_access and allow_write:
                #print 33
                self.cur.execute(
                """
                INSERT INTO radius_session(
                account_id, sessionid, date_start,
                caller_id, called_id, framed_ip_address, nas_id, framed_protocol, checkouted_by_time, checkouted_by_trafic
                )
                VALUES (%s, '%s','%s', '%s', '%s', '%s', '%s', '%s', %s, %s)
                """ % (account_id, self.packetobject['Acct-Session-Id'][0], now,
                     self.packetobject['Calling-Station-Id'][0], self.packetobject['Called-Station-Id'][0], self.packetobject['Framed-IP-Address'][0],
                     self.packetobject['NAS-IP-Address'][0], self.access_type, False, False))
            #print 34
            if allow_write:
                #print 35
                self.cur.execute(
                """
                INSERT INTO radius_activesession(
                account_id, sessionid, date_start,
                caller_id, called_id, framed_ip_address, nas_id, framed_protocol, session_status
                )
                VALUES (%s, '%s','%s','%s', '%s', '%s', '%s', '%s', 'ACTIVE');
                """ % (account_id, self.packetobject['Acct-Session-Id'][0], now,
                     self.packetobject['Calling-Station-Id'][0], self.packetobject['Called-Station-Id'][0], self.packetobject['Framed-IP-Address'][0],
                     self.packetobject['NAS-IP-Address'][0], self.access_type))
                #print 36
                #print 'start', True
            #self.connection.commit()
            #print 37
        #print 4
        if self.packetobject['Acct-Status-Type']==['Alive']:
            bytes_in, bytes_out=self.get_bytes()
            if time_access:
                self.cur.execute(
                            """
                            INSERT INTO radius_session(
                            account_id, sessionid, interrim_update,
                            caller_id, called_id, framed_ip_address, nas_id, session_time,
                            bytes_out, bytes_in, framed_protocol, checkouted_by_time, checkouted_by_trafic)
                            VALUES ( %s, '%s', '%s', '%s', '%s', '%s', '%s',
                            '%s', '%s', '%s', '%s', %s, %s);
                            """ % (account_id, self.packetobject['Acct-Session-Id'][0],
                                 now, self.packetobject['Calling-Station-Id'][0],
                                 self.packetobject['Called-Station-Id'][0], self.packetobject['Framed-IP-Address'][0],
                                 self.packetobject['NAS-IP-Address'][0],
                                 self.packetobject['Acct-Session-Time'][0],
                                 bytes_in, bytes_out, self.access_type, False, False)
                            )
            self.cur.execute(
                        """
                        UPDATE radius_activesession
                        SET interrim_update='%s',bytes_out='%s', bytes_in='%s', session_time='%s', session_status='ACTIVE'
                        WHERE sessionid='%s' and nas_id='%s';
                        """ % (now, bytes_in, bytes_out, self.packetobject['Acct-Session-Time'][0], self.packetobject['Acct-Session-Id'][0], self.packetobject['NAS-IP-Address'][0])
            )

            #self.connection.commit()

        if self.packetobject['Acct-Status-Type']==['Stop']:
            bytes_in, bytes_out=self.get_bytes()
            if time_access:
                self.cur.execute(
                """
                INSERT INTO radius_session(
                account_id, sessionid, interrim_update, date_end,
                caller_id, called_id, framed_ip_address, nas_id, session_time,
                bytes_in, bytes_out, framed_protocol, checkouted_by_time, checkouted_by_trafic)
                VALUES ( %s, '%s', '%s', '%s', '%s',
                '%s', '%s', '%s', '%s','%s', '%s', '%s', %s, %s);
                """ % (account_id, self.packetobject['Acct-Session-Id'][0],
                      now, now, self.packetobject['Calling-Station-Id'][0],
                      self.packetobject['Called-Station-Id'][0], self.packetobject['Framed-IP-Address'][0], 
                      self.packetobject['NAS-IP-Address'][0],
                      self.packetobject['Acct-Session-Time'][0],
                      bytes_in, bytes_out, self.access_type, False, False)
                )

            self.cur.execute(
               """
               UPDATE radius_activesession
               SET date_end='%s', session_status='ACK'
               WHERE sessionid='%s' and nas_id='%s';
               """ % (now,self.packetobject['Acct-Session-Id'][0], self.packetobject['NAS-IP-Address'][0])
               )
            #self.connection.commit()
        #print "acct end"
        self.connection.commit()
        print 5
        self.connection.close()
        self.cur.close()
        
        #data_to_send=replypacket.ReplyPacket()
        return self.replypacket


#radius

class BaseAuth(DatagramRequestHandler):
    def handle(self):
        pass


class RadiusAuth(BaseAuth):

      def handle(self):
        global numauth
        if numauth>=50:
            print "PREVENTING DoS"
            
            return
        
        numauth+=1
        t = clock()
        returndata=''
        data=self.request[0] # or recv(bufsize, flags)
        assert len(data)<=4096
        addrport=self.client_address
        #print addrport
        #print 1
        packetobject=packet.Packet(dict=dict,packet=data)
        access_type = get_accesstype(packetobject)
        if access_type in ['PPTP', 'PPPOE']:
            coreconnect = HandleAuth(packetobject=packetobject, access_type=access_type)
            secret, packetfromcore=coreconnect.handle()
            if packetfromcore is None: numauth-=1; return
            authobject=Auth(packetobject=packetobject, packetfromcore=packetfromcore, secret=secret)
            returndata=authobject.ReturnPacket()
            del coreconnect
            del packetfromcore
            del authobject
        elif access_type in ['DHCP'] :
            coreconnect = HandleDHCP(packetobject=packetobject)
            packetfromcore=coreconnect.handle()
            if packetfromcore is None: numauth-=1; return
            packetobject.secret=packetfromcore.secret
            authobject=Auth(packetobject=packetobject, packetfromcore=packetfromcore)
            returndata=authobject.ReturnPacket()
            del coreconnect
            del packetfromcore
            del authobject
        else:
            returnpacket = HandleNA(packetobject).handle()
            if returnpacket is None:numauth-=1; return
            
            returndata=authNA(returnpacket)
            
        #print returndata    
        if returndata!="":
            self.socket.sendto(returndata,addrport)
            #print numauth
            
            del data
            del addrport
            del packetobject
            del access_type
            del returndata
        numauth-=1
        #print "AUTH:%.20f" % (clock()-t)

class RadiusAcct(BaseAuth):

      def handle(self):
        global numacct
        if numacct>=100:
            return "PREVENTING ACCT DoS"
        numacct+=1
        t = clock()
        data=self.request[0] # or recv(bufsize, flags)
        assert len(data)<=4096
        addrport=self.client_address
        packetobject=packet.AcctPacket(dict=dict,packet=data)

        coreconnect = HandleAcct(packetobject=packetobject, nasip=self.client_address[0])
        packetfromcore = coreconnect.handle()
        if packetfromcore is not None: 
            returndat=packetfromcore.ReplyPacket()
            self.socket.sendto(returndat,addrport)
            del returndat
        #print "ACC:%.20f" % (clock()-t)
        #del coreconnect
        #print numacct
        numacct-=1
        del packetfromcore
        del coreconnect
        



class Starter(Thread):
        def __init__ (self, address, handler):
            self.address=address
            self.handler=handler
            Thread.__init__(self)

        def run(self):
            server = ThreadingUDPServer(self.address, self.handler)
            server.allow_reuse_address = True
            server.serve_forever()

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



    
    server_auth = Starter(("0.0.0.0", 1812), RadiusAuth)
    server_auth.start()

    server_acct = Starter(("0.0.0.0", 1813), RadiusAcct)
    server_acct.start()

import socket
if socket.gethostname() not in ['dolphinik','sserv.net','sasha', 'kail','billing','medusa', 'Billing.NemirovOnline']:
    import sys
    print "Licension key error. Exit from application."
    sys.exit(1)

if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    if os.name=='nt':
        setpriority(priority=4)
        config.read("ebs_config.ini")
    else:
        os.chdir("/opt/ebs/data")
        config.read("/opt/ebs/data/ebs_config.ini")
        
    dict=dictionary.Dictionary("dicts/dictionary","dicts/dictionary.microsoft", 'dicts/dictionary.mikrotik')
    
    pool = PooledDB(
        mincached=3,
        maxcached=10,
        blocking=True,
        creator=psycopg2,
    #    setsession=['SET AUTOCOMMIT = 1'],
        dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"),
                                                               config.get("db", "username"),
                                                               config.get("db", "host"),
                                                               config.get("db", "password"))
    )


    try:
        common_vpn = config.get("radius", "common_vpn")
        #print "from config", common_vpn
    except Exception, e:
        #print e
        common_vpn=False
    
    main()

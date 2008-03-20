#-*-coding=utf-8-*-

from auth import Auth
from time import clock
from threading import Thread

import os,datetime
from SocketServer import ThreadingUDPServer
from SocketServer import DatagramRequestHandler
from threading import Thread
import dictionary, packet

from utilites import in_period
from db import get_nas_by_ip, get_account_data_by_username, get_nas_id_by_tarif_id, time_periods_by_tarif_id


import settings
import psycopg2
from DBUtils.PooledDB import PooledDB

class HandleBase(object):
    
    def get_accesstype(self):
        """
        Returns access type name by which a user connects to the NAS
        """
        if self.packetobject['NAS-Port-Type'][0]=='Virtual':
            return 'PPTP'
        elif self.packetobject['NAS-Port-Type'][0]=='Ethernet':
            return 'PPPOE'
        return     
    
    def auth_NA(self):
        """
        Denides access
        """
        self.replypacket.username=None
        self.replypacket.password=None
        # Access denided
        self.replypacket.code=3
        return self.replypacket
    
    # Main
    def handle(self):
        pass

#auth_class
class HandleAuth(HandleBase):
    
    def __init__(self, nasip, packetobject):
        self.nasip = nasip
        self.packetobject = packetobject 
        self.replypacket=packet.Packet(secret='None',dict=dict)
        self.access_type=self.get_accesstype()
        
        
    def handle(self):
        db_connection = pool.connection()
        cur = db_connection.cursor()
      
        row = get_nas_by_ip(cur, self.nasip).fetchone()
        if row==None:
            return self.auth_NA()

        nas_id=str(row[0])
        secret=str(row[1])

        self.replypacket.secret = secret
        row = get_account_data_by_username(cur, self.packetobject['User-Name'][0]).fetchone()
        if row==None:
            return self.auth_NA()

        username, password, ipaddress, tarif_id, status, ballance, disabled_by_limit = row

        row=get_nas_id_by_tarif_id(cur, tarif_id).fetchone()
        if row==None:
            return self.auth_NA()

        if int(row[0])!=int(nas_id) or row[1]!=self.access_type:
           return self.auth_NA()

        #TimeAccess 
        rows = time_periods_by_tarif_id(cur, tarif_id).fetchall()
        for row in rows:
            if in_period(row[2],row[3],row[4])==False:
                return self.auth_NA()
        #for key,value in packetobject.items():
        #    print packetobject._DecodeKey(key),packetobject[key][0]


        cur.close()
        if self.packetobject['User-Name'][0]==username and status=='Enabled' and  ballance>0 and not disabled_by_limit:
           self.replypacket.code=2
           self.replypacket.username=str(username) #Нельзя юникод
           self.replypacket.password=str(password) #Нельзя юникод
           self.replypacket.AddAttribute('Service-Type', 2)
           self.replypacket.AddAttribute('Framed-Protocol', 1)
           self.replypacket.AddAttribute('Framed-IP-Address', ipaddress)
           self.replypacket.AddAttribute('Framed-Routing', 0)
           #replypacket.AddAttribute((14988,8),'128k')

        else:
             return self.auth_NA()

        #data_to_send=replypacket.ReplyPacket()
        return self.replypacket


#acct class
class HandleAcct(HandleBase):
    """
    process account information after connection
    """
    
    def __init__(self, packetobject, nasip):
        self.packetobject=packetobject
        self.nasip=nasip
        self.replypacket=packetobject.CreateReply()
        self.access_type=self.get_accesstype()
        
   
    def get_bytes(self):
        if self.packetobject.has_key('Acct-Input-Gigawords') and self.packetobject['Acct-Input-Gigawords'][0]!=0:
            bytes_in=self.packetobject['Acct-Input-Octets'][0]*self.packetobject['Acct-Input-Gigawords'][0]
        else:
            bytes_in=self.packetobject['Acct-Input-Octets'][0]
            
        if self.packetobject.has_key('Acct-Output-Gigawords') and self.packetobject['Acct-Output-Gigawords'][0]!=0:
            bytes_out=self.packetobject['Acct-Output-Octets'][0]*self.packetobject['Acct-Output-Gigawords'][0]
        else:
            bytes_out=self.packetobject['Acct-Output-Octets'][0]
        return (bytes_in, bytes_out)
    
    def handle(self):
        db_connection = pool.connection()
        cur = db_connection.cursor()
        cur.execute("""SELECT secret from nas_nas WHERE ipaddress='%s'""" % self.nasip)
        rows = cur.fetchone()
        if rows==None:
            return self.acct_NA(self.replypacket)
        #Проверяем знаем ли мы такого пользователя
        #for key,value in packetobject.items():
        #    print packetobject._DecodeKey(key),packetobject[packetobject._DecodeKey(key)][0]
        cur.execute(
        """
        SELECT id FROM billservice_account WHERE username='%s';
        """ % self.packetobject['User-Name'][0]
        )
        row=cur.fetchone()
        if row==None:
            return self.acct_NA(self.replypacket)

        account_id=row[0]

        secret=str(rows[0])
        self.replypacket.secret=str(secret)
        self.replypacket.code=5
        now=datetime.datetime.now()

               
        if self.packetobject['Acct-Status-Type']==['Start']:

            cur.execute(
            """
            INSERT INTO radius_session(
            account_id, sessionid, date_start,
            caller_id, called_id, nas_id, framed_protocol, checkouted_by_time, checkouted_by_trafic
            )
            VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s);
            """, (account_id, self.packetobject['Acct-Session-Id'][0], now, 
                 self.packetobject['Calling-Station-Id'][0], self.packetobject['Called-Station-Id'][0], 
                 self.packetobject['NAS-IP-Address'][0], self.access_type, False, False))

            cur.execute(
            """
            INSERT INTO radius_activesession(
            account_id, sessionid, date_start,
            caller_id, called_id, nas_id, framed_protocol, session_status
            )
            VALUES (%s, %s,%s, %s, %s, %s, %s, 'ACTIVE');
            """, (account_id, self.packetobject['Acct-Session-Id'][0], now, 
                 self.packetobject['Calling-Station-Id'][0], self.packetobject['Called-Station-Id'][0], 
                 self.packetobject['NAS-IP-Address'][0], self.access_type))

            db_connection.commit()


        if self.packetobject['Acct-Status-Type']==['Alive']:
            bytes_in, bytes_out=self.get_bytes()
            cur.execute(
            """
            INSERT INTO radius_session(
            account_id, sessionid, interrim_update,
            caller_id, called_id, nas_id, session_time,
            bytes_out, bytes_in, framed_protocol, checkouted_by_time, checkouted_by_trafic)
            VALUES ( %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s);
            """, (account_id, self.packetobject['Acct-Session-Id'][0],
                 now, self.packetobject['Calling-Station-Id'][0],
                 self.packetobject['Called-Station-Id'][0], self.packetobject['NAS-IP-Address'][0],
                 self.packetobject['Acct-Session-Time'][0],
                 bytes_in, bytes_out, self.access_type, False, False)
            )
            cur.execute(
            """
            UPDATE radius_activesession
            SET interrim_update='%s',bytes_out='%s', bytes_in='%s', session_time='%s'
            WHERE account_id='%s' and sessionid='%s' and nas_id='%s';
            """ % (now, self.packetobject['Acct-Input-Octets'][0], self.packetobject['Acct-Output-Octets'][0], self.packetobject['Acct-Session-Time'][0], account_id, self.packetobject['Acct-Session-Id'][0], self.packetobject['NAS-IP-Address'][0])
            )
            db_connection.commit()

        if self.packetobject['Acct-Status-Type']==['Stop']:
            bytes_in, bytes_out=self.get_bytes()
            cur.execute(
            """
            INSERT INTO radius_session(
            account_id, sessionid, interrim_update, date_end,
            caller_id, called_id, nas_id, session_time,
            bytes_in, bytes_out, framed_protocol, checkouted_by_time, checkouted_by_trafic)
            VALUES ( %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s);
            """, (account_id, self.packetobject['Acct-Session-Id'][0],
                  now, now, self.packetobject['Calling-Station-Id'][0],
                  self.packetobject['Called-Station-Id'][0], self.packetobject['NAS-IP-Address'][0],
                  self.packetobject['Acct-Session-Time'][0],
                  bytes_in, bytes_out, self.access_type, False, False)
            )

            cur.execute(
               """
               UPDATE radius_activesession
               SET date_end='%s', session_status='ACK'
               WHERE account_id='%s' and sessionid='%s' and nas_id='%s';
               """ % (now,account_id, self.packetobject['Acct-Session-Id'][0], self.packetobject['NAS-IP-Address'][0])
               )
            db_connection.commit()
        cur.close()

        #data_to_send=replypacket.ReplyPacket()
        return self.replypacket


#radius

class BaseAuth(DatagramRequestHandler):
    def handle(self):
        pass


class RadiusAuth(BaseAuth):
      
      def handle(self):
        t = clock()
        data=self.request[0] # or recv(bufsize, flags)
        assert len(data)>=4096
        addrport=self.client_address
        packetobject=packet.Packet(dict=dict,packet=data)
        coreconnect = HandleAuth(nasip=self.client_address[0], packetobject=packetobject)
        packetfromcore=coreconnect.handle()
        
        #Обавляем Secret
        packetobject.secret=packetfromcore.secret
        authobject=Auth(packetobject=packetobject, packetfromcore=packetfromcore)
        returndata=authobject.ReturnPacket()
        self.socket.sendto(returndata,addrport)
        del coreconnect
        del packetfromcore
        del packetobject
        print "AUTH:%.20f" % (clock()-t)

class RadiusAcct(BaseAuth):
      
      def handle(self):
        t = clock()
        data=self.request[0] # or recv(bufsize, flags)
        assert len(data)>=4096
        addrport=self.client_address
        packetobject=packet.AcctPacket(dict=dict,packet=data)
        
        coreconnect = HandleAcct(packetobject=packetobject, nasip=self.client_address[0])
        
        packetfromcore = coreconnect.handle()
        
        #replyobj=packet.AcctPacket(id=requestpacket.id, code=packetfromcore.code, secret=packetfromcore.secret, authenticator=requestpacket.authenticator, dict=dict)
        returndat=packetfromcore.ReplyPacket()
        self.socket.sendto(returndat,addrport)
        print "ACC:%.20f" % (clock()-t)
        del coreconnect
        del packetfromcore



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
        
    import win32api,win32process,win32con
    
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
    
if __name__ == "__main__":
    
    pool = PooledDB(
        mincached=3,
        maxcached=60,
        blocking=True,
        creator=psycopg2,
        dsn="dbname='%s' user='%s' host='%s' password='%s'" % (settings.DATABASE_NAME,
                                                               settings.DATABASE_USER,
                                                               settings.DATABASE_HOST,
                                                               settings.DATABASE_PASSWORD)
    )

    
    if os.name=='nt':
        setpriority(priority=4)
        
    dict=dictionary.Dictionary("dicts/dictionary","dicts/dictionary.microsoft", 'dicts/dictionary.mikrotik')
    server_auth = Starter(("0.0.0.0", 1812), RadiusAuth)
    server_auth.start()

    server_acct = Starter(("0.0.0.0", 1813), RadiusAcct)
    server_acct.start()
    
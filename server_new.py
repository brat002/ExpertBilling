#-*-coding=utf-8-*-
from log import simple_log

from auth import Auth
from time import clock
from threading import Thread

import os,datetime
from SocketServer import ThreadingUDPServer
from SocketServer import DatagramRequestHandler
from threading import Thread
import dictionary, packet

from utilites import in_period, create_speed_string, DAE
from db import get_default_speed_parameters, get_speed_parameters, get_nas_by_ip, get_account_data_by_username, time_periods_by_tarif_id


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
        elif self.packetobject['NAS-Port-Type'][0]=='Ethernet' and self.packetobject.has_key('Service-Type'):
            return 'PPPOE'
        elif self.packetobject['NAS-Port-Type'][0]=='Ethernet' and not self.packetobject.has_key('Service-Type'):
            return 'DHCP'
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

    def __init__(self,  packetobject):
        self.nasip = packetobject['NAS-IP-Address'][0]
        self.packetobject = packetobject

        self.access_type=self.get_accesstype()
        self.connection = pool.connection()
        self.cur = self.connection.cursor()


        row=self.get_nas_info()

        if row==None:
            self.cur.close()
            return self.auth_NA()

        self.nas_id=str(row[0])
        self.nas_type=row[2]
        self.replypacket=packet.Packet(secret=str(row[1]),dict=dict)


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
                print speed[0],speed[1],speed[2]
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
            print "params=", result_params

        if self.nas_type[:8]==u'mikrotik' and result_params!='':
            self.replypacket.AddAttribute((14988,8),result_params)

    def get_nas_info(self):
        row = get_nas_by_ip(self.cur, self.nasip)
        return row

    def handle(self):
        #TO-DO: Добавить проверку на balance_blocked

        #for key,value in self.packetobject.items():
        #    print self.packetobject._DecodeKey(key),self.packetobject[key][0]

        #simple_log(packet=self.packetobject)
        if self.get_accesstype() in ('PPTP', 'PPPOE'):
            row = get_account_data_by_username(self.cur, self.packetobject['User-Name'][0])

            if row==None:
                self.cur.close()
                print 1
                return self.auth_NA()

            username, password, nas_id, ipaddress, tarif_id, access_type, status, ballance, disabled_by_limit, speed = row
            #Проверка на то, указан ли сервер доступа
            #row=get_nas_id_by_tarif_id(self.cur, tarif_id)
            #if row==None:
            #    self.cur.close()
            #    self.connection.close()
            #    return self.auth_NA() 
            if int(nas_id)!=int(self.nas_id) or access_type!=self.access_type:
               self.cur.close()
               self.connection.close()
               print 2
               return self.auth_NA()


            #TimeAccess
            rows = time_periods_by_tarif_id(self.cur, tarif_id)
            allow_dial=False
            for row in rows:
                #print row[0],row[1],u"%s" % row[2]
                if in_period(row[0],row[1],row[2])==True:
                    allow_dial=True
                    print 3
                    break


            if self.packetobject['User-Name'][0]==username and allow_dial and status and  ballance>0 and not disabled_by_limit:
               print 4
               self.replypacket.code=2
               self.replypacket.username=str(username) #Нельзя юникод
               self.replypacket.password=str(password) #Нельзя юникод
               self.replypacket.AddAttribute('Service-Type', 2)
               self.replypacket.AddAttribute('Framed-Protocol', 1)
               self.replypacket.AddAttribute('Framed-IP-Address', ipaddress)
               self.replypacket.AddAttribute('Framed-Routing', 0)
               self.create_speed(tarif_id, speed=speed)
               self.cur.close()
               self.connection.close()
            else:
                 self.cur.close()
                 self.connection.close()
                 print 5
                 return self.auth_NA()
        elif self.get_accesstype()=='DHCP':
            pass
        #data_to_send=replypacket.ReplyPacket()
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
        self.access_type=self.get_accesstype()
        self.connection = pool.connection()
        self.cur = self.connection.cursor()

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

        self.cur.execute("""SELECT secret from nas_nas WHERE ipaddress='%s'""" % self.nasip)
        rows = self.cur.fetchone()
        if rows==None:
            return self.acct_NA(self.replypacket)
        #Проверяем знаем ли мы такого пользователя
        #for key,value in packetobject.items():
        #    print packetobject._DecodeKey(key),packetobject[packetobject._DecodeKey(key)][0]
        simple_log(packet=self.packetobject)

        self.cur.execute(
        """
        SELECT account.id, tariff.time_access_service_id FROM billservice_account as account
        JOIN billservice_accounttarif as accounttariff ON accounttariff.id=(SELECT id FROM billservice_accounttarif WHERE account_id=account.id AND datetime<now() ORDER BY datetime DESC LIMIT 1)
        JOIN billservice_tariff as tariff ON tariff.id=accounttariff.tarif_id
        WHERE account.username='%s';
        """ % self.packetobject['User-Name'][0]
        )
        row=self.cur.fetchone()
        if row==None:
            return self.acct_NA(self.replypacket)

        account_id, time_access=row

        secret=str(rows[0])
        self.replypacket.secret=str(secret)
        self.replypacket.code=5
        now=datetime.datetime.now()


        if self.packetobject['Acct-Status-Type']==['Start']:
            #Проверяем нет ли такой сессии в базе
            #self.cur.execute("""
            #SELECT id
            #FROM radius_session
            #WHERE account_id=%s and sessionid='%s' and
            #caller_id='%s' and called_id='%s' and nas_id='%s' and framed_protocol='%s';
            #""" % (account_id, self.packetobject['Acct-Session-Id'][0], self.packetobject['Calling-Station-Id'][0],
            #       self.packetobject['Called-Station-Id'][0], self.packetobject['NAS-IP-Address'][0],self.access_type))

            #allow_write = self.cur.fetchone()==[]
            allow_write=True
            if time_access and allow_write:
                self.cur.execute(
                """
                INSERT INTO radius_session(
                account_id, sessionid, date_start,
                caller_id, called_id, nas_id, framed_protocol, checkouted_by_time, checkouted_by_trafic
                )
                VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s);
                """, (account_id, self.packetobject['Acct-Session-Id'][0], now,
                     self.packetobject['Calling-Station-Id'][0], self.packetobject['Called-Station-Id'][0],
                     self.packetobject['NAS-IP-Address'][0], self.access_type, False, False))

            if allow_write:
                self.cur.execute(
                """
                INSERT INTO radius_activesession(
                account_id, sessionid, date_start,
                caller_id, called_id, nas_id, framed_protocol, session_status
                )
                VALUES (%s, %s,%s, %s, %s, %s, %s, 'ACTIVE');
                """, (account_id, self.packetobject['Acct-Session-Id'][0], now,
                     self.packetobject['Calling-Station-Id'][0], self.packetobject['Called-Station-Id'][0],
                     self.packetobject['NAS-IP-Address'][0], self.access_type))

            self.connection.commit()


        if self.packetobject['Acct-Status-Type']==['Alive']:
            bytes_in, bytes_out=self.get_bytes()
            if time_access:
                self.cur.execute(
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
            self.cur.execute(
                        """
                        UPDATE radius_activesession
                        SET interrim_update='%s',bytes_out='%s', bytes_in='%s', session_time='%s'
                        WHERE account_id='%s' and sessionid='%s' and nas_id='%s';
                        """ % (now, self.packetobject['Acct-Input-Octets'][0], self.packetobject['Acct-Output-Octets'][0], self.packetobject['Acct-Session-Time'][0], account_id, self.packetobject['Acct-Session-Id'][0], self.packetobject['NAS-IP-Address'][0])
            )

            self.connection.commit()

        if self.packetobject['Acct-Status-Type']==['Stop']:
            bytes_in, bytes_out=self.get_bytes()
            if time_access:
                self.cur.execute(
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

            self.cur.execute(
               """
               UPDATE radius_activesession
               SET date_end='%s', session_status='ACK'
               WHERE account_id='%s' and sessionid='%s' and nas_id='%s';
               """ % (now,account_id, self.packetobject['Acct-Session-Id'][0], self.packetobject['NAS-IP-Address'][0])
               )
            self.connection.commit()
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
        t = clock()
        data=self.request[0] # or recv(bufsize, flags)
        assert len(data)<=4096
        addrport=self.client_address
        simple_log('Auth Request From:%s:%s' % addrport)
        packetobject=packet.Packet(dict=dict,packet=data)
        simple_log('Create Initial response packet Ok')
        coreconnect = HandleAuth(packetobject=packetobject)
        packetfromcore=coreconnect.handle()

        #Обавляем Secret
        packetobject.secret=packetfromcore.secret
        authobject=Auth(packetobject=packetobject, packetfromcore=packetfromcore)
        returndata=authobject.ReturnPacket()
        self.socket.sendto(returndata,addrport)

        del packetfromcore
        del packetobject
        print "AUTH:%.20f" % (clock()-t)

class RadiusAcct(BaseAuth):

      def handle(self):
        t = clock()
        data=self.request[0] # or recv(bufsize, flags)
        assert len(data)<=4096
        addrport=self.client_address
        packetobject=packet.AcctPacket(dict=dict,packet=data)

        coreconnect = HandleAcct(packetobject=packetobject, nasip=self.client_address[0])
        packetfromcore = coreconnect.handle()

        #replyobj=packet.AcctPacket(id=requestpacket.id, code=packetfromcore.code, secret=packetfromcore.secret, authenticator=requestpacket.authenticator, dict=dict)
        returndat=packetfromcore.ReplyPacket()
        self.socket.sendto(returndat,addrport)
        print "ACC:%.20f" % (clock()-t)
        #del coreconnect
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
print 123
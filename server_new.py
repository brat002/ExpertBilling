#-*-coding=utf-8-*-
import dictionary
import packet
import auth
from time import clock
import settings
from coreconnection import RequestPacket
import corepacket
#import utilites
from threading import Thread
#core
import sys,time,os,datetime
from SocketServer import ThreadingUDPServer
from SocketServer import DatagramRequestHandler
from threading import Thread
import dictionary
import packet
import struct, tools
import corepacket
from utilites import in_period
from db import get_nas_by_ip, get_account_data_by_username, get_nas_id_by_tarif_id, time_periods_by_tarif_id

import psycopg2

from DBUtils.PooledDB import PooledDB

pool = PooledDB(
     mincached=2,
     maxcached=60,
     blocking=True,
    creator=psycopg2,
    dsn="dbname='mikrobill' user='mikrobill' host='localhost' password='1234'"

)

#auth_class
class handle_auth_core:
    def auth_NA(self, replypacket):
        replypacket.username='None'
        replypacket.password='None'
        replypacket.code=3
        data_to_send=replypacket.ReplyPacket()
        return data_to_send

    def handle(self, response, nasip):
        db_connection = pool.connection()
        cur = db_connection.cursor()
        packetobject=packet.Packet(dict=dict,packet=response)
        
        if packetobject['NAS-Port-Type'][0]=='Virtual':
            access_type='PPTP'
        elif packetobject['NAS-Port-Type'][0]=='Ethernet':
            access_type='PPPOE'
            
        replypacket=corepacket.CorePacket(secret='None',dict=dict)
        row = get_nas_by_ip(cur, nasip).fetchone()
        if row==None:
            return self.auth_NA(replypacket)

        nas_id=str(row[0])
        secret=str(row[1])
        
        replypacket.secret = secret
        row = get_account_data_by_username(cur, packetobject['User-Name'][0]).fetchone()
        if row==None:
            return self.auth_NA(replypacket)

        username, password, ipaddress, tarif_id, status, banned, ballance = row

        row=get_nas_id_by_tarif_id(cur, tarif_id).fetchone()
        if row==None:
            return self.auth_NA(replypacket)

        if int(row[0])!=int(nas_id) or row[1]!=access_type:
           return self.auth_NA(replypacket)

        #TimeAccess
        rows = time_periods_by_tarif_id(cur, tarif_id).fetchall()
        for row in rows:
            if in_period(row[2],row[3],row[4])==False:
                return self.auth_NA(replypacket)
        #for key,value in packetobject.items():
        #    print packetobject._DecodeKey(key),packetobject[key][0]
        
        cur.close()
        if packetobject['User-Name'][0]==username and status=='Enabled' and banned=='Disabled' and ballance>0:
           replypacket.code=2
           replypacket.username=str(username) #Нельзя юникод
           replypacket.password=str(password) #Нельзя юникод
           replypacket.AddAttribute('Service-Type', 2)
           replypacket.AddAttribute('Framed-Protocol', 1)
           replypacket.AddAttribute('Framed-IP-Address', ipaddress)
           replypacket.AddAttribute('Framed-Routing', 0)
           #replypacket.AddAttribute((14988,8),'128k')

        else:
             return self.auth_NA(replypacket)

        data_to_send=replypacket.ReplyPacket()
        return data_to_send


#acct class
class handle_acct_core:
    def acct_NA(self, replypacket):
        # Если мы не знаем такого сервера доступа-ничего не отвечаем на запрос
        replypacket.code=3
        data_to_send=replypacket.ReplyPacket()
        #self.request.sendto(data_to_send,self.client_address) # or send(data, flags)
        return data_to_send

    def handle(self, response, nasip):
        db_connection = pool.connection()
        cur = db_connection.cursor()
        bufsize=4096
        #response=self.request.recv(bufsize).strip() # or recv(bufsize, flags)
        #(requestpacketid, code, nasip, length)=struct.unpack("!LB4sH",response[:11])
        #nasip=tools.DecodeAddress(nasip)
        packetobject=packet.Packet(dict=dict,packet=response)

        replypacket=corepacket.CorePacket(username="None", secret='None', password="None", dict=dict)

        cur.execute("""SELECT secret from nas_nas WHERE ipaddress='%s'""" % nasip)
        rows = cur.fetchone()
        if rows==None:
            return self.acct_NA(replypacket)
        #Проверяем знаем ли мы такого пользователя
        #for key,value in packetobject.items():
        #    print packetobject._DecodeKey(key),packetobject[packetobject._DecodeKey(key)][0]
        cur.execute(
        """
        SELECT id FROM billservice_account WHERE username='%s';
        """ % packetobject['User-Name'][0]
        )
        row=cur.fetchone()
        if row==None:
            return self.acct_NA(replypacket)
        
        account_id=row[0]

        secret=str(rows[0])
        replypacket.secret=str(secret)
        replypacket.code=5
        now=datetime.datetime.now()
        if packetobject['Acct-Status-Type']==['Start']:
            if packetobject['NAS-Port-Type'][0]=='Virtual':
              access_type='PPTP'
            elif packetobject['NAS-Port-Type'][0]=='Ethernet':
               access_type='PPPOE'

            cur.execute(
           """
           INSERT INTO radius_session(
           account_id, sessionid, date_start, 
           caller_id, called_id, nas_id, framed_protocol, checkouted_by_time, checkouted_by_trafic
           )
           VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s);
           """, (account_id, packetobject['Acct-Session-Id'][0], now, packetobject['Calling-Station-Id'][0], packetobject['Called-Station-Id'][0], packetobject['NAS-IP-Address'][0], access_type, False, False))

            cur.execute(
           """
           INSERT INTO radius_activesession(
           account_id, sessionid, date_start, 
           caller_id, called_id, nas_id, framed_protocol, session_status
           )
           VALUES (%s, %s,%s, %s, %s, %s, %s, 'ACTIVE');
           """, (account_id, packetobject['Acct-Session-Id'][0], now, packetobject['Calling-Station-Id'][0], packetobject['Called-Station-Id'][0], packetobject['NAS-IP-Address'][0], access_type))

            db_connection.commit()


        if packetobject['Acct-Status-Type']==['Alive']:
           cur.execute(
           """
           INSERT INTO radius_session(
           account_id, sessionid, interrim_update,
           caller_id, called_id, nas_id, session_time,
           bytes_out, bytes_in, checkouted_by_time, checkouted_by_trafic)
           VALUES ( %s, %s, %s, %s, %s, %s,
           %s, %s, %s, %s, %s);
           """, (account_id, packetobject['Acct-Session-Id'][0],
                 now, packetobject['Calling-Station-Id'][0],
                 packetobject['Called-Station-Id'][0], packetobject['NAS-IP-Address'][0],
                 packetobject['Acct-Session-Time'][0],
                 packetobject['Acct-Input-Octets'][0], packetobject['Acct-Output-Octets'][0], False, False)
           )
           cur.execute(
           """
           UPDATE radius_activesession
           SET interrim_update='%s',bytes_out='%s', bytes_in='%s', session_time='%s'
           WHERE account_id='%s' and sessionid='%s' and nas_id='%s';
           """ % (now, packetobject['Acct-Input-Octets'][0], packetobject['Acct-Output-Octets'][0], packetobject['Acct-Session-Time'][0], account_id, packetobject['Acct-Session-Id'][0], packetobject['NAS-IP-Address'][0])
           )
           db_connection.commit()

        if packetobject['Acct-Status-Type']==['Stop']:
            cur.execute(
            """
            INSERT INTO radius_session(
            account_id, sessionid, interrim_update, date_end,
            caller_id, called_id, nas_id, session_time,
            bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic)
            VALUES ( %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s);
            """, (account_id, packetobject['Acct-Session-Id'][0],
                  now, now, packetobject['Calling-Station-Id'][0],
                  packetobject['Called-Station-Id'][0], packetobject['NAS-IP-Address'][0],
                  packetobject['Acct-Session-Time'][0],
                  packetobject['Acct-Input-Octets'][0], packetobject['Acct-Output-Octets'][0], False, False)
            )
            
            cur.execute(
               """
               UPDATE radius_activesession
               SET date_end='%s', session_status='ACK'
               WHERE account_id='%s' and sessionid='%s' and nas_id='%s';
               """ % (now,account_id, packetobject['Acct-Session-Id'][0], packetobject['NAS-IP-Address'][0])
               )
            db_connection.commit()
        cur.close()

        data_to_send=replypacket.ReplyPacket()
        return data_to_send


#radius


RequireLogin=1
LoginAllowed=2
LoginDisabled=3

#dict=dictionary.Dictionary("dicts/dictionary","dicts/dictionary.microsoft", 'dicts/dictionary.mikrotik')
dict=dictionary.Dictionary("dicts/dictionary","dicts/dictionary.microsoft")

class handle_auth(DatagramRequestHandler):
      def handle(self):
        t = clock()
        bufsize=4096
        data,socket=self.request # or recv(bufsize, flags)
        addrport=self.client_address
        #reqpack=RequestPacket(1,(settings.core_host, settings.core_auth), self.client_address[0])
        #corereply=reqpack.getreply(data)
        coreconnect = handle_auth_core()
        corereply = coreconnect.handle(response=data, nasip=self.client_address[0])
        packetfromcore=corepacket.CorePacket(packet=corereply, dict=dict)
        packetobject=packet.Packet(secret=packetfromcore.secret, dict=dict,packet=data)
        authobject=auth.Auth(Packet=packetobject, plainpassword=packetfromcore.password, plainusername=packetfromcore.username, code=packetfromcore.code, attrs=packetfromcore._PktEncodeAttributes())
        returndata=authobject.ReturnPacket()
        self.socket.sendto(returndata,addrport)
        del coreconnect
        del corereply
        del packetfromcore
        del packetobject
        print "AUTH:%.20f" % (clock()-t)

class handle_acct(DatagramRequestHandler):
      def handle(self):
        t = clock()
        bufsize=4096
        data,socket=self.request # or recv(bufsize, flags)
        addrport=self.client_address
        #reqpack=RequestPacket(1,(settings.core_host, settings.core_acct), self.client_address[0])
        #corereply=reqpack.getreply(data)
        coreconnect = handle_acct_core()
        corereply = coreconnect.handle(response=data, nasip=self.client_address[0])
        requestpacket=packet.AcctPacket(dict=dict,packet=data)
        packetfromcore=corepacket.CorePacket(packet=corereply, dict=dict)
        print packetfromcore.code
        replyobj=packet.AcctPacket( id=requestpacket.id, code=packetfromcore.code, secret=packetfromcore.secret, authenticator=requestpacket.authenticator, dict=dict)
        returndat=replyobj.ReplyPacket()
        self.socket.sendto(returndat,addrport)
        print "ACC:%.20f" % (clock()-t)
        del coreconnect
        del corereply
        del packetfromcore
        del replyobj

          

class serve_requests(Thread):
        def __init__ (self, address, handler):
            self.address=address
            self.handler=handler
            Thread.__init__(self)

        def run(self):
            server = ThreadingUDPServer(self.address, self.handler)
            server.allow_reuse_address = True
            server.serve_forever()


server_auth = serve_requests(("0.0.0.0", 1812), handle_auth)
server_auth.start()

server_acct = serve_requests(("0.0.0.0", 1813), handle_acct)
server_acct.start()

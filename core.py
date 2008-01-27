# coding=utf8
import sys,time,os,datetime
from SocketServer import ThreadingTCPServer
from SocketServer import StreamRequestHandler
from threading import Thread
import dictionary
import packet
import struct, tools
import corepacket
from utilites import in_period
from db import get_nas_by_ip, get_account_data_by_username, get_nas_id_by_tarif_id, time_periods_by_tarif_id

import psycopg2
#from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from DBUtils.PooledDB import PooledDB

pool = PooledDB(
     mincached=2,
     maxcached=60,
     blocking=True,
    creator=psycopg2,
    dsn="dbname='mikrobill' user='mikrobill' host='localhost' password='1234'"
    
)


dict=dictionary.Dictionary("dicts\dictionary","dicts\dictionary.microsoft")
t = time.clock()

class handle_auth(StreamRequestHandler):
    def auth_NA(self, replypacket):
        replypacket.username='None'
        replypacket.password='None'
        replypacket.code=3
        data_to_send=replypacket.ReplyPacket()
        self.request.sendto(data_to_send,self.client_address)
        self.finish()
        return False
        
    def handle(self):
        db_connection = pool.connection()
        cur = db_connection.cursor()
        bufsize=4096
        response=self.request.recv(bufsize).strip() # or recv(bufsize, flags)
        (requestpacketid, code, nasip, length)=struct.unpack("!LB4sH",response[:11])
        nasip=tools.DecodeAddress(nasip)
        packetobject=packet.Packet(dict=dict,packet=response[11:])
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

        if int(row[0])!=int(nas_id):
           return self.auth_NA(replypacket)
       
        #TimeAccess
        rows = time_periods_by_tarif_id(cur, tarif_id).fetchall()
        for row in rows:
            if in_period(row[2],row[3],row[4])==False:
                return self.auth_NA(replypacket)

        cur.close()
        #Сделать проверку "как работает пользователь". В кредит или по предоплате
        if packetobject['User-Name'][0]==username and status=='Enabled' and banned=='Disabled' and ballance>0:
           replypacket.code=2
           replypacket.username=str(username) #Нельзя юникод
           replypacket.password=str(password) #Нельзя юникод
           replypacket.AddAttribute('Service-Type', 2)
           replypacket.AddAttribute('Framed-Protocol', 1)
           replypacket.AddAttribute('Framed-IP-Address', ipaddress)
           replypacket.AddAttribute('Framed-Routing', 0)

        else:
             return self.auth_NA(replypacket)

        data_to_send=replypacket.ReplyPacket()
        self.request.sendto(data_to_send,self.client_address) # or send(data, flags)

class handle_acct(StreamRequestHandler):
    def acct_NA(self, replypacket):
        # Если мы не знаем такого сервера доступа-ничего не отвечаем на запрос
        replypacket.code=3
        data_to_send=replypacket.ReplyPacket()
        self.request.sendto(data_to_send,self.client_address) # or send(data, flags)
        return False
    
    def handle(self):
        db_connection = pool.connection()
        cur = db_connection.cursor()
        bufsize=4096
        response=self.request.recv(bufsize).strip() # or recv(bufsize, flags)
        (requestpacketid, code, nasip, length)=struct.unpack("!LB4sH",response[:11])
        nasip=tools.DecodeAddress(nasip)
        packetobject=packet.Packet(dict=dict,packet=response[11:])
        replypacket=corepacket.CorePacket(username="None", secret='None', password="None", dict=dict)
        
        cur.execute("""SELECT secret from nas_nas WHERE ipaddress='%s'""" % nasip)
        rows = cur.fetchone()
        if rows==None:
            return self.acct_NA(replypacket)
        
        secret=str(rows[0])
        replypacket.secret=str(secret)
        replypacket.code=5
        
        if packetobject['Acct-Status-Type']==['Start']:
            cur.execute(
            """
            INSERT INTO radius_session(
            account_id, sessionid, date_start, interrim_update,
            caller_id, called_id, nas_id, framed_protocol, checkouted_by_time, checkouted_by_trafic
            )
            VALUES ((SELECT id FROM billservice_account WHERE username=%s), %s, %s,%s, %s, %s, %s, 'PPTP', %s, %s);
            """, (packetobject['User-Name'][0], packetobject['Acct-Session-Id'][0], datetime.datetime.now(), datetime.datetime.now(), packetobject['Calling-Station-Id'][0], packetobject['Called-Station-Id'][0], packetobject['NAS-IP-Address'][0], False, False))
            db_connection.commit()
            

        if packetobject['Acct-Status-Type']==['Alive']:
            cur.execute(
            """
            INSERT INTO radius_session(
            account_id, sessionid, interrim_update,
            caller_id, called_id, nas_id, session_time,
            bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic)
            VALUES ( (SELECT id FROM billservice_account WHERE username=%s), %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s);
            """, (packetobject['User-Name'][0], packetobject['Acct-Session-Id'][0],
                  datetime.datetime.now(), packetobject['Calling-Station-Id'][0],
                  packetobject['Called-Station-Id'][0], packetobject['NAS-IP-Address'][0],
                  packetobject['Acct-Session-Time'][0],
                  packetobject['Acct-Input-Octets'][0], packetobject['Acct-Output-Octets'][0], False, False)
            )
            db_connection.commit()
            
        if packetobject['Acct-Status-Type']==['Stop']:
            now=datetime.datetime.now()
            cur.execute(
            """
            INSERT INTO radius_session(
            account_id, sessionid, interrim_update, date_end,
            caller_id, called_id, nas_id, session_time,
            bytes_in, bytes_out, checkouted_by_time, checkouted_by_trafic)
            VALUES ( (SELECT id FROM billservice_account WHERE username=%s), %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s);
            """, (packetobject['User-Name'][0], packetobject['Acct-Session-Id'][0],
                  now, now, packetobject['Calling-Station-Id'][0],
                  packetobject['Called-Station-Id'][0], packetobject['NAS-IP-Address'][0],
                  packetobject['Acct-Session-Time'][0],
                  packetobject['Acct-Input-Octets'][0], packetobject['Acct-Output-Octets'][0], False, False)
            )
            db_connection.commit()
        cur.close()




        
        data_to_send=replypacket.ReplyPacket()
        self.request.sendto(data_to_send,self.client_address) # or send(data, flags)
        

    
class serve_auth(Thread):
        def __init__ (self,address, handler):
            self.address=address
            self.handler=handler
            self.allow_reuse_address=True
            Thread.__init__(self)

        def run(self):
            server = ThreadingTCPServer(self.address, self.handler)
            server.serve_forever()


server_auth = serve_auth(("0.0.0.0", 2224), handle_auth)
server_auth.start()
		    
server_acct = serve_auth(("0.0.0.0", 2225), handle_acct)
server_acct.start()
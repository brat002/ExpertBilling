#-*-coding= utf-8 -*-

import os, sys
import ConfigParser
import datetime, time
import fnmatch
import shutil
import time
import psycopg2
import sys, time, binascii, socket, select, md5

config = ConfigParser.ConfigParser()
billing_config = ConfigParser.ConfigParser()
billing_config.read("/opt/ebs/data/ebs_config.ini")
#billing_config.read("d:/projects/mikrobill/ebs_config.ini")
#########################
host = billing_config.get("db", "host")
port = billing_config.getint('db', 'port')
database = billing_config.get('db', 'name')
user = billing_config.get('db', 'username')
password = billing_config.get('db', 'password')

class ApiRos:
    "Routeros api"
    def __init__(self, sk):
        self.sk = sk
        self.currenttag = 0
        
    def login(self, username, pwd):
        for repl, attrs in self.talk(["/login"]):
            chal = binascii.unhexlify(attrs['=ret'])
        md = md5.new()
        md.update('\x00')
        md.update(pwd)
        md.update(chal)
        self.talk(["/login", "=name=" + username,
                   "=response=00" + binascii.hexlify(md.digest())])

    def talk(self, words):
        if self.writeSentence(words) == 0: return
        r = []
        while 1:
            i = self.readSentence();
            if len(i) == 0: continue
            reply = i[0]
            attrs = {}
            for w in i[1:]:
                j = w.find('=', 1)
                if (j == -1):
                    attrs[w] = ''
                else:
                    attrs[w[:j]] = w[j+1:]
            r.append((reply, attrs))
            if reply == '!done': return r

    def writeSentence(self, words):
        ret = 0
        for w in words:
            self.writeWord(w)
            ret += 1
        self.writeWord('')
        return ret

    def readSentence(self):
        r = []
        while 1:
            w = self.readWord()
            if w == '': return r
            r.append(w)
            
    def writeWord(self, w):
        print "<<< " + w
        self.writeLen(len(w))
        self.writeStr(w)

    def readWord(self):
        ret = self.readStr(self.readLen())
        #print ">>> " + ret
        return ret

    def writeLen(self, l):
        if l < 0x80:
            self.writeStr(chr(l))
        elif l < 0x4000:
            l |= 0x8000
            self.writeStr(chr((l >> 8) & 0xFF))
            self.writeStr(chr(l & 0xFF))
        elif l < 0x200000:
            l |= 0xC00000
            self.writeStr(chr((l >> 16) & 0xFF))
            self.writeStr(chr((l >> 8) & 0xFF))
            self.writeStr(chr(l & 0xFF))
        elif l < 0x10000000:        
            l |= 0xE0000000         
            self.writeStr(chr((l >> 24) & 0xFF))
            self.writeStr(chr((l >> 16) & 0xFF))
            self.writeStr(chr((l >> 8) & 0xFF))
            self.writeStr(chr(l & 0xFF))
        else:                       
            self.writeStr(chr(0xF0))
            self.writeStr(chr((l >> 24) & 0xFF))
            self.writeStr(chr((l >> 16) & 0xFF))
            self.writeStr(chr((l >> 8) & 0xFF))
            self.writeStr(chr(l & 0xFF))

    def readLen(self):              
        c = ord(self.readStr(1))    
        if (c & 0x80) == 0x00:      
            pass                    
        elif (c & 0xC0) == 0x80:    
            c &= ~0xC0              
            c <<= 8                 
            c += ord(self.readStr(1))    
        elif (c & 0xE0) == 0xC0:    
            c &= ~0xE0              
            c <<= 8                 
            c += ord(self.readStr(1))    
            c <<= 8                 
            c += ord(self.readStr(1))    
        elif (c & 0xF0) == 0xE0:    
            c &= ~0xF0              
            c <<= 8                 
            c += ord(self.readStr(1))    
            c <<= 8                 
            c += ord(self.readStr(1))    
            c <<= 8                 
            c += ord(self.readStr(1))    
        elif (c & 0xF8) == 0xF0:    
            c = ord(self.readStr(1))     
            c <<= 8                 
            c += ord(self.readStr(1))    
            c <<= 8                 
            c += ord(self.readStr(1))    
            c <<= 8                 
            c += ord(self.readStr(1))    
        return c                    

    def writeStr(self, str):        
        n = 0;                      
        while n < len(str):         
            r = self.sk.send(str[n:])
            if r == 0: raise RuntimeError, "connection closed by remote end"
            n += r                  

    def readStr(self, length):      
        ret = ''                    
        while len(ret) < length:    
            s = self.sk.recv(length - len(ret))
            if s == '': raise RuntimeError, "connection closed by remote end"
            ret += s
        return ret
    
def rosExecute(apiros, command):

    x=['']
    commands = command.split(" ")

    commands.append(" ")
    result = []
    apiros.writeSentence(commands)
    while True:
        x = apiros.readSentence()
        #print x
        if x[0]=='!done':
            break
        result.append(x)
        
    #s.close()

    return make_dict(result)      
  
def rosClient(nas_ip, nas_login, nas_password):
    """
    @param host: IP address or Hostname
    @param login: Username of System user
    @param password: Password os system user
    @param commant: command for execution    
    """
    global s, apiros
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((nas_ip, 8728))
    except Exception, e:
        print e
        return []
        
    apiros = ApiRos(s);
    apiros.login(str(nas_login), str(nas_password))
    return apiros

def make_dict(res):
    
    out = []
    if not res: return []
    for item in res:
        d={}
        for x in item:
            r=x.split('=')
            if len(r)<2: continue
            d[r[1]]=r[2]
        out.append(d)
    return out

def get_id(d):
    #print d
    if '.id' in d.keys():
        return d['.id']
    else:
        return 0
    
try:
    connection = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (database, user, host, password, port));
except Exception, e:
    print "I am unable to connect to the database"
    print e
    sys.exit()

connection.set_isolation_level(1)
cur = connection.cursor()

cur.execute("select identify, ipaddress, login, decrypt_pw(password, 'ebscryptkeytest') FROM nas_nas;")
sessions = []
for identify, ipaddress, login, password in cur.fetchall():
    apiros=rosClient(ipaddress, login, password)
    if not apiros: continue
    command = '/ppp/active/getall ?service=pptp'
    sessions += rosExecute(apiros, command)
    
    #id=get_id(res)
    #print "id=", id
#ids = map(lambda x: x.lower()[2:] if x.startswith('0x') else x.lower(), [item.get('session-id').lower() for item in sessions])
ids = map(lambda x: x.lower(), [item.get('name').lower() for item in sessions])
cur.execute("SELECT sessionid, ipinuse_id, framed_ip_address FROM radius_activesession as r WHERE  session_status='ACTIVE' and (SELECT username FROM billservice_subaccount WHERE id=r.subaccount_id ) not  in %s", (tuple(ids), ) )
data = cur.fetchall()
print len(data)
print data
for sessionid, ipinuse_id in data:
    cur.execute('UPDATE billservice_ipinuse SET disabled=now() WHERE id=%s', (ipinuse_id))
    cur.execute("UPDATE radius_activesession SET session_status='ACK' WHERE sessionid=%s", (sessionid, ))
#print ids

connection.commit()

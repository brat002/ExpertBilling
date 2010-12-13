#!/usr/bin/python

import sys, posix, time, md5, binascii, socket, select

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
    
def rosClient(host, login, password, command):
    """
    @param host: IP address or Hostname
    @param login: Username of System user
    @param password: Password os system user
    @param commant: command for execution    
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, 8728))
    except Exception, e:
        print e
        return []
        
    apiros = ApiRos(s);
    apiros.login(str(login), str(password))
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
        
    s.close()
    return make_dict(result)

def make_dict(res):
    d={}
    if not res: return d
    for x in res[0]:
        r=x.split('=')
        if len(r)<2: continue
        d[r[1]]=r[2]
    return d

def get_id(d):
    if 'id' in d.keys():
        return d['id']
    else:
        return -1
host='10.20.3.1'
login='ebs'
password='ebspassword'
command='/queue/simple/print ?name=<pptp-ilia>'
#command='/queue/simple/set ?name=parent_360 name=parent_361'
res=rosClient(host, login, password, command)
print res
#print make_dict(res)
command='/queue/simple/remove =.id=*681'
res=rosClient(host, login, password, command)
print res
#print make_dict(res)


def add_subaccount():
    pass
    #command="""{/ip firewall address-list add list=internet_users address=$subacc_vpn_ip_address disabled=yes comment=acc_$acc_account_id-$subacc_id;:local new "$subacc_vpn_ip_address/32"; :local res [/queue simple get parent_$acc_account_id target-addresses ]; :if ([:tostr [:find [:toarray $res] $new]] = "") do={:set res ($res + $new)};  /queue simple set parent_$acc_account_id target-address=$res  disabled=no;}
"""
    accountid = sys.argv[4]
    address = sys.argv[2]
    comment = sys.argv[3]
    subaccount_ip = sys.argv[5]

    command = '/ip/firewall/address-list/print ?address=%s ?comment=%s' % (address, comment)
    res=rosClient(host, login, password, command)
    id=get_id(res)
    if not id:
        command='/ip/firewall/address-list/add list=internet-users address=%s comment=%s disabled=yes' % (address, comment)
	rosClient(host, login, password, command)
    
    command = '/queue/simple/print ?name=acc_%s' % account_id
    res=rosClient(host, login, password, command)
    id=get_id(res)
    if not id:
        command = '/queue/simple/add name=acc_%s disabled=yes' % accountid
        rosClient(host, login, password, command)
    
    command = '/queue/simple/print ?name=acc_%s' % accountid
    res = rosClient(host, login, password, command)
    
    id=get_id(res)
    addresses = res.get('target-address', '')

    if addresses:
        addr_list = addresses.split(',')
        if str(subaccount_ip) not in addr_list:
        #add subaccount_ip
            addr_list.append(str(subaccount_ip))
            addresses = ','.join(addr_list)
            command = '/queue/simple/set =.id=%s disabled=no target-address=%s' % (id, addresses)
    

def enable_subaccount():
    address = sys.argv[2]
    comment = sys.argv[3]
    command = '/ip/firewall/address-list/print ?address=%s ?comment=%s' % (address, comment)
    res=rosClient(host, login, password, command)
    id=get_id(res)
    if id:
        command='/ip/firewall/address-list/set =.id=%s disabled=no' % (id, )
        rosClient(host, login, password, command)


def disable_subaccount():
    address = sys.argv[2]
    comment = sys.argv[3]
    command = '/ip/firewall/address-list/print ?address=%s ?comment=%s' % (address, comment)
    res=rosClient(host, login, password, command)
    id=get_id(res)
    if id:
        command='/ip/firewall/address-list/set =.id=%s disabled=yes' % (id, )
        rosClient(host, login, password, command)


def del_subaccount():
    address = sys.argv[2]
    comment = sys.argv[3]
    command = '/ip/firewall/address-list/print ?address=%s ?comment=%s' % (address, comment)
    res=rosClient(host, login, password, command)
    id=get_id(res)
    if id:
        command='/ip/firewall/address-list/remove =.id=%s' % (id, )
        rosClient(host, login, password, command)

    command = '/queue/simple/print ?name=acc_%s' % accountid
    res = rosClient(host, login, password, command)

    id=get_id(res)
    addresses = res.get('target-address', '')

    if addresses:
        addr_list = addresses.split(',')
        if str(subaccount_ip)  in addr_list:
            r=[]
            for x in addr_list:
                if x!=subaccount_ip: r.append(x)
        #add subaccount_ip
            #addr_list.append(str(subaccount_ip))
            addresses = ','.join(r)
            if addresses:
                command = '/queue/simple/set =.id=%s disabled=no target-address=%s' % (id, addresses)
                
            else:
                 command = '/queue/simple/set =.id=%s disabled=yes'
            rosClient(host, login, password, command)


def set_ipn_speed_subaccount():

    accountid = sys.argv[4]
    speed_settings = sys.argv[5]
    command = '/queue/simple/print ?name=acc_%s' % accountid
    res = rosClient(host, login, password, command)

    id=get_id(res)
    if id:
        command = '/queue/simple/set =.id=%s ?name=acc_%s %s' % (id, accountid, speed_settings)
    rosClient(host, login, password, command)


def reset_vpn_session(command):
    #command='/queue/simple/print ?name=<access_-ilia>'
    res=rosClient(host, login, password, command)
    id=get_id(res)
    if id:
        command='/queue/simple/remove =.id=%s' % id
        res=rosClient(host, login, password, command)
        return True
    return False



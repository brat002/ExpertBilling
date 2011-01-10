#!c:/python26/python.exe

import sys, time, binascii, socket, select, md5
#from hashlib import md5

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
    
def rosExecute(command):
    global apiros
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
    global s
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
    d={}
    if not res: return d
    for x in res[0]:
        r=x.split('=')
        if len(r)<2: continue
        d[r[1]]=r[2]
    return d

def get_id(d):
    #print d
    if '.id' in d.keys():
        return d['.id']
    else:
        return 0

def add_subaccount(accountid,subaccount_id, subaccount_ip, comment):
    global nas_ip, nas_login, nas_password
    command = '/ip/firewall/address-list/print ?address=%s ?comment=%s' % (subaccount_ip, comment)
    res=rosExecute(command)
    print res
    id=get_id(res)
    print "id=", id
    if not id:
        command='/ip/firewall/address-list/add =list=internet-users =address=%s =comment=%s =disabled=yes' % (subaccount_ip, comment)
        rosExecute(command)
    
    command = '/queue/simple/print ?name=acc_%s' % accountid
    res=rosExecute(command)
    id=get_id(res)
    if not id:
        command = '/queue/simple/add =name=acc_%s =disabled=yes' % accountid
        rosExecute(command)
    
    command = '/queue/simple/print ?name=acc_%s' % accountid
    res = rosExecute(command)
    
    id=get_id(res)
    print res
    print "simple queue id=", id
    addresses = res.get('target-addresses', '')


    addr_list = addresses.split(',')
    if not addr_list:
        addr_list=[]
    subaccount_ip = "%s/32" % subaccount_ip
    if str(subaccount_ip) not in addr_list:
        #add subaccount_ip
        print "not in addr_list"
        addr_list.append(str(subaccount_ip))
        addresses = ','.join(addr_list)
        print "addresses", addresses
        command = '/queue/simple/set =.id=%s =disabled=no =target-addresses=%s' % (id, addresses)
        print rosExecute(command)
    

def enable_subaccount(subaccount_ip, comment):
    global nas_ip, nas_login, nas_password
    #address = sys.argv[2]
    #comment = sys.argv[3]
    command = '/ip/firewall/address-list/print ?address=%s ?comment=%s' % (subaccount_ip, comment)
    res=rosExecute(command)
    id=get_id(res)
    if id:
        command='/ip/firewall/address-list/set =.id=%s =disabled=no' % (id, )
        rosExecute(command)


def disable_subaccount(subaccount_ip, comment):
    global nas_ip, nas_login, nas_password

    command = '/ip/firewall/address-list/print ?address=%s ?comment=%s' % (subaccount_ip, comment)
    res=rosExecute(command)
    id=get_id(res)
    if id:
        command='/ip/firewall/address-list/set =.id=%s =disabled=yes' % (id, )
        rosExecute(command)


def del_subaccount(accountid, subaccount_ip, comment):
    global nas_ip, nas_login, nas_password
    #address = sys.argv[2]
    #comment = sys.argv[3]
    command = '/ip/firewall/address-list/print ?address=%s ?comment=%s' % (subaccount_ip, comment)
    res=rosExecute(command)
    id=get_id(res)
    if id:
        command='/ip/firewall/address-list/remove =.id=%s' % (id, )
        rosExecute(command)

    command = '/queue/simple/print ?name=acc_%s' % accountid
    res = rosExecute(command)

    id=get_id(res)
    addresses = res.get('target-addresses', '')
    subaccount_ip = "%s/32" % subaccount_ip
    if addresses:
        addr_list = addresses.split(',')
        print 'addr_list', addr_list, type(addr_list)
        if subaccount_ip in addr_list:
            r=[]
            for x in addr_list:
                print "x=",x
                if x!=subaccount_ip: r.append(x)
            print r
        #add subaccount_ip
            #addr_list.append(str(subaccount_ip))
            addresses = ','.join(r)
            if addresses:
                command = '/queue/simple/set =.id=%s =disabled=no =target-addresses=%s' % (id, addresses)
            else:
                command = '/queue/simple/set =.id=%s =disabled=yes =target-addresses=%s' % (id, addresses)
            rosExecute(command)


def set_ipn_speed_subaccount(accountid, speed_settings):
    global nas_ip, nas_login, nas_password
    print "speed_settings", speed_settings
    #accountid = sys.argv[4]
    #speed_settings = sys.argv[5]
    command = '/queue/simple/print ?name=acc_%s' % accountid
    res = rosClient(nas_ip, nas_login, nas_password, command)

    id=get_id(res)
    if id:
        command = '/queue/simple/set =.id=%s %s' % (id, speed_settings)
    rosClient(nas_ip, nas_login, nas_password, command)


def reset_vpn_session(access_type, username):
    global nas_ip, nas_login, nas_password
    command='/interface/%s-server/print ?user=%s' % (access_type, username)
    res=rosClient(nas_ip, nas_login, nas_password, command)
    id=get_id(res)
    if id:
        command='/interface/%s-server/remove =.id=%s' % (access_type, id)
        res=rosClient(nas_ip, nas_login, nas_password, command)
        return True
    return False

def main():
    global nas_ip, nas_login, nas_password, apiros, s
    nas_ip = sys.argv[1]
    nas_login = sys.argv[2]
    nas_password = sys.argv[3]
    action = sys.argv[4]
    apiros=rosClient(nas_ip, nas_login, nas_password)
    if action=='add':
        accountid = sys.argv[5]
        subaccount_id = sys.argv[6]
        subaccount_ip = sys.argv[7]
        comment = sys.argv[8]
        add_subaccount(accountid,subaccount_id, subaccount_ip, comment)
        
    elif action == 'enable':
        subaccount_ip = sys.argv[5]  
        comment = sys.argv[6]      
        enable_subaccount(subaccount_ip, comment)
    elif action == 'disable':
        subaccount_ip = sys.argv[5]  
        comment = sys.argv[6]  
        disable_subaccount(subaccount_ip, comment)
    elif action == 'delete':
        accountid = sys.argv[5]
        subaccount_ip = sys.argv[6]
        comment = sys.argv[7]        
        del_subaccount(accountid, subaccount_ip, comment)
    elif action == 'reset':
        access_type = sys.argv[5]
        username = sys.argv[6]
        reset_vpn_session(access_type, username)
    elif action == 'set_speed':
        accountid = sys.argv[5]
        speed_settings = sys.argv[6]
        set_ipn_speed_subaccount(accountid, speed_settings)
    s.close()
    
    

if __name__=='__main__':
    """
    import getopt
    opts, args = getopt.getopt(
        sys.argv[ 1 : ],
        'a:',
        ['nas_ip=', 'nas_login=', 'nas_password=', 'account_id=', 'subaccount_id=', 'subaccount_ip=', 'comment=' , 'speed=']
    )
    print 'args', args
    print 'opts', opts
    for o in opts:
        print o
    """
    
    main()
    

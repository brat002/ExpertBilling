#-*-coding=utf-8-*-
import paramiko
import commands
import re
import sys, time, binascii, socket, select
import hashlib
md5 = hashlib.md5()

SSH_BACKEND=None
def ssh_client(host, username, password, command):
    #print command
    global SSH_BACKEND
    global logger
    #logger = isdlogger.isdlogger('logging', loglevel=0, ident="ebs_core", filename="log/core_log")
    print command    
    if SSH_BACKEND==None:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(host, username=username, password=password)
        #logger.debug("NAS Manipulation command string %s", (command, ))   
        stdin, stdout, stderr = ssh.exec_command(command)
        out = stdout.readlines()
        err = stderr.readlines()
        ssh.close()
        return out, err==[]
    else:
        command_string=command_string_parser(command_string=SSH_BACKEND, command_dict=
                            {'host': host, 'username': username,'password': password,
                             'command': command})    
        #logger.debug("NAS Manipulation command string %s", (command_string, ))    
        status, output = commands.getstatusoutput(command_string)
        #logger.debug("NAS Manipulation try status=%s output=%s", (status, output))
        return output,status==0


def cred(account, subacc, access_type, nas, format_string):
        """
        
        """
        command_dict={
                             'access_type':unicode(access_type),
                    }
        d = account
        for x in d.keys():
            
            command_dict.update({
                          'acc_%s' % x: unicode(d[x]),
                           })
        d = nas
        for x in d.keys():
            
            command_dict.update({
                          'nas_%s' % x: unicode(d[x]),
                           })
        if subacc :
            d = subacc
            for x in d.keys():
                
                command_dict.update({
                              'subacc_%s' % x: unicode(d[x]),
                               })

        command_string=command_string_parser(command_string=format_string, command_dict=command_dict)        
        if not command_string: return True
        #print command_string
        #print command_dict
        #log_debug_('CRED ssh dictionary: %s' % command_dict) 
        try:
            
            
            if nas.get('type')!='localhost':
                sshclient=ssh_client(host=nas.get('ipaddress'), username=nas.get('login'), password=nas.get('password'), command = command_string)
                
                del sshclient
            elif nas.get("type")=='localhost':
                status, output = commands.getstatusoutput(command_string)
                
            return True
        except Exception, e:
            print 'CRED ssh error: %s' % repr(e)
            return False


        
cs_pattern = re.compile('\$[_\w]+')
def command_string_parser(command_string='', command_dict={}):
    """
    
    """    
    if command_string==None:
        return ''
    import re
    if len(command_string) == 0 or len(command_dict) == 0:
        return ''
    
    match = cs_pattern.finditer(command_string)
    if match is None:
        return ''
    params = [m.group()[1:] for m in match]
    for p in params :
        if p in command_dict.keys() :
            cs_str = re.compile( '\$%s' % p)
            command_string = cs_str.sub(str(command_dict[p]),command_string)
    #print command_string
    return command_string



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
    global s
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((nas_ip, 8728))
        s.settimeout(5)
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

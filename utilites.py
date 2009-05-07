#-*-coding=utf-8-*-

from __future__ import with_statement
from distutils.dist import command_re
from dateutil.relativedelta import relativedelta
#from log_adapter import log_debug_, log_info_, log_warning_, log_error_
from period_utilities import in_period, in_period_info, settlement_period_info

import re
import glob
import packet
import socket
import cPickle
import logging
import psycopg2
import traceback
import datetime, calendar, time
import os, sys, time, md5, binascii, socket, select

ssh_exec = False
#try: 
#    from ssh_utilities import SSHClient, ssh_execute
#    ssh_exec = True
#except:
#    print >> sys.stderr, "Problems with importing ssh wrapper from ssh_utilities, reverting to paramiko"
from ssh_paramiko import SSHClient

def log_info_(lstr, level=1):
    log_adapt(lstr, level)
    
def log_debug_(lstr, level=0):
    log_adapt(lstr, level)
    
def log_warning_(lstr, level=2):
    log_adapt(lstr, level)
    
def log_error_(lstr, level=3):
    log_adapt(lstr, level)
    
def log_adapt(lstr, level):
    print lstr
    
class IPNAccount(object):
    def __init__(self):
        nas_ip=''
        login=''
        password=''
        format_string=''
        access_type=''
        username=''
        user_id=''
        ipaddress=''
        mac_address=''

def PoD(dict, account_id, account_name, account_vpn_ip, account_ipn_ip, account_mac_address, access_type, nas_ip, nas_type, nas_name='', nas_secret='', nas_login='', nas_password='', session_id='', format_string=''):
    """
    @param account_id: ID of account
    @param account_name: name of account
    @param account_vpn_ip: VPN Address
    @param account_ipn_ip: IPN Address
    @param account_mac_address: Hardware address of account computer  
    @param nas_ip: IP address of NAS
    @param nas_name: Network Identify NAS
    @param nas_secret: Secret phrase
    @param nas_login: Login for SSH
    @param nas_password: Password for SSH
    @param session_id: ID of VPN session
    @param format_string: format string       
    """
    #log_debug_('PoD args: %s' % str([account_id, account_name, account_vpn_ip, account_ipn_ip, account_mac_address, access_type, nas_ip, nas_type, nas_name, nas_secret, nas_login, nas_password, session_id, format_string]))
    
    access_type = access_type.lower()
    if format_string=='' and access_type in ['pptp', 'pppoe']:
        
        log_debug_("Send PoD")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0',24000))
        doc = packet.AcctPacket(code=40, secret=str(nas_secret), dict=dict)
        doc.AddAttribute('NAS-IP-Address', str(nas_ip))
        doc.AddAttribute('NAS-Identifier', str(nas_name))
        doc.AddAttribute('User-Name', str(account_name))
        doc.AddAttribute('Acct-Session-Id', str(session_id))
        doc.AddAttribute('Framed-IP-Address', str(account_vpn_ip))
        doc_data=doc.RequestPacket()
        sock.sendto(doc_data,(str(nas_ip), 1700))
        (data, addrport) = sock.recvfrom(8192)
        doc=packet.AcctPacket(secret=nas_secret, dict=dict, packet=data)
        sock.close()

        return doc.has_key("Error-Cause")==False
    elif format_string!='' and access_type in ['pptp', 'pppoe']:
        #ssh
        log_debug_('POD ROS')
        command_string=command_string_parser(command_string=format_string, command_dict=
                            {'access_type': access_type, 'username': account_name,'user_id': account_id,
                             'account_ipn_ip': account_ipn_ip, 'account_vpn_ip': account_vpn_ip,
                             'account_mac_address':account_mac_address,'session': session_id})
        #print command_string
        if nas_type=='mikrotik3' and False:
            """
            Закомментировано до разъяснения ситуации с ROS API
            """
            """
            ДОбавить проверку что вернул сервер доступа
            """
            log_debug_('POD ROS3')
            rosClient(host=nas_ip, login=nas_login, password=nas_password, command=command_string)
            return True
        else:
            try:
                if ssh_exec:
                    sshclient = ssh_execute(nas_login, nas_ip, nas_password, command_string)
                    log_debug_('PoD ssh %s' % sshclient)
                else:
                    sshclient=SSHClient(host=nas_ip, port=22, username=nas_login, password=nas_password)
                    log_debug_('ssh connected')
                    res=sshclient.send_command(command_string)
                    sshclient.close_channel()
                
                log_debug_('POD SSH')
                return True
            except Exception, e:
                log_error_('PoD SSH exception: %s' % repr(e))
                return False

def change_speed(dict, account_id, account_name, account_vpn_ip, account_ipn_ip, account_mac_address, nas_ip, nas_type, nas_name, nas_login, nas_password, nas_secret='',session_id='', access_type='', format_string='', speed=''):
    
    access_type = access_type.lower()
    print access_type
    if format_string=='' and access_type in ['pptp', 'pppoe']:
        #Send CoA
        
        #speed_string= create_speed_string(speed, coa=True)
        speed_string= create_speed_string(speed)
        #print speed_string
        log_debug_('send CoA')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0',24000))
        doc = packet.AcctPacket(code=43, secret=nas_secret, dict=dict)
        doc.AddAttribute('NAS-IP-Address', nas_ip)
        doc.AddAttribute('NAS-Identifier', nas_name)
        doc.AddAttribute('User-Name', account_name)
        doc.AddAttribute('Acct-Session-Id', str(session_id))
        doc.AddAttribute('Framed-IP-Address', str(account_vpn_ip))
        doc.AddAttribute((14988,8), speed_string)
            
        doc_data=doc.RequestPacket()
        sock.sendto(doc_data,(nas_ip, 1700))
        (data, addrport) = sock.recvfrom(8192)
        doc=packet.AcctPacket(secret=nas_secret, dict=dict, packet=data)

        #for key,value in doc.items():
        #    print doc._DecodeKey(key),doc[doc._DecodeKey(key)][0]

        sock.close()
        #try:
        #    print doc['Error-Cause'][0]
        #except:
        #    pass
        return doc.has_key("Error-Cause")==False
    elif format_string!='' and access_type in ['pptp', 'pppoe', 'ipn']:
        #ssh
        log_debug_('SetSpeed Via SSH')
        command_dict={
                             'access_type':access_type,
                             'username': account_name,
                             'user_id':account_id,
                             'account_ipn_ip': account_ipn_ip,
                             'account_vpn_ip': account_vpn_ip,
                             'account_mac_address':account_mac_address,
                             'session': session_id,
                             }
        speed = get_decimals_speeds(speed)
        #print speed
        speed = speed_list_to_dict(speed)
        command_dict.update(speed)
        print 'command_dict=', command_dict
        command_string=command_string_parser(command_string=format_string, command_dict=command_dict)
        
        log_debug_("Change Speedcommand_string= %s" % command_string)
        try:
            if ssh_exec:
                    sshclient = ssh_execute(nas_login, nas_ip, nas_password, command_string)
                    log_debug_('Change speed SSH reply: %s' % sshclient)
            else:
                sshclient=SSHClient(host=nas_ip, port=22, username=nas_login, password=nas_password)
                log_debug_('ssh connected')
                res=sshclient.send_command(command_string)
                sshclient.close_channel()
            return True
        except Exception, e:
            log_error_('Change Speed ssh exception %s' % repr(e))
            return False
    return False

def cred(account_id, account_name, account_password, access_type, account_vpn_ip, account_ipn_ip, account_mac_address, nas_ip, nas_login, nas_password, format_string):
        """
        Функция для вклюения/выключения пользователй на сервере доступа
        """
        command_dict={'access_type':access_type,
                      'password':account_password, 'username': account_name, 'user_id':account_id,        
                      'account_ipn_ip': account_ipn_ip, 'account_vpn_ip': account_vpn_ip,
                      'account_mac_address':account_mac_address}

        command_string=command_string_parser(command_string=format_string, command_dict=command_dict)        
        #print command_string
        try:
            if ssh_exec:
                sshclient = ssh_execute(nas_login, nas_ip, nas_password, command_string)
                log_debug_('CRED ssh reply: %s' % sshclient)
            else:
                sshclient=SSHClient(host=nas_ip, port=22, username=nas_login, password=nas_password)
                log_debug_('CRED ssh connected')
                res=sshclient.send_command(command_string)
                sshclient.close_channel()
            return True
        except Exception, e:
            log_error_('CRED ssh error: %s' % repr(e))
            return False

cs_pattern = re.compile('\$[_\w]+')
def command_string_parser(command_string='', command_dict={}):
    """
    
    """    
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


def create_nulls(param):
    if param==None:
        return 0
    if param=="None":
        return 0

def create_speed_string(params, coa=False):
    #print params
    #params=map(lambda x: params[x]=='None' and 0 or x, params)
    result=''

    if coa==True:
        result+="%s" % params['max_limit']
        #burst_limit
        result+=" %s" % params['burst_limit']
        #burst_treshold
        result+=" %s" % params['burst_treshold']
        #burst_time
        result+=" %s" % params['burst_time']
        #priority
        result+=" %s" % params['priority']
        #min_limit        
        result+=" %s" % params['min_limit']
        
    else:
        result+="%s" % params[0]
        #burst_limit
        result+=" %s" % params[1]
        #burst_treshold
        result+=" %s" % params[2]
        #burst_time
        result+=" %s" % params[3]
        #priority
        result+=" %s" % params[4]
        #min_limit
        result+=" %s" % params[5]

    return str(result)

# Parsers

class ActiveSessionsParser:
    """
    parse strings like
    Flags: R - radius
    0 R name=dolphinik service=pptp caller-id=10.10.1.2 address=192.168.12.3 uptime=1h56m6s encoding="" session-id=0x81A00000 limit-bytes-in=0 limit-bytes-out=0
    1   name=ppp1 service=pptp caller-id=10.10.1.3 address=192.168.12.2 uptime=51s encoding=MPPE128 stateless session-id=0x81A00001 limit-bytes-in=0 limit-bytes-out=0
    giving

    Usage:

    asp = ActiveSessionsParser(test_string)
    list = sap.parse()

    print list
    >> [{'caller-id': '10.10.1.2', 'session-id': '0x81A00000', 'name': 'dolphinik', 'service': 'pptp', 'address': '192.168.12.3'},
    >> {'caller-id': '10.10.1.3', 'session-id': '0x81A00001', 'name': 'ppp1', 'service': 'pptp', 'address': '192.168.12.2'}]

    """
    start_field = 'name'
    fields = ('name','service','caller-id','address','session-id','target-addresses')
    strings = []
    ar = []

    def __init__(self, string):
        import re
        #sts = string.split('\n')
        for s in string :
            m = re.search('(%s.*)' % self.start_field,s)
            try:
                self.strings.append(m.groups()[0])
            except:
                pass
        #print self.strings


    def parse(self):
        """
        return list of dicts
        """
        for s in self.strings:
            strstr = {}
            for s in [x.strip() for x in s.split(' ') if len(x) >0] :
                try:
                    x,y = s.split('=')
                    if x in self.fields :
                        strstr[x] = y
                except ValueError :
                    pass
            self.ar.append(strstr)
        return self.ar

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
    return result

def get_sessions_for_nas(nas):
    sessions = []
    if nas['type'] in ['mikrotik2.8', 'mikrotik2.9']:
        #Use SSH For fetching sessions
        if ssh_exec:
            try:
                sshclient = ssh_execute(nas_login, nas_ip, nas_password, "/ppp active print terse without-paging")
            except Exception, e:
                log_error_('Get sessions for nas SSH sshexec error: %s' % repr(e))
                return []
                
            log_info_('Get sessions for nas SSH sshexec reply: %s' % sshclient)
            if nas['type'] in ['mikrotik2.9', 'mikrotik2.8']:
                sessions=ActiveSessionsParser(sshclient.split(':')[1].strip()).parse()
        else:
            try:            
                ssh=SSHClient(host=nas['ipaddress'], port=22, username=nas['login'], password=nas['password'])
                response=ssh.send_command("/ppp active print terse without-paging")[0]
                response = response.readlines()
                log_info_('Get sessions for nas SSH sshclient reply: %s' % response)
            except Exception, e:
                log_error_('Get sessions for nas SSH error: %s' % repr(e))
                return []
                
            #print response
            if nas['type'] in ['mikrotik2.9', 'mikrotik2.8']:
                sessions=ActiveSessionsParser(response).parse()
            ssh.close_channel()
        
    elif nas['type']==u'mikrotik3':
        #Use ROS API for fetching sessions
        try:
            sessions = convert(rosClient(nas['ipaddress'], nas['login'], nas['password'], r"/ppp/active/getall"))
        except Exception, e:
            log_error_('Get sessions for nas SSH rosapi error: %s' % repr(e))

    return sessions

def get_active_sessions(nas):
    return get_sessions_for_nas(nas)     
    
def convert(alist):
    return [dict(y[1:].split('=') for y in x if not y[0] in ('.','!')) for x in alist]

def convert_values(value):
    if str(value).endswith('k'):
        return str(int(str(value)[0:-1])*1000)
    elif str(value).endswith('M'):
        return str(int(str(value)[0:-1])*1000*1000)
    else:
        return str(value)
                
def get_decimals_speeds(params):
    #print "before", params
    i = 0
    for param in params:
        #values = map(convert_values, str(params[param]).split('/'))
        values = map(convert_values, str(param).split('/'))
        #print values
        params[i] ='/'.join(values)
        i += 1
    #print 'after', params
    return params

def formatator(x,y):
    if x!=-1 and y==-1:
        return "%s/%s" % (x,x)
    elif x==-1 and y==-1:
        return "0/0"
    elif x!=-1 and y!=-1:
        return "%s/%s" % (x,y)


rawstr = r"""^(?:(?P<rxrate>\w+)(?:/(?P<txrate>\w*))?(?:\s+(?P<rxbrate>\w*)(?:/(?P<txbrate>\w*))?(?:\s+(?P<rbthr>\w*)(?:/(?P<tbthr>\w*))?)?(?:\s+(?P<rbtm>\w*)(?:/(?P<tbtm>\w*))?)?(?:\s+(?P<prt>\d))?(?:\s+(?P<rrm>\w*)(?:/(?P<trm>\w*))?)?)?)"""
compile_obj = re.compile(rawstr)    
def parse_custom_speed(speed_string):
    # common variables
    #print speed_string
    #rawstr = r"""^(?:(?P<rxrate>\w+)(?:/(?P<txrate>\w*))?(?:\s+(?P<rxbrate>\w*)(?:/(?P<txbrate>\w*))?(?:\s+(?P<rbthr>\w*)(?:/(?P<tbthr>\w*))?)?(?:\s+(?P<rbtm>\w*)(?:/(?P<tbtm>\w*))?)?(?:\s+(?P<prt>\d))?(?:\s+(?P<rrm>\w*)(?:/(?P<trm>\w*))?)?)?)"""
    #embedded_rawstr = r"""^(?:(?P<rxrate>\w+)(?:/(?P<txrate>\w*))?(?:\s+(?P<rxbrate>\w*)(?:/(?P<txbrate>\w*))?(?:\s+(?P<rbthr>\w*)(?:/(?P<tbthr>\w*))?)?(?:\s+(?P<rbtm>\w*)(?:/(?P<tbtm>\w*))?)?(?:\s+(?P<prt>\d))?(?:\s+(?P<rrm>\w*)(?:/(?P<trm>\w*))?)?)?)"""
    #matchstr = """128k/128k   200k/200k     100k/100k     5/5 1  40k/40k"""
    
    # method 1: using a compile object
    #compile_obj = re.compile(rawstr)
    match_obj = compile_obj.search(speed_string)
    
    # Retrieve group(s) by name
    rxrate = match_obj.group('rxrate') or -1
    txrate = match_obj.group('txrate') or -1
    rxbrate = match_obj.group('rxbrate') or -1
    txbrate = match_obj.group('txbrate') or -1
    rbthr = match_obj.group('rbthr') or -1
    tbthr = match_obj.group('tbthr') or -1
    rbtm = match_obj.group('rbtm') or -1
    tbtm = match_obj.group('tbtm') or -1
    prt = match_obj.group('prt') or 8
    rrm = match_obj.group('rrm') or -1
    trm = match_obj.group('trm') or -1

    return {'max_limit': formatator(rxrate, txrate), "burst_limit": formatator( rxbrate, txbrate), 'burst_treshold': formatator(rbthr, tbthr), 'burst_time': formatator(rbtm, tbtm), 'priority': prt, 'min_limit': formatator(rrm, trm)}

def speed_list_to_dict(spList):
    dkeys = ['max_limit', "burst_limit", 'burst_treshold', 'burst_time', 'priority', 'min_limit']
    return dict(zip(dkeys, spList))

def parse_custom_speed_lst(speed_string):
    match_obj = compile_obj.search(speed_string)    
    # Retrieve group(s) by name
    rxrate = match_obj.group('rxrate') or -1
    txrate = match_obj.group('txrate') or -1
    rxbrate = match_obj.group('rxbrate') or -1
    txbrate = match_obj.group('txbrate') or -1
    rbthr = match_obj.group('rbthr') or -1
    tbthr = match_obj.group('tbthr') or -1
    rbtm = match_obj.group('rbtm') or -1
    tbtm = match_obj.group('tbtm') or -1
    prt = match_obj.group('prt') or 8
    rrm = match_obj.group('rrm') or -1
    trm = match_obj.group('trm') or -1
    return [formatator(rxrate, txrate), formatator(rxbrate, txbrate), formatator(rbthr, tbthr), formatator(rbtm, tbtm), prt, formatator(rrm, trm)]

def split_speed(speed):
    return speed.split("/")

def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).
    """

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(int(el))
    return result

def correct_speed(speed, correction):
    """
    Возвращает скорректированную скорость
    """
    res = []
    #max
    res.append("%s/%s" % (speed[0]*correction[0]/100, speed[1]*correction[1]/100))
    #burst in
    res.append("%s/%s" % (speed[2]*correction[2]/100, speed[3]*correction[3]/100))
    #burst treshold
    res.append("%s/%s" % (speed[4]*correction[4]/100, speed[5]*correction[5]/100))
    #burst time
    res.append("%s/%s" % (correction[6], correction[7]))
    #priority
    res.append("%s" % correction[8])
    #min
    res.append("%s/%s" % (speed[9]*correction[9]/100, speed[10]*correction[10]/100))
    return res



   
def get_corrected_speed(speed, correction):
    if correction is not None:
        return correct_speed(flatten(map(split_speed,get_decimals_speeds(speed))), correction)
    else:
        return speed
    
'''use Old = use old caches if any errors were encountered during renewing process'''
def renewCaches(cur, cacheMaster, cacheType, code, cargs=(), useOld = True):
    ptime =  time.time()
    ptime = ptime - (ptime % 20)
    cacheDate = datetime.datetime.fromtimestamp(ptime)
    try:
        caches = cacheType(cacheDate, *cargs)
        caches.getdata(cur)
        cur.connection.commit()
        caches.reindex()
    except Exception, ex:
        if isinstance(ex, psycopg2.DatabaseError):
            log_error_('#30%s0001 renewCaches attempt failed due to database error: %s' % (code, repr(ex)))
        else: 
            log_error_('#30%s0002 renewCaches attempt failed due to error: %s \n %s' % (code, repr(ex), traceback.format_exc()))
    else:
        cacheMaster.read = True
            
    if cacheMaster.read:
        with cacheMaster.lock:
            cacheMaster.cache, cacheMaster.date = caches, cacheDate
    elif useOld and cacheMaster.cache:
        log_warning_('#30%s0001 renewCaches: using old caches!' % (code,))
        with cacheMaster.lock:
            cacheMaster.date = cacheDate
    else:
        raise Exception("#30%s0049 renewCaches: attempt failed: fail propagated" % (code,))
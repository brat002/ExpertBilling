#-*-coding: utf-8 -*-

from celery.task import task
import os, sys
import decimal
import commands
from pyrad import dictionary
import re
import socket
from pyrad import packet
import paramiko
import psycopg2
import datetime
from hashlib import md5
import binascii
import ConfigParser
import urllib, urllib2
import BeautifulSoup
import simplejson
config = ConfigParser.ConfigParser()
BILLING_PATH = '/opt/ebs/data/'
config.read(os.path.join(BILLING_PATH, "ebs_config.ini"))
SSH_BACKEND = config.get("core", "ssh_backend") if config.has_option("core", "ssh_backend") else None 
db_name = "db"
DICT = dictionary.Dictionary(os.path.join(BILLING_PATH, "dicts/dictionary"),os.path.join(BILLING_PATH, "dicts/dictionary.microsoft"), os.path.join(BILLING_PATH, 'dicts/dictionary.mikrotik') , os.path.join(BILLING_PATH, 'dicts/dictionary.cisco'))
import logging


DSN = "dbname='%s' user='%s' host='%s' port='%s' password='%s'" % (config.get(db_name, "name"), config.get(db_name, "username"), \
                                                                         config.get(db_name, "host"), config.get(db_name, "port"), config.get(db_name, "password"))

def get_connection():
    conn = psycopg2.connect(DSN)
    conn.set_client_encoding('UTF8')
    conn.set_isolation_level(0)
    return conn

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
            command_string = cs_str.sub(unicode(command_dict[p]),command_string)
    #print command_string
    return command_string

def ssh_client(host, username, password, command, logger):
    if not SSH_BACKEND:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(host, username=username, password=password, allow_agent=False, look_for_keys=False)
        logger.debug("NAS Manipulation command string %s" % (command, ))   
        stdin, stdout, stderr = ssh.exec_command(command)
        out = stdout.readlines()
        err = stderr.readlines()
        ssh.close()
        return err==[]
    else:
        command_string=command_string_parser(command_string=SSH_BACKEND, command_dict=
                            {'host': host, 'username': username,'password': password,
                             'command': command})    
        logger.debug("NAS Manipulation command string %s", (command_string, ))    
        status, output = commands.getstatusoutput(command_string)
        logger.debug("NAS Manipulation try status=%s output=%s", (status, output))
        return output,status==0

def convert_values(value):
    if str(value).endswith(('k', 'K')):
        return str(int(str(value)[0:-1])*1000)
    elif str(value).endswith(('M', 'm')):
        return str(int(str(value)[0:-1])*1000*1000)
    else:
        return str(value)

@task
def update_vpn_speed_state(nas_id, nas_port_id, session_id, newspeed):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""UPDATE radius_activesession SET speed_string=%s, speed_change_queued=NULL WHERE id=%s and nas_int_id=%s and nas_port_id=%s;
                """ , (newspeed, session_id, nas_id, nas_port_id))
    conn.commit()
    cur.close()
    conn.close()

@task
def update_ipn_speed_state(subaccount_id, newspeed):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE billservice_subaccount SET speed=%s, ipn_queued=NULL WHERE id=%s;", (newspeed, subaccount_id))
    conn.commit()
    cur.close()
    conn.close()

@task
def ipn_add_state(subaccount_id, cb):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE billservice_subaccount SET ipn_added=%s, ipn_queued=NULL WHERE id=%s",  (True, subaccount_id))
    conn.commit()
    cur.close()
    conn.close()
        
@task
def ipn_del_state(subaccount_id, cb):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE billservice_subaccount SET ipn_added=%s, ipn_queued=NULL WHERE id=%s",  (False, subaccount_id))
    conn.commit()
    cur.close()
    conn.close()
    if cb:
        cb.apply()
    
@task
def adds_enable_state(id, cb):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE billservice_accountaddonservice SET action_status=%s WHERE id=%s", (True, id,))
    conn.commit()
    cur.close()
    conn.close()
    if cb:
        cb.apply()
        
@task
def adds_disable_state(id, cb):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE billservice_accountaddonservice SET action_status=%s WHERE id=%s", (False, id))
    conn.commit()
    cur.close()
    conn.close()
    if cb:
        cb.apply()
        
@task
def ipn_enable_state(subaccount_id, cb):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE billservice_subaccount SET ipn_enabled=%s, ipn_queued=NULL WHERE id=%s",  (True, subaccount_id))
    conn.commit()
    cur.close()
    conn.close()
    if cb:
        cb.apply()
        
@task
def ipn_disable_state(subaccount_id, cb):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE billservice_subaccount SET ipn_enabled=%s, ipn_queued=NULL WHERE id=%s",  (False, subaccount_id))
    conn.commit()
    cur.close()
    conn.close()
    if cb:
        cb.apply()


@task
def update_pod_state(nas_id, nas_port_id, session_id):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""UPDATE radius_activesession SET pod_queued=NULL WHERE id=%s and nas_int_id=%s and nas_port_id=%s;
                """ , ( session_id, nas_id, nas_port_id))
    conn.commit()
    cur.close()
    conn.close()


def get_decimals_speeds(params):
    #print "before", params
    i = 0
    res = []
    for param in params:
        res.append(convert_values(param))
        i += 1
    #print 'after', params
    return res
def speed_list_to_dict(spList):
    dkeys = ['max_limit_rx', 'max_limit_tx', "burst_limit_rx", "burst_limit_tx", 'burst_treshold_rx', 'burst_treshold_tx', 'burst_time_rx', 'burst_time_tx', 'min_limit_rx', 'min_limit_tx', 'priority']
    return dict(zip(dkeys, spList))


@task
def PoD(account, subacc, nas, access_type, session_id='', vpn_ip_address='', caller_id='', format_string='', cb=None):
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
    logger = logging.basicConfig(filename='log/workers_pod.log', level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)
    logger = logging
    access_type = access_type.lower()
    if (nas.get('speed_value1') or nas.get('speed_value2')) and ((format_string=='' and access_type in ['pptp', 'l2tp', 'pppoe', 'lisg'] ) or access_type=='hotspot' or nas.get('type')=='cisco'):
        logger.info("Send PoD")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT ap.access_type FROM billservice_account as a
            JOIN billservice_tariff as t ON t.id=get_tarif(a.id)
            JOIN billservice_accessparameters as ap ON ap.id=t.access_parameters_id
            WHERE a.id=%s
        """, (account.get('account_id'),))
        conn.commit()
        tariff_access_type = cur.fetchone()[0]
        cur.close()
        conn.close()
    
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(20)
        sock.bind(('0.0.0.0', 0))
        doc = packet.AcctPacket(code=40, secret=str(nas.get('secret')), dict=DICT)
        doc.AddAttribute('NAS-IP-Address', str(nas.get('ipaddress')))
        if nas.get('type')!='cisco' and nas.get('identify'):
            doc.AddAttribute('NAS-Identifier', str(nas.get('identify')))
            
        if access_type=='lisg':
            doc.AddAttribute('User-Name', str(subacc.get('ipn_ip_address')))
        elif subacc.get('username') and tariff_access_type not in ['HotSpotIp+Mac', 'HotSpotIp+Password', 'HotSpotMac', 'HotSpotMac+Password']:
            doc.AddAttribute('User-Name', unicode(subacc.get('username')))
            
        if nas.get('type')=='cisco':
            logger.info("Normalization cisco session id")
            doc.AddAttribute('Acct-Session-Id', re.sub('^0+', '', str(session_id) ))
        else:
            doc.AddAttribute('Acct-Session-Id', str(session_id))
            
        if access_type=='hotspot' and vpn_ip_address and  tariff_access_type not in [ 'HotSpotMac', ]:
            doc.AddAttribute('Framed-IP-Address', str(vpn_ip_address))
        elif access_type not in ('hotspot', 'lisg') and vpn_ip_address:
            doc.AddAttribute('Framed-IP-Address', str(vpn_ip_address))
            
        if caller_id and nas.get('type')!='cisco' :
            doc.AddAttribute('Calling-Station-Id', str(caller_id))
            
        doc_data=doc.RequestPacket()
        sock.sendto(doc_data,(str(nas.get('ipaddress')), 1700))
        (data, addrport) = sock.recvfrom(8192)
        doc=packet.AcctPacket(secret=str(nas.get('secret')), dict=dict, packet=data)
        sock.close()

        if cb:
            cb.apply()
        return doc.get("Error-Cause")
    elif format_string!='' and access_type in ['pptp', 'l2tp', 'pppoe']:
        #ssh
        
        logger.info('POD ROS')
        
        command_dict={'access_type': access_type, 'session': session_id}

        for x in nas.keys():
            
            command_dict.update({
                          'nas_%s' % x: unicode(nas[x]),
                           })

        for x in account.keys():
            command_dict.update({
                          'acc_%s' % x: unicode(account[x]),
                           })
        if subacc:
            for x in subacc.keys():
                
                command_dict.update({
                              'subacc_%s' % x: unicode(subacc[x]),
                               })
        command_dict.update({'framed_ip_address': vpn_ip_address})
        command_string=command_string_parser(command_string=format_string, command_dict=command_dict)

        try:
            output=''
            if nas.get('type')!='localhost':
                sshclient=ssh_client(host=nas.get('ipaddress'), username=nas.get('login'), password=nas.get('password'), command = command_string, logger = logger)
                logger.info('ssh connected')
                del sshclient
            elif nas.get('type')=='localhost':
                status, output = commands.getstatusoutput(command_string)
                logger.info('Local command %s was executed with status %s and output %s' % (command_string, status, output))
                if status!=0:return False

            if cb:
                cb.apply()
            logger.info('POD SSH')
            return True
        except Exception, e:
            logger.error('PoD SSH exception: %s' % repr(e))
            return False

@task
def change_speed(account, subacc ,nas, session_id='', vpn_ip_address='', access_type='', format_string='', speed='', cb=None):
    
    access_type = access_type.lower()
    """
    acc.account_id,acc.username,
    acc.vpn_ip_address,acc.ipn_ip_address,
    acc.ipn_mac_address
    nas.ipaddress,
    nas.type,
    nas.name,
    nas.login,
    nas.password,
    access_type=access_type,
    format_string=nas.ipn_speed_action,
    """
    logging.basicConfig(filename='log/workers_change_speed.log', level=logging.INFO)
    logger = logging
    speed = get_decimals_speeds(speed)
    speed = speed_list_to_dict(speed)
    status = False
    if (nas.get('speed_value1') or nas.get('speed_value2')) and ((format_string=='' and access_type in ['pptp', 'l2tp', 'pppoe', 'lisg']) or access_type=='hotspot' or nas.get('type')=='cisco'):

        logger.info('send CoA')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(20)
        sock.bind(('0.0.0.0', 0))
        doc = packet.AcctPacket(code=43, secret=str(nas.get('secret')), dict=DICT)
        doc.AddAttribute('NAS-IP-Address', str(nas.get('ipaddress')))
        if nas.get('type')!='cisco' and nas.get('identify'):
            doc.AddAttribute('NAS-Identifier', str(nas.get('identify')))
        if access_type=='lisg':
            doc.AddAttribute('User-Name', str(subacc.get('ipn_ip_address')))
        else:
            doc.AddAttribute('User-Name', unicode(subacc.get('username')))
        if nas.get('type')=='cisco':
            logger.info("Normalization cisco session id")
            doc.AddAttribute('Acct-Session-Id', re.sub('^0+', '', str(session_id) ))
        else:
            doc.AddAttribute('Acct-Session-Id', str(session_id))
        if access_type=='hotspot' and vpn_ip_address:
            doc.AddAttribute('Framed-IP-Address', str(subacc.get('ipn_ip_address')))
        elif access_type not in ('hotspot', 'lisg') and vpn_ip_address:
            doc.AddAttribute('Framed-IP-Address', str(vpn_ip_address))
        #doc.AddAttribute((14988,8), speed_string)
        command_dict={
                             'access_type':str(access_type),
                             'session': str(session_id),
                             }


        for x in nas.keys():
            
            command_dict.update({
                          'nas_%s' % x: unicode(nas[x]),
                           })
            

        for x in account.keys():
            
            command_dict.update({
                          'acc_%s' % x: unicode(account[x]),
                           }) 
        if subacc:

            for x in subacc.keys():
                
                command_dict.update({
                              'subacc_%s' % x: unicode(subacc[x]),
                               })    
        

        command_dict.update(speed)
        command_dict.update({'framed_ip_address': vpn_ip_address})
        if nas.get('speed_value1'):
            result_params = unicode(command_string_parser(command_string=nas.get('speed_value1'), command_dict=speed))
            if result_params and nas.get('speed_vendor_1'):
                doc.AddAttribute((nas.get('speed_vendor_1'), nas.get('speed_attr_id1')),result_params)
            elif result_params and not nas.get('speed_vendor_1'):
                doc.AddAttribute(nas.get('speed_attr_id1'),unicode(result_params))

        if nas.get('speed_value2'):
            result_params = unicode(command_string_parser(command_string=nas.get('speed_value2'), command_dict=speed))
            if result_params and nas.get('speed_vendor_2'):
                doc.AddAttribute((nas.get('speed_vendor_2'), nas.get('speed_attr_id2')),result_params)
            elif result_params and not nas.get('speed_vendor_2'):
                doc.AddAttribute(nas.get('speed_attr_id2'),unicode(result_params))
                    
        doc_data=doc.RequestPacket()
        logger.info('CoA socket send: %s' % unicode(nas.ipaddress))
        sock.sendto(doc_data,(nas.get('ipaddress'), 1700))
        (data, addrport) = sock.recvfrom(8192)
        logger.info('CoA socket get: %s' % str(addrport))
        doc=packet.AcctPacket(secret=nas.get('secret'), dict=dict, packet=data)

        sock.close()

        status = doc.has_key("Error-Cause")==False
        if status==True and cb:
            cb.apply()
        return status
    elif format_string!='' and access_type in ['pptp', 'l2tp', 'pppoe', 'ipn']:
        #ssh
        logger.info('SetSpeed Via SSH/local command')
        command_dict={
                             'access_type':str(access_type),
                             'session': str(session_id),
                    }

        for x in nas.keys():
            
            command_dict.update({
                          'nas_%s' % x: unicode(nas[x]),
                           })
            

        for x in account.keys():
            
            command_dict.update({
                          'acc_%s' % x: unicode(account[x]),
                           }) 
        if subacc:
            for x in subacc.keys():
                command_dict.update({
                              'subacc_%s' % x: unicode(subacc[x]),
                               })   
                

        command_dict.update(speed)
        command_dict.update({'framed_ip_address': vpn_ip_address})
        command_string=command_string_parser(command_string=format_string, command_dict=command_dict)
        if not command_string: return True
        #print command_string
        logger.info("Change Speed command_string= %s" % command_string)
        try:
            status = True
            output=''
            if nas.get('type')!='localhost':
                status=ssh_client(host=nas.get('ipaddress'), username=nas.get('login'), password=nas.get('password'), command = command_string, logger=logger)
                logger.info('ssh connected')

            elif nas.get('type')=='localhost':
                status, output = commands.getstatusoutput(command_string)
                status = True if status==0 else False
            if status==True and cb:
                cb.apply()
                logger.info('Command %s was executed with status %s and output %s' % (command_string, status, output))
        except Exception, e:
            logger.info('Change Speed ssh exception %s' % repr(e))
            return False
    return status


@task
def cred(account, subacc, access_type, nas, addonservice={},format_string='', cb=None):
    logging.basicConfig(filename='log/workers_pod.log', level=logging.INFO)
    logger = logging
    command_dict={
                         'access_type':unicode(access_type),
                }
    for x in nas.keys():
        
        command_dict.update({
                      'nas_%s' % x: unicode(nas[x]),
                       })
        

    for x in account.keys():
        
        command_dict.update({
                      'acc_%s' % x: unicode(account[x]),
                       }) 
    if subacc:
        for x in subacc.keys():
            command_dict.update({
                          'subacc_%s' % x: unicode(subacc[x]),
                           })   
    if addonservice:
        for x in addonservice.keys():
            command_dict.update({
                          'addons_%s' % x: unicode(addonservice[x]),
                           })   
            
    command_string=command_string_parser(command_string=format_string, command_dict=command_dict)        
    if not command_string: return True

    try:
        output=''
        if nas.get('type')!='localhost':
            status=ssh_client(host=nas.get('ipaddress'), username=nas.get('login'), password=nas.get('password'), command = command_string, logger=logger)
            logger.info('CRED ssh connected')
        elif nas.get('type')=='localhost':
            status, output = commands.getstatusoutput(command_string)
            status = True if status==0 else False
            logger.info('Local command %s was executed with status %s and output %s' % (command_string, status, output))
        if status==True and cb:
            cb.apply()
    except Exception, e:
        logger.error('CRED ssh error: %s' % repr(e))
        return False
        
class ApiRos:
    "Routeros api"
    def __init__(self, sk):
        self.sk = sk
        self.currenttag = 0
        
    def close(self):
        self.sk.close()
        
    def login(self, username, pwd):
        for repl, attrs in self.talk(["/login"]):
            chal = binascii.unhexlify(attrs['=ret'])
        md = md5()
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


def rosClient(host, login, password):
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
    return apiros


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

def make_dict(res):
    d={}
    if not res: return d
    for x in res[0]:
        r=x.split('=')
        if len(r)<2: continue
        d[r[1]]=r[2]
    return d

class HttpBot(object):
    """an HttpBot represents one browser session, with cookies."""
    def __init__(self):
        cookie_handler= urllib2.HTTPCookieProcessor()
        redirect_handler= urllib2.HTTPRedirectHandler()
        self._opener = urllib2.build_opener(redirect_handler, cookie_handler)

    def GET(self, url):
        logging.basicConfig(filename='log/workers_http_bot.log', level=logging.INFO)
        logger = logging
        logger.debug(url)
        return self._opener.open(url).read()
    
    def POST(self, url, parameters={}):
        logging.basicConfig(filename='log/workers_http_bot.log', level=logging.INFO)
        logger = logging
        logger.debug("%s %s" % (url, parameters))
        try:
            if type(parameters)==dict:
                return self._opener.open(url, urllib.urlencode(parameters)).read()
            else:
                return self._opener.open(url, parameters).read()
        except urllib2.HTTPError, e:
            logger.error(e)
        except urllib2.URLError, e:
            logger.error(e)
@task
def http_get(url):
    return HttpBot().GET(url)

@task
def http_post(url, parameters):
    st = HttpBot().POST(url, parameters)

    return st

@task
def sendsms_post(url, parameters, id=None):
    response = HttpBot().POST(url, parameters)
    logging.basicConfig(filename='log/workers_sendsms.log', level=logging.INFO)
    logger = logging
    response = BeautifulSoup.BeautifulSoup(response)

    status = response.state.text

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE sendsms_message SET sended=now(), response=%s WHERE id=%s",  (status, id))
    conn.commit()
    cur.close()
    conn.close()


@task
def sendsmsru_post(url, parameters, id=None):
    response = HttpBot().POST(url, parameters)
    logging.basicConfig(filename='log/workers_sendsms.log', level=logging.INFO)
    logger = logging
    print response

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE sendsms_message SET sended=now(), response=%s WHERE id=%s",  (response, id))
    conn.commit()
    cur.close()
    conn.close()
    
@task
def sendsmspilotru_post(url, parameters, id=None):
    headers = {
        'Content-type': 'application/json',
        'Accept': 'text/plain'
    }
    js = simplejson.dumps(parameters, ensure_ascii=False)
    
    req = urllib2.Request(url, js.encode('utf-8'), headers)
    response = urllib2.urlopen(req).read()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE sendsms_message SET sended=now(), response=%s WHERE id=%s",  (response, id))
    conn.commit()
    cur.close()
    conn.close()


@task
def subass_recreate(acc, subacc, nas, access_type='IPN'):
    cb = cred.s(acc, subacc, access_type, nas, format_string=nas.get('subacc_delete_action'), cb=ipn_del_state.s(subacc.get('id')))
    bcb = cred.s(acc, subacc, access_type, nas, format_string=nas.get('subacc_add_action'), cb = ipn_add_state.s(id, cb = cb))
    cred.delay(acc, subacc, access_type, nas, format_string=nas.get('subacc_enable_action'), cb = ipn_enable_state.s(id, cb = bcb)).apply_async()
    
    
@task
def subass_delete(acc, subacc, nas, access_type='IPN'):
    cb = cred.s(acc, subacc, access_type, nas, format_string=nas.get('subacc_disable_action'), cb=ipn_disable_state.s(subacc.get('id')))
    cred.delay(acc, subacc, access_type, nas, format_string=nas.get('subacc_delete_action'), cb=ipn_del_state.s(subacc.get('id'), cb=cb)).apply()

    
@task
def pinger(subaccount_id, ip):
    status, output = commands.getstatusoutput('ping -c 3 %s' % ip)
    
    
u"""
1. Активен/не активен 1.3.6.1.2.1.2.2.1.8 (1 - up, 2-down, 3- testing, 4- unknown, 5 - dormant, 6- notPresent, 7- lowerLayerDown)
2. Маки на порту 1.3.6.1.2.1.17.4.3.1.2 mac by port, 
3. Версия прошивки 1.3.6.1.2.1.16.19.2
4. Порты вкл/откл 1.3.6.1.2.1.2.2.1.7 (1-up, 2-down, 3-testing)
5. Скорость порта .1.3.6.1.2.1.2.2.1.5
6. Передано/приннято байт через порт .1.3.6.1.2.1.2.2.1.16/.1.3.6.1.2.1.2.2.1.10
7. Скорость на порту delta 6
8. Количество ошибок на порту .1.3.6.1.2.1.2.2.1.14/.1.3.6.1.2.1.2.2.1.20
9. Комментарий к порту iso.0.8802.1.1.2.1.3.7.1.4.
10. Возможность включить/отключить порт 1.3.6.1.2.1.2.2.1.7 (1-up, 2-down, 3-testing)
"""
@task
def get_mac_by_port(switch_ip, community='public', snmp_version='2c', port=None):
    status, output = commands.getstatusoutput('snmpwalk -v %s -c %s -O fnqT %s 1.3.6.1.2.1.17.4.3.1.2' % (snmp_version, community, switch_ip))
    
    port_mac = {}
    for line in output:
        oid, port = line.split(" ")
        mac = '.'.join(map(lambda x: hex(int(x)), oid.split('.')[:-6]))
        if not port in port_mac:
            port_mac[port]= []
        port_mac[port].append(mac)
    
    return port_mac
@task
def get_port_oper_status(switch_ip, community='public', snmp_version='2c', port=''):
    status, output = commands.getstatusoutput('snmpwalk -v %s -c %s -O fnqT %s 1.3.6.1.2.1.2.2.1.8%s' % (snmp_version, community, switch_ip, '.%s' % port if port else ''))
    
    port_status = {}
    for line in output:
        oid, port = line.split(" ")
        status = oid.split('.')[:-1]
        port_status[port]= status
    if port:
        return port_status[port]
    return port_status
@task
def get_port_speed(switch_ip, community='public', snmp_version='2c', port=None):
    status, output = commands.getstatusoutput('snmpwalk -v %s -c %s -O fnqT %s .1.3.6.1.2.1.2.2.1.5' % (snmp_version, community, switch_ip))
    
    port_status = {}
    for line in output:
        oid, port = line.split(" ")
        status = oid.split('.')[:-1]
        port_status[port]= status
    
    return port_status

@task
def get_ports_comment(switch_ip, community='public', snmp_version='2c', port=None):
    status, output = commands.getstatusoutput('snmpwalk -v %s -c %s -O fnqT %s iso.0.8802.1.1.2.1.3.7.1.4.' % (snmp_version, community, switch_ip))
    
    port_status = {}
    for line in output:
        oid, port = line.split(" ")
        status = oid.split('.')[:-1]
        port_status[port]= status
    return port_status

@task
def get_port_inout(switch_ip, community='public', snmp_version='2c', port=None):
    #in
    status, output = commands.getstatusoutput('snmpwalk -v %s -c %s -O fnqT %s .1.3.6.1.2.1.2.2.1.16' % (snmp_version, community, switch_ip))
    
    port_status = {}
    for line in output:
        oid, port = line.split(" ")
        status = oid.split('.')[:-1]
        if not port in port_status:
            port_status[port]=[]
        port_status[port][0]= status

    #out
    status, output = commands.getstatusoutput('snmpwalk -v %s -c %s -O fnqT %s .1.3.6.1.2.1.2.2.1.10' % (snmp_version, community, switch_ip))
    
    port_status = {}
    for line in output:
        oid, port = line.split(" ")
        status = oid.split('.')[:-1]
        if not port in port_status:
            port_status[port]=[]
        port_status[port][1]= status

    
    return port_status

@task
def get_port_errors(switch_ip, community='public', snmp_version='2c', port=None):
    #in
    status, output = commands.getstatusoutput('snmpwalk -v %s -c %s -O fnqT %s .1.3.6.1.2.1.2.2.1.14' % (snmp_version, community, switch_ip))
    
    port_status = {}
    for line in output:
        oid, port = line.split(" ")
        status = oid.split('.')[:-1]
        if not port in port_status:
            port_status[port]=[]
        port_status[port][0]= status

    #out
    status, output = commands.getstatusoutput('snmpwalk -v %s -c %s -O fnqT %s .1.3.6.1.2.1.2.2.1.20' % (snmp_version, community, switch_ip))
    
    port_status = {}
    for line in output:
        oid, port = line.split(" ")
        status = oid.split('.')[:-1]
        if not port in port_status:
            port_status[port]=[]
        port_status[port][1]= status

    
    return port_status


@task
def get_switch_fw_version(switch_ip, community='public', snmp_version='2c'):
    status, output = commands.getstatusoutput('snmpget -v %s -c %s -O fnqT %s 1.3.6.1.2.1.16.19.2.0' % (snmp_version, community, switch_ip))

@task
def set_switch_port_admin_status(switch_ip, port, community='private', snmp_version='2c', status=True):
    status, output = commands.getstatusoutput('snmpset -v %s -c %s -O fnqT %s 1.3.6.1.2.1.2.2.1.7.%s integer %s' % (snmp_version, community, switch_ip, port, 1 if status else 2))

from celery.task.schedules import crontab
from celery.task import periodic_task

@periodic_task(run_every=crontab(minute="*/5"))
def get_switch_function():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, snmp_version, snmp_community, ipaddress FROM billservice_switch WHERE snmp_support=True")
    conn.commit()
    cur.close()
    conn.close()    
    
@periodic_task(run_every=crontab(minute="*/1"))
def get_radius_stat():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT nas_int_id, count(*) FROM radius_activesession WHERE session_status='ACTIVE' GROUP BY nas_int_id ")
    conn.commit()
    now = datetime.datetime.now()
    data = cur.fetchall()
    if data:
        for nas_id, count in data:
            cur.execute("""SELECT radiusstat_active_insert(%s,  %s, %s::timestamp without time zone)
                                            """, (nas_id, count, now))
            conn.commit()
    cur.close()
    conn.close()   

@periodic_task(run_every=crontab(minute="0"))
def clear_ipinuse_function():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("delete from billservice_ipinuse where datetime <now()-interval '2 days' and  disabled is not null;")
    conn.commit()
    cur.close()
    conn.close()


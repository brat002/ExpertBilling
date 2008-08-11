#-*-coding=utf-8-*-
from distutils.dist import command_re
import packet
import socket
import datetime, calendar
from dateutil.relativedelta import relativedelta
import paramiko
import sys,  time, md5, binascii, socket, select

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
    #print account_id, account_name, account_vpn_ip, account_ipn_ip, account_mac_address, access_type, nas_ip, nas_type, nas_name, nas_secret, nas_login, nas_password, session_id, format_string
    
    access_type = access_type.lower()
    if format_string=='' and access_type in ['pptp', 'pppoe']:
        
        #Send PoD
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

        #for key,value in doc.items():
        #    print doc._DecodeKey(key),doc[doc._DecodeKey(key)][0]

        sock.close()
        #try:
        #    print doc['Error-Cause'][0]
        #except:
        #    pass
        return doc.has_key("Error-Cause")==False
    elif format_string!='' and access_type in ['pptp', 'pppoe']:
        #ssh
        print 'POD ROS'
        command_string=command_string_parser(command_string=format_string, command_dict=
                            {
                             'access_type':access_type,
                             'username': account_name,
                             'user_id':account_id,
                             'account_ipn_ip': account_ipn_ip,
                             'account_vpn_ip': account_vpn_ip,
                             'account_mac_address':account_mac_address,
                             'session': session_id
                             }
                            )
        #print command_string
        if nas_type=='mikrotik3':
            """
            ДОбавить проверку что вернул сервер доступа
            """
            print 'POD ROS3'
            rosClient(host=nas_ip, login=nas_login, password=nas_password, command=command_string)
            return True
        else:
            try:
                sshclient=SSHClient(host=nas_ip, port=22, username=nas_login, password=nas_password)
                #print 'ssh connected'
                res=sshclient.send_command(command_string)
                sshclient.close_chanel()
                print 'POD SSH'
                return True
            except Exception, e:
                print e
                return False

def change_speed(dict, account_id, account_name, account_vpn_ip, account_ipn_ip, account_mac_address, nas_ip, nas_type, nas_name, nas_secret, nas_login, nas_password, session_id, access_type, format_string, speed):
    
    access_type = access_type.lower()
    #print access_type
    if format_string=='' and access_type in ['pptp', 'pppoe']:
        #Send CoA
        
        speed_string= create_speed_string(speed, coa=True)
        print speed_string
        print 'send CoA'
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
        print 'SetSpeed Via SSH'
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
        command_dict.update(speed)
        #print 'command_dict=', command_dict
        command_string=command_string_parser(command_string=format_string, command_dict=command_dict)
        
        print command_string
        try:
            sshclient=SSHClient(host=nas_ip, port=22, username=nas_login, password=nas_password)
            print 'ssh connected'
            res=sshclient.send_command(command_string)
            sshclient.close_chanel()
            return True
        except Exception, e:
            print e
            return False





def DAE(dict, code, nas_ip, username, access_type=None, coa=True, nas_secret=None, nas_id=None, session_id=None, login=None, password=None, speed_string=None):
    """
    Dynamic Authorization Extensions
    http://www.rfc-archive.org/getrfc.php?rfc=3576
    """

    if code==40 or (code==43 and coa==True):
        print 'disconnect request'
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0',24000))
        #sock.connect('10.20.3.1',1700)
        doc = packet.AcctPacket(code=code, secret=nas_secret, dict=dict)
        doc.AddAttribute('NAS-IP-Address', nas_ip)
        doc.AddAttribute('NAS-Identifier', nas_id)
        doc.AddAttribute('User-Name', username)
        doc.AddAttribute('Acct-Session-Id', session_id)
        #doc.AddAttribute('Framed-IP-Address', '192.168.12.3')
        if speed_string:
            #Пока только для микротика
            doc.AddAttribute((14988,8), speed_string)
            #doc.AddAttribute((14988,8), "160k")

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
    else:

        """
        #сначала проверить есть ли, если нет-создать, если есть-установить
        /queue simple set [find interface=<pptp-dolphinik1>] limit-at=60000/60000 max-limit=200000/200000 burst-limit=600000/600000
        """
        print speed_string
        if code==43:
            query= """/queue simple set [find interface="<%s-%s>"] %s""" % (access_type, username, speed_string)
        elif code==40:
            query='/interface %s-server remove [find user="%s"]' % (access_type, username)

        try:
            sshclient=SSHClient(host=nas_ip, port=22, username=login, password=password)
            print 'ssh connected'
            #'/interface pptp-server remove [find user="%s"]' % username
            res=sshclient.send_command(query)
            sshclient.close_chanel()
        except:
            print 'SSH ERROR'

        return res[1].readlines()==[]

def ipn_manipulate(nas_ip, nas_login, nas_password, format_string, account_data={}):
        if account_data!={}:
            command_string=command_string_parser(command_string=format_string, command_dict=
                                {
                                 'access_type':account_data['access_type'],
                                 'username': account_data['username'],
                                 'user_id':str(account_data['user_id']),
                                 'ipaddress':account_data['ipaddress'],
                                 'mac_address':account_data['mac_address'],
                                 }
                                )
        else:
            command_string=format_string

        try:
            sshclient=SSHClient(host=nas_ip, port=22, username=nas_login, password=nas_password)
            print 'ssh connected'
            #'/interface pptp-server remove [find user="%s"]' % username
            print command_string
            res=sshclient.send_command(command_string)
            sshclient.close_chanel()
        except Exception, e:
            print e
        #print res[1].readlines()
        return res[1].readlines()==[]


def in_period(time_start, length, repeat_after, now=None):
        """
        Если повторение-год = проверяем месяц, число, время
        Если повтроение - полугодие = текущий месяц-начальный месяц по-модулю равно 6, совпадает число, время
        Если повтроение - квартал   = (текущий месяц - начальный месяц по модулю)/3=1, совпадает число, время
        Если повторение месяц - смотрим совпадает ли дата, время
        Если повторение неделя - смотрим совпадает ли день недели, время
        если повторение день - смотрим совпадает ли время
        =
        а=Текущее время - начальное время
        текущее_начальное_время_нач=начальное время+таймдельта(а[год],а[месяц],a[день])
        текущее_конечное_время =текущее_начальное_время_нач+таймдельта(length)
        если текущее время >текущее_начальное_время_нач И текущее время < текущее_конечное_время
             ок
        иначе
             вышел за рамки

        """
        if not now:
            now=datetime.datetime.now()
        #time_start=time_start.replace(tzinfo='UTC')
        if repeat_after=='DAY':
            delta_days=now - time_start

            #Когда будет начало в текущем периоде.
            nums,ost= divmod(delta_days.seconds, 86400)
            tnc=now-datetime.timedelta(seconds=ost)
            #Когда это закончится
            tkc=tnc+datetime.timedelta(seconds=length)
            if now>=tnc and now<=tkc:
                return True
            return False
        elif repeat_after=='WEEK':
            delta_days=now - time_start
            #Когда будет начало в текущем периоде.
            nums,ost= divmod(delta_days.seconds, 604800)
            tnc=now-datetime.timedelta(seconds=ost)
            #Когда это закончится
            tkc=tnc+datetime.timedelta(seconds=length)
            if now>=tnc and now<=tkc:
                return True
            return False
        elif repeat_after=='MONTH':
            #Февраль!
            tnc=datetime.datetime(now.year, now.month, time_start.day,time_start.hour,time_start.minute, time_start.second)
            tkc=tnc+datetime.timedelta(seconds=length)
            if now>=tnc and now<=tkc:
                return True
            return False
        elif repeat_after=='YEAR':
            #Февраль!
            tnc=datetime.datetime(now.year, time_start.month, time_start.day,time_start.hour,time_start.minute, time_start.second)
            tkc=tnc+datetime.timedelta(seconds=length)
            if now>=tnc and now<=tkc:
                return True
            return False
        elif repeat_after=='DONT_REPEAT':
            delta_days=now - time_start

            tkc=time_start+datetime.timedelta(seconds=length)
            if now>=time_start and now<=tkc:
                return True
            return False

def in_period_info(time_start, length, repeat_after, now=None):
        """
        Если повторение-год = проверяем месяц, число, время
        Если повтроение - полугодие = текущий месяц-начальный месяц по-модулю равно 6, совпадает число, время
        Если повтроение - квартал   = (текущий месяц - начальный месяц по модулю)/3=1, совпадает число, время
        Если повторение месяц - смотрим совпадает ли дата, время
        Если повторение неделя - смотрим совпадает ли день недели, время
        если повторение день - смотрим совпадает ли время
        =
        а=Текущее время - начальное время
        текущее_начальное_время_нач=начальное время+таймдельта(а[год],а[месяц],a[день])
        текущее_конечное_время =текущее_начальное_время_нач+таймдельта(length)
        если текущее время >текущее_начальное_время_нач И текущее время < текущее_конечное_время
             ок
        иначе
             вышел за рамки

        """
        result=False

        if not now:
            now=datetime.datetime.now()
        tnc=now
        tkc=now

        #time_start=time_start.replace(tzinfo='UTC')
        if repeat_after=='DAY':
            delta_days=now - time_start

            #Когда будет начало в текущем периоде.
            nums,ost= divmod(delta_days.seconds, 86400)
            tnc=now-datetime.timedelta(seconds=ost)
            #Когда это закончится
            tkc=tnc+datetime.timedelta(seconds=length)
            if now>=tnc and now<=tkc:
                result=True

        elif repeat_after=='WEEK':
            delta_days=now - time_start
            #Когда будет начало в текущем периоде.
            nums,ost= divmod(delta_days.seconds, 604800)
            tnc=now-datetime.timedelta(seconds=ost)
            #Когда это закончится
            tkc=tnc+datetime.timedelta(seconds=length)
            if now>=tnc and now<=tkc:
                result=True

        elif repeat_after=='MONTH':
            #Февраль!
            tnc=datetime.datetime(now.year, now.month, time_start.day,time_start.hour,time_start.minute, time_start.second)
            tkc=tnc+datetime.timedelta(seconds=length)
            if now>=tnc and now<=tkc:
                result=True

        elif repeat_after=='YEAR':
            #Февраль!
            tnc=datetime.datetime(now.year, time_start.month, time_start.day,time_start.hour,time_start.minute, time_start.second)
            tkc=tnc+datetime.timedelta(seconds=length)
            if now>=tnc and now<=tkc:
                result=True

        elif repeat_after=='DONT_REPEAT':
            delta_days=now - time_start

            tkc=time_start+datetime.timedelta(seconds=length)
            if now>=time_start and now<=tkc:
                result=True
        return (tnc, tkc, (now-tnc).seconds, result)




def settlement_period_info(time_start, repeat_after='', repeat_after_seconds=0,  now=None):
        """
        Функция возвращает дату начала и дату конца текущегопериода
        """
        
        #print time_start, repeat_after, repeat_after_seconds,  now
        
        if not now:
            now=datetime.datetime.now()
        #time_start=time_start.replace(tzinfo='UTC')
        #print "repeat_after_seconds=",repeat_after_seconds
        if repeat_after_seconds>0:
            #print 1
            delta_days=now - time_start
            length=repeat_after_seconds
            #Когда будет начало в текущем периоде.
            nums,ost= divmod(delta_days.seconds, length)
            tnc=now-datetime.timedelta(seconds=ost)
            #Когда это закончится
            tkc=tnc+datetime.timedelta(seconds=length)
            return (tnc, tkc, length)
        elif repeat_after=='DAY':
            delta_days=now - time_start
            length=86400
            #Когда будет начало в текущем периоде.
            nums,ost= divmod(delta_days.seconds, length)
            tnc=now-datetime.timedelta(seconds=ost)
            #Когда это закончится
            tkc=tnc+datetime.timedelta(seconds=length)
            return (tnc, tkc, length)

        elif repeat_after=='WEEK':
            delta_days=now - time_start
            length=604800
            #Когда будет начало в текущем периоде.
            nums,ost= divmod(delta_days.seconds, length)
            tnc=now-datetime.timedelta(seconds=ost)
            #Когда это закончится
            tkc=tnc+datetime.timedelta(seconds=length)
            return (tnc, tkc, length)
        elif repeat_after=='MONTH':
            months=relativedelta(now,time_start).months
            tnc=time_start+relativedelta(months=months)
            tkc=tnc+relativedelta(months=1)
            delta=tkc-tnc

            return (tnc, tkc, delta.days*86400)
        elif repeat_after=='YEAR':
            #Февраль!
            tnc=datetime.datetime(now.year, time_start.month, time_start.day,time_start.hour,time_start.minute, time_start.second)
            if calendar.isleap(tnc.year)==True:
                length=366
            else:
                length=365
            tkc=tnc+datetime.timedelta(seconds=length)
            delta=tkc-tnc
            return (tnc, tkc, delta.seconds)

def command_string_parser(command_string='', command_dict={}):
    
    import re
    if len(command_string) == 0 or len(command_dict) == 0:
        return ''
    pattern = re.compile('\$[_\w]+')
    match = pattern.finditer(command_string)
    if match is None:
        return ''
    params = [m.group()[1:] for m in match]
    for p in params :
        if p in command_dict.keys() :
            s = re.compile( '\$%s' % p)
            command_string = s.sub(str(command_dict[p]),command_string)
    print command_string
    return command_string

class SSHClient(paramiko.SSHClient):
    def __init__(self, host, port, username, password):
        paramiko.SSHClient.__init__(self)
        self.load_system_host_keys()
        self.set_missing_host_key_policy(policy=paramiko.AutoAddPolicy())
        self.connect(hostname=host,port=port, username=username,password=password)
        #self._transport.get_pty('vt100', 60, 80)

    def send_command(self, text):
        stdin, stdout, stderr = self.exec_command(text)
        #print stderr.readlines()==[]
        return stdout, stderr

    def close_chanel(self):
        self.close()



def create_nulls(param):
    if param==None:
        return 0
    if param=="None":
        return 0

def create_speed_string(params, coa=False):
    print params
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
        print self.strings


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
        try:
            
            ssh=SSHClient(host=nas['ipaddress'], port=22, username=nas['login'], password=nas['password'])
            response=ssh.send_command("/ppp active print terse without-paging")[0]
            response = response.readlines()
            print response
        except Exception, e:
            print e
            return []
            
        #print response
        if nas['type'] in ['mikrotik2.9', 'mikrotik2.8']:
            sessions=ActiveSessionsParser(response).parse()
        ssh.close_chanel()
        
    elif nas['type']==u'mikrotik3':
        #Use ROS API for fetching sessions

        sessions = convert(rosClient(nas['ipaddress'], nas['login'], nas['password'], r"/ppp/active/getall"))

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
    for param in params:
        values = map(convert_values, str(params[param]).split('/'))
        #print values

        params[param]='/'.join(values)
    #print 'after', params
    return params
            
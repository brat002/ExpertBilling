#-*-coding=utf-8-*-
from distutils.dist import command_re
import packet
import socket
import datetime, calendar
from dateutil.relativedelta import relativedelta
import paramiko

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
        if code==43:
            query= """/queue simple set [find interface="<%s-%s>"] %s""" % (access_type, username, speed_string)
        elif code==40:
            query='/interface %s-server remove [find user="%s"]' % (access_type, username)
        #query="/interface print"
        try:
            sshclient=SSHClient(host=nas_ip, port=22, username=login, password=password)
            print 'ssh connected'
            #'/interface pptp-server remove [find user="%s"]' % username
            res=sshclient.send_command(query)
            sshclient.close_chanel()
        except:
            print 'SSH ERROR'
        #print res[1].readlines()
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
        
        print time_start, repeat_after, repeat_after_seconds,  now
        
        if not now:
            now=datetime.datetime.now()
        #time_start=time_start.replace(tzinfo='UTC')
        print "repeat_after_seconds=",repeat_after_seconds
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
            #Февраль!
            # DONT WORKING!
            months=relativedelta(now,time_start).months
            #print dir(delta_days)


            #tnc=datetime.datetime(now.year, now.month, time_start.day,time_start.hour,time_start.minute, time_start.second)
            tnc=time_start+relativedelta(months=months)
            #tkc=tnc+datetime.timedelta(days=calendar.monthrange(tnc.year, tnc.month)[1])
            tkc=tnc+relativedelta(months=1)
            delta=tkc-tnc
            #print tnc
            #print tkc
            #print delta
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
            command_string = s.sub(command_dict[p],command_string)
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

def create_speed_string(params, nas_type, coa=False):
    params=map(lambda x: x=='None' and 0 or x, params)
    result=''
    if nas_type[:8]==u'mikrotik':
        #max_limit
        if coa==True:
            result+="%s" % params[0]

            #burst_limit
            result+=" %s" % params[1]

            #burst_treshold
            result+=" %s" % params[2]

            #burst_time
            result+=" %s" % params[3]

            #priority
            result+=" %s" % params[4]

            #burst_time
            result+=" %s" % params[5]
        else:
            result+="max-limit=%s" % params[0]

            #burst_limit
            result+=" burst-limit=%s" % params[1]

            #burst_treshold
            result+=" burst-treshold=%s" % params[2]

            #burst_time
            result+=" burst-time=%s" % params[3]

            #priority
            result+=" priority=%s" % params[4]

            #burst_time
            result+=" limit-at=%s" % params[5]


    return result

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

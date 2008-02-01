#-*-coding=utf-8-*-
import packet
import socket
import datetime, calendar
from dateutil.relativedelta import relativedelta
import paramiko

def disconnect(dict, code, nas_secret, nas_ip, nas_id, username, session_id, pod, login, password):
    if pod==True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('10.20.3.111',24000))
        #sock.connect('10.20.3.1',1700)
        doc=packet.AcctPacket(code=code,secret=nas_secret, dict=dict)
        doc.AddAttribute('NAS-IP-Address', nas_ip)
        doc.AddAttribute('NAS-Identifier', nas_id)
        doc.AddAttribute('User-Name',username)
        doc.AddAttribute('Acct-Session-Id', session_id)
        doc_data=doc.RequestPacket()
        sock.sendto(doc_data,(nas_ip, 1700))
        (data, addrport) = sock.recvfrom(8192)
        doc=packet.AcctPacket(secret=nas_secret, dict=dict, packet=data)

        #for key,value in doc.items():
        #    print doc._DecodeKey(key),doc[doc._DecodeKey(key)][0]

        sock.close()
        return doc.has_key("Error-Cause")==False
    else:
        sshclient=SSHClient(host=nas_ip, port=22, username=login, password=password)
        res=sshclient.send_command('/interface pptp-server remove [find user="%s"]' % username)
        sshclient.close_chanel()
        return res.readlines()==[]

def in_period(time_start, length, repeat_after):
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

def settlement_period_info(time_start, repeat_after, now=datetime.datetime.now()):
        """
        Функция возвращает дату начала и дату конца текущегопериода
        """
        #time_start=time_start.replace(tzinfo='UTC')
        if repeat_after=='DAY':
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
            if now>=tnc and now<=tkc:
                return True
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
        
def parse_command_string(template, params_dict):
    """
    format string can contains argument names prefixed by '%' - for example
    '/user/add %name %password'
    It will be changed to '/user/add name=value1 password=value2'
    """
    pattern = r'%([-_!@{}#\$&\*\(\)\.\?\w]+)'

    def replace( match ):
        param_name = match.group()[1:]
        try:
            param_value = params_dict[param_name]
        except KeyError:
            param_value = 'undefined'
        return "%s=%s" % (param_name,  param_value)
    import re
    rc = re.compile(pattern)
    return rc.sub(replace, format_string)

class SSHClient(paramiko.SSHClient):
    def __init__(self, host, port, username, password):
        paramiko.SSHClient.__init__(self)
        self.load_system_host_keys()
        self.set_missing_host_key_policy(policy=paramiko.AutoAddPolicy())
        self.connect(hostname=host,port=port, username=username,password=password)
        
    def send_command(self, text):
        stdin, stdout, stderr = self.exec_command(text)
        #print stderr.readlines()==[]
        return stdout
        
    def close_chanel(self):
        self.close()
        

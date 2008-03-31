#-*-coding=utf-8-*-
import packet
import socket
import datetime, calendar
from dateutil.relativedelta import relativedelta
import paramiko

def DAE(dict, code, nas_ip, username, access_type=None, nas_secret=None, nas_id=None, session_id=None, login=None, password=None, speed_string=None):
    """
    Dynamic Authorization Extensions
    http://www.rfc-archive.org/getrfc.php?rfc=3576
    """

    if code==40:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0',24000))
        #sock.connect('10.20.3.1',1700)
        doc=packet.AcctPacket(code=code, secret=nas_secret, dict=dict)
        doc.AddAttribute('NAS-IP-Address', nas_ip)
        doc.AddAttribute('NAS-Identifier', nas_id)
        doc.AddAttribute('User-Name', str(username))
        doc.AddAttribute('Acct-Session-Id', str(session_id))
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
        sshclient=SSHClient(host=nas_ip, port=22, username=login, password=password)
        print 'ssh connected'
        """
        #сначала проверить есть ли, если нет-создать, если есть-установить
        /queue simple set [find interface=<pptp-dolphinik1>] limit-at=60000/60000 max-limit=200000/200000 burst-limit=600000/600000
        """

        #query= """/queue simple set [find interface="<%s-%s>"] %s""" % (access_type, username, speed_string)
        query="/interface print"
        print query
        #'/interface pptp-server remove [find user="%s"]' % username
        res=sshclient.send_command(query)
        sshclient.close_chanel()
        print res[1].readlines()
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




def settlement_period_info(time_start, repeat_after, now=None):
        """
        Функция возвращает дату начала и дату конца текущегопериода
        """
        if not now:
            now=datetime.datetime.now()
        #time_start=time_start.replace(tzinfo='UTC')
        if type(repeat_after)==int and repeat_after>0:
            delta_days=now - time_start
            length=repeat_after
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
        if coa==False:
            result+="%s/%s" % (params[0], params[1])

            #burst_limit
            result+=" %s/%s" % (params[2],params[3])

            #burst_treshold
            result+=" %s/%s" % (params[4], params[5])

            #burst_time
            result+=" %s/%s" % (params[6], params[7])

            #priority
            result+=" %s" % params[8]

            #burst_time
            result+=" %s/%s" % (params[9], params[10])
        else:
            result+="max-limit=%s/%s" % (params[0], params[1])

            #burst_limit
            result+=" burst-limit=%s/%s" % (params[2],params[3])

            #burst_treshold
            result+=" burst-treshold=%s/%s" % (params[4], params[5])

            #burst_time
            result+=" burst-time=%s/%s" % (params[6], params[7])

            #priority
            result+=" priority=%s" % params[8]

            #burst_time
            result+=" limit-at=%s/%s" % (params[9], params[10])


    return result

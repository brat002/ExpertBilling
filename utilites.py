#-*-coding=utf-8-*-

from __future__ import with_statement
#from log_adapter import log_debug_, log_info_, log_warning_, log_error_
from period_utilities import in_period, in_period_info, settlement_period_info
import re
import packet
import socket
import logging
import psycopg2
import commands
import traceback
import datetime, calendar, time
import os, os.path, sys, time, binascii
from hashlib import md5


try:
    from os import kill
except Exception, ex:
    print "NO SIGNALS!"
    kill = lambda x,y: None


STATE_OK = 0
STATE_NULLIFIED = 1
NFR_PACKET_HEADER_FMT = '!IId'

ssh_exec = False
#try: 
#    from ssh_utilities import SSHClient, ssh_execute
#    ssh_exec = True
#except:
#    print >> sys.stderr, "Problems with importing ssh wrapper from ssh_utilities, reverting to paramiko"
from ssh_paramiko import ssh_client

def log_info_(lstr, level=logging.INFO):
    log_adapt(lstr, level)
    
def log_debug_(lstr, level=logging.DEBUG):
    log_adapt(lstr, level)
    
def log_warning_(lstr, level=logging.WARNING):
    log_adapt(lstr, level)
    
def log_error_(lstr, level=logging.ERROR):
    log_adapt(lstr, level)
    
def log_adapt(lstr, level):
    #print lstr
    pass

def PoD(dict, account, subacc, nas, access_type, session_id='', vpn_ip_address='', caller_id='', format_string=''):
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
    if (nas.get('speed_value1') or nas.get('speed_value2')) and ((format_string=='' and access_type in ['pptp', 'l2tp', 'pppoe', 'lisg'] ) or access_type=='hotspot' or nas.get('type')=='cisco'):
        log_debug_("Send PoD")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(20)
        sock.bind(('0.0.0.0',24000))
        doc = packet.AcctPacket(code=40, secret=str(nas.get('secret')), dict=dict)
        doc.AddAttribute('NAS-IP-Address', str(nas.get('ipaddress')))
        if nas.type!='cisco' and nas.get('identify'):
            doc.AddAttribute('NAS-Identifier', str(nas.get('identify')))
            
        if access_type=='lisg':
            doc.AddAttribute('User-Name', str(subacc.get('ipn_ip_address')))
        elif subacc.get('username'):
            doc.AddAttribute('User-Name', str(subacc.get('username')))
            
        if nas.type=='cisco':
            log_debug_("Normalization cisco session id")
            doc.AddAttribute('Acct-Session-Id', re.sub('^0+', '', str(session_id) ))
        else:
            doc.AddAttribute('Acct-Session-Id', str(session_id))
            
        if access_type=='hotspot' and vpn_ip_address:
            doc.AddAttribute('Framed-IP-Address', str(vpn_ip_address))
        elif access_type not in ('hotspot', 'lisg') and vpn_ip_address:
            doc.AddAttribute('Framed-IP-Address', str(vpn_ip_address))
            
        if caller_id and nas.get('type')!='cisco' :
            doc.AddAttribute('Calling-Station-Id', str(caller_id))
            
        doc_data=doc.RequestPacket()
        sock.sendto(doc_data,(str(nas.get('ipaddress')), 1700))
        (data, addrport) = sock.recvfrom(8192)
        doc=packet.AcctPacket(secret=nas.get('secret'), dict=dict, packet=data)
        sock.close()
            
        return doc.has_key("Error-Cause")==False
    elif format_string!='' and access_type in ['pptp', 'l2tp', 'pppoe']:
        #ssh
        
        log_debug_('POD ROS')
        
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
                
        command_string=command_string_parser(command_string=format_string, command_dict=command_dict)

        try:
            if nas.type!='localhost':
                sshclient=ssh_client(host=nas.get('ipaddress'), username=nas.get('login'), password=nas.get('password'), command = command_string)
                log_debug_('ssh connected')
                del sshclient
            elif nas.type=='localhost':
                status, output = commands.getstatusoutput(command_string)
                log_debug_('Local command %s was executed with status %s and output %s' % (command_string, status, output))
                if status!=0:return False
            log_debug_('POD SSH')
            return True
        except Exception, e:
            log_error_('PoD SSH exception: %s' % repr(e))
            return False

def change_speed(dict, account, subacc ,nas, session_id='', vpn_ip_address='', access_type='', format_string='', speed=''):
    
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
    speed = get_decimals_speeds(speed)
    speed = speed_list_to_dict(speed)
    if (nas.get('speed_value1') or nas.get('speed_value2')) and ((format_string=='' and access_type in ['pptp', 'l2tp', 'pppoe', 'lisg']) or access_type=='hotspot' or nas.get('type')=='cisco'):

        log_debug_('send CoA')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(20)
        sock.bind(('0.0.0.0',24000))
        doc = packet.AcctPacket(code=43, secret=str(nas.get('secret')), dict=dict)
        doc.AddAttribute('NAS-IP-Address', str(nas.get('ipaddress')))
        if nas.get('type')!='cisco' and nas.get('identify'):
            doc.AddAttribute('NAS-Identifier', str(nas.get('identify')))
        if access_type=='lisg':
            doc.AddAttribute('User-Name', str(subacc.get('ipn_ip_address')))
        else:
            doc.AddAttribute('User-Name', str(subacc.get('username')))
        if nas.get('type')=='cisco':
            log_debug_("Normalization cisco session id")
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
        
        if nas.get('speed_value1'):
            result_params = str(command_string_parser(command_string=nas.get('speed_value1'), command_dict=speed))
            if result_params and nas.get('speed_vendor_1'):
                doc.AddAttribute((nas.get('speed_vendor_1'), nas.get('speed_attr_id1')),result_params)
            elif result_params and not nas.get('speed_vendor_1'):
                doc.AddAttribute(nas.get('speed_attr_id1'),str(result_params))

        if nas.get('speed_value2'):
            result_params = str(command_string_parser(command_string=nas.get('speed_value2'), command_dict=speed))
            if result_params and nas.get('speed_vendor_2'):
                doc.AddAttribute((nas.get('speed_vendor_2'), nas.get('speed_attr_id2')),result_params)
            elif result_params and not nas.get('speed_vendor_2'):
                doc.AddAttribute(nas.get('speed_attr_id2'),str(result_params))
                    
        doc_data=doc.RequestPacket()
        log_debug_('CoA socket send: %s' % str(nas.ipaddress))
        sock.sendto(doc_data,(nas.get('ipaddress'), 1700))
        (data, addrport) = sock.recvfrom(8192)
        log_debug_('CoA socket get: %s' % str(addrport))
        doc=packet.AcctPacket(secret=nas.get('secret'), dict=dict, packet=data)

        sock.close()

        return doc.has_key("Error-Cause")==False
    
    elif format_string!='' and access_type in ['pptp', 'l2tp', 'pppoe', 'ipn']:
        #ssh
        log_debug_('SetSpeed Via SSH/local command')
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

        command_string=command_string_parser(command_string=format_string, command_dict=command_dict)
        if not command_string: return True
        #print command_string
        log_debug_("Change Speed command_string= %s" % command_string)
        try:
            if nas.type!='localhost':
                sshclient=ssh_client(host=nas.get('ipaddress'), username=nas.get('login'), password=nas.get('password'), command = command_string)
                log_debug_('ssh connected')
                del sshclient
            elif nas.type=='localhost':
                status, output = commands.getstatusoutput(command_string)
                log_debug_('Local command %s was executed with status %s and output %s' % (command_string, status, output))
                if status!=0:return False
            return True
        except Exception, e:
            log_error_('Change Speed ssh exception %s' % repr(e))
            return False
    return False

def cred(account, subacc, access_type, nas, addonservice={},format_string=''):
        """
        
        """
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
            
            if nas.get('type')!='localhost':
                sshclient=ssh_client(host=nas.get('ipaddress'), username=nas.get('login'), password=nas.get('password'), command = command_string)
                log_debug_('CRED ssh connected')
                del sshclient
            elif nas.type=='localhost':
                status, output = commands.getstatusoutput(command_string)
                log_debug_('Local command %s was executed with status %s and output %s' % (command_string, status, output))
            return True
        except Exception, e:
            log_error_('CRED ssh error: %s' % repr(e))
            return False

def create_speed(default, speeds,  correction, addonservicespeed, speed, date_, fMem):          
    if speed=='':            
        defaults = default            
        defaults = map(lambda x: x if x else 0, defaults[:11]) if defaults else [0,0,0,0,0,0,0,0,0,0,8]            
        result=[]            
        min_delta, minimal_period = -1, []            
        now=date_            
        for speed in speeds:                
            #Определяем составляющую с самым котортким периодом из всех, которые папали в текущий временной промежуток
            tnc,tkc,delta,res = fMem.in_period_(speed[11],speed[12],speed[13], now)                
            #print "res=",res                
            if res==True and (delta<min_delta or min_delta==-1):                    
                minimal_period=speed                    
            min_delta=delta            
        
        minimal_period = map(lambda x: x if x else 0, minimal_period[:11]) if minimal_period else [0,0,0,0,0,0,0,0,0,0,8]          
        for k in xrange(0, 11):                
            s=minimal_period[k]                
            if s=='0' or s=='' or s==0 or s==None:                    
                res=defaults[k]                
            else:                    
                res=s                
            result.append(res)   #Проводим корректировку скорости в соответствии с лимитом            
        #print self.caches.speedlimit_cache      

        result = get_corrected_speed(result, correction)            
        if addonservicespeed:                
            result = get_corrected_speed(result, addonservicespeed)                        
        if result==[]:                 
            result = defaults if defaults else [0,0,0,0,0,0,0,0,0,0,8]                            
        
        return get_decimals_speeds(result)
    else:
        try:
            return parse_custom_speed_lst(speed)
        except Exception, ex:
            print "exception: %s \n %s Can not parse account speed %s", (repr(ex), traceback.format_exc(), speed)
            return ["0/0","0/0","0/0","0/0","8","0/0"] 
            
        
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


def create_nulls(param):
    if param==None:
        return 0
    if param=="None":
        return 0
def get_speed_dict(result):
    command_dict={'max_limit_rx': result[0],
                'max_limit_tx': result[1],
                'burst_limit_rx': result[2],
                'burst_limit_tx': result[3],
                'burst_treshold_rx': result[4],
                'burst_treshold_tx': result[5],
                'burst_time_rx': result[6],
                'burst_time_tx': result[7],
                'priority': result[8],
                'min_limit_rx': result[9],
                'min_limit_tx': result[10]}
    
def reverse_speed(val):
    v = val.split("/")
    if len(v)==1: return v
    return "%s/%s" % (v[1], v[0])

def create_speed_string(params, ipn=True):
    #print params
    #params=map(lambda x: params[x]=='None' and 0 or x, params)
    result=''

    if ipn == False:
        result+="%s" % reverse_speed(params['max_limit'])
        #burst_limit
        result+=" %s" % reverse_speed(params['burst_limit'])
        #burst_treshold
        result+=" %s" % reverse_speed(params['burst_treshold'])
        #burst_time
        result+=" %s" % reverse_speed(params['burst_time'])
        #priority
        result+=" %s" % reverse_speed(params['priority'])
        #min_limit        
        result+=" %s" % reverse_speed(params['min_limit'])
        
    if ipn == True:
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

    
def convert(alist):
    return [dict(y[1:].split('=') for y in x if not y[0] in ('.','!')) for x in alist]

def convert_values(value):
    if str(value).endswith(('k', 'K')):
        return str(int(str(value)[0:-1])*1000)
    elif str(value).endswith(('M', 'm')):
        return str(int(str(value)[0:-1])*1000*1000)
    else:
        return str(value)
                
def get_decimals_speeds(params):
    #print "before", params
    i = 0
    res = []
    for param in params:
        res.append(convert_values(param))
        i += 1
    #print 'after', params
    return res

def formatator(x,y):
    if x!=-1 and y==-1:
        return (x,x)
    elif x==-1 and y==-1:
        return 0,0
    elif x!=-1 and y!=-1:
        return (x,y)


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
    dkeys = ['max_limit_rx', 'max_limit_tx', "burst_limit_rx", "burst_limit_tx", 'burst_treshold_rx', 'burst_treshold_tx', 'burst_time_rx', 'burst_time_tx', 'min_limit_rx', 'min_limit_tx', 'priority']
    return dict(zip(dkeys, spList))

def parse_custom_speed_lst(speed_string): # current
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
    return flatten([formatator(txrate, rxrate), formatator(txbrate, rxbrate), formatator(tbthr, rbthr ), formatator(tbtm, rbtm), formatator(trm, rrm), prt])

def parse_custom_speed_lst_rad(speed_string):
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
    if type(speed)==int: return str(speed)
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
            result.append(int(convert_values(el)))
    return result

def speedlimit_logic(speed, limitspeed, speed_unit, speed_change_type):
    #print limitspeed
    if speed_unit=='Kbps':
        limitspeed=limitspeed*1000
    elif speed_unit == 'Mbps':
        limitspeed=limitspeed*1000*1000
    elif speed_unit == '%':
        limitspeed = (limitspeed or 0.00)/100.000
    

    speed = int(speed)
    if speed_change_type=='add' and speed_unit !='%':
        return int(speed+limitspeed)
    elif speed_change_type=='add' and speed_unit =='%':
        return int(speed+limitspeed*speed)  
    elif speed_change_type == 'abs' and speed_unit == '%':
        return int(limitspeed*speed)
    elif speed_change_type == 'abs':
        return int(limitspeed)
         
def correct_speed(speed, correction):
    """
    
    """
    res = []
    #max tx
    if not speed or not correction: return speed
    res.append(speedlimit_logic(speed[0], correction[0], correction[11], correction[12]))
    #max rx            
    res.append(speedlimit_logic(speed[1], correction[1], correction[11], correction[12]))
    #burst tx
    res.append(speedlimit_logic(speed[2], correction[2], correction[11], correction[12]))
    #burst rx 
    res.append(speedlimit_logic(speed[3], correction[3], correction[11], correction[12]))
    #burst treshold
    res.append(speedlimit_logic(speed[4], correction[4], correction[11], correction[12])) 
    res.append(speedlimit_logic(speed[5], correction[5], correction[11], correction[12]))
    #burst time
    res.append(correction[6]) 
    res.append(correction[7])
    res.append(speedlimit_logic(speed[9], correction[9], correction[11], correction[12]))
    
    res.append(speedlimit_logic(speed[10], correction[10], correction[11], correction[12]))
    #priority
    res.append(correction[8])
    #min

    return res



   
def get_corrected_speed(speed, correction):
    #12 - speed_units
    #13 - speed_change_type
    if correction:
        return correct_speed(get_decimals_speeds(speed), correction)
    else:
        return get_decimals_speeds(speed)
    
'''use Old = use old caches if any errors were encountered during renewing process'''
def renewCaches(cur, cacheMaster, cacheType, code, cargs=(), useOld = True):
    ptime =  time.time()
    ptime = ptime - (ptime % 20)
    cacheDate = datetime.datetime.fromtimestamp(ptime)
    cacheMaster.read = False
    try:
        caches = cacheType(cacheDate, *cargs)
        caches.getdata(cur)
        cur.connection.commit()
        caches.reindex()
        if caches.post_caches:
            caches.post_getdata(cur)
            cur.connection.commit()
            caches.post_reindex()
    except Exception, ex:
        if isinstance(ex, psycopg2.DatabaseError):
            try:
                log_error_('#30%s0001 renewCaches attempt failed due to database error: %s' % (code, repr(ex).decode('utf-8')))
            except:
                log_error_('#31%s0001 renewCaches attempt failed due to database error: %s' % (code, repr(ex)))
        else: 
            try:
                log_error_('#30%s0002 renewCaches attempt failed due to error: %s \n %s' % (code, repr(ex).decode('utf-8'), traceback.format_exc()))
            except:
                log_error_('#32%s0002 renewCaches attempt failed due to error: %s \n %s' % (code, repr(ex), traceback.format_exc()))
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
    
def savepid(piddir, procname):
    if not os.path.isdir(piddir): os.mkdir(piddir)
    pfile = open(''.join((piddir, '/', procname, '.pid')), 'wb')
    pfile.write(str(os.getpid()))
    pfile.close()
    
def rempid(piddir, procname):
    try:
        os.unlink(''.join((piddir, '/', procname, '.pid')))
    except:
        pass
    
def readpids(piddir, lastmtime = -1, exclude = []):
    presmtime = os.path.getmtime(piddir)
    if lastmtime == presmtime: return ([], presmtime)
    pidfiles = os.listdir(piddir)
    if exclude:
        pidfiles = list(set(pidfiles).difference(exclude))
    return ([(pidfile[:-4], int(open(''.join((piddir, '/', pidfile)), 'rb').read())) for pidfile in pidfiles], presmtime)
    
#SIGUSR1 = 10    
def killpids(pids, sig):
    for pid in pids:
        try:
            kill(pid, sig)
        except OSError, oerr:
            pass
  
def getpid(piddir, procname):
    try:
        return int(open(''.join((piddir, '/', procname, '.pid')), 'rb').read())
    except:
        return None
    
def check_running(pid, name):
    by_pid = check_running_by_pid(pid)
    if by_pid:
        by_name = check_running_by_name(pid, name)
        return by_name
    return False

def check_running_by_pid(pid):
    if not pid:
        return False
    else:
        try:
            os.kill(pid, 0)
        except Exception, ex:
            #except OSError, oerr:
            #if oerr.errno == 3:
            return False
        else:
            return True
        
def check_running_by_name(pid, name):
    by_name = commands.getstatusoutput('ps -p %d -o comm=' % pid)
    if by_name[0] == 0:
        return by_name[1] == name
    else:
        return False
    
        
def get_connection(dsn, session = []):
    conn = psycopg2.connect(dsn)
    conn.set_client_encoding('UTF8')
    if session:
        cur = conn.cursor()
        for sess_sql in session:
            cur.execute(sess_sql)
        cur.close()
        conn.commit()
    return conn
        
def hex_bytestring(bstr):
    return reduce(lambda x,y: x+y, ("%x" % ord(cbyte) for cbyte in bstr), '')

#def tr_summ(summ, ballance, ps_condition):
#    if ps_condition==1 and summ>
"""
  IF (ps_condition_type_ = 1) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit >= 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 2) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit < 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    ELSIF (ps_condition_type_ = 3) AND (new_summ_ > 0) THEN
        SELECT new_summ_*(ballance+credit > 0)::int INTO new_summ_ FROM billservice_account WHERE id=account_id_;
    END IF;
""" 
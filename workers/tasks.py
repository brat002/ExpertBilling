#-*-coding: utf-8 -*-

from celery.task import task
import os, sys
import commands
from pyrad import dictionary
import re
import socket
from pyrad import packet
import paramiko
import psycopg2
import ConfigParser
config = ConfigParser.ConfigParser()
BILLING_PATH = '/opt/ebs/data/'
config.read(os.path.join(BILLING_PATH, "/ebs_config.ini"))
SSH_BACKEND = config.get("core", "ssh_backend")
db_name = "db"
DICT = dictionary.Dictionary(os.path.join(BILLING_PATH, "dicts/dictionary"),os.path.join(BILLING_PATH, "dicts/dictionary.microsoft"), os.path.join(BILLING_PATH, 'dicts/dictionary.mikrotik') , os.path.join(BILLING_PATH, 'dicts/dictionary.cisco'))
import logging
DSN = "dbname='%s' user='%s' host='%s' port='%s' password='%s'" % (config.get(db_name, "name"), config.get(db_name, "username"), \
                                                                         config.get(db_name, "host"), config.get(db_name, "port"), config.get(db_name, "password"))

SSH_BACKEND = None
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
            command_string = cs_str.sub(str(command_dict[p]),command_string)
    #print command_string
    return command_string

def ssh_client(host, username, password, command, logger):
    if not SSH_BACKEND:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(host, username=username, password=password, allow_agent=True, look_for_keys=True)
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
def update_vpn_speed_state(state, session_id, newspeed):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""UPDATE radius_activesession SET speed_string=%s WHERE id=%s;
                """ , (newspeed, session_id,))
    conn.commit()
    cur.close()
    conn.close()

@task
def update_ipn_speed_state(state, subaccount_id, newspeed):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE billservice_subaccount SET speed=%s WHERE id=%s;", (newspeed, subaccount_id))
    conn.commit()
    cur.close()
    conn.close()

@task
def ipn_add_state(subaccount_id, cb):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE billservice_subaccount SET ipn_added=%s WHERE id=%s",  (True, subaccount_id))
    conn.commit()
    cur.close()
    conn.close()
        
@task
def ipn_del_state(subaccount_id, cb):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE billservice_subaccount SET ipn_added=%s WHERE id=%s",  (False, subaccount_id))
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
    cur.execute("UPDATE billservice_subaccount SET ipn_enabled=%s WHERE id=%s",  (True, subaccount_id))
    conn.commit()
    cur.close()
    conn.close()
    if cb:
        cb.apply()
        
@task
def ipn_disable_state(subaccount_id, cb):

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE billservice_subaccount SET ipn_enabled=%s WHERE id=%s",  (False, subaccount_id))
    conn.commit()
    cur.close()
    conn.close()
    if cb:
        cb.apply()
        

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
def PoD(account, subacc, nas, access_type, session_id='', vpn_ip_address='', caller_id='', format_string=''):
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
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(20)
        sock.bind(('0.0.0.0'))
        doc = packet.AcctPacket(code=40, secret=str(nas.get('secret')), dict=DICT)
        doc.AddAttribute('NAS-IP-Address', str(nas.get('ipaddress')))
        if nas.get('type')!='cisco' and nas.get('identify'):
            doc.AddAttribute('NAS-Identifier', str(nas.get('identify')))
            
        if access_type=='lisg':
            doc.AddAttribute('User-Name', str(subacc.get('ipn_ip_address')))
        elif subacc.get('username'):
            doc.AddAttribute('User-Name', str(subacc.get('username')))
            
        if nas.get('type')=='cisco':
            logger.info("Normalization cisco session id")
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
                
        command_string=command_string_parser(command_string=format_string, command_dict=command_dict)

        try:
            if nas.get('type')!='localhost':
                sshclient=ssh_client(host=nas.get('ipaddress'), username=nas.get('login'), password=nas.get('password'), command = command_string, logger = logger)
                logger.info('ssh connected')
                del sshclient
            elif nas.get('type')=='localhost':
                status, output = commands.getstatusoutput(command_string)
                logger.info('Local command %s was executed with status %s and output %s' % (command_string, status, output))
                if status!=0:return False
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
        sock.bind(('0.0.0.0'))
        doc = packet.AcctPacket(code=43, secret=str(nas.get('secret')), dict=DICT)
        doc.AddAttribute('NAS-IP-Address', str(nas.get('ipaddress')))
        if nas.get('type')!='cisco' and nas.get('identify'):
            doc.AddAttribute('NAS-Identifier', str(nas.get('identify')))
        if access_type=='lisg':
            doc.AddAttribute('User-Name', str(subacc.get('ipn_ip_address')))
        else:
            doc.AddAttribute('User-Name', str(subacc.get('username')))
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
        logger.info('CoA socket send: %s' % str(nas.ipaddress))
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

        command_string=command_string_parser(command_string=format_string, command_dict=command_dict)
        if not command_string: return True
        #print command_string
        logger.info("Change Speed command_string= %s" % command_string)
        try:
            status = True
            if nas.type!='localhost':
                status=ssh_client(host=nas.get('ipaddress'), username=nas.get('login'), password=nas.get('password'), command = command_string)
                logger.info('ssh connected')

            elif nas.type=='localhost':
                status, output = commands.getstatusoutput(command_string)
                status = True if status==0 else False
            if status==True and cb:
                cb.apply()
                logger.info('Local command %s was executed with status %s and output %s' % (command_string, status, output))
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
        
        if nas.get('type')!='localhost':
            status=ssh_client(host=nas.get('ipaddress'), username=nas.get('login'), password=nas.get('password'), command = command_string)
            logger.info('CRED ssh connected')
        elif nas.type=='localhost':
            status, output = commands.getstatusoutput(command_string)
            status = True if status==0 else False
            logger.info('Local command %s was executed with status %s and output %s' % (command_string, status, output))
        if status==True and cb:
            cb.apply()
    except Exception, e:
        logger.error('CRED ssh error: %s' % repr(e))
        return False
        
#-*-coding=utf-8-*-
import paramiko
import commands
import re

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
            elif nas.type=='localhost':
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



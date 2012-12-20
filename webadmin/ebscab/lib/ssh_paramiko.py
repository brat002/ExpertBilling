import paramiko
import commands
import re
#import isdlogger
#import socket
#socket.setdefaulttimeout(20)
#paramiko.common.logging.root.setLevel(logging.DEBUG)
SSH_BACKEND=None

cs_pattern = re.compile('\$[_\w]+')
def command_string_parser(command_string='', command_dict={}):
    """
    
    """    
    
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

class PseudoLogger(object):
    def _pass(self, *args, **kwargs):
        pass
    
    def __getattr__(self, *args, **kwargs):
        return self._pass
    
def install_logger(lgr):
    global logger
    logger = lgr
    paramiko.util.get_logger = lambda name: logger

def ssh_client(host, username, password, command):
    #print command
    global SSH_BACKEND
    global logger
    #logger = isdlogger.isdlogger('logging', loglevel=0, ident="ebs_core", filename="log/core_log")    
    if SSH_BACKEND==None:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password, allow_agent=False, look_for_keys=False, timeout=20)
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
    






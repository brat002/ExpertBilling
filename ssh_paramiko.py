import paramiko
import commands
from utilites import command_string_parser
#import logging
#import socket
#socket.setdefaulttimeout(20)
#paramiko.common.logging.root.setLevel(logging.DEBUG)
SSH_BACKEND=None
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
    if SSH_BACKEND==None:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(host, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        out = stdout.readlines()
        err = stderr.readlines()
        ssh.close()
        return out, err==[]
    else:
        command_string=command_string_parser(command_string=SSH_BACKEND, command_dict=
                            {'host': host, 'username': username,'password': password,
                             'command': command})        
        status, output = commends.getstatusoutsput(command_string)
        logger.debug("NAS Manipulation try status=%s output=%s", (status, output))
        return output,status==0
    






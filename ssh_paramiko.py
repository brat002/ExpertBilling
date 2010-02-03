import paramiko
import logging
#import socket
#socket.setdefaulttimeout(20)
paramiko.common.logging.root.setLevel(logging.DEBUG)

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
    print command
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    ssh.connect(host, username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command(command)
    out = stdout.readlines()
    err = stderr.readlines()
    ssh.close()
    return out, err==[]





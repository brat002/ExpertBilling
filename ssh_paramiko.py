import paramiko
import logging
paramiko.common.logging.root.setLevel(logging.WARNING)


def ssh_client(host, username, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    ssh.connect(host, username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command(command)
    out = stdout.readlines()
    err = stderr.readlines()
    ssh.close()
    return out, err==[]





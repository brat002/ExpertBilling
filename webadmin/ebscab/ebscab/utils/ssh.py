# -*- coding: utf-8 -*-

import commands
import re

import paramiko


SSH_BACKEND = None

cs_pattern = re.compile('\$[_\w]+')


def command_string_parser(command_string='', command_dict={}):
    if len(command_string) == 0 or len(command_dict) == 0:
        return ''

    match = cs_pattern.finditer(command_string)
    if match is None:
        return ''
    params = [m.group()[1:] for m in match]
    for p in params:
        if p in command_dict.keys():
            cs_str = re.compile('\$%s' % p)
            command_string = cs_str.sub(str(command_dict[p]), command_string)
    return command_string


def ssh_client(host, username, password, command):
    global SSH_BACKEND

    if SSH_BACKEND == None:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host,
                    username=username,
                    password=password,
                    allow_agent=False,
                    look_for_keys=False,
                    timeout=20)
        stdin, stdout, stderr = ssh.exec_command(command)
        out = stdout.readlines()
        err = stderr.readlines()
        ssh.close()
        return out, err == []
    else:
        command_string = command_string_parser(
            command_string=SSH_BACKEND,
            command_dict={
                'host': host,
                'username': username,
                'password': password,
                'command': command
            })
        status, output = commands.getstatusoutput(command_string)
        return output, status == 0

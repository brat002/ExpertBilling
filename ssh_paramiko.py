import paramiko
import logging
paramiko.common.logging.root.setLevel(logging.WARNING)

class SSHClient(paramiko.SSHClient):
    def __init__(self, host, port, username, password):
        paramiko.SSHClient.__init__(self)
        self.load_system_host_keys()
        self.set_missing_host_key_policy(policy=paramiko.AutoAddPolicy())
        self.connect(hostname=host,port=port, username=username,password=password)
        #self._transport.get_pty('vt100', 60, 80)

    def send_command(self, text):
        stdin, stdout, stderr = self.exec_command(text)
        #print stderr.readlines()==[]
        return stdout, stderr

    def close_channel(self):
        self.close()



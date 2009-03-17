import pexpect
from pxssh import pxssh, ExceptionPxssh

def ssh_execute(user, host, password, command):
    ssh_answer = 'Are you sure you want to continue connecting'
    ssession = pexpect.spawn('ssh -l %s %s %s'%(user, host, command))
    reply = ssession.expect([pexpect.TIMEOUT, ssh_answer, 'password: '])
    if reply == 0: # Timeout
        raise ExceptionPxssh('ERROR:' + str(ssession.before) + ':' + str(ssession.after))
    if reply == 1: # SSH does not have the public key. Just accept it.
        ssession.sendline ('yes')
        ssession.expect ('password: ')
        reply = ssession.expect([pexpect.TIMEOUT, 'password: '])
        if reply == 0: # Timeout
            ExceptionPxssh('ERROR:' + str(ssession.before) + ':' + str(ssession.after))
    ssession.sendline(password)
    ssession.expect(pexpect.EOF)
    return 'OK:' + str(ssession.before) + ':' + str(ssession.after)

class SSHClient(pxssh):
    def __init__(self, host, port, username, password):
        pxssh.__init__(self)
        self.force_password = True
        self.login(host, username,password=password, port=port)

    def send_command(self, text):
        self.sendline(text)
        self.prompt()
        return self.before

    def close_channel(self):
        self.logout()



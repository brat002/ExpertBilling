#import dmidecode
import commands
import sys
from hashlib import md5
from base64 import b64decode

s,o=commands.getstatusoutput(b64decode('Y2F0IC9wcm9jL2NwdWluZm8gfCBncmVwICJtb2RlbCBuYW1lIg=='))
uid = md5(o).hexdigest()
uid=uid.upper()
print uid

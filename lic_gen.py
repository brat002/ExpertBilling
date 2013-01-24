#import dmidecode
import commands
import sys
from hashlib import md5
#d = dmidecode.system().get('0x0001').get('data',{}).get('UUID')

#uid = md5(d).hexdigest()
# NAME ACCOUNTS HASH
#  1            2         3

print sys.argv, len(sys.argv)

if len(sys.argv)==4:
    uid = str(sys.argv[3].strip())
else:
    uid = md5(str('freedom')).hexdigest().upper()

name = str(sys.argv[1])
accounts = int(sys.argv[2])

uid+=hex(accounts)
uid=uid.upper()
crc = 0
i=0
for x in uid:
    crc+=ord(x)**i-1
    i+=1
    
c=md5(str(crc)).hexdigest().upper()


print uid,md5(str(crc)).hexdigest().upper()

open("license_%s.lic" % name,"w").write("%sAS%s" % (uid,c))

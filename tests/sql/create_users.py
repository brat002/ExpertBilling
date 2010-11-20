"""ustr = '''%s	vpn_%s	Eayb80ae				1	192.168.100.%s	f	0.0.0.0		f	t	t	2009-02-24 15:45:47.562	0	0	f	f			0.0.0.0	f									0	f	f	f	f	f	f		2000-01-01 00:00:00			'''
i = 259
ipn = 1
n = 253
f = open('uout', 'wb')
while n >=0:
    f.write(ustr%(i, ipn, ipn)+ '\n')
    i += 1
    ipn +=1
    n -= 1

ustr3 = '''%s	%s	3	2009-02-24 15:44:00.113688'''
ustr1 = '''%s	%s	1	2009-02-24 15:44:00.113688'''
"""
import random
lstr3 = '''%s	3	l3_%s	1	%s	f	%s	0'''
lstr1 = '''%s	1	l1_%s	1	%s	f	%s	0'''
i = 1
ipn = 1
n = 23
f = open('uout', 'wb')
while n >=0:
    amnts = str(random.randint(100000000, 1000000000000))
    amnt = int(amnts[:2])*10**(len(amnts)-3)
    f.write(lstr3%(i, ipn, amnt, ipn)+ '\n')
    i += 1
    ipn +=1
    n -= 1
n = 23
ipn = 1
while n >=0:
    amnts = str(random.randint(100000000, 1000000000000))
    amnt = int(amnts[:2])*10**(len(amnts)-3)
    f.write(lstr1%(i, ipn, amnt,ipn)+ '\n')
    i += 1
    ipn +=1
    n -= 1
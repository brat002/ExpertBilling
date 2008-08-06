#-*-encoding:utf-8-*-

import sys, time

from datetime import datetime, tzinfo
import random

from bpbl import bpbl
from itertools import chain
import copy

sfm = '%Y-%m-%d %H:%M:%S'
tm1 = datetime.strptime('2008-06-30 16:16:30', sfm)
tm2 = datetime.strptime('2008-06-30 16:27:01', sfm)
tm3 = datetime.strptime('2008-06-28 16:02:30', sfm)
tm4 = datetime.strptime('2008-06-28 16:36:01', sfm)
tm5 = datetime.strptime('2008-07-06 11:02:30', sfm)
tm6 = datetime.strptime('2008-07-10 18:15:01', sfm)
print datetime.now().isoformat(' ')


us1 = u"оттакая хуйня малята"
print us1.encode("unicode_escape")
print us1.encode("raw_unicode_escape")
#print us1.encode("native")
print us1.encode('ascii', 'backslashreplace')
print us1.encode("utf-8")
#print us1.decode("unicode_escape")
#smg = (1, 2, 3,4,5,6,7,8,9,1,2,3,4,5,6,7,8,9)
#smg1 = (1,0)
#data = ((1,2,3), (1,2,3), (1,2,3), (1,2,3), (1,2,3))
#aaa = time.clock()
#tm1 = []
#tm2 = []
#tm3 = []
#[(tm1.append(tuple[0]), tm2.append(tuple[2]), tm3.append(tuple[1])) for tuple in data]
#print aaa
#print tm1, tm2, tm3
#aaa = time.clock()
#tt1 = [tuple[0] for tuple in data]
#tt2 = [tuple[1] for tuple in data]
#tt3 = [tuple[2] for tuple in data]
#print aaa
#print tt1, tt2, tt3
#smg2 = ("blahblah", "zomgzomg")
#proc = '20%'
#cdd = cdDrawer()
#sec=0
#ipts = (21, 80, 113)
#pts = ', '.join(str(pint) for pint in ipts)
#selstr = "SELECT date_start, octets, direction, src_port, dst_port FROM billservice_netflowstream WHERE ((src_port IN (%s)) OR (dst_port IN (%s))) AND (date_start BETWEEN '%s' AND '%s') ORDER BY date_start;" %(pts, pts, tm1.isoformat(' '), tm6.isoformat(' '))
#print selstr
#(times, y_ps, bstr, sec) = bpbl.get_port_speed(selstr, ipts)
#print sec
#print y_ps
#itt = [[],[],[],[0]]
#tdl = [{'a':[], 'b':[]}, {'c':[0]}]
tdd = {'a':[], 'b':[]}
#print tdd.keys()
#tdl2 = tdl[:]
#tdl3 = copy.deepcopy(tdl)
#tdl[0]['a'].append(0)
#print tdl, tdl2, tdl3
#tdl2[0]['a'].append(0)
#print tdl, tdl2, tdl3
#tdl3[0]['a'].append(0)
#print tdl, tdl2, tdl3
#chain(itt).
#print smg[:]
#print str(proc)
#print repr(proc)
#aaa = (2, 5, 3, 4, None, 6, 0)
#print len(aaa)
#print [int for int in aaa if int]
a1 = [1, 2, 3, 4]
a2 = [22, 33, 55, 66]
ad = {'1':a1, '3':"aaa", '75':6, '564':5, '2':a2}
dkey = '7'
#print str(*a2[1:])
#print (ad.has_key(dkey) and (dkey + "zomg" + str(ad[dkey]))) or dkey 
#for it in ad: print it
aa = time.clock()
#print sorted(ad.keys())
#print sorted([int(strg) for strg in ad.keys()])
#print time.clock()- aa
#aa= [int(strg) for strg in ad.iterkeys()]
#aa.sort()
#print aa
#print [str(intg) for intg in sorted([int(strg) for strg in ad.iterkeys()])]
#for i in ad.iteritems():
#    print i
#print max([max(lst) for lst in ad.itervalues()])


#print [(a, aa) for a, aa in a1, a2]
#print  [(a1[i], a2[i]) for i in range(len(a1))]
#selstr = "SELECT date_start, octets, account_id FROM billservice_netflowstream WHERE %s (date_start BETWEEN '%s' AND '%s') %s ORDER BY date_start;" % ("(account_id IN %s) AND " % str((15, 16, 17, 155)), tm1.isoformat(' '), tm6.isoformat(' '), '' )
#print selstr
#(times, y_total_u, bstr, sec) = bpbl.get_total_users_traf(selstr, 6000)
#print y_total_u
aa = time.clock()
#f = open('tmpss111.png', 'wb')
#kwargs = {'return':{}}
#f.write(cdd.cddraw_nfs_total_users_speed((15, 16, 17), tm5, tm6, **kwargs))
#f.close()

#print kwargs['return']['sec']
#print aa


ddc = {'a':"zomg", 'b':54}
#print (ddc.has_key('c') and ddc['a']) 

#if not sec: print "aaa"

#print (((len(smg1)-2)==1) and smg1[2]) or (((len(smg1)-2)==0) and ' ') 
#print len(smg1)
#print proc[-1]
#print int(proc[:-1])

#print str(smg2)
#print '(%s)' % ', '.join([str(int) for int in smg2])

#print range(1, 3)
#print str(tm6)
aa = time.clock()
#print repr(smg1)
#print time.clock() - aa
'''
cvss = []
sc = staticMplCanvas( 6, 6, 96, 'w', "userstrafpie", tm1, tm6, (15, 16))        
cvss.append(sc)
sc = staticQtMplCanvas( None, 7, 3, 96, 'w', "sessions", 15, tm1, tm2)
cvss.append(sc)
sc = staticMplCanvas( 7, 3, 96, 'w', "trans_crd",  tm3, tm4, 240)
cvss.append(sc)
sc = staticMplCanvas( 7, 3, 96, 'w', "nfs_user_traf", 17, tm5, tm6, 300)
cvss.append(sc)
sc = staticMplCanvas( 7, 3, 96, 'w', "nfs_user_traf", 17, tm5, tm6, 600)
cvss.append(sc)
sc = staticMplCanvas( 7, 3, 96, 'w', "nfs_total_traf",  tm5, tm6, 600)
cvss.append(sc)
sc = staticMplCanvas( 7, 3, 96, 'w', "nfs_total_traf_bydir",  tm5, tm6, 600)
cvss.append(sc)
sc = staticMplCanvas( 7, 3, 96, 'w', "nfs_total_speed_bydir",  tm5, tm6, 300)
cvss.append(sc)
sc = staticMplCanvas( 7, 3, 96, 'w', "nfs_total_speed",  tm5, tm6, 600)
cvss.append(sc)
sc = staticMplCanvas( 7, 3, 96, 'w', "nfs_port_speed", 113, tm5, tm6, 300)
cvss.append(sc)
sc = staticMplCanvas( 7, 3, 96, 'w', "nfs_user_speed", 17, tm5, tm6, 600)
cvss.append(sc)
for ssc in cvss:
    i = random.randint(1000000000, 9999999999) 
    print i
    strg = str(i) + '.png'
    f = open(strg, 'wb+')
    ssc.print_png(f)
    f.close()
'''


l1 = [2, 4, 5, 4]
l2 = [3, 7, 1, 4]
l3 = [7, 7, 7, 4]
m1, m2, m3 = max(l1), max(l2), max(l3)
#print m1, m2, m3
z = lambda r: r / 2
aa = time.clock()
#t1, t2, t3 = [(l1[i] / 2, l2[i] / 2, l3[i] / 2) for i in range(len(l1))]
k = 2
t1, t2, t3 =  [ map(z, a) for a in (l1, l2, l3)]
#(l1, l2, l3) = [(a / k, b / k, c / k) for (a, b, c) in (l1, l2, l3)]
#print time.clock() - aa

#print t1, t2, t3

l1 = [2, 4, 5]
l2 = [3, 7, 1]
l3 = [7, 7, 7]
aa = time.clock()
t1 = [l / 2 for l in l1]
t2 = [l / 2 for l in l2]
t3 = [l / 2 for l in l3]
#print time.clock() - aa

#print t1, t2, t3
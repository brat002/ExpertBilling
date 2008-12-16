from bpcdplot import cdDrawer
import sys
from datetime import datetime
import time

cdd = cdDrawer()
sfm = '%Y-%m-%d %H:%M:%S'
tm1 = datetime.strptime('2008-06-30 16:16:30', sfm)
tm2 = datetime.strptime('2008-06-30 16:27:01', sfm)
tm3 = datetime.strptime('2008-06-28 16:02:30', sfm)
tm4 = datetime.strptime('2008-06-28 16:36:01', sfm)
tm5 = datetime.strptime('2008-07-06 11:02:30', sfm)
tm6 = datetime.strptime('2008-07-15 23:15:01', sfm)
aa = time.clock()
#print cdd.get_options("nfs_user_traf")
#cdd.set_options("nfs_user_traf", {'xychart':(700, 700), 'setlinewidth_in':3})
#print cdd.get_options("nfs_user_traf")
f = open('tmpp345678.png', 'wb')

#f.write(cdd.cddraw_nfs_user_traf(17, tm5, tm6, 2400))
f.write(cdd.cddraw("nfs_user_traf", 17, tm5, tm6, 300))
#f.write(cdd.cddraw("nfs_port_speed", 113, tm5, tm6, 300))
#f.write(cdd.cddraw("userstrafpie", tm1, tm6, (15, 16)))
#f.write(cdd.cddraw("sessions", 15, tm1, tm2))
#f.write(cdd.cddraw("trans_crd", tm3, tm4, 240))
f.close()
print time.clock() - aa
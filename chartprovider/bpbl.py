from datetime import datetime, timedelta
from bpplotadapter import bpplotAdapter
from itertools import islice, izip
import copy
import time
import itertools
#dictionary with query strings
selstrdict = {\
    'nfs'           : "SELECT date_start, octets%s FROM billservice_netflowstream WHERE %s (date_start BETWEEN '%s' AND '%s') %s ORDER BY date_start;", \
    'nfs_port_speed': "SELECT date_start, octets, direction, src_port, dst_port FROM billservice_netflowstream WHERE ((src_port IN (%s)) OR (dst_port IN (%s))) AND (date_start BETWEEN '%s' AND '%s') ORDER BY date_start;", \
    'userstrafpie'  : "SELECT bac.username, SUM(octets) FROM billservice_netflowstream AS bnf, billservice_account AS bac WHERE (bnf.account_id = bac.id) AND (bnf.date_start BETWEEN '%s' AND '%s') %s GROUP BY bnf.account_id, bac.username HAVING bnf.account_id IN (%s);", \
    'nfs_mcl_speed' : "SELECT date_start, octets, direction, traffic_class_id FROM billservice_netflowstream WHERE (traffic_class_id && ARRAY[%s]) AND (date_start BETWEEN '%s' AND '%s') %s ORDER BY date_start;", \
    'sessions'      : "SELECT sessionid, date_start, date_end, username, framed_protocol FROM radius_activesession AS ras JOIN billservice_account AS bas ON (ras.account_id = bas.id) WHERE ((account_id IN (%s)) AND ((date_start BETWEEN '%s' AND '%s') OR (date_end BETWEEN '%s' AND '%s'))) ORDER BY date_start;", \
    'trans'         : "SELECT created, summ FROM billservice_transaction WHERE ((summ %s) AND (created BETWEEN '%s' AND '%s')) ORDER BY created;",\
    'nas'           : "SELECT name, id FROM nas_nas WHERE (id %s) ORDER BY name;", \
    'usernames'     : "SELECT username, id FROM billservice_account WHERE (id %s) ORDER BY username;", \
    'classes'       : "SELECT name, id FROM nas_trafficclass WHERE (id %s) ORDER BY name;",\
    'rvclasses'     : "SELECT id, name FROM nas_trafficclass WHERE (id %s) ORDER BY name;",\
    'groupnames'    : "SELECT name, id FROM billservice_group WHERE (id %s) ORDER BY name;", \
    'prepaidtraffic': "SELECT accountprepaystrafic.* FROM billservice_accountprepaystrafic as accountprepaystrafic JOIN billservice_accounttarif as accounttarif ON accounttarif.id=accountprepaystrafic.account_tarif_id WHERE accounttarif.account_id=%s;",\
    'groups'        : "SELECT datetime, bytes%s FROM billservice_groupstat WHERE %s (datetime BETWEEN '%s' AND '%s') %s ORDER BY datetime;",\
    'gstat'         : "SELECT datetime%s FROM billservice_globalstat WHERE %s (datetime BETWEEN '%s' AND '%s') %s ORDER BY datetime;"}

#dict - selstrdict key + function




def selstrGroups(type, *args, **kwargs):
    by_col=kwargs.get('by_col')
    if by_col == 'users':
        selstr = selstrdict['groups'] % (', account_id ', '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                         ret_grp_str(kwargs) + ret_acc_str(kwargs))
    elif by_col == 'groups':
        selstr = selstrdict['groups'] % (', group_id ', '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                         ret_grp_str(kwargs) + ret_acc_str(kwargs))
    elif (by_col == None)  or (by_col == ''):
        selstr = selstrdict['groups'] % (', 0 ', '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                         ret_grp_str(kwargs) + ret_acc_str(kwargs))
    else:
        raise Exception('Unknown column - %s' % by_col)
    return selstr
        

def selstrGstat_globals(type, *args, **kwargs):
    bytes_str = ', bytes_in, bytes_out '
    by_col=kwargs.get('by_col')
    if by_col == 'users':
        selstr = selstrdict['gstat'] % (bytes_str + ', account_id ', '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                         ret_grp_str(kwargs) + ret_acc_str(kwargs) + ret_nas_str(kwargs) + ret_statclass_str(kwargs))
    elif by_col == 'groups':
        selstr = selstrdict['gstat'] % (bytes_str + ', group_id ', '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                         ret_grp_str(kwargs) + ret_acc_str(kwargs) + ret_nas_str(kwargs) + ret_statclass_str(kwargs))
    elif by_col == 'nas':
        selstr = selstrdict['gstat'] % (bytes_str + ', nas_id ', '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                         ret_grp_str(kwargs) + ret_acc_str(kwargs) + ret_nas_str(kwargs) + ret_statclass_str(kwargs))
    elif (by_col == None)  or (by_col == ''):
        selstr = selstrdict['gstat'] % (bytes_str + ', 0 ', '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                         ret_grp_str(kwargs) + ret_acc_str(kwargs) + ret_nas_str(kwargs) + ret_statclass_str(kwargs))
    else:
        raise Exception('Unknown column - %s' % by_col)
    return selstr
    

    
def selstrGstat_multi(type, *args, **kwargs):
    bytes_str = ', classes, classbytes, bytes_in, bytes_out '
    by_col=kwargs.get('by_col')
    if by_col == 'users':
        selstr = selstrdict['gstat'] % (bytes_str + ', account_id ', '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                         ret_grp_str(kwargs) + ret_acc_str(kwargs) + ret_nas_str(kwargs) + ret_statclass_str(kwargs))
    elif by_col == 'groups':
        selstr = selstrdict['gstat'] % (bytes_str + ', group_id ', '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                         ret_grp_str(kwargs) + ret_acc_str(kwargs) + ret_nas_str(kwargs) + ret_statclass_str(kwargs))
    elif by_col == 'classes':
        selstr = selstrdict['gstat'] % (bytes_str, '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                         ret_grp_str(kwargs) + ret_acc_str(kwargs) + ret_nas_str(kwargs) + ret_statclass_str(kwargs))
    elif by_col == 'nas':
        selstr = selstrdict['gstat'] % (bytes_str + ', nas_id ', '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                         ret_grp_str(kwargs) + ret_acc_str(kwargs) + ret_nas_str(kwargs) + ret_statclass_str(kwargs))
    elif (by_col == None) or (by_col == ''):
        selstr = selstrdict['gstat'] % (bytes_str + ', 0 ', '', args[0].isoformat(' '), args[1].isoformat(' '), \
                                         ret_grp_str(kwargs) + ret_acc_str(kwargs) + ret_nas_str(kwargs) + ret_statclass_str(kwargs))

    else:
        raise Exception('Unknown column - %s' % by_col)
    return selstr
    
def selstrMisc(type, *args, **kwargs):
    if type == 'trans_deb':
        selstr = selstrdict['trans'] % ('< 0', args[0].isoformat(' '), args[1].isoformat(' '))
    elif type == 'trans_crd':
        selstr = selstrdict['trans'] % ('> 0', args[0].isoformat(' '), args[1].isoformat(' '))
    elif type == 'sessions':
        selstr = selstrdict['sessions'] % (', '.join([str(intt) for intt in kwargs['users']]), args[0].isoformat(' '), args[1].isoformat(' '), args[0].isoformat(' '), args[1].isoformat(' '))
    elif type == 'usersname':
        selstr = selstrdict['usernames'] % ("IN (%s)" % ', '.join([str(vlint) for vlint in kwargs['users']]))
    elif type == 'nasname':
        selstr = selstrdict['nas'] % ("IN (%s)" % ', '.join([str(vlint) for vlint in kwargs['servers']]))
    elif type == 'rvclassesname':
        selstr = selstrdict['rvclasses'] % ''.join("IN (%s)" % ', '.join([str(vlint) for vlint in kwargs['classes']]))
    elif type == 'classesname':
        selstr = selstrdict['classes'] % ''.join("IN (%s)" % ', '.join([str(vlint) for vlint in kwargs['classes']]))
    elif type == 'groupsname':
        selstr = selstrdict['groupnames'] % ''.join("IN (%s)" % ', '.join([str(vlint) for vlint in kwargs['groups']]))
    else:
        raise Exception('Unknown type - %s!' % type)
    return selstr
    
def ret_acc_str(kwargs):
    return (((kwargs.has_key('users'))   and (" AND (account_id IN (%s)) " % ', '.join([str(vlint) for vlint in kwargs['users']]))) or  ((not kwargs.has_key('users')) and ' '))
def ret_grp_str(kwargs):
    return (((kwargs.has_key('groups'))  and (" AND (group_id IN (%s)) " % ', '.join([str(vlint) for vlint in kwargs['groups']]))) or  ((not kwargs.has_key('groups')) and ' '))
def ret_nas_str(kwargs):
    return (((kwargs.has_key('servers')) and (" AND (nas_id IN (%s)) " % ', '.join([str(vlint) for vlint in kwargs['servers']]))) or  ((not kwargs.has_key('servers')) and ' '))
def ret_nasclass_str(kwargs):
    return (((kwargs.has_key('classes')) and (" AND (traffic_class_id && ARRAY[%s]) " % ', '.join([str(vlint) for vlint in kwargs['classes']]))) or  ((not kwargs.has_key('classes')) and ' '))
def ret_statclass_str(kwargs):
    return (((kwargs.has_key('classes')) and (" AND (classes && ARRAY[%s]) " % ', '.join([str(vlint) for vlint in kwargs['classes']]))) or  ((not kwargs.has_key('classes')) and ' '))
    
selstrFmt = {'groups': (selstrGroups, 'total_multi'), 'gstat_globals': (selstrGstat_globals, 'total_multi'),\
             'gstat_multi': (selstrGstat_multi, 'total_multistat'), 'pie_gmulti': (selstrGstat_multi, 'total_multistat'),\
             'nasname':(selstrMisc, 'names'), 'usersname':(selstrMisc, 'names'), 'groupsname':(selstrMisc, 'names'), \
             'classesname':(selstrMisc, 'names'), 'rvclassesname':(selstrMisc, 'names'),\
             'trans_deb':(selstrMisc, 'trans'), 'trans_crd':(selstrMisc, 'trans'), \
             'sessions':(selstrMisc, 'sessions')}
gops = {1: lambda xlst: xlst[0], 2: lambda xlst: xlst[1] , 3: lambda xlst: xlst[1] + xlst[0], 4: lambda xlst: max(xlst[0], xlst[1])}

methodDefs = {'total_multi':{'sec':0, 'speed':False, 'ttype':'stat', 'gtype':3, 'by_col':''},'total_multistat': {'by_col':'', 'sec':0, 'speed':False, 'gtype':3, 'pie':False},\
              'total': {'sec':0, 'speed':False, 'by_col':''}, 'trans':{'trtype':'crd', 'sec':0}, 'sessions':{}}

class dataProvider(object):
    @staticmethod
    def get_data(type, *args, **kwargs):
        selsProc, proc = selstrFmt.get(type, (None, None))
        if not proc:
            raise Exception("No such data retrieval method #%s#!", type)

        method = getattr(dataProvider, "get_" + proc, None)
        if callable(method):
            defs = methodDefs.get(proc, {})
            for key, val in defs.iteritems():
                if not kwargs.has_key(key): kwargs[key] = val
            try:
                selstr = selsProc(type, *args, **kwargs)
            except Exception, ex: 
                print "Exception %s for selstr with type %s, %s, %s" % (repr(ex), type, args, kwargs) 
                return None
            try:
                data = bpplotAdapter.getdata(selstr)
                tm = data[0]
            except Exception, ex:
                print "dataProvider Data retrieval exception %s in method %s SQL %s with type %s, %s, %s" % (repr(ex), proc, selstr, type, args, kwargs)
                return None
            try:
                res =  method(type, proc, data, *args, **kwargs)
            except Exception, ex:
                print "dataProvider Method evaluation exception %s in method %s with type %s, %s, %s" % (repr(ex), proc, type, args, kwargs)
                return None
            return res
        else:
            raise Exception("Data retrieval method #%s#!", type)
    #get data methods
    @staticmethod
    def get_traf(selstr, sec=0, norm_y=True):
        '''Gets traffic data, sorts by classes, \n performs aggregation and normalizes y(traffic) values \n
	@selstr - query string
	@sec - seconds for aggregation
	@norm_y - normalization choice'''
        #get sata
        try:
            data = bpplotAdapter.getdata(selstr)
        except Exception, ex:
            raise ex
        #set up lists
        times = []
        y_in  = []
        y_out = []
        y_tr  = []
        y_total = []
        #critical place if no data selected!-----------------------
        #get first data value

        try:
            tm = data[0][0]
        except Exception, ex:
            print repr(ex)
            return 0
        # calculate #sec# span and half span
        if not sec:
            sec = bpbl.calc_seconds(data[0][0], data[-1][0])
        tmd = timedelta(days = sec / 86400, seconds=sec % 86400)
        htmd = tmd // 2
        #calculate delta between the first and the last date values
        tmdall = data[-1][0] - data[0][0]        
        #calculate iterations
        iters = (tmdall.days*86400 + tmdall.seconds) / sec
        #add one iteration for the last aggregation time period
        if (((tmdall.days*86400 + tmdall.seconds) % sec) != 0) or (not iters):
            iters +=1
        tnum = 0
        #one-time iteration through the data values and aggregate traffic values of diffeent classes by time periods
        for i in xrange(iters):
            ins, outs, trs = 0, 0, 0
            tm = tm + tmd
            times.append(tm - htmd)
            sleeper = 0
            try:
                while data[tnum][0] < tm:
                    if data[tnum][2] == 'INPUT':
                        ins  += data[tnum][1]
                    elif data[tnum][2] == 'OUTPUT':
                        outs += data[tnum][1]
                    else:
                        pass
                    tnum +=1
                    sleeper += 1
                    if sleeper == 500:
                        sleeper = 0
                        time.sleep(0.01)
                time.sleep(0.1)
            except:
                #catch exception and pass it if out of range (instead of checking)
                pass
            y_in.append(ins)
            y_out.append(outs)
        y_tr = [0]
        bstr = 'b'
        #normalize values
        if (norm_y):
            try:
                m1, m2 = max(y_in), max(y_out)
            except:
                m1, m2 = 0, 0
            y_max = m1 if m1 > m2 else m2
            if y_max < 3000:
                bstr = 'B'
            elif y_max < 3000000:
                nf = lambda y: float(y) / 1024
                y_in, y_out = [ map(nf, yval) for yval in (y_in, y_out)]
                bstr  = 'KB'
            elif y_max < 3000000000:
                nf = lambda y: float (y) / 1048576
                y_in, y_out = [ map(nf, yval) for yval in (y_in, y_out)]
                bstr  = 'MB'
            else:
                nf = lambda y: float (y) / 1073741824
                y_in, y_out = [ map(nf, yval) for yval in (y_in, y_out)]
                bstr  = 'GB'
        return (times, y_in, y_out, y_tr, bstr, sec)

    @staticmethod    
    def get_speed(selstr, sec=0):
        '''Gets speed from traffic data
	@selstr - query string
	@sec - seconds for aggregation'''
        #get traffic data
        norm_y=False
        data = bpbl.get_traf(selstr, sec, norm_y)
        if not data: return 0
        (times, y_in, y_out, y_tr, bstr, sec) = data
        try:
            m1, m2 = max(y_in), max(y_out)
        except:
            m1, m2 = 0, 0
        y_max = m1 if m1 > m2 else (m2)	
        y_max /= sec
        #calculate speed and normalize
        if y_max < 8000:
            nf = lambda y: float (y) * 8/ sec
            y_in, y_out = [ map(nf, yval) for yval in (y_in, y_out)]
            bstr  = 'b\\s'
        elif y_max < 8000000:
            nf = lambda y: float (y) * 8/ (1024*sec)
            y_in, y_out = [ map(nf, yval) for yval in (y_in, y_out)]
            bstr  = 'Kb\\s'
        elif y_max < 8000000000:
            nf = lambda y: float (y) * 8/ (1048576*sec)
            y_in, y_out = [ map(nf, yval) for yval in (y_in, y_out)]
            bstr  = 'Mb\\s'
        else:
            nf = lambda y: float (y) * 8/ (1073741824*sec)
            y_in, y_out = [ map(nf, yval) for yval in (y_in, y_out)]
            bstr  = 'Gb\\s'
        return (times, y_in, y_out, y_tr, bstr, sec)

    @staticmethod
    def get_total_multi(type, proc, data, *args, **kwargs):
        '''Get traffic with traffic classes combined
	for multiple users
	@selstr - query string
	@sec - seconds for aggregation'''
        times     = []; y_total_u = {}; zeros = []
        
        by_col = kwargs['by_col']; speed = kwargs['speed']
        sec = kwargs['sec']; gtype = kwargs['gtype']
        try:
            tm = data[0][0]
        except Exception, ex:
            print repr(ex)
            return 0
        if not sec: sec = dataProvider.calc_seconds(data[0][0], data[-1][0])
        grp = 0 if kwargs['ttype']=='stat' else 1
        tmd = timedelta(days = sec / 86400, seconds=sec % 86400)
        htmd = tmd // 2
        tmdall = data[-1][0] - data[0][0]        
        iters = (tmdall.days*86400 + tmdall.seconds) / sec
        if ((tmdall.days*86400 + tmdall.seconds) % sec) != 0:
            iters +=1
        tnum = 0
        gop = gops[gtype]
        ddata = data
        for i in xrange(iters):
            tm = tm + tmd
            times.append(tm - htmd)
            zeros.append(0)
            for item in y_total_u.itervalues():
                item.append(0)
            for dval in ddata:
                if dval[0] > tm: break
                if grp:
                    dkey = str(dval[2])
                    try: 
                        y_total_u[dkey][-1] += dval[1]
                    except KeyError, kerr:
                        y_total_u[dkey] = zeros[:]
                        y_total_u[dkey][-1] += dval[1]
                else:
                    dkey = str(dval[3])
                    try: 
                        y_total_u[dkey][-1] += gop(dval[1:3])
                    except KeyError, kerr:
                        y_total_u[dkey] = zeros[:]
                        y_total_u[dkey][-1] += gop(dval[1:3])
                tnum +=1
            ddata = itertools.islice(data, tnum, None)
        bstr = ''
        y_total_u, bstr = dataProvider.norm_ys(proc, speed, y_total_u, bstr, sec)
        return (times, y_total_u, bstr, sec)
        
    @staticmethod
    def get_total_multistat(type, proc, data, *args, **kwargs):
        '''Get traffic with traffic classes combined
	for multiple users
	@selstr - query string
	@sec - seconds for aggregation'''
        times     = []
        y_total_u = {}
        zeros     = []
        #classes = set(classes_)
        cls = 1 if kwargs['by_col'] == 'classes' else 0
        pie = kwargs['pie']; speed = kwargs['speed']
        sec = kwargs['sec']; gtype = kwargs['gtype']
        classes = (kwargs.has_key('classes') and kwargs['classes']) or []
        try:
            tm = data[0][0]
        except Exception, ex:
            print repr(ex)
            return 0

        if not sec:
            sec = dataProvider.calc_seconds(data[0][0], data[-1][0])
        tmd = timedelta(days = sec / 86400, seconds=sec % 86400)
        htmd = tmd // 2
        tmdall = data[-1][0] - data[0][0]        
        iters = (tmdall.days*86400 + tmdall.seconds) / sec
        if ((tmdall.days*86400 + tmdall.seconds) % sec) != 0:
            iters +=1
        tnum = 0
        gop = gops[gtype]
        ddata = data
        if pie: zeros.append(0)
        for i in xrange(iters):
            tm = tm + tmd
            times.append(tm - htmd)
            if not pie:
                zeros.append(0)
                for item in y_total_u.itervalues():
                    item.append(0)
            for dval in ddata:
                if dval[0] > tm: break
                if classes:
                    cdct = dict(zip(dval[1], dval[2]))
                    for class_ in classes:
                        cdlst = cdct.get(class_)
                        if cdlst:
                            dkey = str(class_) if cls else str(dval[5])
                            try: 
                                y_total_u[dkey][-1] += gop(cdlst)
                            except KeyError, kerr:
                                y_total_u[dkey] = zeros[:]
                                y_total_u[dkey][-1] += gop(cdlst)
                else:
                    dkey = str(dval[5])
                    try: 
                        y_total_u[dkey][-1] += gop(dval[3:5])
                    except KeyError, kerr:
                        y_total_u[dkey] = zeros[:]
                        y_total_u[dkey][-1] += gop(dval[3:5])                    
                tnum +=1
            ddata = itertools.islice(data, tnum, None)       
        bstr = ''
        y_total_u, bstr = dataProvider.norm_ys(proc, speed, y_total_u, bstr, sec)
        return (times, y_total_u, bstr, sec)
    
    @staticmethod
    def get_total_multi_traf(selstr, sec=0, norm_y=True):
        '''Get traffic with traffic classes combined
	for multiple users
	@selstr - query string
	@sec - seconds for aggregation'''
        data = bpplotAdapter.getdata(selstr)
        times     = []
        y_total_u = {}
        zeros     = []
        try:
            tm = data[0][0]
        except Exception, ex:
            print "GUTF: exception"
            print repr(ex)
            return 0

        if not sec:
            sec = bpbl.calc_seconds(data[0][0], data[-1][0])
        tmd = timedelta(days = sec / 86400, seconds=sec % 86400)
        htmd = tmd // 2
        tmdall = data[-1][0] - data[0][0]        
        iters = (tmdall.days*86400 + tmdall.seconds) / sec
        if ((tmdall.days*86400 + tmdall.seconds) % sec) != 0:
            iters +=1
        tnum = 0
        for i in range(iters):
            #totals = 0
            tm = tm + tmd
            times.append(tm - htmd)
            zeros.append(0)
            for item in y_total_u.itervalues():
                item.append(0)
            sleeper = 0
            try:
                while data[tnum][0] < tm:
                    #totals  += data[tnum][1]
                    try: 
                        y_total_u[str(data[tnum][2])][-1] += data[tnum][1]
                    except:
                        y_total_u[str(data[tnum][2])] = zeros[:]
                        y_total_u[str(data[tnum][2])][-1] += data[tnum][1]
                    tnum +=1
                    sleeper += 1
                    if sleeper == 500:
                        sleeper = 0
                        time.sleep(0.01)
                time.sleep(0.1)
            except:
                pass
            #y_total.append(totals)
        bstr = ''
        if norm_y:
            try:
                y_max = max([max(lst) for lst in y_total_u.itervalues()])
            except:
                y_max = 0
            if y_max < 8000:
                bstr = 'B'
            elif y_max < 8000000:
                for y_total in y_total_u.iterkeys():
                    y_total_u[y_total]  = [float(y) / 1024 for y in y_total_u[y_total]]
                bstr  = 'KB'
            elif y_max < 8000000000:
                for y_total in y_total_u.iterkeys():
                    y_total_u[y_total]  = [float(y) / 1048576 for y in y_total_u[y_total]]
                bstr  = 'MB'
            else:
                for y_total in y_total_u.iterkeys():
                    y_total_u[y_total]  = [float(y) / 1073741824 for y in y_total_u[y_total]]
                bstr  = 'GB'
        return (times, y_total_u, bstr, sec)

    @staticmethod
    def get_total_multi_speed(selstr, sec=0):
        '''Gets speed from traffic data
	@selstr - query string
	@sec - seconds for aggregation'''
        
        norm_y=False
        data = bpbl.get_total_users_traf(selstr, sec, norm_y)
        if not data:
            return 0
        (times, y_total_u, bstr, sec) = data
        try:
            y_max = max([max(lst) for lst in y_total_u.itervalues()]) * 8
        except:
            y_max = 0
        y_max /= sec
        #calculate speed and normalize
        if y_max < 8000:
            for y_total in y_total_u.iterkeys():
                y_total_u[y_total]  = [float(y) * 8 / sec for y in y_total_u[y_total]]
            bstr  = 'b\\s'
        elif y_max < 8000000:
            norm = 1024*sec
            for y_total in y_total_u.iterkeys():
                y_total_u[y_total]  = [float(y) * 8/ norm for y in y_total_u[y_total]]
            bstr  = 'Kb\\s'
        elif y_max < 8000000000:
            norm = 1048576*sec
            for y_total in y_total_u.iterkeys():
                y_total_u[y_total]  = [float(y) * 8 / norm for y in y_total_u[y_total]]
            bstr  = 'Mb\\s'
        else:
            norm = 1073741824*sec
            for y_total in y_total_u.iterkeys():
                y_total_u[y_total]  = [float(y) * 8 / norm for y in y_total_u[y_total]]
            bstr  = 'Gb\\s'
        return (times, y_total_u, bstr, sec)
    
    @staticmethod
    def get_total(type, proc, data, *args, **kwargs):

        by_col = kwargs['by_col']; speed = kwargs['speed']; sec = kwargs['sec']
        if not sec:
            sec = bpbl.calc_seconds(data[0][0], data[-1][0])
        tmd = timedelta(days = sec / 86400, seconds=sec % 86400)
        htmd = tmd // 2
        tmdall = data[-1][0] - data[0][0]        
        iters = (tmdall.days*86400 + tmdall.seconds) / sec
        if ((tmdall.days*86400 + tmdall.seconds) % sec) != 0:
            iters +=1
        tnum = 0
        ddata = data
        for i in xrange(iters):
            totals = 0
            tm = tm + tmd
            times.append(tm - htmd)
            for dval in ddata:
                if dval[0] > tm: break
                totals  += data[tnum][1]
                tnum +=1
            ddata = itertools.islice(data, tnum, None)
            y_total.append(totals)
        bstr = ''
        y_total, bstr = dataProvider.norm_ys(proc, speed, y_total, bstr)
        return (times, y_total, bstr, sec)
        
    
    @staticmethod
    def get_total_traf(selstr, sec=0, norm_y=True):
        '''Get traffic with traffic classes combined
	@selstr - query string
	@sec - seconds for aggregation'''
        data = bpplotAdapter.getdata(selstr)
        times   = []
        y_total = []
        try:
            tm = data[0][0]
        except Exception, ex:
            print repr(ex)
            return 0

        if not sec:
            sec = bpbl.calc_seconds(data[0][0], data[-1][0])
        tmd = timedelta(days = sec / 86400, seconds=sec % 86400)
        htmd = tmd // 2
        tmdall = data[-1][0] - data[0][0]        
        iters = (tmdall.days*86400 + tmdall.seconds) / sec
        if ((tmdall.days*86400 + tmdall.seconds) % sec) != 0:
            iters +=1
        tnum = 0
        for i in range(iters):
            totals = 0
            tm = tm + tmd
            times.append(tm - htmd)
            try:
                while data[tnum][0] < tm:
                    totals  += data[tnum][1]
                    tnum +=1
                    sleeper += 1
            except:
                pass
            y_total.append(totals)
        bstr = ''
        if norm_y:
            try:
                y_max = max(y_total)
            except:
                y_max = 0
            if y_max < 8000:
                bstr = 'B'
            elif y_max < 8000000:
                y_total  = [float(y) / 1024 for y in y_total]
                bstr  = 'KB'
                y_total  = [float(y) / 1048576 for y in y_total]
                bstr  = 'MB'
            else:
                y_total  = [float(y) / 1073741824 for y in y_total]
                bstr  = 'GB'
        return (times, y_total, bstr, sec)

    @staticmethod
    def get_total_speed(selstr, sec=0):
        '''Get speed for traffic traffic classes combined
	@selstr - query string
	@sec - seconds for aggregation'''
        norm_y=False
        data = bpbl.get_total_traf(selstr, sec, norm_y)
        if not data: return 0
        (times, y_total, bstr, sec) = data
        try:
            y_max = max(y_total)*8 / sec
        except:
            y_max = 0
        if y_max < 8000:
            y_total  = [float(y) * 8/ sec for y in y_total]
            bstr = 'B\\s'
        elif y_max < 8000000:
            y_total  = [float(y) * 8/ (1024*sec) for y in y_total]
            bstr  = 'Kb\\s'
        elif y_max < 8000000000:
            y_total  = [float(y) * 8/ (1048576*sec) for y in y_total]
            bstr  = 'Mb\\s'
        else:
            y_total  = [float(y) * 8/ (1073741824*sec) for y in y_total]
            bstr  = 'Gb\\s'
        return (times, y_total, bstr, sec)

    
    @staticmethod
    def get_multi_speed(selstr, objs, counts, sec=0, arr=0):
        '''Get speed with traffic classes combined for a certain ports
	@selstr - query string
	@sec - seconds for aggregation
	@ports - ports tuple to count traffic on'''
        data = bpplotAdapter.getdata(selstr)
        times  = []
        y_ps = {}
        #zeros = [{'input': [], 'output': []}, {'input': [], 'output': []}]
        zeros = [{'input': [], 'output': [], 'transit': []}]
        try:
            tm = data[0][0]
        except Exception, ex:
            print repr(ex)
            return 0
        if not sec:
            sec = bpbl.calc_seconds(data[0][0], data[-1][0])
        tmd = timedelta(days = sec / 86400, seconds=sec % 86400)
        htmd = tmd // 2
        tmdall = data[-1][0] - data[0][0]        
        iters = (tmdall.days*86400 + tmdall.seconds) / sec
        if ((tmdall.days*86400 + tmdall.seconds) % sec) != 0:
            iters +=1
        tnum = 0

        for i in range(iters):
            tm = tm + tmd
            times.append(tm - htmd)
            for dct in zeros:
                for lst in dct.itervalues():
                    lst.append(0)

            for val in y_ps.itervalues():
                for dct in val:
                    for lst in dct.itervalues():
                        lst.append(0)
            try:
                while data[tnum][0] < tm:
                    for cts in range(counts):
                        if not arr:
                            if data[tnum][3+cts] in objs:
                                try:
                                    y_ps[str(data[tnum][3+cts])][0][data[tnum][2].lower()][-1] += data[tnum][1]
                                except:
                                    y_ps[str(data[tnum][3+cts])] = copy.deepcopy(zeros)
                                    y_ps[str(data[tnum][3+cts])][0][data[tnum][2].lower()][-1] += data[tnum][1]
                        else:
                            for ctval in data[tnum][3+cts]:
                                try:
                                    y_ps[str(ctval)][0][data[tnum][2].lower()][-1] += data[tnum][1]
                                except:
                                    y_ps[str(ctval)] = copy.deepcopy(zeros)
                                    y_ps[str(ctval)][0][data[tnum][2].lower()][-1] += data[tnum][1]
                        
                    tnum +=1
                    sleeper += 1
                    if sleeper == 500:
                        sleeper = 0
                        time.sleep(0.01)
                time.sleep(0.1)
                

            except IndexError, ierr:
                pass
        y_maxmums = [max([max([max(xlst) for xlst in xdct.values()]) for xdct in lstm]) for lstm in y_ps.itervalues()]

        i = 0
        bstr = {}
        bstr['0'] = '' 
        for val in y_ps.iteritems():
            try:
                y_max = y_maxmums[i] * 8
            except:
                y_max = 0
            
            if y_max < 6000:
                bstr[val[0]]  = 'b\\s'
            elif y_max < 8000000:
                for dct in val[1]:
                    for dirk in dct.iterkeys():
                        dct[dirk] = [(float(y) * 8)/ 1024 for y in dct[dirk]]
                bstr[val[0]]  = 'Kb\\s'
            elif y_max < 6000000000:
                for dct in val[1]:
                    for dirk in dct.iterkeys():
                        dct[dirk] = [(float(y) * 8)/ 1048576 for y in dct[dirk]]
                bstr[val[0]]  = 'Mb\\s'
            else:
                for dct in val[1]:
                    for dirk in dct.iterkeys():
                        dct[dirk] = [(float(y) * 8)/ 1073741824 for y in dct[dirk]]
                bstr[val[0]]  = 'Gb\\s'
            i += 1
        return (times, y_ps, bstr, sec)

    @staticmethod
    def get_pie_traf(selstr):
        '''Gets data for users-traffic pie plot
	@selstr - query string'''
        data = bpplotAdapter.getdata(selstr)
        try: tmpx = data[0][0]
        except Exception, ex: 
            print repr(ex)
            return 0
        '''x      = [tuple[1] for tuple in data]
	labels = [tuple[0] for tuple in data]'''
        x = []; labels = []
        [(x.append(tuple[1]), labels.append(tuple[0])) for tuple in data]
        try:
            x_max = max(x)
        except:
            x_max = 0
        if x_max < 6000:
            bstr = 'b'
        elif x_max < 6000000:
            x  = [float(numx) / 1024 for numx in x]
            bstr  = 'kb'
        elif x_max < 6000000000:
            x  = [float(numx) / 1048576 for numx in x]
            bstr  = 'Mb'
        else:
            x  = [float(numx) / 1073741824 for numx in x]
            bstr  = 'Gb'
        return (x, labels, bstr)

    @staticmethod
    def get_trans(type, proc, data, *args, **kwargs):
        '''Gets transactions data
	@selstr - query string
	@sec - seconds for aggregation
	@trtype - transaction type 'crd'- for credit, 'dbt' - for debit'''

        times = []
        summ  = []        
        sec = kwargs['sec']; trtype = kwargs['trtype']
        if not sec:
            sec = dataProvider.calc_seconds(data[0][0], data[-1][0])
            
        try:
            tm = data[0][0]
        except Exception, ex:
            print repr(ex)
            return 0
        sec = sec * 20
        tmd = timedelta(days = sec / 86400, seconds=sec % 86400)
        htmd = tmd // 2
        tmdall = data[-1][0] - data[0][0]        
        iters = (tmdall.days*86400 + tmdall.seconds) / sec
        if ((tmdall.days*86400 + tmdall.seconds) % sec) != 0:
            iters +=1
        tnum = 0
        for i in range(iters):
            smv = 0
            tm = tm + tmd
            times.append(tm - htmd)
            try: 
                while data[tnum][0] < tm:
                    smv  += data[tnum][1]
                    tnum += 1
            except: pass
            #sum of previous values
            try: smv += summ[-1]
            except: pass
            summ.append(smv)
        if trtype == 'crd':
            summ = [abs(x) for x in summ]

        bstr = ''
        '''summ_max = max(summ) 
	if summ_max < 15000:
            bstr = '%d'
        elif summ_max < 15000000:
            summ = map(lambda y: float(y) / 1024, y_out) 
            bstr = '%.2f k'
        else:
            summ = map(lambda y: float(y) / 1048576, y_out) 
            bstr = '%.2f M' '''
        return (times, summ, bstr, sec)

    @staticmethod
    def get_sessions(type, proc, data, *args, **kwargs):
        '''Gets sessions data
	@selstr - query string'''
        t_start = []; t_end = []; sessid = []; username = []; protocol = []
        [(t_start.append(tuple[1]), t_end.append(tuple[2]), sessid.append(tuple[0]), username.append(tuple[3]), protocol.append(tuple[4])) for tuple in data]
        return (t_start, t_end, sessid, username, protocol)

    @staticmethod
    def get_names(type, proc, data, *args, **kwargs):
        return data

    @staticmethod
    def calc_seconds(date_start, date_end):
        tmd = date_end - date_start
        seconds = abs(tmd.days*86400 + tmd.seconds)
        if seconds < 360: return 1
        else: return seconds / 360


    @staticmethod
    def norm_ys(type, speed, *args):
        if type == 'total':
            return dataProvider.norm_total(speed, *args)
        elif type in ('total_multi', 'total_multistat'):
            return dataProvider.norm_total_multi(speed, *args)
        else:
            raise Exception("Norm_ys: Unknown type: %s" % type) 
    @staticmethod
    def norm_total(speed, *args):
        y_total = args[0]
        bstr = args[1]
        sec  = args[2]
        if speed:
            try:
                y_max = max(y_total)*8 / sec
            except:
                y_max = 0
            if y_max < 8000:
                y_total  = [float(y) * 8/ sec for y in y_total]
                bstr = 'B\\s'
            elif y_max < 8000000:
                y_total  = [float(y) * 8/ (1024*sec) for y in y_total]
                bstr  = 'Kb\\s'
            elif y_max < 8000000000:
                y_total  = [float(y) * 8/ (1048576*sec) for y in y_total]
                bstr  = 'Mb\\s'
            else:
                y_total  = [float(y) * 8/ (1073741824*sec) for y in y_total]
                bstr  = 'Gb\\s'
        else:
            try:
                y_max = max(y_total)
            except:
                y_max = 0
            if y_max < 8000:
                bstr = 'B'
            elif y_max < 8000000:
                y_total  = [float(y) / 1024 for y in y_total]
                bstr  = 'KB'
                y_total  = [float(y) / 1048576 for y in y_total]
                bstr  = 'MB'
            else:
                y_total  = [float(y) / 1073741824 for y in y_total]
                bstr  = 'GB'
                
        return (y_total, bstr)
    
    @staticmethod
    def norm_total_multi(speed, *args):
        y_total_u = args[0]
        bstr = args[1]
        sec  = args[2]
        if speed:
            try:
                y_max = max([max(lst) for lst in y_total_u.itervalues()]) * 8
            except:
                y_max = 0
            y_max /= sec
            #calculate speed and normalize
            if y_max < 8000:
                for y_total in y_total_u.iterkeys():
                    y_total_u[y_total]  = [float(y) * 8 / sec for y in y_total_u[y_total]]
                bstr  = 'b\\s'
            elif y_max < 8000000:
                norm = 1024*sec
                for y_total in y_total_u.iterkeys():
                    y_total_u[y_total]  = [float(y) * 8/ norm for y in y_total_u[y_total]]
                bstr  = 'Kb\\s'
            elif y_max < 8000000000:
                norm = 1048576*sec
                for y_total in y_total_u.iterkeys():
                    y_total_u[y_total]  = [float(y) * 8 / norm for y in y_total_u[y_total]]
                bstr  = 'Mb\\s'
            else:
                norm = 1073741824*sec
                for y_total in y_total_u.iterkeys():
                    y_total_u[y_total]  = [float(y) * 8 / norm for y in y_total_u[y_total]]
                bstr  = 'Gb\\s'
        else:
            try:
                y_max = max([max(lst) for lst in y_total_u.itervalues()])
            except:
                y_max = 0
            if y_max < 8000:
                bstr = 'B'
            elif y_max < 8000000:
                for y_total in y_total_u.iterkeys():
                    y_total_u[y_total]  = [float(y) / 1024 for y in y_total_u[y_total]]
                bstr  = 'KB'
            elif y_max < 8000000000:
                for y_total in y_total_u.iterkeys():
                    y_total_u[y_total]  = [float(y) / 1048576 for y in y_total_u[y_total]]
                bstr  = 'MB'
            else:
                for y_total in y_total_u.iterkeys():
                    y_total_u[y_total]  = [float(y) / 1073741824 for y in y_total_u[y_total]]
                bstr  = 'GB'
                
        return (y_total_u, bstr)
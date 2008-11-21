from datetime import datetime, timedelta
from bpplotadapter import bpplotAdapter
import copy

#dictionary with query strings
selstrdict = {\
    'nfs'           : "SELECT date_start, octets%s FROM billservice_netflowstream WHERE %s (date_start BETWEEN '%s' AND '%s') %s ORDER BY date_start;", \
    'nfs_port_speed': "SELECT date_start, octets, direction, src_port, dst_port FROM billservice_netflowstream WHERE ((src_port IN (%s)) OR (dst_port IN (%s))) AND (date_start BETWEEN '%s' AND '%s') ORDER BY date_start;", \
    'userstrafpie'  : "SELECT bac.username, SUM(octets) FROM billservice_netflowstream AS bnf, billservice_account AS bac WHERE (bnf.account_id = bac.id) AND (bnf.date_start BETWEEN '%s' AND '%s') %s GROUP BY bnf.account_id, bac.username HAVING bnf.account_id IN (%s);", \
    'nfs_mcl_speed' : "SELECT date_start, octets, direction, traffic_class_id FROM billservice_netflowstream WHERE (traffic_class_id IN (%s)) AND (date_start BETWEEN '%s' AND '%s') %s ORDER BY date_start;", \
    'sessions'      : "SELECT sessionid, date_start, date_end, username, framed_protocol FROM radius_activesession AS ras JOIN billservice_account AS bas ON (ras.account_id = bas.id) WHERE ((account_id IN (%s)) AND ((date_start BETWEEN '%s' AND '%s') OR (date_end BETWEEN '%s' AND '%s'))) ORDER BY date_start;", \
    'trans'         : "SELECT created, summ FROM billservice_transaction WHERE ((summ %s) AND (created BETWEEN '%s' AND '%s')) ORDER BY created;",\
    'nas'           : "SELECT name, id FROM nas_nas WHERE (id %s) ORDER BY name;", \
    'usernames'     : "SELECT username, id FROM billservice_account WHERE (id %s) ORDER BY username;", \
    'classes'       : "SELECT name, id FROM nas_trafficclass WHERE (id %s) ORDER BY name;",\
    'rvclasses'     : "SELECT id, name FROM nas_trafficclass WHERE (id %s) ORDER BY name;",\
    'prepaidtraffic': "SELECT accountprepaystrafic.* FROM billservice_accountprepaystrafic as accountprepaystrafic JOIN billservice_accounttarif as accounttarif ON accounttarif.id=accountprepaystrafic.account_tarif_id WHERE accounttarif.account_id=%s;"}

class bpbl(object):
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
            print ex
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
        for i in range(iters):
            ins, outs, trs = 0, 0, 0
            tm = tm + tmd
            times.append(tm - htmd)
            try:
                while data[tnum][0] < tm:
                    if data[tnum][2] == 'INPUT':
                        ins  += data[tnum][1]
                    elif data[tnum][2] == 'OUTPUT':
                        outs += data[tnum][1]
                    else:
                        #trs  += data[tnum][1]
                        pass
                    tnum +=1
            except:
                #catch exception and pass it if out of range (instead of checking)
                pass
            y_in.append(ins)
            y_out.append(outs)
            #y_tr.append(trs)
        y_tr = [0]
        bstr = 'b'
        #normalize values
        if (norm_y):
            try:
                m1, m2, m3 = max(y_in), max(y_out), max(y_tr)
            except: 
                m1, m2, m3 = 0, 0, 0
            y_max = m1 if m1 > m2 else (m2 if m2 > m3 else m3)	    
            if y_max < 3000:
                bstr = 'B'
            elif y_max < 3000000:
                nf = lambda y: float(y) / 1024
                y_in, y_out, y_tr = [ map(nf, yval) for yval in (y_in, y_out, y_tr)]
                bstr  = 'KB'
            elif y_max < 3000000000:
                nf = lambda y: float (y) / 1048576
                y_in, y_out, y_tr = [ map(nf, yval) for yval in (y_in, y_out, y_tr)]
                bstr  = 'MB'
            else:
                nf = lambda y: float (y) / 1073741824
                y_in, y_out, y_tr = [ map(nf, yval) for yval in (y_in, y_out, y_tr)]
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
            m1, m2, m3 = max(y_in), max(y_out), max(y_tr)
        except:
            m1, m2, m3 = 0, 0, 0
        y_max = m1 if m1 > m2 else (m2 if m2 > m3 else m3)	
        y_max /= sec
        #calculate speed and normalize
        if y_max < 8000:
            nf = lambda y: float (y) * 8/ sec
            y_in, y_out, y_tr = [ map(nf, yval) for yval in (y_in, y_out, y_tr)]
            bstr  = 'b\\s'
        elif y_max < 8000000:
            nf = lambda y: float (y) * 8/ (1024*sec)
            y_in, y_out, y_tr = [ map(nf, yval) for yval in (y_in, y_out, y_tr)]
            bstr  = 'Kb\\s'
        elif y_max < 8000000000:
            nf = lambda y: float (y) * 8/ (1048576*sec)
            y_in, y_out, y_tr = [ map(nf, yval) for yval in (y_in, y_out, y_tr)]
            bstr  = 'Mb\\s'
        else:
            nf = lambda y: float (y) * 8/ (1073741824*sec)
            y_in, y_out, y_tr = [ map(nf, yval) for yval in (y_in, y_out, y_tr)]
            bstr  = 'Gb\\s'
        return (times, y_in, y_out, y_tr, bstr, sec)

    @staticmethod
    def get_total_users_traf(selstr, sec=0, norm_y=True):
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
            print ex
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

            try:
                while data[tnum][0] < tm:
                    #totals  += data[tnum][1]
                    try: 
                        y_total_u[str(data[tnum][2])][-1] += data[tnum][1]
                    except:
                        y_total_u[str(data[tnum][2])] = zeros[:]
                        y_total_u[str(data[tnum][2])][-1] += data[tnum][1]
                    tnum +=1
            except:
                pass
            #y_total.append(totals)
        bstr = ''
        if norm_y:
            try:
                y_max = max([max(lst) for lst in y_total_u.itervalues()])
            except:
                y_max = 0
            #print y_max
            if y_max < 8000:
                bstr = 'B'
            elif y_max < 8000000:
                #y_total = map(lambda y: float(y) / 1024, y_total)
                for y_total in y_total_u.iterkeys():
                    y_total_u[y_total]  = [float(y) / 1024 for y in y_total_u[y_total]]
                bstr  = 'KB'
            elif y_max < 8000000000:
                #y_total = map(lambda y: float(y) / 1048576, y_total)
                for y_total in y_total_u.iterkeys():
                    y_total_u[y_total]  = [float(y) / 1048576 for y in y_total_u[y_total]]
                bstr  = 'MB'
            else:
                for y_total in y_total_u.iterkeys():
                    y_total_u[y_total]  = [float(y) / 1073741824 for y in y_total_u[y_total]]
                bstr  = 'GB'
        return (times, y_total_u, bstr, sec)

    @staticmethod
    def get_total_users_speed(selstr, sec=0):
        '''Gets speed from traffic data
	@selstr - query string
	@sec - seconds for aggregation'''
        #get traffic data
        print "GUTS: start"
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
            '''y_in  = [float(y) / sec for y in y_in]
	    y_out = [float(y) / sec for y in y_out]
	    y_tr  = [float(y) / sec for y in y_tr]'''
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
            print ex
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
                #y_total = map(lambda y: float(y) / 1024, y_total)
                y_total  = [float(y) / 1024 for y in y_total]
                bstr  = 'KB'
            elif y_max < 8000000000:
                #y_total = map(lambda y: float(y) / 1048576, y_total)
                y_total  = [float(y) / 1048576 for y in y_total]
                bstr  = 'MB'
            else:
                y_total  = [float(y) / 1073741824 for y in y_total]
                bstr  = 'GB'
        print y_total
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
    #@staticmethod
    """def get_port_speed(selstr, ports, sec=0):
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
            print ex
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
                    if data[tnum][3] in ports:
                        try:
                            y_ps[str(data[tnum][3])][0][data[tnum][2].lower()][-1] += data[tnum][1]
                        except:
                            y_ps[str(data[tnum][3])] = copy.deepcopy(zeros)
                            y_ps[str(data[tnum][3])][0][data[tnum][2].lower()][-1] += data[tnum][1]

                    if data[tnum][4] in ports:
                        try:
                            y_ps[str(data[tnum][4])][0][data[tnum][2].lower()][-1] += data[tnum][1]
                        except:
                            y_ps[str(data[tnum][4])] = copy.deepcopy(zeros)
                            y_ps[str(data[tnum][4])][0][data[tnum][2].lower()][-1] += data[tnum][1]

                    tnum +=1

            except IndexError, ierr:
                pass
        y_maxmums = [max([max(max(dct.itervalues())) for dct in lstm]) for lstm in y_ps.itervalues()]

        i = 0
        bstr = {}
        bstr['0'] = '' 
        for val in y_ps.iteritems():
            y_max = y_maxmums[i]
            if y_max < 6000:
                bstr[val[0]]  = 'b'
            elif y_max < 8000000:
                for dct in val[1]:
                    for dirk in dct.iterkeys():
                        dct[dirk] = [float(y) * 8/ 1024 for y in dct[dirk]]
                bstr[val[0]]  = 'Kb'
            elif y_max < 6000000000:
                for dct in val[1]:
                    for dirk in dct.iterkeys():
                        dct[dirk] = [float(y) * 8/ 1048576 for y in dct[dirk]]
                bstr[val[0]]  = 'Mb'
            else:
                for dct in val[1]:
                    for dirk in dct.iterkeys():
                        dct[dirk] = [float(y) * 8/ 1073741824 for y in dct[dirk]]
                bstr[val[0]]  = 'Gb'
            i += 1
        return (times, y_ps, bstr, sec)"""
    
    @staticmethod
    def get_multi_speed(selstr, objs, counts, sec=0):
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
            print ex
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
                        if data[tnum][3+cts] in objs:
                            try:
                                y_ps[str(data[tnum][3+cts])][0][data[tnum][2].lower()][-1] += data[tnum][1]
                            except:
                                y_ps[str(data[tnum][3+cts])] = copy.deepcopy(zeros)
                                y_ps[str(data[tnum][3+cts])][0][data[tnum][2].lower()][-1] += data[tnum][1]

                    tnum +=1

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
            print ex
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
    def get_trans(selstr, trtype, sec=0):
        '''Gets transactions data
	@selstr - query string
	@sec - seconds for aggregation
	@trtype - transaction type 'crd'- for credit, 'dbt' - for debit'''
        data  = bpplotAdapter.getdata(selstr)
        times = []
        summ  = []
        try:
            tm = data[0][0]
        except Exception, ex:
            print ex
            return 0

        if not sec:
            sec = bpbl.calc_seconds(data[0][0], data[-1][0])
        #-------------------------------

        sec = sec * 20
        #-------------------------------
        tmd = timedelta(days = sec / 86400, seconds=sec % 86400)
        htmd = tmd // 2
        tmdall = data[-1][0] - data[0][0]        
        iters = (tmdall.days*86400 + tmdall.seconds) / sec
        if ((tmdall.days*86400 + tmdall.seconds) % sec) != 0:
            iters +=1
        tnum = 0
        print iters
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
    def get_sessions(selstr):
        '''Gets sessions data
	@selstr - query string'''

        data = bpplotAdapter.getdata(selstr)
        try:
            datetm = data[0][0]
        except Exception, ex:
            print ex
            return 0
        '''t_start  = [tuple[1] for tuple in data]
	t_end    = [tuple[2] for tuple in data]
	sessid   = [tuple[0] for tuple in data]
	username = [tuple[3] for tuple in data]
	protocol = [tuple[4] for tuple in data]'''
        t_start = []; t_end = []; sessid = []; username = []; protocol = []
        [(t_start.append(tuple[1]), t_end.append(tuple[2]), sessid.append(tuple[0]), username.append(tuple[3]), protocol.append(tuple[4])) for tuple in data]
        return (t_start, t_end, sessid, username, protocol)

    @staticmethod
    def get_nas(selstr):
        data = bpplotAdapter.getdata(selstr)
        try:
            datetm = data[0][0]
        except Exception, ex:
            print ex
            return 0
        return data

    @staticmethod
    def get_usernames(selstr):
        data = bpplotAdapter.getdata(selstr)
        try:
            datetm = data[0][0]
        except Exception, ex:
            print ex
            return 0
        return data

    @staticmethod
    def calc_seconds(date_start, date_end):
        tmd = date_end - date_start
        seconds = abs(tmd.days*86400 + tmd.seconds)
        if seconds < 360: return 1
        else: return seconds / 360




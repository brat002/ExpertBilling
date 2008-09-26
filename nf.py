#-*-coding=utf-8-*-

import socket, select, struct, datetime, time, sys
from IPy import *
try:
    import mx.DateTime
except:
    print "cannot inport mx"
import settings
import psycopg2
#import dummy_threading as threading
import threading
import gc
#from DBUtils.PooledDB import PooledDB

trafficclasses_pool = []
dcache   = {}
nascache = {}
#nascache = []
tdMinute = datetime.timedelta(seconds=60)
sleepTime = 300.0

def RefreshClasses():
    pool = []
    cur.execute("SELECT id, name, weight, store, passthrough FROM nas_trafficclass ORDER BY weight, passthrough;")
    traffic_classes=cur.fetchall()
    for traffic_class in traffic_classes:
        #ORDER BY tn.direction DESC - для того, чтобы сравнение начиналось с нод, описывающих транзитное направление.
        cur.execute(
        """
        SELECT tn.name, tn.direction, tn.protocol, tn.src_ip, tn.src_mask, tn.src_port, tn.dst_ip, tn.dst_mask, tn.dst_port,
        tn.next_hop
        FROM nas_trafficnode as tn
        WHERE tn.traffic_class_id=%s ORDER BY tn.direction DESC;
        """ % traffic_class[0]
        )
        traffic_nodes=cur.fetchall()
        pool.append(TrafficClass(traffic_class, nodes=traffic_nodes))

    return pool

class TrafficNode(object):
    """
    В src или dst не должны попадать строки статистики, которые описаны как транзитные
    """
    def __init__(self, node_data):
        self.name, \
        self.direction, \
        self.protocol, \
        self.src_ip, \
        self.src_mask, \
        self.src_port, \
        self.dst_ip, \
        self.dst_mask, \
        self.dst_port, \
        self.next_hop = node_data
        #self.src = IP("%s/%s" % (self.src_ip, self.src_mask))
        #self.dst = IP("%s/%s" % (self.dst_ip, self.dst_mask))
	self.src = IP(self.src_ip)
	self.dst = IP(self.dst_ip)
        self.n_hop = IP(self.next_hop)

    def check_class(self, src_ip, src_port, dst_ip, dst_port, protocol, next_hop):
        if IP(src_ip) in self.src and IP(dst_ip) in self.dst and (IP(next_hop)==self.n_hop or self.next_hop=='0.0.0.0') and (src_port==self.src_port or self.src_port==0) and (dst_port==self.dst_port or self.dst_port==0) and (protocol==self.protocol or self.protocol==0):
            return True, self.direction
        else:
            return False, self.direction

class TrafficClass(object):
    def __init__(self, class_data, nodes):
        self.id, \
        self.name, \
        self.weight, \
        self.store,\
        self.passthtough = class_data
        self.data=[]
        
        for node in nodes:
            self.data.append(TrafficNode(node))

    def check(self, src, src_port, dst, dst_port, protocol, next_hop):
        #print src, src_port, dst, dst_port, protocol, next_hop
        for node in self.data:
            res=node.check_class(src, src_port, dst, dst_port, protocol, next_hop)
            #print res
            if res[0]:
                return self.id, res[1]
        return False, False





class Flow(object):
	# Virtual base class
	LENGTH = 0
	def __init__(self, data):
		if len(data) != self.LENGTH:
			raise ValueError, "Short flow"

	def _int_to_ipv4(self, addr):
	    return ".".join(map(str, struct.unpack("BBBB", addr)))
	    #return "%d.%d.%d.%d" % (addr >> 24 & 0xff, addr >> 16 & 0xff, addr >> 8 & 0xff, addr & 0xff)

class Header(object):
	# Virtual base class
	LENGTH = 0
	def __init__(self, data):
		if len(data) != self.LENGTH:
			raise ValueError, "Short flow header"

class Header5(Header):
	LENGTH = struct.calcsize("!HHIIIIBBH")
	def __init__(self, data):
		if len(data) != self.LENGTH:
			raise ValueError, "Short flow header"

		_nh = struct.unpack("!HHIIIIBBH", data)
		self.version = _nh[0]
		self.num_flows = _nh[1]
		self.sys_uptime = _nh[2]
		self.time_secs = _nh[3]
		self.time_nsecs = _nh[4]

	def __str__(self):
		ret  = "NetFlow Header v.%d containing %d flows\n" % \
		    (self.version, self.num_flows)
		ret += "    Router uptime: %d\n" % self.sys_uptime
		ret += "    Current time:  %d.%09d\n" % \
		    (self.time_secs, self.time_nsecs)

		return ret

class Flow5(Flow):


	LENGTH = struct.calcsize("!4s4s4sHHIIIIHHBBBBHHBBH")
	#print LENGTH
	def __init__(self, data):
		if len(data) != self.LENGTH:
			raise ValueError, "Short flow: data length: %d; LENGTH: %d" % (len(data), self.LENGTH)

		_ff = struct.unpack("!4s4s4sHHIIIIHHBBBBHHBBH", data)
		self.src_addr = self._int_to_ipv4(_ff[0])
		self.dst_addr = self._int_to_ipv4(_ff[1])
		self.next_hop = self._int_to_ipv4(_ff[2])
		self.in_index = _ff[3]
		self.out_index = _ff[4]
		self.packets = _ff[5]
		self.octets = _ff[6]
		self.start = _ff[7]
		self.finish = _ff[8]
		self.src_port = _ff[9]
		self.dst_port = _ff[10]
		# pad
		self.tcp_flags = _ff[12]
		self.protocol = _ff[13]
		self.tos = _ff[14]
		self.source_as = _ff[15]
		self.dst_as = _ff[16]
		self.src_netmask_length = _ff[17]
		self.dst_netmask_length = _ff[18]

class NetFlowPacket:
    FLOW_TYPES = {
		5 : (Header5, Flow5),
	}
    def __init__(self, data, addrport, flowCache):
	self.fc = flowCache
        if len(data) < 16:
            raise ValueError, "Short packet"
        '''nas_id = None
	for ip, nid in nascache:
	    #print ip, addrport[0]
	    if ip == addrport[0]:
		nas_id = nid
		break'''
		
	nas_id = nascache.get(addrport[0])
	if not nas_id:
	    cur.execute("""SELECT id from nas_nas WHERE  ipaddress='%s'""" % addrport[0])
	    #print "after_nas", time.clock()-a
	    try:
		nas_id = cur.fetchone()[0]
		#nascache.append((addrport[0], nas_id))
		nascache[addrport[0]] = nas_id
	    except Exception, e:
		print e
		return
        flows=[]
        if nas_id!=None:	    
            _nf = struct.unpack("!H", data[:2])
            self.version = _nf[0]
            if not self.version in self.FLOW_TYPES.keys():
                raise RuntimeWarning, \
                "NetFlow version %d is not yet implemented" % \
            	    self.version
            hdr_class = self.FLOW_TYPES[self.version][0]
            flow_class = self.FLOW_TYPES[self.version][1]
            self.hdr = hdr_class(data[:hdr_class.LENGTH])
            # получаем классы трафика

            
            for n in range(self.hdr.num_flows):

                offset = self.hdr.LENGTH + (flow_class.LENGTH * n)

                flow_data = data[offset:offset + flow_class.LENGTH]
                
                
                flow=flow_class(flow_data)
		flow.nas_id = nas_id
		self.fc.addflow5(flow)
                #print "after_flow_class", time.clock()-a
                #traffic_class=None
                #print flow
		#print """SELECT * FROM append_netflow2(%d, '%s', '%s','%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d);""" % (nas_id,flow.src_addr, flow.dst_addr, flow.next_hop, flow.in_index, flow.out_index, flow.packets, flow.octets, flow.src_port, flow.dst_port, flow.tcp_flags, flow.protocol, flow.tos, flow.source_as, flow.dst_as, flow.src_netmask_length, flow.dst_netmask_length)
		#cur.execute("""SELECT * FROM append_netflow(%d, '%s', '%s','%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d);""" % (nas_id,flow.src_addr, flow.dst_addr, flow.next_hop, flow.in_index, flow.out_index, flow.packets, flow.octets, flow.src_port, flow.dst_port, flow.tcp_flags, flow.protocol, flow.tos, flow.source_as, flow.dst_as, flow.src_netmask_length, flow.dst_netmask_length))
		
		#print cur.fetchall()
	    
                #match = False
                '''for traffic_class in trafficclasses_pool:
		    cur.execute("""SELECT id FROM billservice_account WHERE (nas_id=%d) AND (vpn_ip_address='%s' OR vpn_ip_address='%s' OR ipn_ip_address='%s' OR ipn_ip_address='%s') LIMIT 1;""" % (nas_id, flow.src_addr, flow.src_addr, flow.dst_addr, flow.dst_addr))
		    
		    acc_id = cur.fetchone()
		    if acc_id:
			acc_id=acc_id[0]
			res=traffic_class.check(flow.src_addr, flow.src_port, flow.dst_addr, flow.dst_port, flow.protocol, flow.next_hop)
                    #print "after_trafic_check", time.clock()-a
                    #print res
			if res[0] and match==False:
			    #print res[0]
			    if traffic_class.passthtough==False:
				match=True
				
			    traffic_class, direction = res
			    flows.append(
			    {
			    'nas_id':nas_id, 'date_start':datetime.datetime.now(),
			    'src_addr':flow.src_addr, 'dst_addr':flow.dst_addr,
			    'traffic_class_id':traffic_class,
			    'direction': direction,
			    'next_hop': flow.next_hop,
			    'in_index':flow.in_index,
			    'out_index' : flow.out_index,
			    'packets' : flow.packets,
			    'octets' : flow.octets,
			    'src_port' : flow.src_port,
			    'dst_port' : flow.dst_port,
			    'tcp_flags' : flow.tcp_flags,
			    'protocol' : flow.protocol,
			    'tos' : flow.tos,
			    'source_as' : flow.source_as,
			    'dst_as' : flow.dst_as,
			    'src_netmask_length' : flow.src_netmask_length,
			    'dst_netmask_length' : flow.dst_netmask_length,
			    'fetched':False,
			    'account_id':acc_id
			    }
			    )
	    #cur.connection.commit()
            #print flows
            #print flows
            #print "before_insert", time.clock()-a
            cur.executemany("""
                        INSERT INTO billservice_rawnetflowstream(nas_id, date_start, src_addr, dst_addr, traffic_class_id, direction, next_hop,in_index, out_index,packets, octets,src_port,dst_port,tcp_flags,protocol,tos, source_as, dst_as, src_netmask_length, dst_netmask_length, fetched, account_id)
                        VALUES (%(nas_id)s,%(date_start)s,%(src_addr)s,%(dst_addr)s,%(traffic_class_id)s,%(direction)s,%(next_hop)s,%(in_index)s, %(out_index)s, %(packets)s, %(octets)s,%(src_port)s,%(dst_port)s,%(tcp_flags)s,%(protocol)s,%(tos)s, %(source_as)s, %(dst_as)s, %(src_netmask_length)s, %(dst_netmask_length)s, %(fetched)s, %(account_id)s);""" ,\
                        flows)
            db_connection.commit()'''
            #print "after_insert", time.clock()-a


class FlowCache:
    
    def __init__(self):
	dcache = {}
	nascache = {}
	#print "gc threshold", gc.get_threshold()
	gc.set_threshold(700, 1000, 100)
	self.cMonitor = threading.Timer(sleepTime, monitorCache)
	self.cMonitor.start()
	
    def addflow(self, version, flow):
	method = getattr(self, "addflow" + str(version), None)
	return method(flow)
    
    def addflow5(self, flow):
	#assert isinstance(flow, Flow5)
	
	#key = (flow.src_addr, flow.dst_addr, flow.next_hop, flow.src_port, flow.dst_port, flow.protocol)
	key = ''.join([str(var) for var in (flow.src_addr, flow.dst_addr, flow.next_hop, flow.src_port, flow.dst_port, flow.protocol)])
	val = dcache.get(key)
	if not val:
	    flow.cur = cur.connection.cursor()
	    #flow.stime = datetime.datetime.now()
	    flow.stime = time.time()
	    #flow.fltimer = threading.Timer(60.0 + 1.0 / (flow.src_port + 1), applyFlow, (key,))
	    #flow.fltimer.start()
	    dcache[key] = flow
	else:
	    dflow= dcache[key]
	    dflow.octets  += flow.octets
	    dflow.packets += flow.packets
	    dflow.finish = flow.finish
	    #if (dflow.stime + tdMinute) <=  datetime.datetime.now():
	    if (dflow.stime + 60) <= time.time():
		flow = dcache.pop(key)
		flow.cur.execute("""SELECT * FROM append_netflow(%d, '%s', '%s','%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d);""" % (flow.nas_id,flow.src_addr, flow.dst_addr, flow.next_hop, flow.in_index, flow.out_index, flow.packets, flow.octets, flow.src_port, flow.dst_port, flow.tcp_flags, flow.protocol, flow.tos, flow.source_as, flow.dst_as, flow.src_netmask_length, flow.dst_netmask_length))
		#print "exec"
	    #print 'cached'
	    
def monitorCache():
    while True:
	for k, v in dcache.items():
	    #if (v.stime + tdMinute) <  datetime.datetime.now():
	    if (v.stime + 61) <  time.time():
		try:
		    flow = dcache.pop(k)
		    flow.cur.execute("""SELECT * FROM append_netflow(%d, '%s', '%s','%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d);""" % (flow.nas_id,flow.src_addr, flow.dst_addr, flow.next_hop, flow.in_index, flow.out_index, flow.packets, flow.octets, flow.src_port, flow.dst_port, flow.tcp_flags, flow.protocol, flow.tos, flow.source_as, flow.dst_as, flow.src_netmask_length, flow.dst_netmask_length))
		    #print "monitor pop"
		except Exception, ex:
		    print "monitor exception ", ex
		    
	#print nascache
	#nascache = {}
	#nascache = []
	print "monitor len dcache ", len(dcache)
	#print "time", time.clock()
	time.sleep(sleepTime)
def applyFlow(key):
    flow = dcache.pop(key)
    flow.cur.execute("""SELECT * FROM append_netflow(%d, '%s', '%s','%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d);""" % (flow.nas_id,flow.src_addr, flow.dst_addr, flow.next_hop, flow.in_index, flow.out_index, flow.packets, flow.octets, flow.src_port, flow.dst_port, flow.tcp_flags, flow.protocol, flow.tos, flow.source_as, flow.dst_as, flow.src_netmask_length, flow.dst_netmask_length))
    #flow.cur.connection.commit()
    #print "committed"
				      
#===============================================================================
# pool = PooledDB(
#     mincached=1,
#     maxcached=5,
#     blocking=True,
#     creator=psycopg2,
#     dsn="dbname='%s' user='%s' host='%s' password='%s'" % (settings.DATABASE_NAME,
#                                                            settings.DATABASE_USER,
#                                                            settings.DATABASE_HOST,
#                                                            settings.DATABASE_PASSWORD)
# )
# db_connection = pool.connection()
#===============================================================================

try:
    db_connection = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (settings.DATABASE_NAME,
                                                            settings.DATABASE_USER,
                                                            settings.DATABASE_HOST,
                                                            settings.DATABASE_PASSWORD))
    cur = db_connection.cursor()
except Exeption, ex:
    print "I am unable to connect to the database ", ex
    sys.exit()


def main ():
    addrs = socket.getaddrinfo(settings.NF_HOST, settings.NF_PORT, socket.AF_UNSPEC,
                               socket.SOCK_DGRAM, 0, socket.AI_PASSIVE)
    socks = []
    
    for addr in addrs:
    	sock = socket.socket(addr[0], addr[1])
    	sock.bind(addr[4])
    	socks.append(sock)
    	print "listening on [%s]:%d" % (addr[4][0], addr[4][1])
        
#TestSuite
#===============================================================================
    #f = file('nf_data2.dat', "rb")
    #packets = f.read()
    #plist = packets.split('======')
##    data=f.read()
##    print len(data)
    #addrport=('10.10.1.100', 9996)
    ##import sys
    ##global a
    #plist.pop()
    tFC = FlowCache() 
    #a=time.clock()
    #ff = 0
    i = 0
    #for i in range(200):
	#for data in plist:
	    #data = data[:-1]
	    #print repr(data)
	    #print len(data)
	    #print repr(data[-1])
	#for i in range(1000):
	#while True:
	#f = file('nf_data2.dat', "wb")
    while True:
    # #===============================================================================
	(rlist, wlist, xlist) = select.select(socks, [], socks)
	for sock in rlist:
	    (data, addrport) = sock.recvfrom(8192)
	    #f.write(data)
	    #f.flush()
	    #f.close()
 
	    #print "Received flow packet from %s:%d" % addrport
	    
	    #global a
	    #a=time.clock()
	#global trafficclasses_pool
	#trafficclasses_pool = RefreshClasses()
	    #print "after_refresh", time.clock()-a
	    
	if (i % 50) == 0:
	#if ff == 50:
	    #ff = 0
	    print i
	    print "len dcache ", len(dcache)
	    print "time", time.clock()
	    #print nascache
	    cur.connection.commit()
	try:
	    NetFlowPacket(data, addrport, tFC)
	except Exception, ex:
	    print "NFP exception %d: %s" % (i, ex)
	#ff += 1
	i += 1
		#sys.exit()
	cur.connection.commit()
    print "after_nfpacket", time.clock()-a
# #===============================================================================
#        print "after_nfpacket", time.clock()-a
#        NetFlowPacket(data, addrport)
#        #time.sleep(0.1)
#        
#===============================================================================

    
    #while True:
	    #(rlist, wlist, xlist) = select.select(socks, [], socks)
	    #for sock in rlist:
		    #(data, addrport) = sock.recvfrom(8192)
            ##f.write(data)
            ##f.flush()
            ##f.close()
 
		    ##print "Received flow packet from %s:%d" % addrport
            
            ##global a
            ##a=time.clock()
            ##global trafficclasses_pool
            ##trafficclasses_pool = RefreshClasses()
            ##print "after_refresh", time.clock()-a
            ##sys.exit()
            #NetFlowPacket(data, addrport)
    return



import socket
if socket.gethostname() not in ['dolphinik','sserv.net','sasha', 'kail','billing', 'medusa']:
    import sys
    print "License key error. Exit from application."
    sys.exit(1)
    
if __name__=='__main__':
    main()




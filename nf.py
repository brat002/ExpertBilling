#-*-coding=utf-8-*-

import socket, select, struct, datetime
from IPy import *
import mx.DateTime
import settings
import psycopg2
from DBUtils.PooledDB import PooledDB

trafficclasses_pool = []

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


    def check_class(self, src_ip, src_port, dst_ip, dst_port, protocol, next_hop):
        src = IP("%s/%s" % (self.src_ip, self.src_mask))
        dst = IP("%s/%s" % (self.dst_ip, self.dst_mask))
        n_hop = IP(self.next_hop)
        
        res={'src':False, 'src_port':False, 'dst':False,'dst_port':False, 'protocol':False, 'next_hop':False}

        if IP(src_ip) in src:
            res['src']=True


        if IP(dst_ip) in dst:
            res['dst']=True
            
        if IP(next_hop)==n_hop or self.next_hop:
            res['next_hop']=True


        if src_port==self.src_port or self.src_port==0:
            res['src_port']=True

        if dst_port==self.dst_port or self.dst_port==0:
            res['dst_port']=True

        if protocol==int(self.protocol) or int(self.protocol)==0:
            res['protocol']=True
            
        res['direction']=self.direction
        #print res
        return res


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
            if res['src'] and res['dst'] and res['src_port'] and res['dst_port'] and res['protocol'] and res['next_hop']:
                
                return self.id, res['direction']
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
			raise ValueError, "Short flow"

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
    def __init__(self, data, addrport):
        if len(data) < 16:
            raise ValueError, "Short packet"

        cur.execute("""SELECT id from nas_nas WHERE  ipaddress='%s'""" % addrport[0])
        try:
            nas_id = cur.fetchone()[0]
        except Exception, e:
            #print e
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

                traffic_class=None
                #print flow
                match = False
                for traffic_class in trafficclasses_pool:
                    res=traffic_class.check(flow.src_addr, flow.src_port, flow.dst_addr, flow.dst_port, flow.protocol, flow.next_hop)
                    #print res
                    if res[0] and match==False:
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
                        'fetched':False
                        }
                        )

            #print flows
            #print flows
            cur.executemany("""
                        INSERT INTO billservice_rawnetflowstream(nas_id, date_start, src_addr, dst_addr, traffic_class_id, direction, next_hop,in_index, out_index,packets, octets,src_port,dst_port,tcp_flags,protocol,tos, source_as, dst_as, src_netmask_length, dst_netmask_length, fetched)
                        VALUES (%(nas_id)s,%(date_start)s,%(src_addr)s,%(dst_addr)s,%(traffic_class_id)s,%(direction)s,%(next_hop)s,%(in_index)s, %(out_index)s, %(packets)s, %(octets)s,%(src_port)s,%(dst_port)s,%(tcp_flags)s,%(protocol)s,%(tos)s, %(source_as)s, %(dst_as)s, %(src_netmask_length)s, %(dst_netmask_length)s, %(fetched)s);""" ,\
                        flows)
            db_connection.commit()
            


    
def main ():
    addrs = socket.getaddrinfo(settings.NF_HOST, settings.NF_PORT, socket.AF_UNSPEC,
                               socket.SOCK_DGRAM, 0, socket.AI_PASSIVE)
    socks = []
    
    for addr in addrs:
    	sock = socket.socket(addr[0], addr[1])
    	sock.bind(addr[4])
    	socks.append(sock)
    	print "listening on [%s]:%d" % (addr[4][0], addr[4][1])

    while True:
	    (rlist, wlist, xlist) = select.select(socks, [], socks)
	    for sock in rlist:
		    (data, addrport) = sock.recvfrom(8192)
		    #print "Received flow packet from %s:%d" % addrport
            global trafficclasses_pool
            trafficclasses_pool = RefreshClasses()
            NetFlowPacket(data, addrport)

pool = PooledDB(
     mincached=1,
     maxcached=5,
     blocking=True,
     creator=psycopg2,
     dsn="dbname='%s' user='%s' host='%s' password='%s'" % (settings.DATABASE_NAME,
                                                            settings.DATABASE_USER,
                                                            settings.DATABASE_HOST,
                                                            settings.DATABASE_PASSWORD)
)

db_connection = pool.connection()
cur = db_connection.cursor()
import socket
if socket.gethostname() not in ['dolphinik','sasha', 'kail','billing']:
    import sys
    print "Licension key error. Exit from application."
    sys.exit(1)
    
if __name__=='__main__':
    main()




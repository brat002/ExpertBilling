import socket, select, struct, sys,os,datetime
sys.path.append(os.path.abspath('c:/Python25/Scripts/'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'mikrobill.settings'
from mikrobill.nas.models import Collector, NetFlowStream

from django.conf import settings
import settings

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
try:
    conn = psycopg2.connect("dbname='mikrobill' user='mikrobill' host='localhost' password='1234'")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
except:
    print "I am unable to connect to the database"

cur = conn.cursor()

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
	print LENGTH
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

##	def __str__(self):
##		ret = "src-mask %s proto %d %s:%d > %s:%d %d bytes" % \
##		    (self.out_index,self.protocol, self.src_addr, self.src_port, \
##		     self.dst_addr, self.dst_port, self.octets)
##		return ret


class NetFlowPacket:
    FLOW_TYPES = {
		5 : (Header5, Flow5),
	}
    def __init__(self, data, addrport):
        if len(data) < 16:
            raise ValueError, "Short packet"
        _nf = struct.unpack("!H", data[:2])
        self.version = _nf[0]
        if not self.version in self.FLOW_TYPES.keys():
            raise RuntimeWarning, \
            "NetFlow version %d is not yet implemented" % \
        	    self.version
        hdr_class = self.FLOW_TYPES[self.version][0]
        flow_class = self.FLOW_TYPES[self.version][1]
        self.hdr = hdr_class(data[:hdr_class.LENGTH])

        #collector=Collector.objects.get(ipaddress=addrport[0])
        cur.execute("""SELECT id from nas_collector WHERE ipaddress='%s'""" % addrport[0])
        collector_id = cur.fetchone()[0]
        flows=[]
        for n in range(self.hdr.num_flows):
   			offset = self.hdr.LENGTH + (flow_class.LENGTH * n)
			flow_data = data[offset:offset + flow_class.LENGTH]
			flow=flow_class(flow_data)
			flows.append({'collector_id':collector_id, 'date_start':datetime.datetime.now(),
              'src_addr':flow.src_addr, 'dst_addr':flow.dst_addr,
              'next_hop': flow.next_hop, 'in_index':flow.in_index,
              'out_index' : flow.out_index, 'packets' : flow.packets,
              'octets' : flow.octets, 'start' : flow.start,
              'finish' : flow.finish, 'src_port' : flow.src_port,
              'dst_port' : flow.dst_port, 'tcp_flags' : flow.tcp_flags,
              'protocol' : flow.protocol, 'tos' : flow.tos,
              'source_as' : flow.source_as, 'dst_as' : flow.dst_as,
              'src_netmask_length' : flow.src_netmask_length,'dst_netmask_length' : flow.dst_netmask_length
             }
            )

        cur.executemany("""
        INSERT INTO nas_netflowstream(collector_id,date_start,src_addr,dst_addr,next_hop,in_index, out_index,packets,octets,start,finish,src_port,dst_port,tcp_flags,protocol,tos, source_as, dst_as, src_netmask_length, dst_netmask_length)
        VALUES (%(collector_id)s,%(date_start)s,%(src_addr)s,%(dst_addr)s,%(next_hop)s,%(in_index)s, %(out_index)s,%(packets)s,%(octets)s,%(start)s,%(finish)s,%(src_port)s,%(dst_port)s,%(tcp_flags)s,%(protocol)s,%(tos)s, %(source_as)s, %(dst_as)s, %(src_netmask_length)s, %(dst_netmask_length)s)"""
         , flows)

##			offset = self.hdr.LENGTH + (flow_class.LENGTH * n)
##			flow_data = data[offset:offset + flow_class.LENGTH]
##			flow=flow_class(flow_data)
##			netflowstream.collector = collector
##			netflowstream.date_start = datetime.datetime.now()
##			netflowstream.src_addr = flow.src_addr
##			netflowstream.dst_addr = flow.dst_addr
##			netflowstream.next_hop = flow.next_hop
##			netflowstream.in_index = flow.in_index
##			netflowstream.out_index = flow.out_index
##			netflowstream.packets = flow.packets
##			netflowstream.octets = flow.octets
##			netflowstream.start = flow.start
##			netflowstream.finish = flow.finish
##			netflowstream.src_port = flow.src_port
##			netflowstream.dst_port = flow.dst_port
##			netflowstream.tcp_flags = flow.tcp_flags
##			netflowstream.protocol = flow.protocol
##			netflowstream.tos = flow.tos
##			netflowstream.src_mask = flow.src_mask
##			netflowstream.save()
            

##	def __str__(self):
##		ret = str(self.hdr)
##		i = 0
##		for flow in self.flows:
##			ret += "Flow %d: " % i
##			ret += "%s\n" % str(flow)
##			i += 1
##
##		return ret

host = None
port = 9996

addrs = socket.getaddrinfo(host, port, socket.AF_UNSPEC,
    socket.SOCK_DGRAM, 0, socket.AI_PASSIVE)
socks = []

for addr in addrs:
	sock = socket.socket(addr[0], addr[1])
	sock.bind(addr[4])
	socks.append(sock)

	print "listening on [%s]:%d" % (addr[4][0], addr[4][1])

while 1:
	(rlist, wlist, xlist) = select.select(socks, [], socks)

	for sock in rlist:
		(data, addrport) = sock.recvfrom(8192)
		print "Received flow packet from %s:%d" % addrport
		print NetFlowPacket(data, addrport)


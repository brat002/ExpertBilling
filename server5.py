import socket, select, struct, sys,os,datetime
sys.path.append(os.path.abspath('c:/Python25/Scripts/'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'mikrobill.settings'
from mikrobill.nas.models import Collector, NetFlowStream

from django.conf import settings
import settings

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


	LENGTH = struct.calcsize("!4s4s4sHHIIIIHHBBBBHHBBBB")
	print LENGTH
	def __init__(self, data):
		if len(data) != self.LENGTH:
			raise ValueError, "Short flow"

		_ff = struct.unpack("!4s4s4sHHIIIIHHBBBBHHBBBB", data)
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
		self.src_mask = _ff[18]

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

        collector=Collector.objects.get(ipaddress=addrport[0])

        for n in range(self.hdr.num_flows):
			offset = self.hdr.LENGTH + (flow_class.LENGTH * n)
			flow_data = data[offset:offset + flow_class.LENGTH]
			flow=flow_class(flow_data)
			netflowstream = NetFlowStream()
			netflowstream.collector = collector
			netflowstream.date_start = datetime.datetime.now()
			netflowstream.src_addr = flow.src_addr
			netflowstream.dst_addr = flow.dst_addr
			netflowstream.next_hop = flow.next_hop
			netflowstream.in_index = flow.in_index
			netflowstream.out_index = flow.out_index
			netflowstream.packets = flow.packets
			netflowstream.octets = flow.octets
			netflowstream.start = flow.start
			netflowstream.finish = flow.finish
			netflowstream.src_port = flow.src_port
			netflowstream.dst_port = flow.dst_port
			netflowstream.tcp_flags = flow.tcp_flags
			netflowstream.protocol = flow.protocol
			netflowstream.tos = flow.tos
			netflowstream.src_mask = flow.src_mask
			netflowstream.save()

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


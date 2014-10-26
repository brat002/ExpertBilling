import os,sys,copy,time,random,struct,socket
import psycopg2
from IPy import IP, IPint, parseAddress
import random
from random import random, randint, choice
from struct import pack
from copy import copy, deepcopy
from datetime import datetime
import time
#("!LLLHHIIIIHHBBBBHHBBH")

class PseudoFile(object):
    
    def __init__(self):
        pass
    def write(self, *args):
        pass
    def close(self):
        pass
    def flush(self):
        pass
        
def runTests(tests, sock, addrport, output):
    global globalopts
    testCount = 0
    print addrport
    now  = datetime.now
    for test in tests:
        flowCount = 0
        tdct, tpairs = test
        writeIP    = tdct['write_ip']
        testByPair = tdct['by_pair']
        sleepTime  = tdct['sleep'] 
        totalOctets = tdct['octets']        
        flowPrePack = [777L, 777L, tdct['next_hop'],2,3,0, 777, 0,0, 0, 0,0,0, tdct['protocol'],0,0,0,0,0,0]
        headPrePack = [5, 777, 0, time.time(),0,0,0,0,0]
        output.write('%s Running test #%s opts %s \n' % (now(), testCount, tdct))
        if testByPair:            
            for pair in tpairs:
                sentOctets = 0
                breakCond = False
                flowCount = 0
                flows = ''
                inp_src, inp_dst = pair
                if inp_src.netmask() != 0xffffffffL:
                    src_gtr = lambda: randint(inp_src.int(), inp_src.broadcast())
                else:
                    src_gtr = lambda: inp_src.int()
                if inp_dst.netmask() != 0xffffffffL:
                    dst_gtr = lambda: randint(inp_dst.int(), inp_dst.broadcast())
                else:
                    dst_gtr = lambda: inp_dst.int()
                header = headPrePack
                packetCount = 0
                while True:
                    octets = randint(100, 50000)
                    if octets + sentOctets >= totalOctets:
                        octets = totalOctets - sentOctets
                        breakCond = True
                    else: 
                        sentOctets += octets
                    flow = flowPrePack
                    flow[6] = octets
                    flow[0] = src_gtr()
                    flow[1] = dst_gtr()
                    flow[9] = choice(tdct['src_port'])
                    flow[10] = choice(tdct['dst_port'])
                    if writeIP:
                        output.write('%s %s:%s->%s:%s | %s \n' % (now(), IPint(flow[0]).strNormal(), flow[9], IPint(flow[1]).strNormal(), flow[10], flow[6]))
                    else:
                        output.write('%s %X:%s->%X:%s | %s \n' % (now(), flow[0], flow[9], flow[1], flow[10], flow[6]))
                    flows += pack("!LLLHHIIIIHHBBBBHHBBH", *flow)
                    flowCount += 1
                    if flowCount == 63 or breakCond:
                        header[1] = flowCount
                        flows = pack("!HHIIIIBBH", *header) + flows
                        sock.sendto(flows, addrport)
                        packetCount += 1
                        flowCount = 0
                        flows = ''
                        output.write('%s Packet #%s sent\n' % (now(), packetCount))
                        time.sleep(sleepTime)
                    if breakCond: break
                    
            output.flush()
                    
            
        else:
            flowCount = 0
            packetCount = 0
            header = headPrePack
            sentOctets = 0
            breakCond = False                
            flows = ''
            while True:                
                pair = choice(tpairs)
                inp_src, inp_dst = pair
                if inp_src.netmask() != 0xffffffffL:
                    src_gtr = lambda: randint(inp_src.int(), inp_src.broadcast())
                else:
                    src_gtr = lambda: inp_src.int()
                if inp_dst.netmask() != 0xffffffffL:
                    dst_gtr = lambda: randint(inp_dst.int(), inp_dst.broadcast())
                else:
                    dst_gtr = lambda: inp_dst.int()
                    
                octets = randint(64, 4096)
                if octets + sentOctets >= totalOctets:
                    octets = totalOctets - sentOctets
                    breakCond = True
                else: 
                    sentOctets += octets
                flow = flowPrePack
                flow[6] = octets
                flow[0] = src_gtr()
                flow[1] = dst_gtr()
                flow[9] = choice(tdct['src_port'])
                flow[10] = choice(tdct['dst_port'])
                if writeIP:
                    output.write('%s %s:%s->%s:%s | %s \n' % (now(), IPint(flow[0]).strNormal(), flow[9], IPint(flow[1]).strNormal(), flow[10], flow[6]))
                else:
                    output.write('%s %X:%s->%X:%s | %s \n' % (now(), flow[0], flow[9], flow[1], flow[10], flow[6]))
                flows += pack("!LLLHHIIIIHHBBBBHHBBH", *flow)
                flowCount += 1
                if flowCount == 63 or breakCond:
                    header[1] = flowCount
                    flows = pack("!HHIIIIBBH", *header) + flows
                    sock.sendto(flows, addrport)
                    packetCount += 1
                    flowCount = 0
                    flows = ''
                    output.write('%s Packet #%s sent, total sent octets: %s\n' % (now(), packetCount, sentOctets))
                    output.flush()
                    time.sleep(sleepTime)
                if breakCond: break
                
        testCount += 1
        output.flush()
            

def parseFile(filename):
    global globalopts
    #nas = 10.10.1.1
    tf = open(filename, 'rb')
    tlist = []
    tdct = {'octets':0,'sleep':0,'by_pair':1, 'write_ip':0, 'next_hop':0L, 'nas':168427777L, 'src_port':[80], 'dst_port':[80], 'protocol':0, 'num':0}
    for tline in tf:
        if tline.startswith('test|'):
            ndct = deepcopy(tdct)
            psline = tline[5:].strip().split(' ')
            for token in psline:
                try:
                    tkey, tval = token.split(':')
                    if tkey == 'octets':
                        if tval[-1] == 'G': tval = int(tval[:-1])*1073741824
                        elif tval[-1] == 'M': tval = int(tval[:-1])*1048576
                        elif tval[-1] == 'k': tval = int(tval[:-1])*1024
                        else: tval = int(tval)
                    elif tkey == 'next_hop' or tkey == 'nas':
                        tval = parseAddress(tval)[0]
                    elif tkey == 'src_port' or tkey == 'dst_port':
                        tval = [int(sint) for sint in tval[1:-1].split(',')]
                    elif tkey == 'sleep':
                        tval = float(tval)
                    elif tkey == 'time':
                        globalopts[tkey] = tval
                        continue
                    else:
                        tval = int(tval)
                    ndct[tkey] = tval
                except Exception, ex:
                    print 'test line tokens parsing exception %s || %s\n' % (token,repr(ex))
            
            tlist.append([ndct, []])
        else:
            try:
                src_ip, dst_ip = tline.strip().split('->')
                tlist[-1][1].append((IPint(src_ip), IPint(dst_ip)))
            except Exception, ex:
                    print 'ip line parsing exception %s || %s \n' (tline, repr(ex))
    tf.close()               
    return tlist
            
            
    
            
if __name__=='__main__':
    #binary strings lengthes
    globalopts = {'time':'stopped'}
    
    tests_ = parseFile(sys.argv[1])
    sock_ = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock_.settimeout(10)
    host, port = sys.argv[2].split(':')
    addrport_ = (host, int(port))
    if len(sys.argv) > 3:
        output_ = open(sys.argv[3], 'wb')
    else:
        output_ = PseudoFile()
    runTests(tests_, sock_, addrport_, output_)
    sock_.close()
    output_.close()
    
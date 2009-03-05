'''nf_gen log files miner stub'''
import os,sys,copy,time,random,struct,socket
from datetime import datetime


if __name__=='__main__':
    tf = open(sys.argv[1], 'r')
    in_str = sys.argv[2]
    oct_counter = 0
    for fline in tf:
        if fline.find(in_str) != -1:
            oct_counter += int(fline.split('|')[1])
            
    print 'Search for: ', in_str
    print 'Total octets: ', oct_counter
    print 'Total octets: %s M' % (oct_counter / 1048576.0)
#coding=UTF-8
import time, sys


def get_abon():
    print "Снятие"


n=(24*60*60)/float(sys.argv[1])

while True:
    print time.strftime('%X')
    time.sleep(n)

#-*- coding: utf-8 -*-
import commands
import sys, os
import os.path
import time

snmpget='/usr/bin/snmpget'
snmpwalk='/usr/bin/snmpwalk'
host='10.244.0.6'
community='public'
db_path='/tmp/bandwidth_%s.rrd'
db_template="/usr/bin/rrdtool create %s --start N DS:in:COUNTER:120:U:U DS:out:COUNTER:120:U:U RRA:AVERAGE:0.5:1:432" % db_path
status, output = commands.getstatusoutput("snmpwalk -v 1 -Oqs -c public %s iso.3.6.1.2.1.31.1.1.1.1" % host)
unixstamp = int(time.time())+1
start_unixstamp = unixstamp-86400-1
if status==0:
    for line in output.split("\n"):
        try:
            oid, value=line.split(" ")
        except Exception, e:
            print line, e
            continue
        id=oid.split(".")[-1]
        value = value.replace("\"", '')
        try:
            user=value.split('-',1)[1].strip('>')
        except IndexError:
            continue
        user_db_path = db_path % user
	if not os.path.isfile(user_db_path):
	    st, out=commands.getstatusoutput(db_template % user)
	    print "st=",st, out
	    #sys.exit()

        #print id, value
        status, output_in = commands.getstatusoutput("snmpget -v 1 -Oqv -c public %s .1.3.6.1.2.1.2.2.1.10.%s" % (host,id))
        status, output_out = commands.getstatusoutput("snmpget -v 1 -Oqv -c public %s .1.3.6.1.2.1.2.2.1.16.%s" % (host,id))
        print id, value,output_in, output_out, user_db_path
        status, output=commands.getstatusoutput("rrdtool updatev %s N:%s:%s" % (user_db_path, output_in, output_out,))
        print "status=%s output=%s" % (status, output)
        #continue
        status, output = commands.getstatusoutput("""rrdtool graph /tmp/bandwidth_%s.png -a PNG -h 125 -v "Данные о загрузке eth0" --start %s --end %s 'DEF:in=%s:in:AVERAGE' 'DEF:out=%s:out:AVERAGE' 'CDEF:kbin=in,1024,/' 'CDEF:kbout=out,1024,/' 'AREA:in#00FF00:Загрузка In' 'LINE1:out#0000FF:Загрузка Out\j' 'GPRINT:kbin:LAST:Последнее значение In\: %%3.2lf кБ-сек' 'GPRINT:kbout:LAST:Последнее значение Out\: %%3.2lfкБсек\j'""" % (user, start_unixstamp, unixstamp, user_db_path, user_db_path,))
        print status, output
        print "===="*10

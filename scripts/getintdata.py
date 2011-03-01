#-*- coding: utf-8 -*-
import commands
import sys, os
import os.path
import time
import psycopg2
import psycopg2.extras
import re
p=re.compile('^\<(pptp|ovpn|pppoe|l2tp|sstp)\-(.*)\>$')
#########################
host = '127.0.0.1'
port = '5433'
database = 'ebs_new'
user = 'ebs'
password = 'ebspassword'

try:
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (database, user, host, password, port));
except:
    print "I am unable to connect to the database"
    sys.exit()

conn.set_isolation_level(0)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

cur.execute('SELECT username, ARRAY(SELECT username FROM billservice_subaccount WHERE account_id=acc.id and vpn_ip_address!=\'0.0.0.0/0\') FROM billservice_account as acc')
accounts = cur.fetchall()
cur.execute("""SELECT ipaddress FROM nas_nas as nas  WHERE nas.id in(select nas_id FROM billservice_subaccount as subacc WHERE subacc.username is not Null and nas_id is not Null) GROUP BY nas.ipaddress""")
subaccs = cur.fetchall()

nasses=[]
for s in subaccs:
    nasses.append(s['ipaddress'])
"nas_id:counter"
nas_sessions={}
"id:[in, out]"
nas_bytes = {}
#########################
snmpget='/usr/bin/snmpget'
snmpwalk='/usr/bin/snmpwalk'
community='public'
db_path='/tmp/bandwidth_%s.rrd'
db_template="/usr/bin/rrdtool create %s -s 300 DS:in:DERIVE:600:0:U DS:out:DERIVE:600:0:U RRA:AVERAGE:0.5:1:576 RRA:AVERAGE:0.5:6:672 RRA:AVERAGE:0.5:24:732 RRA:AVERAGE:0.5:144:1460" % db_path

for nas in nasses:
    nas_db_path=db_template % "nas_%s" % nas
    if not os.path.isfile(nas_db_path):
            st, out=commands.getstatusoutput(nas_db_path)
    session_counter=0
    bytes_in, bytes_out = 0,0
    #print "snmpwalk -v 1 -Oqs -c public %s iso.3.6.1.2.1.31.1.1.1.1" % nas
    status, output = commands.getstatusoutput("%s -v 1 -Oqsn -c public %s iso.3.6.1.2.1.31.1.1.1.1" % (snmpwalk,nas))
    print status, output
    unixstamp = int(time.time())+1
    start_unixstamp = unixstamp-86400-1
    if status==0:
        for line in output.split("\n"):
            print line
            if line.rfind("iso.")==-1:continue
            try:
                oid, value=line.split(" ")
            except Exception, e:
                print line, e
                continue
            id=oid.split(".")[-1]
            value = value.replace("\"", '')
            m=p.match(value)
            try:
                user=m.group(2)
            except:
                continue
            user_db_path = db_path % user
            if not os.path.isfile(user_db_path):
                st, out=commands.getstatusoutput(db_template % user)
                print "st=",st, out
                status, output_in = commands.getstatusoutput("snmpget -v 1 -Oqv -c public %s .1.3.6.1.2.1.2.2.1.10.%s" % (host,id))
                status, output_out = commands.getstatusoutput("snmpget -v 1 -Oqv -c public %s .1.3.6.1.2.1.2.2.1.16.%s" % (host,id))
                print id, value,output_in, output_out, user_db_path
                status, output=commands.getstatusoutput("rrdtool updatev %s N:%s:%s" % (user_db_path, output_in, output_out,))
                print "status=%s output=%s" % (status, output)
                session_counter+=1
                bytes_in+=int(output_in)
                bytes_out+=(output_out)
                #continue
                #status, output = commands.getstatusoutput("""rrdtool graph /tmp/bandwidth_%s.png -a PNG -h 125 -v "Данные о загрузке eth0" --start %s --end %s 'DEF:in=%s:in:AVERAGE' 'DEF:out=%s:out:AVERAGE' 'CDEF:kbin=in,1024,/' 'CDEF:kbout=out,1024,/' 'AREA:in#00FF00:Загрузка In' 'LINE1:out#0000FF:Загрузка Out\j' 'GPRINT:kbin:LAST:Последнее значение In\: %%3.2lf кБ-сек' 'GPRINT:kbout:LAST:Последнее значение Out\: %%3.2lfкБсек\j'""" % (user, start_unixstamp, unixstamp, user_db_path, user_db_path,))
                print status, output
                print "===="*10
        status, output=commands.getstatusoutput("rrdtool updatev %s N:%s:%s" % (nas_db_path, bytes_in, bytes_out,))


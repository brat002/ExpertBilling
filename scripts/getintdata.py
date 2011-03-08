#-*- coding: utf-8 -*-
import commands
import sys, os
import os.path
import time
import psycopg2
import psycopg2.extras
import re
from hashlib import md5
p=re.compile('^\<(pptp|ovpn|pppoe|l2tp|sstp)\-(.*)\>$')
#########################
host = '127.0.0.1'
port = '5432'
database = 'ebs'
user = 'ebs'
password = 'ebspassword'

try:
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (database, user, host, password, port));
except:
    print "I am unable to connect to the database"
    sys.exit()

conn.set_isolation_level(0)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

cur.execute(r"SELECT username, nas_id FROM billservice_subaccount WHERE vpn_ip_address!='0.0.0.0'")
subacc = cur.fetchall()
subaccount_by_nas={}
subaccounts=[]
for item in subacc:
    if not subaccount_by_nas.get(item['nas_id']):
        subaccount_by_nas[item['nas_id']]=[]
    subaccount_by_nas[item['nas_id']].append(item['username'])
    subaccounts.append(item['username'])
    
cur.execute("""SELECT id, ipaddress FROM nas_nas as nas  WHERE nas.id in(select nas_id FROM billservice_subaccount as subacc WHERE subacc.username is not Null and nas_id is not Null)""")
subaccs = cur.fetchall()

nasses=[]
for s in subaccs:
    nasses.append((s['id'], s['ipaddress']))
"nas_id:counter"
nas_sessions={}
"id:[in, out]"
nas_bytes = {}
#########################
snmpget='/usr/bin/snmpget'
snmpwalk='/usr/bin/snmpwalk'
#host='10.244.0.6'
community='public'
db_path='/opt/ebs/stats/bandwidth_%s.rrd'
db_template="/usr/bin/rrdtool create %s -s 300 DS:in:DERIVE:600:0:U DS:out:DERIVE:600:0:U RRA:AVERAGE:0.5:1:576 RRA:AVERAGE:0.5:6:672 RRA:AVERAGE:0.5:24:732 RRA:AVERAGE:0.5:144:1460" % db_path
nas_session_count_template="/usr/bin/rrdtool create %s -s 300 DS:sessions:DERIVE:600:0:U RRA:AVERAGE:0.5:1:576 RRA:AVERAGE:0.5:6:672 RRA:AVERAGE:0.5:24:732 RRA:AVERAGE:0.5:144:1460 RRA:MAX:0.5:1:576 RRA:MAX:0.5:6:672 RRA:MAX:0.5:24:732 RRA:MAX:0.5:144:1460" % db_path

for nas_id, nas in nasses:
    host=nas
    nas_md5 = 'nas_'+md5(nas).hexdigest()
    nas_create_rrd=db_template % nas_md5
    nas_db_path=db_path % nas_md5
    if not os.path.isfile(nas_db_path):
        st, out=commands.getstatusoutput(nas_db_path)
        
    nas_sessions_md5 = 'nas_sessions_'+md5(nas).hexdigest()
    nas_sessions_db_path= db_path % nas_sessions_md5
    nas_sessions_create_rrd = nas_session_count_template % nas_sessions_md5
    if not os.path.isfile(nas_sessions_md5):
        st, out=commands.getstatusoutput(nas_sessions_create_rrd)
    session_counter=0
    bytes_in, bytes_out = 0,0
    #print "snmpwalk -v 1 -Oqs -c public %s iso.3.6.1.2.1.31.1.1.1.1" % nas
    status, output = commands.getstatusoutput("%s -v 2c -Oqsn -c public %s iso.3.6.1.2.1.31.1.1.1.1" % (snmpwalk,nas))
    print "status=",status, output
    unixstamp = int(time.time())+1
    start_unixstamp = unixstamp-86400-1
    if status!=0:continue
    
    for line in output.split("\n"):
        print 'line=',line
        if line.rfind(".")==-1:continue
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
        
        if user not in subaccount_by_nas.get(nas_id, []):
            if user not in subaccounts:continue
            
        user=md5(user).hexdigest()
        user_db_path = db_path % user
        if not os.path.isfile(user_db_path):
            st, out=commands.getstatusoutput(db_template % user)
            print "st=",st, out
        status, output_out = commands.getstatusoutput("snmpget -v 1 -Oqv -c public %s .1.3.6.1.2.1.2.2.1.10.%s" % (host,id))
        status, output_in = commands.getstatusoutput("snmpget -v 1 -Oqv -c public %s .1.3.6.1.2.1.2.2.1.16.%s" % (host,id))
        print id, value,output_in, output_out, user_db_path
        status, output=commands.getstatusoutput("rrdtool updatev %s N:%s:%s" % (user_db_path, output_in, output_out,))
        print "status=%s output=%s" % (status, output)
        session_counter+=1
        bytes_in+=int(output_in)
        bytes_out+=int(output_out)
        print status, output
        print "===="*10
    status, output=commands.getstatusoutput("rrdtool updatev %s N:%s:%s" % (db_path % nas_md5, bytes_in, bytes_out,))
    status, output=commands.getstatusoutput("rrdtool updatev %s N:%s:%s" % (db_path % nas_md5, bytes_in, bytes_out,))
    status, output=commands.getstatusoutput("rrdtool updatev %s N:%s" % (nas_sessions_db_path, session_counter,))
    
    print "nas_status, nas_output", status, output
        
#!/usr/bin/python

#coding=utf-8
import commands
import sys, os
import os.path
import time
import psycopg2
import psycopg2.extras
import re
from hashlib import md5
import ConfigParser
config = ConfigParser.ConfigParser()
config.read("/opt/ebs/data/ebs_config.ini")
p=re.compile('^\<(pptp|ovpn|pppoe|l2tp|sstp)\-(.*)\>$')
#########################
host = config.get("db", "host")
port = config.getint('db', 'port')
database = config.get('db', 'name')
user = config.get('db', 'username')
password = config.get('db', 'password')

community='public'

snmpget='/usr/bin/snmpget'
snmpwalk='/usr/bin/snmpwalk'
#host='10.244.0.6'

db_path='/opt/ebs/stats/bandwidth_%s.rrd'
db_template="/usr/bin/rrdtool create %s -s 300 DS:in:DERIVE:600:0:U DS:out:DERIVE:600:0:U RRA:AVERAGE:0.5:1:576 RRA:AVERAGE:0.5:6:672 RRA:AVERAGE:0.5:24:732 RRA:AVERAGE:0.5:144:1460 DS:packets_in:DERIVE:600:0:U DS:packets_out:DERIVE:600:0:U" % db_path
nas_session_count_template="/usr/bin/rrdtool create %s -s 300 DS:sessions:GAUGE:600:0:U RRA:AVERAGE:0.5:1:576 RRA:AVERAGE:0.5:6:672 RRA:AVERAGE:0.5:24:732 RRA:AVERAGE:0.5:144:1460 RRA:MAX:0.5:1:576 RRA:MAX:0.5:6:672 RRA:MAX:0.5:24:732 RRA:MAX:0.5:144:1460" % db_path

try:
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (database, user, host, password, port));
except:
    print "I am unable to connect to the database"
    sys.exit()

conn.set_isolation_level(0)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#=============================================
cur.execute(r"SELECT id, username, nas_id FROM billservice_subaccount WHERE vpn_ip_address!='0.0.0.0'")
subacc = cur.fetchall()
subaccount_by_nas={}
subaccounts=[]
subaccounts_id_by_name={}
for item in subacc:
    if not subaccount_by_nas.get(item['nas_id']):
        subaccount_by_nas[item['nas_id']]=[]
    subaccount_by_nas[item['nas_id']].append(item['username'])
    subaccounts.append(item['username'])
    if item['nas_id']:
        subaccounts_id_by_name[(item['username'],item['nas_id'])]=item['id']
    else:
        subaccounts_id_by_name[item['username']]=item['id']
    
#print subaccount_by_nas
cur.execute("""SELECT id, ipaddress FROM nas_nas as nas  WHERE nas.id in(select nas_id FROM billservice_subaccount as subacc WHERE subacc.username is not Null and nas_id is not Null)""")
subaccs = cur.fetchall()

nasses=[]
for s in subaccs:
    nasses.append((s['id'], s['ipaddress']))
#=============================================    
"nas_id:counter"
nas_sessions={}
"id:[in, out]"
nas_bytes = {}

#########################

for nas_id, nas_ipaddress in nasses:
    host=nas_ipaddress
    nas_file = 'nas_%s' % nas_id
    nas_create_rrd=db_template % nas_file
    nas_db_path=db_path % nas_file
    if not os.path.isfile(nas_db_path):
        st, out=commands.getstatusoutput(nas_create_rrd)
        
    nas_sessions_file = 'nas_sessions_%s' % nas_id
    nas_sessions_db_path= db_path % nas_sessions_file
    nas_sessions_create_rrd = nas_session_count_template % nas_sessions_file
    if not os.path.isfile(nas_sessions_db_path):
        st, out=commands.getstatusoutput(nas_sessions_create_rrd)
        
    session_counter=0
    bytes_in, bytes_out, packets_in, packets_out = 0,0,0,0
    
    #Получение списка интерфейсов с сервера доступа
    status, output = commands.getstatusoutput("%s -v 2c -Oqsn -c public %s iso.3.6.1.2.1.31.1.1.1.1" % (snmpwalk,nas_ipaddress))
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
            user=unicode(m.group(2))
        except:
            continue
        
        #Ищем ID пользователя
        if user not in subaccount_by_nas.get(nas_id, []):
            if user not in subaccounts:continue
            else:
                subaccount_id=subaccounts_id_by_name.get(user)   
        else:
            subaccount_id=subaccounts_id_by_name.get((user,nas_id))
            
        user_db_path = db_path % subaccount_id

        if not os.path.isfile(user_db_path):
            st, out=commands.getstatusoutput(db_template % subaccount_id)

        status, output_out = commands.getstatusoutput("%s -v 1 -Oqv -c public %s .1.3.6.1.2.1.2.2.1.10.%s" % (snmpget,host,id))
        status, output_in = commands.getstatusoutput("%s -v 1 -Oqv -c public %s .1.3.6.1.2.1.2.2.1.16.%s" % (snmpget,host,id))
        status, session_packets_out = commands.getstatusoutput("%s -v 1 -Oqv -c public %s .1.3.6.1.2.1.2.2.1.11.%s" % (snmpget,host,id))
        status, session_packets_in = commands.getstatusoutput("%s -v 1 -Oqv -c public %s .1.3.6.1.2.1.2.2.1.17.%s" % (snmpget,host,id))

        #Обновляем информаци о байтах и пакетах
        status, output=commands.getstatusoutput("rrdtool updatev %s N:%s:%s:%s:%s" % (user_db_path, output_in, output_out,session_packets_in, session_packets_out))

        session_counter+=1
        try:
            bytes_in+=int(output_in)
            bytes_out+=int(output_out)
            packets_in+=int(session_packets_in)
            packets_out+=int(session_packets_out)
        except Exception, e:
            print e
            continue

    status, output=commands.getstatusoutput("rrdtool updatev %s N:%s:%s:%s:%s" % (nas_db_path, bytes_in, bytes_out,packets_in, packets_out))
    status, output=commands.getstatusoutput("rrdtool updatev %s N:%s" % (nas_sessions_db_path, session_counter,))
    

        
#-*- coding: utf-8 -*-

import sys, os
import os.path
import psycopg2
import psycopg2.extras
import time
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
conn.set_client_encoding('UTF8')
cur = conn.cursor()

all=[]
cur.execute("SELECT id,username FROM billservice_account order by id")
accounts=cur.fetchall()

for account in accounts:
    
    cur.execute('SELECT datetime FROM billservice_periodicalservicelog WHERE accounttarif_id=(SELECT id FROM billservice_accounttarif WHERE account_id=%s and datetime<now() ORDER BY ID DESC LIMIT 1)', (account[0],))
    pl_datetime = cur.fetchone()
    if pl_datetime:
        pl_datetime = pl_datetime[0]
        
    cur.execute('SELECT created FROM billservice_periodicalservicehistory WHERE accounttarif_id=(SELECT id FROM billservice_accounttarif WHERE account_id=%s and datetime<now() ORDER BY ID DESC LIMIT 1) ORDER BY created DESC LIMIT 1', (account[0],))
    psh_datetime = cur.fetchone()
    if psh_datetime:
        psh_datetime = psh_datetime[0]
        
        
    cur.execute("""
    select DISTINCT account_id from billservice_balancehistory WHERE account_id=%s GROUP by account_id, datetime HAVING count(*)>1
    """, (account[0], ))
    
    bh = cur.fetchall()
    if not bh: 
        continue
    if psh_datetime is None or pl_datetime is None: continue
    if pl_datetime==psh_datetime: continue
    print "*"*20
    print account
    print bh
    cur.execute('UPDATE billservice_periodicalservicelog SET datetime=%s WHERE accounttarif_id=(SELECT id FROM billservice_accounttarif WHERE account_id=%s AND datetime<=%s ORDER BY ID desc LIMIT 1)',  (psh_datetime, account[0], psh_datetime))
    
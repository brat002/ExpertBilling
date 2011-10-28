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
cur.execute("SELECT id,username,created FROM billservice_account where get_tarif(id)=10 and created<now()-interval '3 days' and status=1")
accounts=cur.fetchall()

for account in accounts:
    cur.execute("UPDATE billservice_account SET status=2 WHERE id=%s", (account[0],))
    print "set account %s creation time %s status=2" % (account[1],account[2])
    all.append(account)
    
cur.execute("SELECT id,username,created FROM billservice_account where get_tarif(id)=6 and created<now()-interval '7 days' and status=1")
accounts=cur.fetchall()

for account in accounts:
    cur.execute("UPDATE billservice_account SET status=2 WHERE id=%s", (account[0],))
    print "set account %s creation time %s status=2" % (account[1],account[2])
    all.append(account)
    
    
cur.execute("SELECT id,username,created FROM billservice_account where get_tarif(id)=5 and created<now()-interval '30 days' and status=1")
accounts=cur.fetchall()

for account in accounts:
    cur.execute("UPDATE billservice_account SET status=2 WHERE id=%s", (account[0],))
    print "set account %s creation time %s status=2" % (account[1],account[2])
    all.append(account)
    
print "sleeping 360 seconds\nzzzzzz..."
time.sleep(360)    
print "wake up and delete accounts"

for a in all:
    
    cur.execute("DELETE FROM billservice_account WHERE id=%s", (a[0],))
    print "deleting account %s was completed" % a[1]

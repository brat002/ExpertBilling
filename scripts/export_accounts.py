#-*- coding: utf-8 -*-
import commands
import sys, os
import os.path
import time
import psycopg2
import psycopg2.extras
import re

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

conn.set_isolation_level(1)
conn.set_client_encoding('UTF8')
cur = conn.cursor()

cur.execute("""
SELECT contract, username, password, (SELECT name FROM billservice_tariff WHERE id=get_tarif(account.id)) as tarif_name, ballance,
       fullname, street, house, house_bulk, room, 
       phone_h, phone_m
  FROM billservice_account as account;
""")
accounts = cur.fetchall()

f=open('export.csv', 'w')
for account in accounts:
    f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (account[0],account[1],account[2],account[3],"%.2f" % account[4],account[5],account[6],account[7],account[8],account[9],account[10],account[11]))
    
f.close()
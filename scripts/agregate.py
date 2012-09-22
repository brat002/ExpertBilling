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
database = 'ebs_alt_new'
user = 'ebs'
password = 'ebspassword'

try:
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (database, user, host, password, port));
except:
    print "I am unable to connect to the database"
    sys.exit()

conn.set_isolation_level(1)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

start_date=''
end_date=''
what=''
    
if len(sys.argv)==4:
    start_date=sys.argv[2]
    end_date=sys.argv[3]
    what=sys.argv[1]
    print start_date, end_date
if what=='periodicalservicehistory':
    print "Aggregating of billservice_periodicalservicehistory and subtables"
    cur.execute("""
    SELECT count(*) as cnt
      FROM billservice_periodicalservicehistory 
      WHERE created between %s and %s
      ;
    """,(start_date,end_date,))
    
    print "current rows=", cur.fetchone()['cnt']
    cur.execute("""
    SELECT service_id, accounttarif_id, sum(summ) as summ, 
           account_id, type_id, max(created) as created
      FROM billservice_periodicalservicehistory 
      WHERE created between %s and %s
      GROUP BY service_id, accounttarif_id, account_id, type_id;
    """,(start_date,end_date,))
    items = cur.fetchall()
    print "deleting selected rows"
    cur.execute("delete from billservice_periodicalservicehistory WHERE created between %s and %s", (start_date,end_date,))
    i=0
    print "inserting aggregated rows"
    for item in items:
        cur.execute(""" 
        INSERT INTO billservice_periodicalservicehistory(service_id, created, accounttarif_id, summ, account_id, type_id)
        VALUES (%s, %s, %s, %s, %s, %s);    
        """, (item['service_id'],item['created'],item['accounttarif_id'],item['summ'],item['account_id'],
              item['type_id'],))
        i+=1
    
    print "total rows inserted=", i
    
    conn.commit()
    sys.exit()
if what=='traffictransaction':
    print "Aggregating of billservice_traffictransaction and subtables"
    cur.execute("""
    SELECT count(*) as cnt
      FROM billservice_traffictransaction 
      WHERE datetime between %s and %s
      ;
    """,(start_date,end_date,))
    
    print "current rows=", cur.fetchone()['cnt']
    cur.execute("""
    SELECT traffictransmitservice_id, account_id, accounttarif_id, sum(summ) as summ, 
           max(created) as created, radiustraffictransmitservice_id
      FROM billservice_traffictransaction
      WHERE created between  %s and  %s
      GROUP BY traffictransmitservice_id, account_id, accounttarif_id, radiustraffictransmitservice_id;
    """,(start_date,end_date,))
    items = cur.fetchall()
    print "deleting selected rows"
    cur.execute("delete from billservice_traffictransaction WHERE created between %s and %s", (start_date,end_date,))
    i=0
    print "inserting aggregated rows"
    for item in items:
        cur.execute(""" 
        INSERT INTO billservice_traffictransaction(traffictransmitservice_id, account_id, accounttarif_id, summ, 
           datetime, radiustraffictransmitservice_id)
        VALUES (%s, %s, %s, %s, %s, %s);    
        """, (item['traffictransmitservice_id'],item['account_id'],item['accounttarif_id'],item['summ'],item['created'],
              item['radiustraffictransmitservice_id'],))
        i+=1
    
    print "total rows inserted=", i
    
    conn.commit()
    sys.exit()
if what=='radiusactivesession':
    print "Deleting old sessions from radius_activesession table"
    cur.execute("""
    DELETE FROM radius_activesession WHERE date_start between %s and %s;
    """,(start_date,end_date,))
    print "Rows was deleted"
    conn.commit()
    sys.exit()
 
print "Script for managing ExpertBilling database tables"
print ""   
print "usage: python agregate.py <periodicalservicehistory|traffictransaction|radiusactivesession> date_start date_end"
print "example: python agregate.py periodicalservicehistory 01.01.2011 01.02.2011"
print "example: python agregate.py traffictransaction 01.01.2011 01.05.2011"



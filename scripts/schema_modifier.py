#-*-coding= utf-8 -*-

import os, sys
import ConfigParser
import datetime, time
import fnmatch
import shutil
import time
import psycopg2

config = ConfigParser.ConfigParser()
billing_config = ConfigParser.ConfigParser()
billing_config.read("/opt/ebs/data/ebs_config.ini")
#billing_config.read("d:/projects/mikrobill/ebs_config.ini")
#########################
host = billing_config.get("db", "host")
port = billing_config.getint('db', 'port')
database = billing_config.get('db', 'name')
user = billing_config.get('db', 'username')
password = billing_config.get('db', 'password')
try:
    connection = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (database, user, host, password, port));
except Exception, e:
    print "I am unable to connect to the database"
    print e
    sys.exit()

connection.set_isolation_level(1)
cur = connection.cursor()

cur.execute("select tablename FROM pg_tables WHERE schemaname='public' and tablename LIKE 'billservice_balancehistory%';")

for table in cur.fetchall():
    dt = table[0].replace('billservice_balancehistory', '')
    if not dt: continue
    cur.execute("""ALTER TABLE billservice_balancehistory%s DROP INDEX billservice_balancehistory%s_account_id; 
                   CREATE INDEX billservice_balancehistory%s_account_id_datetime
  ON billservice_balancehistory%s
  USING btree
  (account_id, datetime);""" % (dt, dt, dt))
    
connection.commit()



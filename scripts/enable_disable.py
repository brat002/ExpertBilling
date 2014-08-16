#!/usr/bin/env python

import psycopg2
import sys
import ConfigParser
import psycopg2, psycopg2.extras
from DBUtils.PooledDB import PooledDB
from DBUtils.PersistentDB import PersistentDB


config = ConfigParser.ConfigParser()
config.read("../ebs_config.ini")
    
persist = PersistentDB(
    setsession=["SET synchronous_commit TO OFF;", 'SET DATESTYLE TO ISO;'],
    creator=psycopg2,
    dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"), config.get("db", "username"), 
                                                               config.get("db", "host"), config.get("db", "password")))

connection = persist.connection()
cur = connection.cursor()
print sys.argv
if sys.argv[1]=='enable':
    cur.execute("UPDATE billservice_account SET status = 1 WHERE id=%s" % sys.argv[2])
elif sys.argv[1]=='disable':
    cur.execute("UPDATE billservice_account SET status = 3 WHERE id=%s" % sys.argv[2])


cur.connection.commit()

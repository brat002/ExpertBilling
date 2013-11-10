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

def get_cursor():
    try:
        connection = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (database, user, host, password, port));
    except Exception, e:
        print "I am unable to connect to the database"
        print e
        sys.exit()
    
    connection.set_isolation_level(1)
    cur = connection.cursor()
    return cur

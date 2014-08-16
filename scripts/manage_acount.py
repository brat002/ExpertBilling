#!/usr/bin/env python

import psycopg2
import sys
import ConfigParser

"""
./manage_account.py disable_notifications now() account_id 
"""

config = ConfigParser.ConfigParser()
config.read("/opt/ebs/data/ebs_config.ini")
    
try:
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='5432'" % (
                                                                                         config.get("db", "name"),
                                                                                         config.get("db", "username"),
                                                                                         config.get("db", "host"),
                                                                                         config.get("db", "password")
                                                                                         ))
except:
    print "I am unable to connect to the database"
    sys.exit()

cur = conn.cursor()

cur.execute("UPDATE billservice_account SET %s = %s WHERE id=%s" % (sys.argv[1], sys.argv[2], sys.argv[3]))

conn.commit()

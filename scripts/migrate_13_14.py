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
port = '5433'
database = 'ebs_new'
user = 'ebs'
password = 'ebspassword'

try:
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (database, user, host, password, port));
except:
    print "I am unable to connect to the database"
    sys.exit()

conn.set_isolation_level(1)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

cur.execute("""
SELECT id, account_id, username, "password", vpn_ip_address, ipn_ip_address, 
       ipn_mac_address, nas_id, ipn_added, ipn_enabled, need_resync, 
       speed, switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, 
       allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
       allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip, 
       associate_pppoe_ipn_mac, ipn_speed, vpn_speed, allow_addonservice, 
       ipn_sleep, vpn_ipinuse_id, ipn_ipinuse_id, allow_ipn_with_null, 
       allow_ipn_with_minus, allow_ipn_with_block
  FROM billservice_subaccount;
""")
accounts = cur.fetchall()

for account in accounts:
    cur.execute(""" 
    INSERT INTO billservice_subaccount(
            account_id, username, "password", vpn_ip_address, ipn_ip_address, 
            ipn_mac_address, nas_id, ipn_added, ipn_enabled, need_resync, 
            speed, switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, 
            allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
            allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip, 
            associate_pppoe_ipn_mac, ipn_speed, vpn_speed, allow_addonservice, 
            ipn_sleep, vpn_ipinuse_id, ipn_ipinuse_id, allow_ipn_with_null, 
            allow_ipn_with_minus, allow_ipn_with_block)
    VALUES (?, ?, ?, ?, ?, 
            ?, ?, ?, ?, ?, 
            ?, ?, ?, ?, ?, 
            ?, ?, ?, 
            ?, ?, ?, 
            ?, ?, ?, ?, 
            ?, ?, ?, ?, 
            ?, ?);    
    """)

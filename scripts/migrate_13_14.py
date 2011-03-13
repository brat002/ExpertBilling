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
SELECT id, username, "password", fullname, email, address, nas_id, vpn_ip_address, 
       assign_ipn_ip_from_dhcp, ipn_ip_address, ipn_mac_address, ipn_status, 
       status, suspended, created, ballance, credit, disabled_by_limit, 
       balance_blocked, ipn_speed, vpn_speed, ipn_added, city, 
       postcode, region, street, house, house_bulk, entrance, room, 
       vlan, allow_webcab, allow_expresscards, assign_dhcp_null, assign_dhcp_block, 
       allow_vpn_null, allow_vpn_block, passport, passport_date, passport_given, 
       phone_h, phone_m, vpn_ipinuse_id, ipn_ipinuse_id, associate_pptp_ipn_ip, associate_pppoe_mac
  FROM billservice_account;
""")
accounts = cur.fetchall()

for account in accounts:
    cur.execute(""" 
    INSERT INTO billservice_subaccount(
            account_id, username, "password", vpn_ip_address, ipn_ip_address, 
            ipn_mac_address, nas_id, ipn_added, ipn_enabled, 
            allow_dhcp, allow_dhcp_with_null, 
            allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
            allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip, 
            associate_pppoe_ipn_mac, ipn_speed, vpn_speed, allow_addonservice, 
            vpn_ipinuse_id, ipn_ipinuse_id, allow_ipn_with_null, 
            allow_ipn_with_minus, allow_ipn_with_block)
    VALUES (%s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, 
            %s, %s, %s, 
            %s, %s, %s, 
            %s, %s, %s, %s, 
            %s);    
    """, (account['id'],account['username'],account['password'],account['vpn_ip_address'],account['ipn_ip_address'],
          account['ipn_mac_address'],account['nas_id'],account['ipn_added'],account['ipn_status'],
          account['assign_ipn_ip_from_dhcp'],account['assign_dhcp_null'],
          account['assign_dhcp_null'],account['assign_dhcp_block'],account['allow_vpn_null'],
          account['allow_vpn_null'],account['allow_vpn_block'],account['associate_pptp_ipn_ip'],
          account['associate_pppoe_mac'],account['ipn_speed'],account['vpn_speed'],True,
          account['vpn_ipinuse_id'],account['ipn_ipinuse_id'], False, False, False, 
          ))

cur.execute("UPDATE billservice_accountaddonservice as accs SET account_id=Null, subaccount_id=(SELECT id FROM billservice_subaccount  WHERE account_id=accs.account_id LIMIT 1) WHERE accs.deactivated is Null")
cur.execute("UPDATE billservice_account set nas_id = Null")
conn.commit()

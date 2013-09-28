import memcache
import psycopg2.extras
mc = memcache.Client(['127.0.0.1:11211'], debug=0)
NAS_CACHE_TIMEOUT = 60
SUBACC_CACHE_TIMEOUT = 60
ACC_CACHE_TIMEOUT = 60
COMMON_CACHE_TIMEOUT = 60

cache_prefix='__cache_'
def get_nas_by_identify(connection, cryptkey, identify):
    current_key = 'nas__by_identify_%s'
    cache_key = (cache_prefix+current_key) % identify
    obj = mc.get(cache_key)
    if obj: return obj
    
    cursor = connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cursor.execute('''SELECT id, decrypt_pw(secret, %s)::text as secret, type, multilink, 
               ipaddress, identify, speed_vendor_1, speed_vendor_2, 
               speed_attr_id1, speed_attr_id2, speed_value1, speed_value2, 
               acct_interim_interval 
               FROM nas_nas WHERE identify=%s;''' , (cryptkey, identify))
    res = cursor.fetchall()
    obj = mc.set(cache_key, res, NAS_CACHE_TIMEOUT)
    return res

def get_nas_by_ip(connection, cryptkey, ip):
    current_key = 'nas__by_ip_%s'
    cache_key = (cache_prefix+current_key) % ip
    obj = mc.get(cache_key)
    if obj: return obj
    
    cursor = connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cursor.execute('''SELECT id, decrypt_pw(secret, %s)::text as secret, type, multilink, 
               ipaddress, identify, speed_vendor_1, speed_vendor_2, 
               speed_attr_id1, speed_attr_id2, speed_value1, speed_value2, 
               acct_interim_interval 
               FROM nas_nas WHERE ipaddress=%s;''' , (cryptkey, ip))
    res = cursor.fetchall()
    obj = mc.set(cache_key, res, NAS_CACHE_TIMEOUT)
    
    return res

def get_nas_by_id(connection, cryptkey, id):
    current_key = 'nas__by_id_%s'
    cache_key = (cache_prefix+current_key) % id
    obj = mc.get(cache_key)
    if obj: return obj
    
    cursor = connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cursor.execute('''SELECT id, decrypt_pw(secret, %s)::text as secret, type, multilink, 
               ipaddress, identify, speed_vendor_1, speed_vendor_2, 
               speed_attr_id1, speed_attr_id2, speed_value1, speed_value2, 
               acct_interim_interval 
               FROM nas_nas WHERE id=%s;''' , (cryptkey, id))
    res = cursor.fetchall()
    obj = mc.set(cache_key, res, NAS_CACHE_TIMEOUT)
    return res

def get_subaccount_by_ipn_ip(connection, cryptkey, ipn_ip_address):
    current_key = 'subaccount__by_ipn_ip_address_%s'
    cache_key = (cache_prefix+current_key) % ipn_ip_address
    obj = mc.get(cache_key)
    if obj: return obj
    
    cursor = connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cursor.execute("""SELECT id, account_id, username, decrypt_pw(password, %s)::text as password, 
                                      vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, 
                                      switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, 
                                      allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
                                      allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip,
                                       associate_pppoe_ipn_mac, vpn_speed, ipn_speed, vlan, 
                                       vpn_ipv6_ip_address, ipv4_vpn_pool_id, sessionscount 
                                       FROM billservice_subaccount
                                       WHERE ipn_ip_address=%s
                                       ;""", (cryptkey, ipn_ip_address))
    res = cursor.fetchall()
    obj = mc.set(cache_key, res, SUBACC_CACHE_TIMEOUT)
    
    return res
    
def get_subaccount_by_mac(connection, cryptkey, ipn_mac_address):
    current_key = 'subaccount__by_ipn_mac_address_%s'
    cache_key = (cache_prefix+current_key) % ipn_mac_address
    obj = mc.get(cache_key)
    if obj: return obj
    
    cursor = connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cursor.execute("""SELECT id, account_id, username, decrypt_pw(password, %s)::text as password, 
                                      vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, 
                                      switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, 
                                      allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
                                      allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip,
                                       associate_pppoe_ipn_mac, vpn_speed, ipn_speed, vlan, 
                                       vpn_ipv6_ip_address, ipv4_vpn_pool_id, sessionscount 
                                       FROM billservice_subaccount
                                       WHERE ipn_mac_address=%s
                                       ;""", (cryptkey, ipn_mac_address))
    res = cursor.fetchall()
    obj = mc.set(cache_key, res, SUBACC_CACHE_TIMEOUT)
    
    return res
    
def get_subaccount_by_username(connection, cryptkey, username):
    current_key = 'subaccount__by_username_%s'
    cache_key = (cache_prefix+current_key) % username
    obj = mc.get(cache_key)
    if obj: return obj
    
    cursor = connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cursor.execute("""SELECT id, account_id, username, decrypt_pw(password, %s)::text as password, 
                                      vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, 
                                      switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, 
                                      allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
                                      allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip,
                                       associate_pppoe_ipn_mac, vpn_speed, ipn_speed, vlan, 
                                       vpn_ipv6_ip_address, ipv4_vpn_pool_id, sessionscount 
                                       FROM billservice_subaccount
                                       WHERE username=%s
                                       ;""", (cryptkey, username))
    res = cursor.fetchall()
    obj = mc.set(cache_key, res, SUBACC_CACHE_TIMEOUT)
    
    return res

def get_subaccount_by_id(connection, cryptkey, id):
    current_key = 'subaccount__by_id_%s'
    cache_key = (cache_prefix+current_key) % id
    obj = mc.get(cache_key)
    if obj: return obj
    
    cursor = connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cursor.execute("""SELECT id, account_id, username, decrypt_pw(password, %s)::text as password, 
                                      vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, 
                                      switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, 
                                      allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
                                      allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip,
                                       associate_pppoe_ipn_mac, vpn_speed, ipn_speed, vlan, 
                                       vpn_ipv6_ip_address, ipv4_vpn_pool_id, sessionscount 
                                       FROM billservice_subaccount
                                       WHERE id=%s
                                       ;""", (cryptkey, id))
    res = cursor.fetchall()
    obj = mc.set(cache_key, res, SUBACC_CACHE_TIMEOUT)
    
    return res

def get_subaccount_by_username_w_ipn_vpn_link(connection, cryptkey, username, ipn_key):
    current_key = 'subaccount__by_id_%s'
    cache_key = (cache_prefix+current_key) % ipn_key
    obj = mc.get(cache_key)
    if obj: return obj
    
    cursor = connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    
    if ipn_key.count(':')==5:
        
        cursor.execute("""SELECT id, account_id, username, decrypt_pw(password, %s)::text as password, 
                                          vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, 
                                          switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, 
                                          allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
                                          allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip,
                                           associate_pppoe_ipn_mac, vpn_speed, ipn_speed, vlan, 
                                           vpn_ipv6_ip_address, ipv4_vpn_pool_id, sessionscount 
                                           FROM billservice_subaccount
                                           WHERE username=%s and ipn_mac_address=%s
                                           ;""", (cryptkey, username, ipn_key))
    else:
        cursor.execute("""SELECT id, account_id, username, decrypt_pw(password, %s)::text as password, 
                                          vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, 
                                          switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, 
                                          allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
                                          allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip,
                                           associate_pppoe_ipn_mac, vpn_speed, ipn_speed, vlan, 
                                           vpn_ipv6_ip_address, ipv4_vpn_pool_id, sessionscount 
                                           FROM billservice_subaccount
                                           WHERE username=%s and ipn_ip_address=%s
                                           ;""", (cryptkey, username, ipn_key))
    res = cursor.fetchall()
    obj = mc.set(cache_key, res, SUBACC_CACHE_TIMEOUT)
    
    return res


def get_account_by_id(connection, id):
    current_key = 'account__by_id_%s'
    cache_key = (cache_prefix+current_key) % id
    obj = mc.get(cache_key)
    if obj: return obj
    
    cursor = connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cursor.execute("""SELECT ba.id, ba.username,  bt.time_access_service_id, 
                        ba.nas_id, ba.vpn_ip_address, bt.id, accps.access_type, 
                        ba.status, ba.balance_blocked, (ba.ballance+ba.credit) as ballance, 
                        ba.disabled_by_limit, bt.active, 
                        bt.radius_traffic_transmit_service_id, bt.vpn_ippool_id, bt.vpn_guest_ippool_id, accps.sessionscount
                        FROM billservice_account as ba
                        JOIN billservice_accounttarif AS act ON act.id=(SELECT max(id) FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and date_trunc('second', att.datetime)<%s)
                        JOIN billservice_tariff AS bt ON bt.id=act.tarif_id
                        LEFT JOIN billservice_accessparameters as accps on accps.id = bt.access_parameters_id 
                        WHERE bt.deleted is not True and id=%s;""", (id, ))
    res = cursor.fetchall()
    obj = mc.set(cache_key, res, ACC_CACHE_TIMEOUT)
    
    return res

def get_account_by_username(connection, username):
    current_key = 'account__by_username_%s'
    cache_key = (cache_prefix+current_key) % username
    obj = mc.get(cache_key)
    if obj: return obj
    
    cursor = connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cursor.execute("""SELECT ba.id, ba.username,  bt.time_access_service_id, 
                        ba.nas_id, ba.vpn_ip_address, bt.id, accps.access_type, 
                        ba.status, ba.balance_blocked, (ba.ballance+ba.credit) as ballance, 
                        ba.disabled_by_limit, bt.active, 
                        bt.radius_traffic_transmit_service_id, bt.vpn_ippool_id, bt.vpn_guest_ippool_id, accps.sessionscount
                        FROM billservice_account as ba
                        JOIN billservice_accounttarif AS act ON act.id=(SELECT max(id) FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and date_trunc('second', att.datetime)<%s)
                        JOIN billservice_tariff AS bt ON bt.id=act.tarif_id
                        LEFT JOIN billservice_accessparameters as accps on accps.id = bt.access_parameters_id 
                        WHERE bt.deleted is not True and username=%s;""", (username,))
    res = cursor.fetchall()
    obj = mc.set(cache_key, res, COMMON_CACHE_TIMEOUT)
    
    return res

def get_defspeed_by_tarif_id(connection, tarif_id):
    current_key = 'defspeed__by_tarif_id_%s'
    cache_key = (cache_prefix+current_key) % (tarif_id, )
    obj = mc.get(cache_key)
    if obj: return obj
    
    cursor = connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cursor.execute("""SELECT accessparameters.max_tx, accessparameters.max_rx, accessparameters.burst_tx, 
                             accessparameters.burst_rx, accessparameters.burst_treshold_tx, accessparameters.burst_treshold_rx,  
                             accessparameters.burst_time_tx, accessparameters.burst_time_rx, accessparameters.min_tx, 
                             accessparameters.min_rx,  accessparameters.priority,
                        tariff.id
                        FROM billservice_accessparameters as accessparameters
                        JOIN billservice_tariff as tariff ON tariff.access_parameters_id=accessparameters.id
                        WHERE tariff.deleted is not True and tariff.id=%s;""", (tarif_id, ))
    res = cursor.fetchall()
    obj = mc.set(cache_key, res, COMMON_CACHE_TIMEOUT)
    
    return res

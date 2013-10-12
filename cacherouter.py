import pylibmc
import psycopg2.extras
import datetime
import traceback

NAS_CACHE_TIMEOUT = 120
SUBACC_CACHE_TIMEOUT = 120
ACC_CACHE_TIMEOUT = 120
COMMON_CACHE_TIMEOUT = 180

class RealDictRow(dict):
    """A `!dict` subclass representing a data record."""

    __slots__ = ('_column_mapping')

    def __init__(self, cursor):
        dict.__init__(self)
        # Required for named cursors
        if cursor.description and not cursor.column_mapping:
            cursor._build_index()

        self._column_mapping = cursor.column_mapping

    def __setitem__(self, name, value):
        if type(name) == int:
            name = self._column_mapping[name]
        return dict.__setitem__(self, name, value)

    def __getattr__(self, name):
        
        if type(name) == int:
            return self._column_mapping[name]
        return dict.__getitem__(self, name)
    
    def __getstate__(self):
        return (self.copy(), self._column_mapping[:])

    def __setstate__(self, data):
        self.update(data[0])
        self._column_mapping = data[1]
        
class AttrDict(dict):
    
    def __getattr__(self, attr):
        return self[attr]


        
psycopg2.extras.RealDictRow = RealDictRow

from time import time
class memoize_with_expiry(object):
    def __init__(self, expiry_time=0, cache=None, num_args=None):
        self.cache = cache
        self.expiry_time = expiry_time
        self.num_args = num_args
    
    def __call__(self, func):
        def wrapped(*args, **kw):
            if self.cache is None and not hasattr(func, '_cache'):
                func._cache = {}
            cache = self.cache or func._cache
            
            if self.num_args:
                mem_args = args[:self.num_args]
            else:
                mem_args = args
            # frozenset is used to ensure hashability
            if kw: 
                key = mem_args, frozenset(kw.iteritems())
            else:
                key = mem_args
            if key in cache:
                result, timestamp = cache[key]
                # Check the age.
                age = time() - timestamp
                if not self.expiry_time or age < self.expiry_time:
                    return result
            result = func(*args, **kw)
            cache[key] = (result, time())
            return result
        return wrapped

class Cache(object):
    
    def __init__(self, connection, memcached_dsn, crypt_key, logger = None):
        self.connection = connection
        self.memcached_dsn = memcached_dsn
        self.memcached_connect()
        self.cache_prefix='__cache_'
        self.crypt_key = crypt_key
        self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        self.logger = logger
    
    
    def memcached_connect(self):
        self.memcached_connection = pylibmc.Client([self.memcached_dsn], binary=True,
                         behaviors={"tcp_nodelay": True,
                                    "ketama": True})
    
    #@memoize_with_expiry(30)
    def get_nas_by_identify(self,  nas_ip, identify):
        current_key = 'nas__by_identify_%s'
        cache_key = (self.cache_prefix+current_key) % identify
        obj = self.memcached_connection.get(cache_key)
        
        if obj: 
            return obj
        
        try:
            self.cursor.execute('''SELECT id, decrypt_pw(secret, %s)::text as secret, type, multilink, 
                       ipaddress, identify, speed_vendor_1, speed_vendor_2, 
                       speed_attr_id1, speed_attr_id2, speed_value1, speed_value2, 
                       acct_interim_interval 
                       FROM nas_nas WHERE ipaddress=%s and identify=%s;''' , (self.crypt_key, nas_ip, identify))
            res = self.cursor.fetchall()
    
            if res:
                self.memcached_connection.set(cache_key, res, NAS_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = []
            

        return res
    
    #@memoize_with_expiry(30)
    def get_nas_by_ip(self,  ip):
        current_key = 'nas__by_ip_%s'
        cache_key = (self.cache_prefix+current_key) % ip
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj

        try:
            self.cursor.execute('''SELECT id, decrypt_pw(secret, %s)::text as secret, type, multilink, 
                       ipaddress, identify, speed_vendor_1, speed_vendor_2, 
                       speed_attr_id1, speed_attr_id2, speed_value1, speed_value2, 
                       acct_interim_interval 
                       FROM nas_nas WHERE ipaddress=%s;''' , (self.crypt_key, ip))
            res = self.cursor.fetchall()
            obj = self.memcached_connection.set(cache_key, res, NAS_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = []
            
        return res
    
    #@memoize_with_expiry(30)
    def get_nas_by_id(self,  id):
        current_key = 'nas__by_id_%s'
        cache_key = (self.cache_prefix+current_key) % id
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        
        

        try:
            self.cursor.execute('''SELECT id, decrypt_pw(secret, %s)::text as secret, type, multilink, 
                       ipaddress, identify, speed_vendor_1, speed_vendor_2, 
                       speed_attr_id1, speed_attr_id2, speed_value1, speed_value2, 
                       acct_interim_interval 
                       FROM nas_nas WHERE id=%s;''' , (self.crypt_key, id))
            res = self.cursor.fetchone()
    
            obj = self.memcached_connection.set(cache_key, res, NAS_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = None
        return res
    
    #@memoize_with_expiry(30)
    def get_subaccount_by_ipn_ip(self,  ipn_ip_address):
        current_key = 'subaccount__by_ipn_ip_address_%s'
        cache_key = (self.cache_prefix+current_key) % ipn_ip_address
        obj = self.memcached_connection.get(cache_key)
        if obj: 
            
            return obj

        try:
            self.cursor.execute("""SELECT id, account_id, username, decrypt_pw(password, %s)::text as password, 
                                              vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, 
                                              switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, 
                                              allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
                                              allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip,
                                               associate_pppoe_ipn_mac, vpn_speed, ipn_speed, vlan, 
                                               vpn_ipv6_ip_address, ipv4_vpn_pool_id, sessionscount 
                                               FROM billservice_subaccount
                                               WHERE ipn_ip_address=%s
                                               ;""", (self.crypt_key, ipn_ip_address))
            res = self.cursor.fetchone()
            if res:
                res = res[0]
            obj = self.memcached_connection.set(cache_key, res, SUBACC_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = None
            
        return res
    
    
    #@memoize_with_expiry(30)
    def get_subaccount_by_mac(self,  ipn_mac_address):
        current_key = 'subaccount__by_ipn_mac_address_%s'
        cache_key = (self.cache_prefix+current_key) % ipn_mac_address
        obj = self.memcached_connection.get(cache_key)
        if obj: 
            
            return obj
        
        

        
        try:
            self.cursor.execute("""SELECT id, account_id, username, decrypt_pw(password, %s)::text as password, 
                                              vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, 
                                              switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, 
                                              allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
                                              allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip,
                                               associate_pppoe_ipn_mac, vpn_speed, ipn_speed, vlan, 
                                               vpn_ipv6_ip_address, ipv4_vpn_pool_id, sessionscount 
                                               FROM billservice_subaccount
                                               WHERE ipn_mac_address=%s
                                               ;""", (self.crypt_key, ipn_mac_address))
            res = self.cursor.fetchone()
            if res:
                res = res[0]
            obj = self.memcached_connection.set(cache_key, res, SUBACC_CACHE_TIMEOUT)
        
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = None
            
        return res
    #@memoize_with_expiry(30)
    def get_subaccount_by_username(self, username):
        current_key = 'subaccount__by_username_%s'
        cache_key = (self.cache_prefix+current_key) % username
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        


        
        try:
            self.cursor.execute("""SELECT id, account_id, username, decrypt_pw(password, %s)::text as password, 
                                              vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, 
                                              switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, 
                                              allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
                                              allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip,
                                               associate_pppoe_ipn_mac, vpn_speed, ipn_speed, vlan, 
                                               vpn_ipv6_ip_address, ipv4_vpn_pool_id, sessionscount 
                                               FROM billservice_subaccount
                                               WHERE username=%s
                                               ;""", (self.crypt_key, username))
            res = self.cursor.fetchone()
            obj = self.memcached_connection.set(cache_key, res, SUBACC_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = None
        return res
    
    #@memoize_with_expiry(30)
    def get_subaccount_by_id(self, id):
        current_key = 'subaccount__by_id_%s'
        cache_key = (self.cache_prefix+current_key) % id
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        


        
        try:
            self.cursor.execute("""SELECT id, account_id, username, decrypt_pw(password, %s)::text as password, 
                                              vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, 
                                              switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, 
                                              allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
                                              allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip,
                                               associate_pppoe_ipn_mac, vpn_speed, ipn_speed, vlan, 
                                               vpn_ipv6_ip_address, ipv4_vpn_pool_id, sessionscount 
                                               FROM billservice_subaccount
                                               WHERE id=%s
                                               ;""", (self.crypt_key, id))
    
            res = self.cursor.fetchone()
            obj = self.memcached_connection.set(cache_key, res, SUBACC_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = None
        return res
    
    #@memoize_with_expiry(30)
    def get_subaccount_by_username_w_ipn_vpn_link(self,  username, ipn_key):
        current_key = 'subaccount_by_username_w_ipn_vpn_link_%s'
        cache_key = (self.cache_prefix+current_key) % ipn_key
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        
        

        
        try:
            if ipn_key.count(':')==5 or ipn_key.rfind('-')!=-1:
                ipn_key = ipn_key.replace('-', ':')
                
                self.cursor.execute("""SELECT id, account_id, username, decrypt_pw(password, %s)::text as password, 
                                                  vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, 
                                                  switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, 
                                                  allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
                                                  allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip,
                                                   associate_pppoe_ipn_mac, vpn_speed, ipn_speed, vlan, 
                                                   vpn_ipv6_ip_address, ipv4_vpn_pool_id, sessionscount 
                                                   FROM billservice_subaccount
                                                   WHERE username=%s and ipn_mac_address=%s
                                                   ;""", (self.crypt_key, username, ipn_key))
            else:
                self.cursor.execute("""SELECT id, account_id, username, decrypt_pw(password, %s)::text as password, 
                                                  vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, 
                                                  switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, 
                                                  allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
                                                  allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip,
                                                   associate_pppoe_ipn_mac, vpn_speed, ipn_speed, vlan, 
                                                   vpn_ipv6_ip_address, ipv4_vpn_pool_id, sessionscount 
                                                   FROM billservice_subaccount
                                                   WHERE username=%s and ipn_ip_address=%s
                                                   ;""", (self.crypt_key, username, ipn_key))
    
            res = self.cursor.fetchone()
    
            obj = self.memcached_connection.set(cache_key, res, SUBACC_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = None
            
        return res
    
    #@memoize_with_expiry(30)
    def get_account_by_id(self, id):
        current_key = 'account__by_id_%s'
        cache_key = (self.cache_prefix+current_key) % id
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        
        
        try:
            self.cursor.execute("""SELECT ba.id, ba.username,  bt.time_access_service_id, 
                                ba.nas_id, ba.vpn_ip_address, bt.id as tarif_id, accps.access_type, 
                                ba.status, ba.balance_blocked, (ba.ballance+ba.credit) as ballance, 
                                ba.disabled_by_limit, bt.active as tariff_active, 
                                bt.radius_traffic_transmit_service_id, bt.vpn_ippool_id, bt.vpn_guest_ippool_id, accps.sessionscount
                                FROM billservice_account as ba
                                JOIN billservice_accounttarif AS act ON act.id=(SELECT max(id) FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and date_trunc('second', att.datetime)<%s)
                                JOIN billservice_tariff AS bt ON bt.id=act.tarif_id
                                LEFT JOIN billservice_accessparameters as accps on accps.id = bt.access_parameters_id 
                                WHERE bt.deleted is not True and ba.id=%s;""", (datetime.datetime.now(), id, ))
            res = self.cursor.fetchone()
    
            obj = self.memcached_connection.set(cache_key, res, ACC_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = None
            
        return res
    #@memoize_with_expiry(30)
    def get_account_by_username(self, username):
        current_key = 'account__by_username_%s'
        cache_key = (self.cache_prefix+current_key) % username
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        
        

        
        try:
            self.cursor.execute("""SELECT ba.id, ba.username,  bt.time_access_service_id, 
                                ba.nas_id, ba.vpn_ip_address, bt.id as tarif_id, accps.access_type, 
                                ba.status, ba.balance_blocked, (ba.ballance+ba.credit) as ballance, 
                                ba.disabled_by_limit, bt.active as tariff_active, 
                                bt.radius_traffic_transmit_service_id, bt.vpn_ippool_id, bt.vpn_guest_ippool_id, accps.sessionscount
                                FROM billservice_account as ba
                                JOIN billservice_accounttarif AS act ON act.id=(SELECT max(id) FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and date_trunc('second', att.datetime)<%s)
                                JOIN billservice_tariff AS bt ON bt.id=act.tarif_id
                                LEFT JOIN billservice_accessparameters as accps on accps.id = bt.access_parameters_id 
                                WHERE bt.deleted is not True and username=%s;""", (username,))
            res = self.cursor.fetchone()
            obj = self.memcached_connection.set(cache_key, res, COMMON_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = None
            
        return res
    #@memoize_with_expiry(30)
    def get_defspeed_by_tarif_id(self, tarif_id):
        current_key = 'defspeed__by_tarif_id_%s'
        cache_key = (self.cache_prefix+current_key) % (tarif_id, )
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        

        try:
            cursor = self.connection.cursor()
            cursor.execute("""SELECT accessparameters.max_tx, accessparameters.max_rx, accessparameters.burst_tx, 
                                     accessparameters.burst_rx, accessparameters.burst_treshold_tx, accessparameters.burst_treshold_rx,  
                                     accessparameters.burst_time_tx, accessparameters.burst_time_rx, accessparameters.min_tx, 
                                     accessparameters.min_rx,  accessparameters.priority,
                                tariff.id
                                FROM billservice_accessparameters as accessparameters
                                JOIN billservice_tariff as tariff ON tariff.access_parameters_id=accessparameters.id
                                WHERE tariff.deleted is not True and tariff.id=%s;""", (tarif_id, ))
            res = cursor.fetchone()
            cursor.close()
            obj = self.memcached_connection.set(cache_key, res, COMMON_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = None
            
        return res
    
    #@memoize_with_expiry(30)
    def get_speed_by_tarif_id(self, tarif_id):
        current_key = 'speed__by_tarif_id_%s'
        cache_key = (self.cache_prefix+current_key) % (tarif_id, )
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        

        try:
            cursor = self.connection.cursor()
            cursor.execute("""SELECT timespeed.max_tx, timespeed.max_rx, timespeed.burst_tx, timespeed.burst_rx, 
                                 timespeed.burst_treshold_tx, timespeed.burst_treshold_rx,  timespeed.burst_time_tx, 
                                 timespeed.burst_time_rx, timespeed.min_tx, timespeed.min_rx,  timespeed.priority,
                                timenode.time_start, timenode.length, timenode.repeat_after,
                                tariff.id 
                                FROM billservice_timespeed as timespeed
                                JOIN billservice_tariff as tariff ON tariff.access_parameters_id=timespeed.access_parameters_id
                                JOIN billservice_timeperiodnode as timenode ON timespeed.time_id=timenode.time_period_id
                                WHERE tariff.deleted is not True
                                and tariff.id=%s;""", (tarif_id, ))
            res = cursor.fetchall()
            cursor.close()
            obj = self.memcached_connection.set(cache_key, res, COMMON_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = []
            
        return res
    
    #@memoize_with_expiry(30)
    def get_speedlimit_by_account_id(self, account_id):
        current_key = 'speedlimit__by_account_id_%s'
        cache_key = (self.cache_prefix+current_key) % (account_id, )
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        

        try:
            self.cursor.execute("""SELECT accountspeedlimit.id, accountspeedlimit.account_id, speedlimit.max_tx, speedlimit.max_rx, 
                                speedlimit.burst_tx, speedlimit.burst_rx, 
                                speedlimit.burst_treshold_tx, speedlimit.burst_treshold_rx, 
                                speedlimit.burst_time_tx, speedlimit.burst_time_rx, 
                                speedlimit.priority,
                                speedlimit.min_tx, speedlimit.min_rx, speedlimit.speed_units, speedlimit.change_speed_type
                                FROM billservice_speedlimit as speedlimit, billservice_accountspeedlimit as accountspeedlimit
                                WHERE accountspeedlimit.speedlimit_id=speedlimit.id 
                                and accountspeedlimit.account_id=%s;""", (account_id, ))
            res = self.cursor.fetchall()
            obj = self.memcached_connection.set(cache_key, res, ACC_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = []
            
        return res
    #@memoize_with_expiry(30)
    def get_accountaddonservice_by_account_id(self, account_id):
        current_key = 'accountaddonservice__by_account_id_%s'
        cache_key = (self.cache_prefix+current_key) % (account_id, )
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        

        try:
            self.cursor.execute("""SELECT accs.id, accs.service_id, accs.account_id, accs.activated, accs.deactivated, accs.action_status, 
        
                                        accs.speed_status, accs.temporary_blocked, date_trunc('second',accs.last_checkout) as last_checkout, accs.subaccount_id, COALESCE(accs.cost, addons.cost) as cost
        
                                   FROM billservice_accountaddonservice as accs 
                                   JOIN billservice_addonservice as addons ON addons.id=accs.service_id
                                   WHERE accs.account_id=%s and (accs.account_id is not NULL and (SELECT True from billservice_account WHERE id=accs.account_id and deleted is NULL)=True) and  (accs.deactivated is Null or (accs.last_checkout<accs.deactivated AND (SELECT service_type FROM billservice_addonservice as adds WHERE adds.id=accs.id)='periodical') or 
                                   ((SELECT service_type FROM billservice_addonservice as adds WHERE adds.id=accs.service_id)='onetime' and (accs.action_status=True or accs.last_checkout is Null))) or (accs.action_status=True and accs.deactivated is not Null and addons.action=True);""", (account_id, ))
            res = self.cursor.fetchall()
            obj = self.memcached_connection.set(cache_key, res, ACC_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = []
            
        return res
    
    #@memoize_with_expiry(30)
    def get_accountaddonservice_by_subaccount_id(self, subaccount_id):
        current_key = 'accountaddonservice__by_subaccount_id_%s'
        cache_key = (self.cache_prefix+current_key) % (subaccount_id, )
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        
        try:
            self.cursor.execute("""SELECT accs.id, accs.service_id, accs.account_id, accs.activated, accs.deactivated, accs.action_status, 
        
                                        accs.speed_status, accs.temporary_blocked, date_trunc('second',accs.last_checkout) as last_checkout, accs.subaccount_id, COALESCE(accs.cost, addons.cost) as cost
        
                                   FROM billservice_accountaddonservice as accs 
                                   JOIN billservice_addonservice as addons ON addons.id=accs.service_id
                                   WHERE accs.subaccount_id=%s and (accs.account_id is not NULL and (SELECT True from billservice_account WHERE id=accs.account_id and deleted is NULL)=True) and  (accs.deactivated is Null or (accs.last_checkout<accs.deactivated AND (SELECT service_type FROM billservice_addonservice as adds WHERE adds.id=accs.id)='periodical') or 
                                   ((SELECT service_type FROM billservice_addonservice as adds WHERE adds.id=accs.service_id)='onetime' and (accs.action_status=True or accs.last_checkout is Null))) or (accs.action_status=True and accs.deactivated is not Null and addons.action=True);""", (subaccount_id, ))
            res = self.cursor.fetchall()
            obj = self.memcached_connection.set(cache_key, res, ACC_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = []
            
        return res
    
    #@memoize_with_expiry(30)
    def get_addonservice_by_id(self, id):
        current_key = 'addonservice_by_id_%s'
        cache_key = (self.cache_prefix+current_key) % (id, )
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        
        try:
            self.cursor.execute("""SELECT id, "name", allow_activation, service_type, sp_type, sp_period_id, 
                                        timeperiod_id, "cost", cancel_subscription, wyte_period_id, wyte_cost, 
                                        "action", nas_id, service_activation_action, service_deactivation_action, 
                                        deactivate_service_for_blocked_account, change_speed, change_speed_type, 
                                        speed_units, max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, 
                                        burst_treshold_rx, burst_time_tx, burst_time_rx, min_tx, min_rx, 
                                        priority
                                   FROM billservice_addonservice WHERE id=%s;""", (id, ))
            res = self.cursor.fetchone()
            obj = self.memcached_connection.set(cache_key, res, COMMON_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = []
            
        return res
    #@memoize_with_expiry(30)
    def get_timeperiodnode_by_timeperiod_id(self, timeperiod_id):
        current_key = 'timeperiodnode_by_timeperiod_id_%s'
        cache_key = (self.cache_prefix+current_key) % (timeperiod_id)
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        
        try:
            self.cursor.execute("""SELECT tpn.id, tpn.name, date_trunc('second', tpn.time_start) as time_start, tpn.length, tpn.repeat_after, tpn.time_period_id 
                                FROM billservice_timeperiodnode as tpn WHERE tpn.time_period_id =%s;""", (timeperiod_id, ))
            res = self.cursor.fetchall()
            obj = self.memcached_connection.set(cache_key, res, COMMON_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = []
            
        return res
    
    #@memoize_with_expiry(30)
    def get_ippool_by_id(self, id):
        current_key = 'ippool_by_id_%s'
        cache_key = (self.cache_prefix+current_key) % (id)
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        
        try:
            self.cursor.execute("""SELECT id, next_ippool_id as next_pool_id FROM billservice_ippool WHERE id =%s;""", (id, ))
            res = self.cursor.fetchone()
            obj = self.memcached_connection.set(cache_key, res, COMMON_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = None
            
        return res
    #@memoize_with_expiry(30)
    def get_switch_by_id(self, id):
        current_key = 'switch_by_id_%s'
        cache_key = (self.cache_prefix+current_key) % (id,)
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        
        try:
            self.cursor.execute("""SELECT id, identify, option82, option82_auth_type, option82_template, remote_id FROM billservice_switch WHERE id =%s;""", (id, ))
            res = self.cursor.fetchone()
            obj = self.memcached_connection.set(cache_key, res, COMMON_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = None
            
        return res

    #@memoize_with_expiry(30)
    def get_radiusattr_by_tarif_id(self, tarif_id):
        current_key = 'radiusattr_by_tarif_id_%s'
        cache_key = (self.cache_prefix+current_key) % (tarif_id,)
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj
        
        try:
            self.cursor.execute("""SELECT vendor, attrid, value, account_status, tarif_id, nas_id 
                                       FROM billservice_radiusattrs WHERE tarif_id=%s;""", (tarif_id, ))
            res = self.cursor.fetchall()
            obj = self.memcached_connection.set(cache_key, res, COMMON_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = None
            
        return res
    
    #@memoize_with_expiry(30)
    def get_radiusattr_by_nas_id(self, nas_id):
        current_key = 'radiusattr_by_nas_id_%s'
        cache_key = (self.cache_prefix+current_key) % (nas_id,)
        obj = self.memcached_connection.get(cache_key)
        if obj: return obj

        try:
            self.cursor.execute("""SELECT vendor, attrid, value, account_status, tarif_id, nas_id 
                                       FROM billservice_radiusattrs WHERE nas_id=%s;""", (nas_id, ))
            res = self.cursor.fetchall()
            obj = self.memcached_connection.set(cache_key, res, COMMON_CACHE_TIMEOUT)
        except Exception as ex:
            self.logger.error("%s database or memcached subsystem error: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
            res = None
            
        return res

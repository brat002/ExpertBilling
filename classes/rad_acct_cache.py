from operator import itemgetter, setitem
from cacheutils import CacheCollection, CacheItem, SimpleDefDictCache, SimpleDictCache
from cache_sql import rad_sql
from collections import defaultdict
from rad_class.AccountData import AccountData
from rad_class.NasData import NasData
from rad_class.SubAccountsData import SubAccountsData



class RadAcctCaches(CacheCollection):
    __slots__ = ('account_cache', 'nas_cache',  'subaccount_cache')
    
    def __init__(self, date, crypt_key):
        super(RadAcctCaches, self).__init__(date)
        #self.account_cache = AccountCache(date)
        #self.nas_cache = NasCache(crypt_key)
        #self.subaccount_cache = SubAccountsCache(crypt_key)
        #self.caches = [self.account_cache, self.nas_cache,self.subaccount_cache]
        self.caches = []


class AccountCache(CacheItem):
    __slots__ = ('by_username', 'by_id')
    
    datatype = AccountData
    sql = rad_sql['accounts']
    
    def __init__(self, date):
        super(AccountCache, self).__init__()
        self.vars = (date,)
        
    def reindex(self):
        self.by_username = {}
        self.by_id = {}

        for acct in self.data:
            self.by_username[acct.username] = acct
            self.by_id[acct.account_id] = acct
            
            
class NasCache(CacheItem):
    __slots__ = ('by_id', 'by_ip','by_ip_n_identify')
    datatype = NasData
    sql = rad_sql['nas']
    
    def __init__(self, crypt_key):
        super(NasCache, self).__init__()
        self.vars = (crypt_key, )
        self.by_ip = {}
        self.by_ip_n_identify = {}
        self.by_id = {}
        
    def reindex(self):
        self.by_ip = {}
        self.by_ip_n_identify = {}
        for nas in self.data:
            
            if not self.by_ip_n_identify.get((str(nas.ipaddress), str(nas.identify))):
                self.by_ip_n_identify[(str(nas.ipaddress), str(nas.identify))] = []
            self.by_ip_n_identify[(str(nas.ipaddress), str(nas.identify))].append(nas)
            
            if not self.by_ip.get(str(nas.ipaddress)):
                self.by_ip[str(nas.ipaddress)] = []
            self.by_ip[str(nas.ipaddress)].append(nas)
            
            self.by_id[nas.id] = nas
            
            
            
class SubAccountsCache(CacheItem):
    __slots__ = ('by_id', 'by_username', 'by_username_w_ipn_vpn_link', 'by_mac', 'by_ipn_ip', 'by_vpn_ip', 'by_ipn_ip_nas_id', 'by_switch_port')
    
    datatype = SubAccountsData
    sql = rad_sql['subaccounts']
    
    def __init__(self, crypt_key):
        super(SubAccountsCache, self).__init__()
        self.vars = (crypt_key, )
        
    def reindex(self):
        self.by_id = {}
        self.by_username = {}
        self.by_mac = {}
        self.by_ipn_ip = {}
        self.by_vpn_ip = {}
        self.by_ipn_ip_nas_id = {}
        self.by_username_w_ipn_vpn_link = {}
        self.by_switch_port = {}
        #self.by_username_w_pppoe_mac = {}
        
        for item in self.data:
            self.by_id[item.id] = item
            if item.username:
                self.by_username[item.username] = item
            if item.ipn_mac_address:
                self.by_mac[item.ipn_mac_address.lower()] = item
            if item.ipn_ip_address and item.ipn_ip_address is not "0.0.0.0" :
                self.by_ipn_ip[item.ipn_ip_address] = item
                #self.by_ipn_ip_nas_id[(item.ipn_ip_address, item.nas_id)] = item                
            if item.vpn_ip_address and item.vpn_ip_address is not "0.0.0.0" :
                self.by_vpn_ip[item.vpn_ip_address] = item
            if item.ipn_ip_address and item.ipn_ip_address is not "0.0.0.0" and item.associate_pptp_ipn_ip==True:
                self.by_username_w_ipn_vpn_link[(item.username, item.ipn_ip_address)]=item

            if item.ipn_mac_address  and item.associate_pppoe_ipn_mac==True:
                self.by_username_w_ipn_vpn_link[(item.username, item.ipn_mac_address)]=item
                
            if item.switch_id and item.switch_port:
                self.by_switch_port[(item.switch_id,item.switch_port)]=item
                
            
    

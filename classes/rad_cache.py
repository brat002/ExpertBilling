from operator import itemgetter, setitem
from cacheutils import CacheCollection, CacheItem, SimpleDefDictCache, SimpleDictCache
from cache_sql import rad_sql, core_sql
from collections import defaultdict
from rad_class.AccountData import AccountData
from rad_class.NasData import NasData
from rad_class.DefaultSpeedData import DefaultSpeedData
from rad_class.SpeedData import SpeedData
from rad_class.SpeedlimitData import SpeedlimitData
from rad_class.RadiusAttrsData import RadiusAttrsData
from rad_class.SubAccountsData import SubAccountsData
from core_cache import TimePeriodAccessCache as PeriodCache
from common.AddonServiceData import AddonServiceData
#from common.AddonServiceTarifData import AddonServiceTarifData
from common.AccountAddonServiceData import AccountAddonServiceData

from core_cache import AddonServiceCache, AddonServiceTarifCache, AccessParametersCache

class RadCaches(CacheCollection):
    __slots__ = ('account_cache', 'period_cache', 'nas_cache', 'defspeed_cache', 'speed_cache', 'speedlimit_cache', 'radattrs_cache', 'addonservice_cache', 'accountaddonservice_cache', 'subaccounts_cache')
    
    def __init__(self, date, fMem):
        super(RadCaches, self).__init__(date)
        self.account_cache = AccountCache(date)
        self.period_cache  = PeriodCache(date, fMem)
        self.nas_cache = NasCache()
        self.defspeed_cache = DefaultSpeedCache()
        self.speed_cache = SpeedCache()
        self.speedlimit_cache = SpeedlimitCache()
        self.radattrs_cache = RadiusAttrsCache()
        self.addonservice_cache = AddonServiceCache()
        self.accountaddonservice_cache = AccountAddonServiceCache()
        self.subaccount_cache = SubAccountsCache()
        self.caches = [self.account_cache, self.period_cache, self.nas_cache, self.defspeed_cache, self.speed_cache, self.speedlimit_cache, self.radattrs_cache, self.addonservice_cache, self.accountaddonservice_cache, self.subaccount_cache]


class AccountCache(CacheItem):
    __slots__ = ('by_username', 'by_ipn_mac', 'by_ipn_ip_nas')
    
    datatype = AccountData
    sql = rad_sql['accounts']
    
    def __init__(self, date):
        super(AccountCache, self).__init__()
        self.vars = (date,)
        
    def reindex(self):
        self.by_username = {}
        self.by_ipn_mac  = {}
        self.by_ipn_ip_nas = {}

        for acct in self.data:
            self.by_username[str(acct.username)] = acct
            self.by_ipn_mac[str(acct.ipn_mac_address)] = acct
            self.by_ipn_ip_nas[(acct.ipn_ip_address, acct.nas_id)] = acct
            
class DefaultSpeedCache(SimpleDictCache):
    '''By tarif id'''
    __slots__ = ()
    datatype = DefaultSpeedData
    sql = rad_sql['defspeed']
    num = 6

class SpeedCache(SimpleDefDictCache):
    '''by tarif_id'''
    __slots__ = ()
    datatype = SpeedData
    sql = rad_sql['speed']
    num = 9 

class SpeedlimitCache(SimpleDictCache):
    '''By account_id'''
    __slots__ = ('by_account_id')
    datatype = SpeedlimitData
    sql = rad_sql['limit']
    num = 0
    
    def reindex(self):
        self.by_account_id = {}
        for speed_l in self.data:
            self.by_account_id[speed_l[1]] = speed_l[2:]
            
class NasCache(CacheItem):
    __slots__ = ('by_id', 'by_ip','by_ip_n_identify')
    datatype = NasData
    sql = rad_sql['nas']
    
    def __init__(self):
        super(NasCache, self).__init__()
        self.by_ip = {}
        self.by_ip_n_identify = {}
        self.by_id = {}
        
    def reindex(self):
        self.by_ip = {}
        self.by_ip_n_identify = {}
        for nas in self.data:
            self.by_ip_n_identify[(str(nas.ipaddress), str(nas.identify))] = nas
            self.by_ip[str(nas.ipaddress)] = nas
            self.by_id[nas.id] = nas
            
class RadiusAttrsCache(SimpleDefDictCache):
    '''by tarif_id'''
    __slots__ = ()
    datatype = RadiusAttrsData
    sql = rad_sql['attrs']
    num = 3


class AddonServiceCache(SimpleDictCache):
    '''By id'''
    __slots__ = ()
    datatype = AddonServiceData
    sql = core_sql['addon_service']
    
class AccountAddonServiceCache(CacheItem):
    __slots__ = ('by_id', 'by_account', 'by_service')
    
    datatype = AccountAddonServiceData
    sql = core_sql['addon_account']
    
    def __init__(self):
        super(AccountAddonServiceCache, self).__init__()
        self.by_id = {}
        self.by_service = defaultdict(list)
        #index on tariff_id
        self.by_account = defaultdict(list)
        
    def reindex(self):
        self.by_id.clear()
        #index on accounttarif.id
        self.by_service.clear()
        #index on tariff_id
        self.by_account.clear()
        for addon in self.data:
            self.by_id[addon.id]  = addon
            self.by_account[addon.account_id].append(addon)
            self.by_service[addon.service_id].append(addon)
            
            
class SubAccountsCache(CacheItem):
    __slots__ = ('by_account_id', 'by_username', 'by_mac')
    
    datatype = AccountData
    sql = rad_sql['subaccounts']
    
    def __init__(self, date):
        super(SubAccountsCache, self).__init__()
        
    def reindex(self):
        self.by_account_id = {}
        self.by_username = {}
        self.by_mac = {}
        
        for item in self.data:
            self.by_account_id[item.account_id] = item
            if item.username:
                self.by_username[item.username] = item
            if item.ipn_mac_address:
                self.by_mac[item.ipn_mac_address] = item

            
    

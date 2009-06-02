from operator import itemgetter, setitem
from cacheutils import CacheCollection, CacheItem, SimpleDefDictCache, SimpleDictCache
from cache_sql import rad_sql
from collections import defaultdict
from rad_class.AccountData import AccountData
from rad_class.NasData import NasData
from rad_class.DefaultSpeedData import DefaultSpeedData
from rad_class.SpeedData import SpeedData
from rad_class.SpeedlimitData import SpeedlimitData
from rad_class.RadiusAttrsData import RadiusAttrsData
from core_cache import TimePeriodAccessCache as PeriodCache

class RadCaches(CacheCollection):
    __slots__ = ('account_cache', 'period_cache', 'nas_cache', 'defspeed_cache', 'speed_cache', 'speedlimit_cache', 'radattrs_cache')
    
    def __init__(self, date, fMem):
        super(RadCaches, self).__init__(date)
        self.account_cache = AccountCache(date)
        self.period_cache  = PeriodCache(date, fMem)
        self.nas_cache = NasCache()
        self.defspeed_cache = DefaultSpeedCache()
        self.speed_cache = SpeedCache()
        self.speedlimit_cache = SpeedlimitCache()
        self.radattrs_cache = RadiusAttrsCache()
        self.caches = [self.account_cache, self.period_cache, self.nas_cache, self.defspeed_cache, self.speed_cache, self.speedlimit_cache, self.radattrs_cache]


class AccountCache(CacheItem):
    __slots__ = ('by_username', 'by_ipn_mac')
    
    datatype = AccountData
    sql = rad_sql['accounts']
    
    def __init__(self, date):
        super(AccountCache, self).__init__()
        self.vars = (date,)
        
    def reindex(self):
        self.by_username = {}
        self.by_ipn_mac  = {}

        for acct in self.data:
            self.by_username[str(acct.username)] = acct
            self.by_ipn_mac[str(acct.ipn_mac_address)] = acct
            
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
    __slots__ = ()
    datatype = SpeedlimitData
    sql = rad_sql['limit']
    num = 11
   
class NasCache(CacheItem):
    __slots__ = ('by_ip',)
    datatype = NasData
    sql = rad_sql['nas']
    
    def reindex(self):
        self.by_ip = {}
        for nas in self.data:
            self.by_ip[str(nas.ipaddress)] = nas
            
class RadiusAttrsCache(SimpleDefDictCache):
    '''by tarif_id'''
    __slots__ = ()
    datatype = RadiusAttrsData
    sql = rad_sql['attrs']
    num = 3
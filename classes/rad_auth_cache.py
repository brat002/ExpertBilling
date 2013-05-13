from operator import itemgetter, setitem
from cacheutils import CacheCollection, CacheItem, SimpleDefDictCache, SimpleDictCache
from cache_sql import rad_sql, core_sql
from collections import defaultdict
from rad_class.AccountData import AccountData
from rad_class.NasData import NasData
from rad_class.SwitchData import SwitchData
from rad_class.DefaultSpeedData import DefaultSpeedData
from rad_class.SpeedData import SpeedData
from rad_class.SpeedlimitData import SpeedlimitData
from rad_class.RadiusAttrsData import RadiusAttrsData
from rad_class.SubAccountsData import SubAccountsData
from core_cache import TimePeriodAccessCache as PeriodCache
from core_class.TimePeriodNodeData import TimePeriodNodeData
from rad_class.IpPoolData import IpPoolData
from common.AddonServiceData import AddonServiceData
#from common.AddonServiceTarifData import AddonServiceTarifData
from common.AccountAddonServiceData import AccountAddonServiceData

from core_cache import AddonServiceCache, AddonServiceTarifCache, AccessParametersCache

class RadAuthCaches(CacheCollection):
    __slots__ = ('account_cache', 'period_cache', 'nas_cache', 'defspeed_cache', 'speed_cache', 'speedlimit_cache', 'radattrs_cache', 'addonservice_cache', 'accountaddonservice_cache', 'subaccount_cache','ippool_cache', 'switch_cache', 'timeperiodnode_cache')
    
    def __init__(self, date, fMem, crypt_key):
        super(RadAuthCaches, self).__init__(date)
        self.account_cache = AccountCache(date)
        self.period_cache  = PeriodCache(date, fMem)
        self.nas_cache = NasCache()
        self.defspeed_cache = DefaultSpeedCache()
        self.speed_cache = SpeedCache()
        self.speedlimit_cache = SpeedlimitCache()
        self.radattrs_cache = RadiusAttrsCache()
        self.addonservice_cache = AddonServiceCache()
        self.accountaddonservice_cache = AccountAddonServiceCache()
        self.subaccount_cache = SubAccountsCache(crypt_key)
        self.ippool_cache = IpPoolCache()
        self.switch_cache = SwitchCache()
        self.timeperiodnode_cache = TimePeriodNodeCache()
        self.caches = [self.account_cache, self.period_cache, self.nas_cache, self.defspeed_cache, self.speed_cache, self.speedlimit_cache, self.radattrs_cache, self.addonservice_cache, self.accountaddonservice_cache, self.subaccount_cache, self.ippool_cache, self.switch_cache, self.timeperiodnode_cache]


class AccountCache(CacheItem):
    __slots__ = ('by_username', 'by_ipn_mac', 'by_ipn_ip_nas', 'by_id')
    
    datatype = AccountData
    sql = rad_sql['accounts']
    
    def __init__(self, date):
        super(AccountCache, self).__init__()
        self.vars = (date, )

    def reindex(self):
        self.by_username = {}
        self.by_ipn_mac  = {}
        self.by_ipn_ip_nas = {}
        self.by_id = {}

        for acct in self.data:
            self.by_username[acct.username] = acct
            self.by_id[acct.account_id] = acct

class DefaultSpeedCache(SimpleDictCache):
    '''By tarif id'''
    __slots__ = ()
    datatype = DefaultSpeedData
    sql = rad_sql['defspeed']
    num = 11

class SpeedCache(SimpleDefDictCache):
    '''by tarif_id'''
    __slots__ = ()
    datatype = SpeedData
    sql = rad_sql['speed']
    num = 14 

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
            
            if not self.by_ip_n_identify.get((str(nas.ipaddress), str(nas.identify))):
                self.by_ip_n_identify[(str(nas.ipaddress), str(nas.identify))] = []
            self.by_ip_n_identify[(str(nas.ipaddress), str(nas.identify))].append(nas)
            
            if not self.by_ip.get(str(nas.ipaddress)):
                self.by_ip[str(nas.ipaddress)] = []
            self.by_ip[str(nas.ipaddress)].append(nas)
            
            self.by_id[nas.id] = nas
            
class RadiusAttrsCache(CacheItem):
    '''by tarif_id'''
    __slots__ = ('by_tarif_id','by_nas_id')
    datatype = RadiusAttrsData
    sql = rad_sql['attrs']

    def reindex(self):
        self.by_tarif_id={}
        self.by_nas_id={}
        for item in self.data:
            if item.tarif_id:
                if item.tarif_id not in self.by_tarif_id:
                    self.by_tarif_id[item.tarif_id]=[]
                self.by_tarif_id[item.tarif_id].append(item)
            if item.nas_id:
                if item.tarif_id not in self.by_tarif_id:
                    self.by_nas_id[item.nas_id]=[]
                self.by_nas_id[item.nas_id].append(item)


class AddonServiceCache(SimpleDictCache):
    '''By id'''
    __slots__ = ()
    datatype = AddonServiceData
    sql = core_sql['addon_service']
    
class SwitchCache(CacheItem):
    '''By id'''
    __slots__ = ('by_remote_id','by_id')
    datatype = SwitchData
    sql = rad_sql['switch']

    def __init__(self):
        super(SwitchCache, self).__init__()
        self.by_remote_id = {}
        self.by_id = {}
        
    def reindex(self):

        for switch in self.data:
            self.by_id[switch.id]=switch
            if switch.remote_id:
                self.by_remote_id[switch.remote_id]=switch
            
class IpPoolCache(SimpleDictCache):
    '''By id'''
    __slots__ = ()
    datatype = IpPoolData
    sql = rad_sql['ippool']
    
        
class AccountAddonServiceCache(CacheItem):
    __slots__ = ('by_id', 'by_account', 'by_subaccount', 'by_service')
    
    datatype = AccountAddonServiceData
    sql = core_sql['addon_account']
    
    def __init__(self):
        super(AccountAddonServiceCache, self).__init__()
        self.by_id = {}
        self.by_service = defaultdict(list)
        #index on tariff_id
        self.by_account = defaultdict(list)
        self.by_subaccount = defaultdict(list)
        
    def reindex(self):
        self.by_id.clear()
        #index on accounttarif.id
        self.by_service.clear()
        #index on tariff_id
        self.by_account.clear()
        self.by_subaccount.clear()
        for addon in self.data:
            self.by_id[addon.id]  = addon
            if addon.account_id:
                self.by_account[addon.account_id].append(addon)
            if addon.subaccount_id:
                self.by_subaccount[addon.subaccount_id].append(addon)
            self.by_service[addon.service_id].append(addon)
            
            
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
                
            
    
class TimePeriodNodeCache(SimpleDefDictCache):
    '''By timeperiod_id'''
    __slots__ = ()
    datatype = TimePeriodNodeData
    sql = core_sql['timepnode']
    num = 5
    
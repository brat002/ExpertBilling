from operator import itemgetter, setitem
from cacheutils import CacheCollection, CacheItem, SimpleDefDictCache, SimpleDictCache
from cache_sql import core_sql, rad_sql
from collections import defaultdict

from core_class.AccountData import AccountData
from core_class.TrafficTransmitSData import TrafficTransmitSData
from core_class.SettlementPeriodData import SettlementPeriodData
from core_class.NasData import NasData
from core_class.AccessParametersDefault import AccessParametersDefault
from core_class.SpeedParameters import SpeedParameters
from core_class.PeriodicalServiceSettlementData import PeriodicalServiceSettlementData
from core_class.TimeAccessNodeData import TimeAccessNodeData
from core_class.TimePeriodNodeData import TimePeriodNodeData
from core_class.TrafficLimitData import TrafficLimitData
from core_class.ShedulelogData import ShedulelogData
from core_class.TimeAccessServiceData import TimeAccessServiceData
from core_class.OneTimeServiceData import OneTimeServiceData
from core_class.AccessParametersData import AccessParametersData
from core_class.IpnSpeedData import IpnSpeedData
from core_class.SuspendedPeriodData import SuspendedPeriodData
from core_class.RadiusTrafficTransmitSData import RadiusTrafficTransmitSData
from core_class.RadiusTrafficNodeData import RadiusTrafficNodeData
from common.AddonServiceData import AddonServiceData
from common.AddonServiceTarifData import AddonServiceTarifData
from common.AccountAddonServiceData import AccountAddonServiceData
from core_class.AddonPeriodicalData import AddonPeriodicalData
from core_class.SubAccountData import SubAccountData

class CoreCaches(CacheCollection):
    __slots__ = () + ('account_cache','traffictransmitservice_cache','settlementperiod_cache','nas_cache','defspeed_cache','speed_cache','periodicaltarif_cache','periodicalsettlement_cache','timeaccessnode_cache','timeperiodnode_cache','trafficlimit_cache','shedulelog_cache','timeaccessservice_cache','onetimeservice_cache','accessparameters_cache','ipnspeed_cache','onetimehistory_cache','suspended_cache','timeperiodaccess_cache', 'speedlimit_cache',  'addonservice_cache', 'addontarifservice_cache', 'accountaddonservice_cache', 'addonperiodical_cache', 'subaccount_cache', 'radius_traffic_transmit_service_cache', 'radius_traffic_node_cache')
    
    def __init__(self, date, fMem, crypt_key=''):
        super(CoreCaches, self).__init__(date)
        self.account_cache = AccountCache(date, crypt_key)
        self.traffictransmitservice_cache = TrafficTransmitServiceCache()
        self.settlementperiod_cache = SettlementPeriodCache()
        self.nas_cache = NasCache()
        self.defspeed_cache = DefSpeedParametersCache()
        self.speed_cache = SpeedParametersCache()
        self.periodicaltarif_cache = PeriodicalTarifCache()
        self.periodicalsettlement_cache = PeriodicalServiceSettlementCache(date)
        self.timeaccessnode_cache = TimeAccessNodeCache()
        self.timeperiodnode_cache = TimePeriodNodeCache()
        self.trafficlimit_cache = TrafficLimitCache()
        self.shedulelog_cache = ShedulelogCache()
        self.timeaccessservice_cache = TimeAccessServiceCache()
        self.onetimeservice_cache = OneTimeServiceCache()
        self.accessparameters_cache = AccessParametersCache()
        self.ipnspeed_cache = IpnSpeedCache()
        self.onetimehistory_cache = OnetimeHistoryCache(date)
        self.suspended_cache = SuspendedCache(date)
        self.timeperiodaccess_cache = TimePeriodAccessCache(date, fMem)
        self.speedlimit_cache = SpeedLimitCache()
        self.addonservice_cache = AddonServiceCache()
        self.addontarifservice_cache = AddonServiceTarifCache()
        self.accountaddonservice_cache = AccountAddonServiceCache()
        self.addonperiodical_cache = AddonPeriodicalCache()
        self.subaccount_cache = SubAccountsCache(crypt_key)
        self.radius_traffic_transmit_service_cache = RadiusTrafficTransmitServiceCache()
        self.radius_traffic_node_cache = RadiusTrafficNodeCache()
        self.caches = [self.account_cache, self.traffictransmitservice_cache, self.settlementperiod_cache, self.nas_cache, self.defspeed_cache, self.speed_cache, self.periodicaltarif_cache, self.periodicalsettlement_cache, self.timeaccessnode_cache, self.timeperiodnode_cache, self.trafficlimit_cache, self.shedulelog_cache, self.timeaccessservice_cache, self.onetimeservice_cache, self.accessparameters_cache, self.ipnspeed_cache, self.onetimehistory_cache, self.suspended_cache, self.timeperiodaccess_cache, self.speedlimit_cache,  self.addonservice_cache, self.addontarifservice_cache, self.accountaddonservice_cache, self.addonperiodical_cache, self.subaccount_cache, self.radius_traffic_transmit_service_cache, self.radius_traffic_node_cache]
        
        
class AccountCache(CacheItem):
    __slots__ = ('by_account', 'by_tarif', 'by_acctf', 'crypt_key')
    
    datatype = AccountData
    sql = core_sql['accounts']
    
    def __init__(self, date, crypt_key):
        super(AccountCache, self).__init__()
        self.vars = (crypt_key, date,)
        
        self.by_account = {}
        #index on accounttarif.id
        self.by_acctf = {}
        #index on tariff_id
        self.by_tarif = defaultdict(list)
        
    def reindex(self):
        self.by_account.clear()
        #index on accounttarif.id
        self.by_acctf.clear()
        #index on tariff_id
        self.by_tarif.clear()
        for acct in self.data:
            self.by_account[acct.account_id]  = acct
            if acct[4]:
                self.by_tarif[acct.tarif_id].append(acct)
            if acct[12]:
                self.by_acctf[acct.acctf_id] = acct
                
class TrafficTransmitServiceCache(SimpleDictCache):
    __slots__ = ()
    datatype = TrafficTransmitSData
    sql = core_sql['traftrss']
    num = 0

class RadiusTrafficTransmitServiceCache(CacheItem):
    __slots__ = ('by_id',)
    datatype = RadiusTrafficTransmitSData
    sql = core_sql['radiustraftrss']
    def __init__(self):
        super(RadiusTrafficTransmitServiceCache, self).__init__()
        self.by_id = {}
    #def transformdata(self): pass
    def reindex(self):
        for item in self.data:
            self.by_id[item.id] = item
        
class RadiusTrafficNodeCache(SimpleDefDictCache): 
    __slots__ = ()
    sql = core_sql['radiustrafnodes']
    datatype = RadiusTrafficNodeData
    num=0

               
class SettlementPeriodCache(SimpleDictCache):
    __slots__ = ()
    datatype = SettlementPeriodData
    sql = core_sql['settlper']
    num = 0
    
class NasCache(CacheItem):
    __slots__ = ('by_id','by_ip')
    datatype = NasData
    sql = core_sql['nas']
    def reindex(self):
        self.by_id = {}
        self.by_ip = {}
        for nas in self.data:
            self.by_id[nas[0]] = nas
            self.by_ip[str(nas.ipaddress)] = nas
            
class DefSpeedParametersCache(SimpleDictCache):
    '''By tarif id'''
    __slots__ = ()
    datatype = AccessParametersDefault
    sql = core_sql['defsp']
    num = 11

class SpeedParametersCache(SimpleDefDictCache):
    __slots__ = ()
    datatype = SpeedParameters
    sql = core_sql['newsp']
    num = 14

class PeriodicalTarifCache(CacheItem):
    __slots__ = ()
    datatype = tuple
    sql = core_sql['periodtf']
    def transformdata(self): pass
    
class PeriodicalServiceSettlementCache(SimpleDefDictCache):
    '''By tarif id'''
    __slots__ = ()
    datatype = PeriodicalServiceSettlementData
    sql = core_sql['periodset']
    num = 9
    def __init__(self, date):
        super(PeriodicalServiceSettlementCache, self).__init__()
        self.vars = (date,)
            
class TimeAccessNodeCache(SimpleDefDictCache):
    '''By time access service id'''
    __slots__ = ()
    datatype = TimeAccessNodeData
    sql = core_sql['timeaccnode']
    num = 2
    
class TimePeriodNodeCache(SimpleDefDictCache):
    '''By timeperiod_id'''
    __slots__ = ()
    datatype = TimePeriodNodeData
    sql = core_sql['timepnode']
    num = 5
    
class TrafficLimitCache(SimpleDefDictCache):
    '''By tarif id'''
    __slots__ = ()
    datatype = TrafficLimitData
    sql = core_sql['tlimits']
    num = 1
    
class ShedulelogCache(SimpleDictCache):
    '''By account_id'''
    __slots__ = ()
    datatype = ShedulelogData
    sql = core_sql['shllog']
    num = 1
    
class TimeAccessServiceCache(SimpleDictCache):
    '''By id'''
    __slots__ = ()
    datatype = TimeAccessServiceData
    sql = core_sql['timeaccs']
    num = 0

   

class OneTimeServiceCache(SimpleDefDictCache):
    '''By tarif id'''
    __slots__ = ()
    datatype = OneTimeServiceData
    sql = core_sql['onetimes']
    num = 1
    
class AccessParametersCache(SimpleDictCache):
    '''By id'''
    __slots__ = ()
    datatype = AccessParametersData
    sql = core_sql['accpars']
    
class IpnSpeedCache(SimpleDictCache):
    '''By account id'''
    __slots__ = ()
    datatype = IpnSpeedData
    sql = core_sql['ipnspeed']
    num = 1
    
class OnetimeHistoryCache(CacheItem):
    __slots__ = ('by_acctf_ots_id',)
    datatype = dict
    sql = core_sql['otshist']
    def __init__(self, date):
        super(OnetimeHistoryCache, self).__init__()
        self.vars = (date,)
    def transformdata(self): pass
    def reindex(self):
        self.by_acctf_ots_id = {}
        for otsh in self.data:
            self.by_acctf_ots_id[(otsh[1], otsh[2])] = otsh[0]
            
class SuspendedCache(SimpleDefDictCache):
    __slots__ = ('by_account_id',)
    datatype = SuspendedPeriodData
    sql = core_sql['suspended']
    num = 1
    
    def __init__(self, date):
        super(SuspendedCache, self).__init__()
        self.vars = (date,date,)
    '''
    def transformdata(self): pass
    '''
    
    def reindex(self):
        self.by_account_id = {}
        for susp in self.data:
            if not self.by_account_id.get(susp.account_id):
                self.by_account_id[susp.account_id] = []
            self.by_account_id[susp.account_id].append(susp)
            
class TimePeriodAccessCache(CacheItem):
    __slots__ = ('in_period', 'fMem', 'date')
    datatype = dict
    sql = core_sql['tpnaccess']
    def __init__(self, date, fMem):
        super(TimePeriodAccessCache, self).__init__()
        self.date = date
        self.vars = (date,)
        self.fMem = fMem
        
    def transformdata(self): pass
    def reindex(self):
        self.in_period = defaultdict(lambda: False)
        for tpnap in self.data:
            self.in_period[tpnap[3]] = self.in_period[tpnap[3]] or self.fMem.in_period_(tpnap[0], tpnap[1], tpnap[2], self.date)[3]
            
class SpeedLimitCache(CacheItem):
    __slots__ = ('by_account_id',)
    datatype = dict
    sql = core_sql['speed_lmt']
    
    def transformdata(self): pass
    
    def reindex(self):
        self.by_account_id = {}
        for speed_l in self.data:
            self.by_account_id[speed_l[1]] = speed_l[2:]
            

                
class AddonServiceCache(SimpleDictCache):
    '''By id'''
    __slots__ = ()
    datatype = AddonServiceData
    sql = core_sql['addon_service']

class AddonServiceTarifCache(CacheItem):
    __slots__ = ('by_id', 'by_tarif', 'by_service')
    
    datatype = AddonServiceTarifData
    sql = core_sql['addon_tarif']
    
    def __init__(self):
        super(AddonServiceTarifCache, self).__init__()
        self.by_id = {}
        self.by_service = defaultdict(list)
        #index on tariff_id
        self.by_tarif = defaultdict(list)
        
    def reindex(self):
        self.by_id.clear()
        #index on accounttarif.id
        self.by_service.clear()
        #index on tariff_id
        self.by_tarif.clear()
        for addon in self.data:
            self.by_id[addon.id]  = addon
            self.by_tarif[addon.tarif_id].append(addon)
            self.by_service[addon.service_id].append(addon)
            
class AccountAddonServiceCache(CacheItem):
    __slots__ = ('by_id', 'by_subaccount', 'by_account', 'by_service')
    
    datatype = AccountAddonServiceData
    sql = core_sql['addon_account']
    
    def __init__(self):
        super(AccountAddonServiceCache, self).__init__()
        self.by_id = {}
        self.by_service = defaultdict(list)
        #index on tariff_id
        self.by_account = defaultdict(list)
        self.by_subaccount =  defaultdict(list)
        
    def reindex(self):
        self.by_id.clear()
        #index on accounttarif.id
        self.by_service.clear()
        #index on tariff_id
        self.by_account.clear()
        self.by_subaccount.clear()
        for addon in self.data:
            self.by_id[addon.id]  = addon
            self.by_account[addon.account_id].append(addon)
            self.by_subaccount[addon.subaccount_id].append(addon)
            self.by_service[addon.service_id].append(addon)
            
class AddonPeriodicalCache(CacheItem):
    __slots__ = ()
    datatype = AddonPeriodicalData
    sql = core_sql['addon_periodical']
    
class SubAccountsCache(CacheItem):
    __slots__ = ('by_account_id', 'by_username', 'by_mac', 'by_ipn_ip', 'by_vpn_ip', 'by_id')
    
    datatype = SubAccountData
    sql = core_sql['subaccounts']
    
    def __init__(self, crypt_key):
        
        super(SubAccountsCache, self).__init__()
        self.vars = (crypt_key,)
        
    def reindex(self):
        self.by_account_id = {}
        self.by_username = {}
        self.by_mac = {}
        self.by_ipn_ip = {}
        self.by_vpn_ip = {}
        self.by_id = {}
        
        for item in self.data:
            if not self.by_account_id.get(item.account_id):
                self.by_account_id[item.account_id]=[]
            self.by_account_id[item.account_id].append(item)
            self.by_id[item.id] = item
            #if item.username:
            #    self.by_username[item.username] = item
            #if item.ipn_mac_address:
            #    self.by_mac[item.ipn_mac_address] = item
            #if item.ipn_ip_address and item.ipn_ip_address is not "0.0.0.0" :
            #    self.by_ipn_ip[item.ipn_ip_address] = item
            #if item.vpn_ip_address and item.vpn_ip_address is not "0.0.0.0" :
            #    self.by_vpn_ip[item.vpn_ip_address] = item

            
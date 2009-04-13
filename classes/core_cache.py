from operator import itemgetter, setitem
from cacheutils import CacheCollection, CacheItem, SimpleDefDictCache, SimpleDictCache
from cache_sql import core_sql

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

class CoreCaches(CacheCollection):
    __slots__ = ()
    
    def __init__(self, cursor, date, fMem):
        super(CoreCaches, self).__init__(cursor, date)
        self.account_cache = AccountCache(date)
        self.traffictransmitservice_cache = TrafficTransmitServiceCache()
        self.settlementperiod_cache = SettlementPeriodCache()
        self.nas_cache = NasCache()
        self.defspeed_cache = DefSpeedParametersCache()
        self.speed_cache = SpeedParametersCache()
        self.periodicaltarif_cache = PeriodicalTarifCache()
        self.periodicalsettlement_cache = PeriodicalServiceSettlementCache()
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
class AccountCache(CacheItem):
    __slots__ = ('by_account', 'by_tarif', 'by_acctf')
    
    datatype = AccountData
    sql = core_sql['accounts']
    
    def __init__(self, date):
        super(AccountCache, self).__init__()
        self.sql = self.sql % date
        
    def reindex(self):
        self.by_account = {}
        #index on accounttarif.id
        self.by_acctf = {}
        #index on tariff_id
        self.by_tarif = defaultdict(list)
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
    num = 6

class SpeedParametersCache(SimpleDefDictCache):
    __slots__ = ()
    datatype = SpeedParameters
    sql = core_sql['newsp']
    num = 9

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
    datatype = TimeAccessNodeData
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
    __slots__ = ('by_acctf_ots_id')
    datatype = dict
    sql = core_sql['otshist']
    def __init__(self, date):
        super(OnetimeHistoryCache, self).__init__()
        self.sql = self.sql % date
    def transformdata(self): pass
    def reindex(self):
        self.by_acctf_ots_id = {}
        for otsh in self.data:
            self.by_acctf_ots_id[(otsh[1], otsh[2])] = otsh[0]
class SuspendedCache(CacheItem):
    __slots__ = ('by_account_id')
    datatype = dict
    sql = core_sql['suspended']
    def __init__(self, date):
        super(SuspendedCache, self).__init__()
        self.sql = self.sql % date
    def transformdata(self): pass
    def reindex(self):
        self.by_account_id = {}
        for susp in self.data:
            self.by_account_id[susp[1]] = susp[0]
            
class TimePeriodAccessCache(CacheItem):
    __slots__ = ('in_period', 'fMem', 'date')
    datatype = dict
    sql = core_sql['tpnaccess']
    def __init__(self, date, fMem):
        super(SuspendedCache, self).__init__()
        self.date = date
        self.sql = self.sql % date
        self.fMem = fMem
        
    def transformdata(self): pass
    def reindex(self):
        self.in_period = defaultdict(lambda: False)
        for tpnap in tpnapsTp:
            self.in_period[tpnap[3]] = self.in_period[tpnap[3]] or self.fMem.in_period_(tpnap[0], tpnap[1], tpnap[2], self.date)[3]
                    
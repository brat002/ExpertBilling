import datetime
from operator import itemgetter, setitem
from cacheutils import CacheCollection, CacheItem, SimpleDefDictCache, SimpleDictCache
from cache_sql import nfroutine_sql
from cache_sql import nf_sql

from collections import defaultdict
from threading import Lock
from nfroutine_class.AccountData import AccountData
from nfroutine_class.TrafficTransmitServiceData import TrafficTransmitServiceData
from nfroutine_class.SettlementData import SettlementData
from nfroutine_class.NodesData import NodesData
from nfroutine_class.AccountGroupBytesData import AccountGroupBytesData
from nfroutine_class.TarifGroupEdgeData import TarifGroupEdgeData
from nfroutine_class.GroupBytesDictData import GroupBytesDictData
from nfroutine_class.AccountTariffTraffServiceData import AccountTariffTraffServiceData
from nf_class.GroupsData import GroupsData

from decimal import Decimal

class NfroutineCaches(CacheCollection):
    __slots__ = ('account_cache', 'period_cache', 'nodes_cache', 'settlement_cache', \
                 'traffictransmit_cache', 'prepays_cache', 'storeclass_cache', 'tarifedge_cache', 
                 'accountbytes_cache', 'accounttariff_traf_service_cache', 'group_cache')
    
    def __init__(self, date, fMem, first_time):
        super(NfroutineCaches, self).__init__(date)
        self.account_cache = AccountCache(date)
        self.period_cache  = PeriodCache(date, fMem)
        self.prepays_cache = PrepaysCache(date)
        self.nodes_cache   = NodesCache()
        self.settlement_cache = SettlementCache()
        self.traffictransmit_cache = TrafficTransmitServiceCache()
        self.storeclass_cache = StoreClassCache()
        self.tarifedge_cache = TarifGroupEdgeCache()
        self.accounttariff_traf_service_cache=AccountTariffTraffServiceCache()
        self.group_cache = GroupsCache()
        
        if not first_time:                
            self.caches = [self.account_cache, self.period_cache, self.prepays_cache, \
                           self.nodes_cache, self.settlement_cache, self.traffictransmit_cache, \
                           self.storeclass_cache, self.tarifedge_cache, 
                           self.accounttariff_traf_service_cache, self.group_cache]
        else:
            self.accountbytes_cache = AccountGroupBytesCache(date)
            self.caches = [self.account_cache, self.period_cache, self.prepays_cache, \
                           self.nodes_cache, self.settlement_cache, self.traffictransmit_cache, \
                           self.storeclass_cache, self.tarifedge_cache, self.accountbytes_cache, 
                           self.accounttariff_traf_service_cache, self.group_cache]

class AccountCache(CacheItem):
    __slots__ = ('by_account',)
    
    datatype = AccountData
    sql = nfroutine_sql['accounts']

    def __init__(self, date):
        super(AccountCache, self).__init__()
        self.vars = (date,)
        
    def reindex(self):
        self.by_account = {}
        for acct in self.data:
            self.by_account[acct.account_id]  = acct

class AccountTariffTraffServiceCache(CacheItem):
    __slots__ = ('by_accounttariff',)
    
    def __init__(self):
        super(AccountTariffTraffServiceCache, self).__init__()
        
    datatype = AccountTariffTraffServiceData
    sql = nfroutine_sql['accounttariffs']

    def reindex(self):
        self.by_accounttariff = {}
        for item in self.data:
            self.by_accounttariff[item.id]  = item
            
class PeriodCache(CacheItem):
    __slots__ = ('in_period', 'fMem', 'date')
    datatype = lambda: defaultdict(lambda: False)
    sql = nfroutine_sql['period']
    
    def __init__(self, date, fMem):
        super(PeriodCache, self).__init__()
        self.date = date
        self.vars = (date,)
        self.fMem = fMem
        
    def transformdata(self): pass
    def reindex(self):
        self.in_period = defaultdict(lambda: False)
        for tpnap in self.data:
            self.in_period[tpnap[3]] = self.in_period[tpnap[3]] or \
                                       self.fMem.in_period_(tpnap[0], tpnap[1], tpnap[2], self.date)[3]
            
class PrepaysCache(CacheItem):
    '''(id, size) by (traffic_transmit_service_id, account_tarif_id, group_id) key'''
    __slots__ = ('by_tts_acctf_group',)
    datatype = dict
    sql = nfroutine_sql['prepays']
    
    def __init__(self, date):
        super(PrepaysCache, self).__init__()
        self.vars = (date,)
    
    def transformdata(self): pass
    
    def reindex(self):
        self.by_tts_acctf_group = {}
        for prep in self.data:
            self.by_tts_acctf_group[(prep[4],prep[2],prep[3])] = [prep[0], prep[1]]
        
class NodesCache(CacheItem):
    '''Traffictransmit- and timeperiod- nodes data by (traffic_transmit_service_id, group_id)'''
    __slots__ = ('by_tts_group', 'by_tts_group_edge')
    datatype = NodesData
    sql = nfroutine_sql['nodes']
    
    def reindex(self):
        self.by_tts_group = defaultdict(list)
        self.by_tts_group_edge = defaultdict(list)
        for trnode in self.data:
            if trnode.group_id:
                self.by_tts_group[(trnode.traffic_transmit_service_id,trnode.group_id)].append(trnode)
                self.by_tts_group_edge[(trnode.traffic_transmit_service_id,trnode.group_id, trnode.edge_value)].append(trnode)
                
class TrafficTransmitServiceCache(SimpleDictCache):
    __slots__ = ()
    datatype = TrafficTransmitServiceData
    sql = nfroutine_sql['tts']
    num = 0

class SettlementCache(SimpleDictCache):
    __slots__ = ()
    datatype = SettlementData
    sql = nfroutine_sql['settlepd']
    num = 0
    
class StoreClassCache(CacheItem):
    '''A set of classes that must be stored'''
    __slots__ = ('classes',)
    datatype = set
    sql = nfroutine_sql['sclasses']
    
    def transformdata(self): pass
    
    def reindex(self):
        try:
            self.classes = set(self.data[0][0])
        except:
            self.classes = set()
            
class AccountGroupBytesCache(CacheItem):
    __slots__ = ('by_acctf',)
    datatype = AccountGroupBytesData
    sql = nfroutine_sql['group_bytes']
    
    def __init__(self, date):
        super(AccountGroupBytesCache, self).__init__()
        self.vars = (date,date)
        self.by_acctf = {}
        
    def reindex(self):
        self.by_acctf = {}
        for acct in self.data:
            gb_dict = {}
            if acct.group_data != '{}':                
                #.replace(',"', '|').replace(')"', '))').replace(',', ',Decimal(').replace('|', ',')
                acct.group_data = eval(acct.group_data.replace('{', '[').replace('}', ']').replace('"', '').replace('\\', ''))
                for gb_group, gb_bytes in acct.group_data:
                    gb_dict[gb_group] = GroupBytesDictData._make((gb_bytes,))                
            acct.group_data = gb_dict
            acct.lock = Lock()
            acct.last_accessed = datetime.datetime.now()
            self.by_acctf[acct.acctf_id] = acct
            
class TarifGroupEdgeCache(CacheItem):
    __slots__ = ('by_tarif')
    datatype = TarifGroupEdgeData
    sql = nfroutine_sql['tarif_groups']
    
    def reindex(self):
        self.by_tarif = {}
        for tf in self.data:
            #print repr(tf)
            tf.datetime = datetime.datetime.now()
            tf.group_edges = dict(eval(tf.group_edges.replace('{', '[').replace('}', ']').replace('"', '').replace('\\', '')))
            self.by_tarif[tf.tarif_id] = tf
            #print tf
        
        
        
class GroupsCache(CacheItem):
    __slots__ = ('by_id',)
    
    datatype = GroupsData
    sql = nf_sql['groups']
    
    def reindex(self):
        self.by_id = {}
        for item in self.data:
            #assert isinstance(item, self.datatype)
            if not item.id:
                continue
            else:
                self.by_id[item.id] = item
                
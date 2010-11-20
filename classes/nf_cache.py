from operator import itemgetter, setitem
from cacheutils import CacheCollection, CacheItem
from cache_sql import nf_sql
from nf_class.AccountData import AccountData
from nf_class.ClassData import ClassData
from nf_class.GroupsData import GroupsData
from IPy import IP, IPint, parseAddress
from collections import defaultdict


class NfCaches(CacheCollection):
    __slots__ = ('nas_cache', 'account_cache', 'class_cache', 'group_cache', 'tfgroup_cache')
    
    def __init__(self, date):
        super(NfCaches, self).__init__(date)
        self.nas_cache = NasCache()
        self.account_cache = AccountCache(date)
        self.class_cache = ClassCache()
        self.group_cache = GroupsCache()
        self.tfgroup_cache = TarifCache(self.group_cache)
        self.caches = [self.nas_cache, self.account_cache, self.class_cache, self.group_cache, self.tfgroup_cache]
    
class NasCache(CacheItem):
    '''Cache id -> nas.ip'''
    __slots__ = ('ip_id',)
    
    datatype = dict
    sql = nf_sql['nas']
    
    def transformdata(self):
        pass
    
    def reindex(self):
        self.ip_id = self.datatype(self.data)
    
class AccountCache(CacheItem):
    __slots__ = ('vpn_ips', 'ipn_ips', 'ipn_range')
    
    datatype = AccountData
    sql = nf_sql['accounts']
    
    def __init__(self, date):
        super(AccountCache, self).__init__()
        
        self.vars = (date,)
        self.vpn_ips = {}
        self.ipn_ips = {}
        self.ipn_range = []
        
        
    def transformdata(self):
        pass
    
    def reindex(self):
        self.vpn_ips = {}
        self.ipn_ips = {}
        self.ipn_range = []
        for acct in self.data:
            vpn_ip, ipn_ip = acct[1:3]
            account_object = self.datatype._make((acct[0], acct[3], acct[4], acct[5]))
            if vpn_ip != '0.0.0.0':
                self.vpn_ips[(parseAddress(vpn_ip)[0], account_object.nas_id)] = account_object
            if ipn_ip != '0.0.0.0':
                if ipn_ip.find('/') != -1:
                    range_ip = IPint(ipn_ip)
                    self.ipn_range.append((range_ip.int(), range_ip.netmask(), account_object))
                else:
                    self.ipn_ips[(parseAddress(ipn_ip)[0], account_object.nas_id)] = account_object
            
class ClassCache(CacheItem):
    __slots__ = ('classes',)
    datatype = ClassData
    sql = nf_sql['nnodes']
    
    def transformdata(self): pass
    
    def reindex(self):
        self.classes = [[0, []]]
        if not self.data:
            return
        tc_id = self.data[0][1]
        for nnode in self.data:
            if nnode[1] != tc_id:
                self.classes.append([0, []])
            nclTmp = self.classes[-1]
            nclTmp[0] = nnode[1]
            tc_id = nnode[1]
            nlist = list(nnode)
            n_hp = parseAddress(nlist.pop())[0]
            d_ip = IPint(nlist.pop())
            s_ip = IPint(nlist.pop())
            nlist.append(n_hp)
            nlist.append(d_ip.netmask())
            nlist.append(d_ip.int())
            nlist.append(s_ip.netmask())
            nlist.append(s_ip.int())
            nlist.reverse()
            nclTmp[1].append(self.datatype._make(nlist))
            
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
                
class TarifCache(CacheItem):
    '''Groups by tarif'''
    __slots__ = ('by_tarif','groupsCache')
    
    datatype = GroupsData
    sql = nf_sql['tgroups']
    
    def __init__(self, groupscache):
        super(TarifCache, self).__init__()
        self.groupsCache = groupscache
        
    def transformdata(self): pass
    
    def reindex(self):
        self.by_tarif = defaultdict(list)
        for tarif_id, groups__ in self.data:
            for grp in set(groups__):
                self.by_tarif[tarif_id].append(self.groupsCache.by_id.get(grp, GroupsData._make([-1,[], None, None])))
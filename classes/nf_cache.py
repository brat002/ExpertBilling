#-*- coding:utf-8 -*-

from operator import itemgetter, setitem
from cacheutils import CacheCollection, CacheItem
from cache_sql import nf_sql
from nf_class.AccountData import AccountData
from nf_class.ClassData import ClassData
from nf_class.GroupsData import GroupsData
from nf_class.NasData import NasData
from nf_class.NasPortData import NasPortData
from IPy import IP, IPint, parseAddress
from collections import defaultdict



class NfCaches(CacheCollection):
    __slots__ = ('nas_cache', 'account_cache', 'class_cache', 'group_cache', 'tfgroup_cache', 'nas_port_cache')
    
    def __init__(self, date):
        super(NfCaches, self).__init__(date)
        self.nas_cache = NasCache()
        self.account_cache = AccountCache(date)
        self.class_cache = ClassCache()
        self.group_cache = GroupsCache()
        self.tfgroup_cache = TarifCache(self.group_cache)
        self.nas_port_cache = NasPortCache()
        self.caches = [self.nas_cache, self.account_cache, self.class_cache, self.group_cache, self.tfgroup_cache, self.nas_port_cache]
    
class NasCache(CacheItem):
    '''Cache id -> nas.ip'''
    __slots__ = ('by_ip',)
    
    datatype = NasData
    sql = nf_sql['nas']
    
    def __init__(self):
        super(NasCache, self).__init__()
        self.by_ip = {}

    
    def reindex(self):
        #self.ip_id = self.datatype(self.data)

        for item in self.data:
            #print item
            #assert isinstance(item, self.datatype)

            #Если такого адреса ещё нету в кэше
            if not self.by_ip.get(item.ipaddress):
                self.by_ip[item.ipaddress] = []
            self.by_ip[item.ipaddress].append(item)
         
class NasPortCache(CacheItem):
    __slots__ = ('by_nas_id',)
    
    datatype = NasPortData
    sql = nf_sql['nas_port']
    
    def __init__(self):
        super(NasPortCache, self).__init__()
        self.by_nas_id = {}

    
    def reindex(self):
        #self.ip_id = self.datatype(self.data)

        for item in self.data:
            #print item
            #assert isinstance(item, self.datatype)

            #Если такого адреса ещё нету в кэше
            if not self.by_nas_id.get(item.nas_id):
                self.by_nas_id[item.nas_id] = {}
                
            self.by_nas_id.get(item.nas_id)[item.nas_port_id]=item.account_id
            #self.by_ip[item.ipaddress].append(item)
                  
class AccountCache(CacheItem):
    __slots__ = ('by_id', 'vpn_ips', 'ipn_ips', 'ipn_range')
    
    datatype = AccountData
    sql = nf_sql['accounts']
    
    def __init__(self, date):
        super(AccountCache, self).__init__()
        
        self.vars = (date,)
        self.vpn_ips = {}
        self.ipn_ips = {}
        self.ipn_range = []
        self.by_id = {}
        
        
    def transformdata(self):
        pass
    
    def reindex(self):
        self.vpn_ips = {}
        self.ipn_ips = {}
        self.ipn_range = []
        for acct in self.data:
            account_object = self.datatype._make((acct[0], acct[2], acct[3]))
            self.by_id[acct[0]]=account_object
            #print acct[1]
            for addr in acct[1]:
                if not addr: continue
                try:
                    vpn_ip, ipn_ip, nas_id = addr.split("|")
                except:
                    continue
                
                if acct[0]==29:
                    pass
                if type(nas_id)==str and nas_id not in ['None', '', None]:
                    nas_id=int(nas_id)
                if nas_id==0:
                    nas_id = None
                if vpn_ip  not in ['0.0.0.0/32', '0.0.0.0', '']:
                    self.vpn_ips[(parseAddress(vpn_ip.split('/')[0])[0], nas_id)] = account_object
                if ipn_ip not in ['0.0.0.0/32', '0.0.0.0', '']:
                    if ipn_ip.find('/') != -1 and ipn_ip[-3:]!='/32':
                        range_ip = IPint(ipn_ip)
                        self.ipn_range.append((range_ip.int(), range_ip.netmask(), nas_id, account_object))
                    else:
                        self.vpn_ips[(parseAddress(ipn_ip.split('/')[0])[0], nas_id)] = account_object
        pass
        #print self.vpn_ips
        #print self.ipn_ips
        #print self.ipn_range
            
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
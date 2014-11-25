#-*- coding:utf-8 -*-

from operator import itemgetter, setitem
from cacheutils import CacheCollection, CacheItem
from cache_sql import nf_sql
from nf_class.ClassData import ClassData
from nf_class.GroupsData import GroupsData
from nf_class.NasData import NasData
from nf_class.IpData import IpData
from collections import defaultdict
from IPy import parseAddress, IPint


class NfCaches(CacheCollection):
    __slots__ = ('nas_cache','class_cache', 'group_cache', 'tfgroup_cache')
    
    def __init__(self, date):
        super(NfCaches, self).__init__(date)
        self.nas_cache = NasCache()
        self.class_cache = ClassCache()
        self.group_cache = GroupsCache()
        self.tfgroup_cache = TarifCache(self.group_cache)


        self.caches = [self.nas_cache, self.class_cache, self.group_cache, self.tfgroup_cache]
    
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
         

                


                  
            
class ClassCache(CacheItem):
    __slots__ = ('classes', 'nodes', 'd')
    datatype = ClassData
    sql = nf_sql['nnodes']
    
    def transformdata(self): pass
    
    def reindex(self):
        self.classes = [[0, []]]
        if not self.data:
            return
        tc_id = self.data[0][1]
        d = []
        for nnode in self.data:
            if nnode[1] != tc_id:
                self.classes.append([0, []])
            nclTmp = self.classes[-1]
            nclTmp[0] = nnode[2]
            tc_id = nnode[1]
            nlist = list(nnode)
            n_hp = parseAddress(nlist.pop())[0] #next_hop
            d_ip = IPint(nlist.pop())
            s_ip = IPint(nlist.pop())
            nlist.append(n_hp)
            nlist.append(d_ip.netmask())
            nlist.append(d_ip.int())
            nlist.append(s_ip.netmask())
            nlist.append(s_ip.int())
            nlist.reverse()
            nclTmp[1].append(self.datatype._make(nlist))
            'store, weight, traffic_class_id, passthrough, protocol, in_index, out_index, src_as, dst_as, dst_port, src_port, src_ip as src_ip_src_mask, dst_ip as dst_ip_dst_mask, next_hop'
            #print (nnode[2], 1 if nnode[0] else 0, s_ip.int(), s_ip.netmask(), d_ip.int(), d_ip.netmask(), n_hp, nnode[10],  nnode[7], nnode[8], nnode[5], nnode[6], nnode[4])
            d.append((nnode[2], 1 if nnode[0] else 0, s_ip.int(), s_ip.netmask(), d_ip.int(), d_ip.netmask(), n_hp, nnode[10],  nnode[9], nnode[7], nnode[8], nnode[5], nnode[6], nnode[4]))
        
        #self.nodes =  numpy.asarray(d, dtype=numpy.int64)
        #print self.nodes


            
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
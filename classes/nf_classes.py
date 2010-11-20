from operator import itemgetter, setitem
from cacheutils import CacheCollection, CacheItem

class NasCache(dict):
    '''Cache id -> nas.ip'''
    __slots__ = ('ip_id',)
    
class AccountCache(CacheItem):
    pass
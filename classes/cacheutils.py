from operator import itemgetter
from collections import defaultdict
from threading import Lock
from datetime import datetime

class DefaultNamedTuple(tuple):
    __slots__ = () 
    _fields = ()
    def __new__(cls):
        raise TypeError("Class DefaultNamedTuple is for demonstration only!")
    @classmethod
    def _make(cls, iterable):
        raise TypeError("Class DefaultNamedTuple is for demonstration only!")

    
class CacheCollection(object):
    __slots__ = ('date', 'cursor', 'caches', 'post_caches')
    
    def __init__(self, date):
        self.date = date
        #self.cursor = cursor
        self.post_caches = []
        self.caches = []

        
    def getdata(self, cursor):
        for cache in self.caches:
            cache.getdata(cursor)
            
    def reindex(self):
        for cache in self.caches:
            cache.reindex()
            
    def post_getdata(self, cursor):
        for cache in self.post_caches:
            cache.getdata(cursor)
            
    def post_reindex(self):
        for cache in self.post_caches:
            cache.reindex()     
            
    def __repr__(self):
        return self.__class__.__name__ + '\n' + '\n\n'.join((field + ': \n' + repr(getattr(self,field)) for field in self.__slots__))

class CacheItem(object):
    __slots__ = ('data','sql', 'vars')
    
    datatype = tuple

    
    def __init__(self):
        self.data = None
        self.vars = ()
        
    def checkdata(self):
        for field in self.datatype._fields:
            try:
                self.sql.index(field)
            except ValueError, verr:
                raise Exception("%s: Field %s of class %s not found in sql" % (self.__class__.__name__, field, self.datatype.__name__))
    
    def getdata(self, cursor):
        cursor.execute(self.sql, self.vars)
        self.data = cursor.fetchall() 
        self.transformdata()
        
    def transformdata(self):
        
        if not hasattr(self.datatype, '_make'):
            raise AttributeError("%s: datatype has no attribute '_make' => probably not a named tuple or a named list." % self.__class__.__name__)
        
        self.data = [self.datatype._make(row) for row in self.data]
   
        
    
    def reindex(self):
        pass
    def __repr__(self):
        return self.__class__.__name__ + '\n'+ 'self.data:' + repr(self.data)  +'\n\n'+ '\n\n'.join((field + ': \n' + repr(getattr(self,field)) for field in self.__slots__))
    
class SimpleDictCache(CacheItem):
    __slots__ = ('by_id','num')
    num = 0
    def reindex(self):
        self.by_id = {}
        for tpl in self.data: 
            self.by_id[tpl[self.num]] = tpl
            
        
    def __repr__(self):
        return self.__class__.__name__ + '\n'+ 'self.data:' + repr(self.data)  +  '\n\n' +repr(self.by_id)

        
class SimpleDefDictCache(CacheItem):
    __slots__ = ('by_id','num')
    num = 0
    def reindex(self):
        self.by_id = defaultdict(list)
        for tpl in self.data: self.by_id[tpl[self.num]].append(tpl)
        
    def __repr__(self):
        return self.__class__.__name__ + '\n'+ 'self.data:' + repr(self.data)  +  '\n\n' + repr(self.by_id)
    
class CacheMaster(object):
    __slots__ = ('date', 'lock', 'cache', 'read', 'first_time')
    
    def __init__(self):
        self.date = datetime(1970,1,1)
        self.lock = Lock()
        self.cache = None
        self.read = False
        self.first_time = True
        
    
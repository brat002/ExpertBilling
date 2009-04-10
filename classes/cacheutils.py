from operator import itemgetter


class DefaultNamedTuple(tuple):
    __slots__ = () 
    _fields = ()
    def __new__(cls):
        raise TypeError("Class DefaultNamedTuple is for demonstration only!")
    @classmethod
    def _make(cls, iterable):
        raise TypeError("Class DefaultNamedTuple is for demonstration only!")

    
class CacheCollection(object):
    __slots__ = ('date', 'cursor', 'caches')
    
    def ___init__(self, date, cursor):
        self.date = date
        self.cursor = cursor
        
    def getdata():
        for cache in caches:
            cache.getdata(cursor)
            
    def reindex():
        for cache in caches:
            cache.reindex()

class CacheItem(object):
    __slots__ = ('data',)
    
    datatype = tuple
    sql = ''
    
    def __init__(self):
        self.data = None
        
    def checkdata(self):
        for field in self.datatype._fields:
            try:
                self.sql.index(field)
            except ValueError, verr:
                raise Exception("%s: Field %s of class %s not found in sql" % (self.__class__.__name__, field, self.datatype.__name__))
    
    
    def getdata(self, cursor):
        cursor.execute(self.sql)
        self.data = cursor.fetchall() 
        self.transformdata()
        
    def transformdata(self):
        
        if not hasattr(self.datatype, '_make'):
            raise AttributeError("%s: datatype has no attribute '_make' => probably not a named tuple." % self.__class__.__name__)

        self.data = [self.datatype._make(row) for row in self.data]
        
    
    def reindex(self):
        pass
    
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
    __slots__ = ()

class CacheItem(object):
    __slots__ = ('datatype', 'sql', 'data')
    
    def __init__(self, datatype=DefaultNamedTuple, sql=''):
        self.datatype = datatype
        self.sql = sql
        self.data = None
        if not hasattr(self.datatype, '_fields'):
            raise AttributeError("%s: datatype has no attribute '_fields' => probably not a named tuple." % self.__class__.__name__)
        if not hasattr(self.datatype, '_make'):
            raise AttributeError("%s: datatype has no attribute '_make' => probably not a named tuple." % self.__class__.__name__)

        
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
        self.data = [self.datatype._make(row) for row in self.data]
        
    
    def reindex(self):
        pass
    
from operator import itemgetter, setitem

class IpPoolData(tuple):
    'IpPoolData(id, next_pool_id)' 

    __slots__ = () 

    _fields = ('id', 'next_pool_id') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, next_pool_id):
        return tuple.__new__(cls, (id, next_pool_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new IpPoolData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 2:
            raise TypeError('Expected 2 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'IpPoolData(id=%r, next_pool_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id':t[0], 'next_pool_id':t[1]} 

    def _replace(self, **kwds):
        'Return a new IpPoolData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'next_pool_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 
    
    id = property(itemgetter(0))
    next_pool_id = property(itemgetter(1))

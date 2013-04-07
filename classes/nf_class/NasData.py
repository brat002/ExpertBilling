from operator import itemgetter, setitem

class NasData(list):
    'NasData(id, ipaddress)' 

    __slots__ = () 

    _fields = ('id', 'ipaddress') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __init__(self, empty=True, id=None, ipaddress=None):
        if not empty:
            self.extend((id, ipaddress)) 

                
    @classmethod
    def _make(cls, iterable):
        'Make a new NasData object from a sequence or iterable'
        result = cls()
        result.extend(iterable)
        if len(result) < 2:
            result.extend([None for i in xrange(2 - len(result))])
        return result 

    def __repr__(self):
        try:
            return 'NasData(id=%r, ipaddress=%r)' % tuple(self) 
        except:
            return repr(tuple(self)) 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'ipaddress': t[1]} 

    def _replace(self, **kwds):
        'Return a new GroupsData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'ipaddress'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0), lambda self_, value_: setitem(self_, 0, value_))
    ipaddress = property(itemgetter(1), lambda self_, value_: setitem(self_, 1, value_))

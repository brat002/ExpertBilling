from operator import itemgetter, setitem

class NasData(tuple):
    'NasData(id, secret, type, multilink, ipaddress, identify)' 

    __slots__ = () 

    _fields = ('id', 'secret', 'type', 'multilink', 'ipaddress', 'identify') 

    def __new__(cls, id, secret, type, multilink, ipaddress, identify):
        return tuple.__new__(cls, (id, secret, type, multilink, ipaddress, identify)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new NasData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 6:
            raise TypeError('Expected 6 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'NasData(id=%r, secret=%r, type=%r, multilink=%r, ipaddress=%r, identify=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field identifys to their values'
        return {'id': t[0], 'secret': t[1], 'type': t[2], 'multilink': t[3], 'ipaddress': t[4], 'identify':t[5]} 

    def _replace(self, **kwds):
        'Return a new NasData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'secret', 'type', 'multilink', 'ipaddress', 'identify'), self))
        if kwds:
            raise ValueError('Got unexpected field identifys: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    secret = property(itemgetter(1))
    type = property(itemgetter(2))
    multilink = property(itemgetter(3))
    ipaddress = property(itemgetter(4))
    identify = property(itemgetter(5))

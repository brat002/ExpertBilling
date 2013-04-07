from operator import itemgetter, setitem

class IpnSpeedData(tuple):
    'IpnSpeedData(id, account_id, speed, state, static, datetime)' 

    __slots__ = () 

    _fields = ('id', 'account_id', 'speed', 'state', 'static', 'datetime') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, account_id, speed, state, static, datetime):
        return tuple.__new__(cls, (id, account_id, speed, state, static, datetime)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new IpnSpeedData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 6:
            raise TypeError('Expected 6 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'IpnSpeedData(id=%r, account_id=%r, speed=%r, state=%r, static=%r, datetime=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'account_id': t[1], 'speed': t[2], 'state': t[3], 'static': t[4], 'datetime': t[5]} 

    def _replace(self, **kwds):
        'Return a new IpnSpeedData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'account_id', 'speed', 'state', 'static', 'datetime'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    account_id = property(itemgetter(1))
    speed = property(itemgetter(2))
    state = property(itemgetter(3))
    static = property(itemgetter(4))
    datetime = property(itemgetter(5))

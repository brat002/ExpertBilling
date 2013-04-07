from operator import itemgetter, setitem

class RadiusTrafficNodeData(tuple):
    'RadiusTrafficNodeData(radiustraffic_id, value, timeperiod_id, cost)' 

    __slots__ = () 

    _fields = ('radiustraffic_id', 'value', 'timeperiod_id', 'cost') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, radiustraffic_id, value, timeperiod_id, cost):
        return tuple.__new__(cls, (radiustraffic_id, value, timeperiod_id, cost)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new RadiusTrafficNodeData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 4:
            raise TypeError('Expected 4 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'RadiusTrafficNodeData(radiustraffic_id=%r, value=%r, timeperiod_id=%r, cost=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'radiustraffic_id':t[0], 'value':t[1], 'timeperiod_id':t[2], 'cost':t[3]} 

    def _replace(self, **kwds):
        'Return a new RadiusTrafficNodeData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('radiustraffic_id', 'value', 'timeperiod_id', 'cost'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    radiustraffic_id = property(itemgetter(0))
    value = property(itemgetter(1))
    timeperiod_id = property(itemgetter(2))
    cost = property(itemgetter(3))

from operator import itemgetter, setitem

class TrafficTransmitSData(tuple):
    'TrafficTransmitSData(id, reset_traffic, cash_method, period_check)' 

    __slots__ = () 

    _fields = ('id', 'reset_traffic', 'cash_method', 'period_check') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, reset_traffic, cash_method, period_check):
        return tuple.__new__(cls, (id, reset_traffic, cash_method, period_check)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new TrafficTransmitSData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 4:
            raise TypeError('Expected 4 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'TrafficTransmitSData(id=%r, reset_traffic=%r, cash_method=%r, period_check=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'reset_traffic': t[1], 'cash_method': t[2], 'period_check': t[3]} 

    def _replace(self, **kwds):
        'Return a new TrafficTransmitSData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'reset_traffic', 'cash_method', 'period_check'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    reset_traffic = property(itemgetter(1))
    cash_method = property(itemgetter(2))
    period_check = property(itemgetter(3))

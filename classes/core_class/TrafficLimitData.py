from operator import itemgetter, setitem

class TrafficLimitData(tuple):
    'TrafficLimitData(trafficlimit_id, tarif_id, name, settlement_period_id, size, group_id, mode, action, speedlimit_id)' 

    __slots__ = () 

    _fields = ('trafficlimit_id', 'tarif_id', 'name', 'settlement_period_id', 'size', 'group_id', 'mode', 'action', 'speedlimit_id') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, trafficlimit_id, tarif_id, name, settlement_period_id, size, group_id, mode, action, speedlimit_id):
        return tuple.__new__(cls, (trafficlimit_id, tarif_id, name, settlement_period_id, size, group_id, mode, action, speedlimit_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new TrafficLimitData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 9:
            raise TypeError('Expected 9 arguments, got %d' % len(result))
        return result 
    
    def __repr__(self):
        return 'TrafficLimitData(trafficlimit_id=%r, tarif_id=%r, name=%r, settlement_period_id=%r, size=%r, group_id=%r, mode=%r, action=%r, speedlimit_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'trafficlimit_id': t[0], 'tarif_id': t[1], 'name': t[2], 'settlement_period_id': t[3], 'size': t[4], 'group_id': t[5], 'mode': t[6], 'action': t[7], 'speedlimit_id': t[8], } 

    def _replace(self, **kwds):
        'Return a new TrafficLimitData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('trafficlimit_id', 'tarif_id', 'name', 'settlement_period_id', 'size', 'group_id', 'mode', 'action', 'speedlimit_id',), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    trafficlimit_id = property(itemgetter(0))
    tarif_id = property(itemgetter(1))
    name = property(itemgetter(2))
    settlement_period_id = property(itemgetter(3))
    size = property(itemgetter(4))
    group_id = property(itemgetter(5))
    mode = property(itemgetter(6))
    action = property(itemgetter(7))
    speedlimit_id = property(itemgetter(8))

    

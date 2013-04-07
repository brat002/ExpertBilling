from operator import itemgetter, setitem

class TimeAccessNodeData(tuple):
    'TimeAccessNodeData(time_period_id, cost, time_access_service_id)' 

    __slots__ = () 

    _fields = ('time_period_id', 'cost', 'time_access_service_id') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, time_period_id, cost, time_access_service_id):
        return tuple.__new__(cls, (time_period_id, cost, time_access_service_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new TimeAccessNodeData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 3:
            raise TypeError('Expected 3 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'TimeAccessNodeData(time_period_id=%r, cost=%r, time_access_service_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'time_period_id': t[0], 'cost': t[1], 'time_access_service_id': t[2]} 

    def _replace(self, **kwds):
        'Return a new TimeAccessNodeData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('time_period_id', 'cost', 'time_access_service_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    time_period_id = property(itemgetter(0))
    cost = property(itemgetter(1))
    time_access_service_id = property(itemgetter(2))

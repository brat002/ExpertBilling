from operator import itemgetter, setitem

class DefaultSpeedData(tuple):
    'DefaultSpeedData(max_limit, burst_limit, burst_treshold, burst_time, priority, min_limit, tarif_id)' 

    __slots__ = () 

    _fields = ('max_limit', 'burst_limit', 'burst_treshold', 'burst_time', 'priority', 'min_limit', 'tarif_id') 

    def __new__(cls, max_limit, burst_limit, burst_treshold, burst_time, priority, min_limit, tarif_id):
        return tuple.__new__(cls, (max_limit, burst_limit, burst_treshold, burst_time, priority, min_limit, tarif_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new DefaultSpeedData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 7:
            raise TypeError('Expected 7 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'DefaultSpeedData(max_limit=%r, burst_limit=%r, burst_treshold=%r, burst_time=%r, priority=%r, min_limit=%r, tarif_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'max_limit': t[0], 'burst_limit': t[1], 'burst_treshold': t[2], 'burst_time': t[3], 'priority': t[4], 'min_limit': t[5], 'tarif_id': t[6]} 

    def _replace(self, **kwds):
        'Return a new DefaultSpeedData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('max_limit', 'burst_limit', 'burst_treshold', 'burst_time', 'priority', 'min_limit', 'tarif_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    max_limit = property(itemgetter(0))
    burst_limit = property(itemgetter(1))
    burst_treshold = property(itemgetter(2))
    burst_time = property(itemgetter(3))
    priority = property(itemgetter(4))
    min_limit = property(itemgetter(5))
    tarif_id = property(itemgetter(6))

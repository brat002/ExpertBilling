from operator import itemgetter, setitem

class SpeedData(tuple):
    'SpeedData(max_limit, burst_limit, burst_treshold, burst_time, priority, min_limit, time_start, length, repeat_after, tarif_id)' 

    __slots__ = () 

    _fields = ('max_limit', 'burst_limit', 'burst_treshold', 'burst_time', 'priority', 'min_limit', 'time_start', 'length', 'repeat_after', 'tarif_id') 

    def __new__(cls, max_limit, burst_limit, burst_treshold, burst_time, priority, min_limit, time_start, length, repeat_after, tarif_id):
        return tuple.__new__(cls, (max_limit, burst_limit, burst_treshold, burst_time, priority, min_limit, time_start, length, repeat_after, tarif_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new SpeedData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 10:
            raise TypeError('Expected 10 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'SpeedData(max_limit=%r, burst_limit=%r, burst_treshold=%r, burst_time=%r, priority=%r, min_limit=%r, time_start=%r, length=%r, repeat_after=%r, tarif_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'max_limit': t[0], 'burst_limit': t[1], 'burst_treshold': t[2], 'burst_time': t[3], 'priority': t[4], 'min_limit': t[5], 'time_start': t[6], 'length': t[7], 'repeat_after': t[8], 'tarif_id': t[9]} 

    def _replace(self, **kwds):
        'Return a new SpeedData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('max_limit', 'burst_limit', 'burst_treshold', 'burst_time', 'priority', 'min_limit', 'time_start', 'length', 'repeat_after', 'tarif_id'), self))
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
    time_start = property(itemgetter(6))
    length = property(itemgetter(7))
    repeat_after = property(itemgetter(8))
    tarif_id = property(itemgetter(9))

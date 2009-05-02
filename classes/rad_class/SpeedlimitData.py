from operator import itemgetter, setitem

class SpeedlimitData(tuple):
    'SpeedlimitData(max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx, burst_time_tx, burst_time_rx, priority, min_tx, min_rx, account_id)' 

    __slots__ = () 

    _fields = ('max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx', 'burst_time_tx', 'burst_time_rx', 'priority', 'min_tx', 'min_rx', 'account_id') 

    def __new__(cls, max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx, burst_time_tx, burst_time_rx, priority, min_tx, min_rx, account_id):
        return tuple.__new__(cls, (max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx, burst_time_tx, burst_time_rx, priority, min_tx, min_rx, account_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new SpeedlimitData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 12:
            raise TypeError('Expected 12 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'SpeedlimitData(max_tx=%r, max_rx=%r, burst_tx=%r, burst_rx=%r, burst_treshold_tx=%r, burst_treshold_rx=%r, burst_time_tx=%r, burst_time_rx=%r, priority=%r, min_tx=%r, min_rx=%r, account_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'max_tx': t[0], 'max_rx': t[1], 'burst_tx': t[2], 'burst_rx': t[3], 'burst_treshold_tx': t[4], 'burst_treshold_rx': t[5], 'burst_time_tx': t[6], 'burst_time_rx': t[7], 'priority': t[8], 'min_tx': t[9], 'min_rx': t[10], 'account_id': t[11]} 

    def _replace(self, **kwds):
        'Return a new SpeedlimitData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx', 'burst_time_tx', 'burst_time_rx', 'priority', 'min_tx', 'min_rx', 'account_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    max_tx = property(itemgetter(0))
    max_rx = property(itemgetter(1))
    burst_tx = property(itemgetter(2))
    burst_rx = property(itemgetter(3))
    burst_treshold_tx = property(itemgetter(4))
    burst_treshold_rx = property(itemgetter(5))
    burst_time_tx = property(itemgetter(6))
    burst_time_rx = property(itemgetter(7))
    priority = property(itemgetter(8))
    min_tx = property(itemgetter(9))
    min_rx = property(itemgetter(10))
    account_id = property(itemgetter(11))

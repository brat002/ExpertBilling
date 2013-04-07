from operator import itemgetter, setitem

class SpeedlimitData(tuple):
    'SpeedlimitData(id, account_id, max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx, burst_time_tx, burst_time_rx, priority, min_tx, min_rx, speed_units, change_speed_type)' 

    __slots__ = () 

    _fields = ('id', 'account_id', 'max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx', 'burst_time_tx', 'burst_time_rx', 'priority', 'min_tx', 'min_rx', 'speed_units', 'change_speed_type') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, account_id, max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx, burst_time_tx, burst_time_rx, priority, min_tx, min_rx, speed_units, change_speed_type):
        return tuple.__new__(cls, (id, account_id, max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx, burst_time_tx, burst_time_rx, priority, min_tx, min_rx, speed_units, change_speed_type)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new SpeedlimitData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 15:
            raise TypeError('Expected 15 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'SpeedlimitData(id=%r, account_id=%r, max_tx=%r, max_rx=%r, burst_tx=%r, burst_rx=%r, burst_treshold_tx=%r, burst_treshold_rx=%r, burst_time_tx=%r, burst_time_rx=%r, priority=%r, min_tx=%r, min_rx=%r, speed_units=%r, change_speed_type=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id':t[0], 'account_id': t[1], 'max_tx': t[2], 'max_rx': t[3], 'burst_tx': t[4], 'burst_rx': t[5], 'burst_treshold_tx': t[6], 'burst_treshold_rx': t[7], 'burst_time_tx': t[8], 'burst_time_rx': t[9], 'priority': t[10], 'min_tx': t[11], 'min_rx': t[12], 'speed_units': t[13], 'change_speed_type': t[14]} 

    def _replace(self, **kwds):
        'Return a new SpeedlimitData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'account_id', 'max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx', 'burst_time_tx', 'burst_time_rx', 'priority', 'min_tx', 'min_rx', 'speed_units','change_speed_type'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 
    
    id = property(itemgetter(0))
    account_id = property(itemgetter(1))
    max_tx = property(itemgetter(2))
    max_rx = property(itemgetter(3))
    burst_tx = property(itemgetter(4))
    burst_rx = property(itemgetter(5))
    burst_treshold_tx = property(itemgetter(6))
    burst_treshold_rx = property(itemgetter(7))
    burst_time_tx = property(itemgetter(8))
    burst_time_rx = property(itemgetter(9))
    priority = property(itemgetter(10))
    min_tx = property(itemgetter(11))
    min_rx = property(itemgetter(12))
    speed_units = property(itemgetter(13))
    change_speed_type = property(itemgetter(14))

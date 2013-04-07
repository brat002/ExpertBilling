from operator import itemgetter, setitem

class AccessParametersData(tuple):
    'AccessParametersData(id, access_type, access_time_id, max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx,  burst_time_tx, burst_time_rx, min_tx, min_rx,  priority, ipn_for_vpn)' 

    __slots__ = () 

    _fields = ('id', 'access_type', 'access_time_id', 'max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx',  'burst_time_tx', 'burst_time_rx', 'min_tx', 'min_rx',  'priority', 'ipn_for_vpn') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, access_type, access_time_id, max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx,  burst_time_tx, burst_time_rx, min_tx, min_rx,  priority, ipn_for_vpn):
        return tuple.__new__(cls, (id, access_type, access_time_id, max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx,  burst_time_tx, burst_time_rx, min_tx, min_rx,  priority, ipn_for_vpn)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new AccessParametersData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 15:
            raise TypeError('Expected 15 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'AccessParametersData(id=%r, access_type=%r, access_time_id=%r, max_tx=%r, max_rx=%r, burst_tx=%r, burst_rx=%r, burst_treshold_tx=%r, burst_treshold_rx=%r,  burst_time_tx=%r, burst_time_rx=%r, min_tx=%r, min_rx=%r,  priority=%r, ipn_for_vpn=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'access_type': t[1], 'access_time_id': t[2],'max_tx':t[3], 'max_rx':t[4], 'burst_tx':t[5], 'burst_rx':t[6], 'burst_treshold_tx':t[7], 'burst_treshold_rx':t[8],  'burst_time_tx':t[9], 'burst_time_rx':t[10], 'min_tx':t[11], 'min_rx':t[12], 'priority': t[13], 'ipn_for_vpn': t[14]} 

    def _replace(self, **kwds):
        'Return a new AccessParametersData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'access_type', 'access_time_id', 'max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx',  'burst_time_tx', 'burst_time_rx', 'min_tx', 'min_rx',  'priority', 'ipn_for_vpn'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    access_type = property(itemgetter(1))
    access_time_id = property(itemgetter(2))
    max_tx = property(itemgetter(3))
    max_rx = property(itemgetter(4))
    burst_tx = property(itemgetter(5))
    burst_rx = property(itemgetter(6))
    burst_treshold_tx = property(itemgetter(7))
    burst_treshold_rx = property(itemgetter(8))
    burst_time_tx = property(itemgetter(9))
    burst_time_rx = property(itemgetter(10))
    min_tx = property(itemgetter(11))
    min_rx = property(itemgetter(12))
    priority = property(itemgetter(13))
    ipn_for_vpn = property(itemgetter(14))

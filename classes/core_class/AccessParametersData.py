from operator import itemgetter, setitem

class AccessParametersData(tuple):
    'AccessParametersData(id, access_type, access_time_id, max_limit, min_limit, burst_limit, burst_treshold, burst_time, priority, ipn_for_vpn)' 

    __slots__ = () 

    _fields = ('id', 'access_type', 'access_time_id', 'max_limit', 'min_limit', 'burst_limit', 'burst_treshold', 'burst_time', 'priority', 'ipn_for_vpn') 

    def __new__(cls, id, access_type, access_time_id, max_limit, min_limit, burst_limit, burst_treshold, burst_time, priority, ipn_for_vpn):
        return tuple.__new__(cls, (id, access_type, access_time_id, max_limit, min_limit, burst_limit, burst_treshold, burst_time, priority, ipn_for_vpn)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new AccessParametersData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 10:
            raise TypeError('Expected 10 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'AccessParametersData(id=%r, access_type=%r, access_time_id=%r, max_limit=%r, min_limit=%r, burst_limit=%r, burst_treshold=%r, burst_time=%r, priority=%r, ipn_for_vpn=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'access_type': t[1], 'access_time_id': t[2], 'max_limit': t[3], 'min_limit': t[4], 'burst_limit': t[5], 'burst_treshold': t[6], 'burst_time': t[7], 'priority': t[8], 'ipn_for_vpn': t[9]} 

    def _replace(self, **kwds):
        'Return a new AccessParametersData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'access_type', 'access_time_id', 'max_limit', 'min_limit', 'burst_limit', 'burst_treshold', 'burst_time', 'priority', 'ipn_for_vpn'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    access_type = property(itemgetter(1))
    access_time_id = property(itemgetter(2))
    max_limit = property(itemgetter(3))
    min_limit = property(itemgetter(4))
    burst_limit = property(itemgetter(5))
    burst_treshold = property(itemgetter(6))
    burst_time = property(itemgetter(7))
    priority = property(itemgetter(8))
    ipn_for_vpn = property(itemgetter(9))

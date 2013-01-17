from operator import itemgetter, setitem

class RadiusSession(tuple):
    'RadiusSession(id, account_id, subaccount_id, sessionid, framed_ip_address, speed_string, access_type, nas_id, time_from_last_update, date_start, ipinuse_id, caller_id, guest_pool, nas_port_id)' 

    __slots__ = () 

    _fields = ('id', 'account_id', 'subaccount_id','sessionid', 'framed_ip_address', 'speed_string', 'access_type', 'nas_id', 'time_from_last_update', 'date_start', 'ipinuse_id', 'caller_id', 'guest_pool', 'nas_port_id') 

    def __new__(cls, id, account_id, subaccount_id, sessionid, framed_ip_address, speed_string, access_type, nas_id, time_from_last_update, date_start,ipinuse_id,caller_id,guest_pool, nas_port_id):
        return tuple.__new__(cls, (id, account_id, subaccount_id, sessionid, framed_ip_address, speed_string, access_type, nas_id, time_from_last_update, date_start,ipinuse_id,caller_id,guest_pool, nas_port_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new RadiusSession object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 14:
            raise TypeError('Expected 14 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'RadiusSession(id=%r, account_id=%r, subaccount_id=%r, sessionid=%r, framed_ip_address=%r, speed_string=%r, access_type=%r, nas_id=%r, time_from_last_update=%r, date_start=%r, ipinuse_id=%r, caller_id=%r, guest_pool=%r, nas_port_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'account_id': t[1], 'subaccount_id':t[2], 'sessionid': t[3], 'framed_ip_address':t[4], 'speed_string': t[5], 'access_type': t[6], 'nas_id': t[7], 'time_from_last_update':t[8], 'date_start':t[9], 'ipinuse_id':t[10], 'caller_id':t[11], 'guest_pool':t[12], 'nas_port_id':t[13]} 

    def _replace(self, **kwds):
        'Return a new RadiusSession object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'account_id', 'subaccount_id','sessionid', 'framed_ip_address','speed_string', 'access_type', 'nas_id', 'time_from_last_update', 'date_start', 'ipinuse_id', 'caller_id', 'guest_pool', 'nas_port_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    account_id = property(itemgetter(1))
    subaccount_id = property(itemgetter(2))
    sessionid = property(itemgetter(3))
    framed_ip_address = property(itemgetter(4))
    speed_string = property(itemgetter(5))
    access_type = property(itemgetter(6))
    nas_id = property(itemgetter(7))
    time_from_last_update = property(itemgetter(8))
    date_start = property(itemgetter(9))
    ipinuse_id = property(itemgetter(10))
    caller_id = property(itemgetter(11))
    guest_pool = property(itemgetter(12))
    nas_port_id = property(itemgetter(13))
    
    
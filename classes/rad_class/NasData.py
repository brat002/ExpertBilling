from operator import itemgetter, setitem

class NasData(tuple):
    'NasData(id, secret, type, multilink, ipaddress, identify, peed_vendor_1, speed_vendor_2, speed_attr_id1, speed_attr_id2, speed_value1, speed_value2, acct_interim_interval)' 

    __slots__ = () 

    _fields = ('id', 'secret', 'type', 'multilink', 'ipaddress', 'identify', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, secret, type, multilink, ipaddress, identify, speed_vendor_1, speed_vendor_2, speed_attr_id1, speed_attr_id2, speed_value1, speed_value2, acct_interim_interval):
        return tuple.__new__(cls, (id, secret, type, multilink, ipaddress, identify, speed_vendor_1, speed_vendor_2, speed_attr_id1, speed_attr_id2, speed_value1, speed_value2, acct_interim_interval)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new NasData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 13:
            raise TypeError('Expected 13 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'NasData(id=%r, secret=%r, type=%r, multilink=%r, ipaddress=%r, identify=%r,speed_vendor_1=%r, speed_vendor_2=%r, speed_attr_id1=%r, speed_attr_id2=%r, speed_value1=%r, speed_value2=%r, acct_interim_interval=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field identifys to their values'
        return {'id': t[0], 'secret': t[1], 'type': t[2], 'multilink': t[3], 'ipaddress': t[4], 'identify':t[5], 'speed_vendor_1':t[6], 'speed_vendor_2':t[7], 'speed_attr_id1':t[8], 'speed_attr_id2':t[9], 'speed_value1':t[10], 'speed_value2':t[11], 'acct_interim_interval':t[12]} 

    def _replace(self, **kwds):
        'Return a new NasData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'secret', 'type', 'multilink', 'ipaddress', 'identify', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval'), self))
        if kwds:
            raise ValueError('Got unexpected field identifys: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    secret = property(itemgetter(1))
    type = property(itemgetter(2))
    multilink = property(itemgetter(3))
    ipaddress = property(itemgetter(4))
    identify = property(itemgetter(5))
    speed_vendor_1 = property(itemgetter(6))
    speed_vendor_2 = property(itemgetter(7))
    speed_attr_id1 = property(itemgetter(8))
    speed_attr_id2 = property(itemgetter(9))
    speed_value1 = property(itemgetter(10))
    speed_value2 = property(itemgetter(11))
    acct_interim_interval = property(itemgetter(12))

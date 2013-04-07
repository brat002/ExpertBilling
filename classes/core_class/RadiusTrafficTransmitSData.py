from operator import itemgetter, setitem

class RadiusTrafficTransmitSData(tuple):
    'RadiusTrafficTransmitSData(id, direction, tarification_step, rounding, prepaid_direction, prepaid_value, reset_prepaid_traffic)' 

    __slots__ = () 

    _fields = ('id', 'direction', 'tarification_step', 'rounding', 'prepaid_direction', 'prepaid_value', 'reset_prepaid_traffic') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, direction, tarification_step, rounding, prepaid_direction, prepaid_value, reset_prepaid_traffic):
        return tuple.__new__(cls, (id, direction, tarification_step, rounding, prepaid_direction, prepaid_value, reset_prepaid_traffic)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new RadiusTrafficTransmitSData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 7:
            raise TypeError('Expected 7 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'RadiusTrafficTransmitSData(id=%r, direction=%r, tarification_step=%r, rounding=%r, prepaid_direction=%r, prepaid_value=%r, reset_prepaid_traffic=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id':t[0], 'direction':t[1], 'tarification_step':t[2], 'rounding':t[3], 'prepaid_direction':t[4], 'prepaid_value':t[5], 'reset_prepaid_traffic':t[6]} 

    def _replace(self, **kwds):
        'Return a new RadiusTrafficTransmitSData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'direction', 'tarification_step', 'rounding', 'prepaid_direction', 'prepaid_value', 'reset_prepaid_traffic'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 
    
    id = property(itemgetter(0))
    direction = property(itemgetter(1))
    tarification_step = property(itemgetter(2))
    rounding = property(itemgetter(3))
    prepaid_direction = property(itemgetter(4))
    prepaid_value = property(itemgetter(5))
    reset_prepaid_traffic = property(itemgetter(6))
    
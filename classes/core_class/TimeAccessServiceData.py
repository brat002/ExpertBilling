from operator import itemgetter, setitem

class TimeAccessServiceData(tuple):
    'TimeAccessServiceData(id, prepaid_time, reset_time, rounding, tarification_step)' 

    __slots__ = () 

    _fields = ('id', 'prepaid_time', 'reset_time', 'rounding', 'tarification_step') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, prepaid_time, reset_time, rounding, tarification_step):
        return tuple.__new__(cls, (id, prepaid_time, reset_time, rounding, tarification_step)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new TimeAccessServiceData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 5:
            raise TypeError('Expected 5 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'TimeAccessServiceData(id=%r, prepaid_time=%r, reset_time=%r, rounding=%r, tarification_step=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'prepaid_time': t[1], 'reset_time': t[2], 'rounding':t[3], 'tarification_step':t[4]} 

    def _replace(self, **kwds):
        'Return a new TimeAccessServiceData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'prepaid_time', 'reset_time', 'rounding', 'tarification_step'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    prepaid_time = property(itemgetter(1))
    reset_time = property(itemgetter(2))
    rounding = property(itemgetter(3))
    tarification_step = property(itemgetter(4))
    

from operator import itemgetter, setitem

class TimeAccessServiceData(tuple):
    'TimeAccessServiceData(id, prepaid_time, reset_time)' 

    __slots__ = () 

    _fields = ('id', 'prepaid_time', 'reset_time') 

    def __new__(cls, id, prepaid_time, reset_time):
        return tuple.__new__(cls, (id, prepaid_time, reset_time)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new TimeAccessServiceData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 3:
            raise TypeError('Expected 3 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'TimeAccessServiceData(id=%r, prepaid_time=%r, reset_time=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'prepaid_time': t[1], 'reset_time': t[2]} 

    def _replace(self, **kwds):
        'Return a new TimeAccessServiceData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'prepaid_time', 'reset_time'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    prepaid_time = property(itemgetter(1))
    reset_time = property(itemgetter(2))

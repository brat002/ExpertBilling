from operator import itemgetter, setitem

class TimePeriodNodeData(tuple):
    'TimePeriodNodeData(id, name, time_start, length, repeat_after, timeperiod_id)' 

    __slots__ = () 

    _fields = ('id', 'name', 'time_start', 'length', 'repeat_after', 'timeperiod_id') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, name, time_start, length, repeat_after, timeperiod_id):
        return tuple.__new__(cls, (id, name, time_start, length, repeat_after, timeperiod_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new TimePeriodNodeData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 6:
            raise TypeError('Expected 6 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'TimePeriodNodeData(id=%r, name=%r, time_start=%r, length=%r, repeat_after=%r, timeperiod_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'name': t[1], 'time_start': t[2], 'length': t[3], 'repeat_after': t[4], 'timeperiod_id': t[5]} 

    def _replace(self, **kwds):
        'Return a new TimePeriodNodeData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'name', 'time_start', 'length', 'repeat_after', 'timeperiod_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    name = property(itemgetter(1))
    time_start = property(itemgetter(2))
    length = property(itemgetter(3))
    repeat_after = property(itemgetter(4))
    timeperiod_id = property(itemgetter(5))

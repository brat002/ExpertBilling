from operator import itemgetter, setitem

class SuspendedPeriodData(tuple):
    'SuspendedPeriodData(id, account_id, start_date, end_date)' 

    __slots__ = () 

    _fields = ('id', 'account_id', 'start_date', 'end_date') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, account_id, start_date, end_date):
        return tuple.__new__(cls, (id, account_id, start_date, end_date)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new SuspendedPeriodData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 4:
            raise TypeError('Expected 4 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'SuspendedPeriodData(id=%r, account_id=%r, start_date=%r, end_date=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'account_id': t[1], 'start_date': t[2], 'end_date': t[3]} 

    def _replace(self, **kwds):
        'Return a new SuspendedPeriodData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'account_id', 'start_date', 'end_date'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    account_id = property(itemgetter(1))
    start_date = property(itemgetter(2))
    end_date = property(itemgetter(3))

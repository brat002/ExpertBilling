from operator import itemgetter, setitem

class OneTimeServiceData(tuple):
    'OneTimeServiceData(id, tarif_id, cost, created)' 

    __slots__ = () 

    _fields = ('id', 'tarif_id', 'cost', 'created') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, tarif_id, cost, created):
        return tuple.__new__(cls, (id, tarif_id, cost, created)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new OneTimeServiceData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 4:
            raise TypeError('Expected 4 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'OneTimeServiceData(id=%r, tarif_id=%r, cost=%r, created=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'tarif_id': t[1], 'cost': t[2], 'created': t[3]} 

    def _replace(self, **kwds):
        'Return a new OneTimeServiceData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'tarif_id', 'cost', 'created'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    tarif_id = property(itemgetter(1))
    cost = property(itemgetter(2))
    created = property(itemgetter(3))

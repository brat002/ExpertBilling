from operator import itemgetter, setitem

class OneTimeServiceData(tuple):
    'OneTimeServiceData(id, tarif_id, cost)' 

    __slots__ = () 

    _fields = ('id', 'tarif_id', 'cost') 

    def __new__(cls, id, tarif_id, cost):
        return tuple.__new__(cls, (id, tarif_id, cost)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new OneTimeServiceData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 3:
            raise TypeError('Expected 3 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'OneTimeServiceData(id=%r, tarif_id=%r, cost=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'tarif_id': t[1], 'cost': t[2]} 

    def _replace(self, **kwds):
        'Return a new OneTimeServiceData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'tarif_id', 'cost'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    tarif_id = property(itemgetter(1))
    cost = property(itemgetter(2))

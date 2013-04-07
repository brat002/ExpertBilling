from operator import itemgetter, setitem

class AddonServiceTarifData(tuple):
    'AddonServiceTarifData(id, tarif_id, service_id, activation_count, activation_count_period_id)' 

    __slots__ = () 

    _fields = ('id', 'tarif_id', 'service_id', 'activation_count', 'activation_count_period_id') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, tarif_id, service_id, activation_count, activation_count_period_id):
        return tuple.__new__(cls, (id, tarif_id, service_id, activation_count, activation_count_period_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new AddonServiceTarifData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 5:
            raise TypeError('Expected 5 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'AddonServiceTarifData(id=%r, tarif_id=%r, service_id=%r, activation_count=%r, activation_count_period_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'tarif_id': t[1], 'service_id': t[2], 'activation_count': t[3], 'activation_count_period_id': t[4]} 

    def _replace(self, **kwds):
        'Return a new AddonServiceTarifData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'tarif_id', 'service_id', 'activation_count', 'activation_count_period_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    tarif_id = property(itemgetter(1))
    service_id = property(itemgetter(2))
    activation_count = property(itemgetter(3))
    activation_count_period_id = property(itemgetter(4))

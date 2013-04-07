from operator import itemgetter, setitem

class RadiusAttrsData(tuple):
    'RadiusAttrsData(vendor, attrid, value, account_status,  tarif_id, nas_id)' 

    __slots__ = () 

    _fields = ('vendor', 'attrid', 'value', 'account_status', 'tarif_id', 'nas_id') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, vendor, attrid, value, account_status, tarif_id, nas_id):
        return tuple.__new__(cls, (vendor, attrid, value, account_status, tarif_id, nas_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new RadiusAttrsData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 6:
            raise TypeError('Expected 6 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'RadiusAttrsData(vendor=%r, attrid=%r, value=%r, account_status=%r, tarif_id=%r, nas_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'vendor': t[0], 'attrid': t[1], 'value': t[2], 'account_status':t[3], 'tarif_id': t[4], 'nas_id':t[5]} 

    def _replace(self, **kwds):
        'Return a new RadiusAttrsData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('vendor', 'attrid', 'value', 'account_status', 'tarif_id', 'nas_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    vendor = property(itemgetter(0))
    attrid = property(itemgetter(1))
    value = property(itemgetter(2))
    account_status = property(itemgetter(3))
    tarif_id = property(itemgetter(4))
    nas_id = property(itemgetter(5))

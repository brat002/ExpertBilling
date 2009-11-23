from operator import itemgetter, setitem

class TarifGroupEdgeData(list):
    'TarifGroupEdgeData(tarif_id,)' 

    __slots__ = () 

    _fields = ('tarif_id',) 

    def __init__(self, empty=True, tarif_id=None):
        if empty:
            pass
        else:
            self.extend((tarif_id,)) 
                
    @classmethod
    def _make(cls, iterable):
        'Make a new TarifGroupEdgeData object from a sequence or iterable'
        result = cls()
        result.extend(iterable)
        if len(result) < 1:
            result.extend([None for i in xrange(1 - len(result))])
        return result 

    def __repr__(self):
        try:
            return 'TarifGroupEdgeData(tarif_id=%r)' % tuple(self) 
        except:
            return repr(tuple(self)) 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'tarif_id': t[0]} 

    def _replace(self, **kwds):
        'Return a new TarifGroupEdgeData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('tarif_id',), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    tarif_id = property(itemgetter(0), lambda self_, value_: setitem(self_, 0, value_))

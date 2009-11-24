from operator import itemgetter, setitem

class TarifGroupEdgeData(list):
    'TarifGroupEdgeData(tarif_id, group_edges)' 

    __slots__ = () 

    _fields = ('tarif_id', 'group_edges') 

    def __init__(self, empty=True, tarif_id=None, group_edges=None):
        if empty:
            pass
        else:
            self.extend((tarif_id, group_edges)) 
                
    @classmethod
    def _make(cls, iterable):
        'Make a new TarifGroupEdgeData object from a sequence or iterable'
        result = cls()
        result.extend(iterable)
        if len(result) < 2:
            result.extend([None for i in xrange(2 - len(result))])
        return result 

    def __repr__(self):
        try:
            return 'TarifGroupEdgeData(tarif_id=%r, group_edges=%r)' % tuple(self) 
        except:
            return repr(tuple(self)) 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'tarif_id': t[0], 'group_edges': t[1]} 

    def _replace(self, **kwds):
        'Return a new TarifGroupEdgeData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('tarif_id', 'group_edges'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    tarif_id = property(itemgetter(0), lambda self_, value_: setitem(self_, 0, value_))
    group_edges = property(itemgetter(1), lambda self_, value_: setitem(self_, 1, value_))

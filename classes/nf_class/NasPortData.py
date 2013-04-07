from operator import itemgetter, setitem

class NasPortData(list):
    'NasPortData(account_id, nas_id, nas_port_id)' 

    __slots__ = () 

    _fields = ('account_id', 'nas_id', 'nas_port_id') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __init__(self, empty=True, account_id=None, nas_id=None, nas_port_id=None):
        if not empty:
            self.extend((account_id, nas_id, nas_port_id)) 

                
    @classmethod
    def _make(cls, iterable):
        'Make a new NasPortData object from a sequence or iterable'
        result = cls()
        result.extend(iterable)
        if len(result) < 3:
            result.extend([None for i in xrange(3 - len(result))])
        return result 

    def __repr__(self):
        try:
            return 'NasPortData(account_id=%r, nas_id=%r, nas_port_id=%r)' % tuple(self) 
        except:
            return repr(tuple(self)) 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'account_id': t[0], 'nas_id': t[1], 'nas_port_id':t[2]} 

    def _replace(self, **kwds):
        'Return a new NasPortData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('account_id', 'nas_id', 'nas_port_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    account_id = property(itemgetter(0), lambda self_, value_: setitem(self_, 0, value_))
    nas_id = property(itemgetter(1), lambda self_, value_: setitem(self_, 1, value_))
    nas_port_id = property(itemgetter(2), lambda self_, value_: setitem(self_, 2, value_))
    

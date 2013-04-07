from operator import itemgetter, setitem

class GroupsData(list):
    'GroupsData(id, trafficclass, direction, type)' 

    __slots__ = () 

    _fields = ('id', 'trafficclass', 'direction', 'type') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __init__(self, empty=True, id=None, trafficclass=None, direction=None, type=None):
        if empty:
            pass
        else:
            self.extend((id, trafficclass, direction, type)) 
                
    @classmethod
    def _make(cls, iterable):
        'Make a new GroupsData object from a sequence or iterable'
        result = cls()
        result.extend(iterable)
        if len(result) < 4:
            result.extend([None for i in xrange(4 - len(result))])
        return result 

    def __repr__(self):
        try:
            return 'GroupsData(id=%r, trafficclass=%r, direction=%r, type=%r)' % tuple(self) 
        except:
            return repr(tuple(self)) 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'trafficclass': t[1], 'direction': t[2], 'type': t[3]} 

    def _replace(self, **kwds):
        'Return a new GroupsData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'trafficclass', 'direction', 'type'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0), lambda self_, value_: setitem(self_, 0, value_))
    trafficclass = property(itemgetter(1), lambda self_, value_: setitem(self_, 1, value_))
    direction = property(itemgetter(2), lambda self_, value_: setitem(self_, 2, value_))
    type = property(itemgetter(3), lambda self_, value_: setitem(self_, 3, value_))

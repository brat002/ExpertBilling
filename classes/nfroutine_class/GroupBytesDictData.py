from operator import itemgetter, setitem

class GroupBytesDictData(list):
    'GroupBytesDictData(bytes, tg_datetime, tg_current, tg_next)' 

    __slots__ = () 

    _fields = ('bytes', 'tg_datetime', 'tg_current', 'tg_next') 
    def __getstate__(self):
        return list(self)
    def __setstate__(self, state):
        return self._make(state)
    def __init__(self, empty=True, bytes=None, tg_datetime=None, tg_current=None, tg_next=None):
        if empty:
            pass
        else:
            self.extend((bytes, tg_datetime, tg_current, tg_next)) 
                
    @classmethod
    def _make(cls, iterable):
        'Make a new GroupBytesDictData object from a sequence or iterable'
        result = cls()
        result.extend(iterable)
        if len(result) < 4:
            result.extend([None for i in xrange(4 - len(result))])
        return result 

    def __repr__(self):
        try:
            return 'GroupBytesDictData(bytes=%r, tg_datetime=%r, tg_current=%r, tg_next=%r)' % tuple(self) 
        except:
            return repr(tuple(self)) 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'bytes': t[0], 'tg_datetime': t[1], 'tg_current': t[2], 'tg_next': t[3]} 

    def _replace(self, **kwds):
        'Return a new GroupBytesDictData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('bytes', 'tg_datetime', 'tg_current', 'tg_next'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    bytes = property(itemgetter(0), lambda self_, value_: setitem(self_, 0, value_))
    tg_datetime = property(itemgetter(1), lambda self_, value_: setitem(self_, 1, value_))
    tg_current = property(itemgetter(2), lambda self_, value_: setitem(self_, 2, value_))
    tg_next = property(itemgetter(3), lambda self_, value_: setitem(self_, 3, value_))

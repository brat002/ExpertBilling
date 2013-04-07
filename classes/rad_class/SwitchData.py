from operator import itemgetter, setitem

class SwitchData(tuple):
    'SwitchData(id, identify,  option82, option82_auth_type, option82_template, remote_id)' 

    __slots__ = () 

    _fields = ('id', 'identify', 'option82', 'option82_auth_type', 'option82_template', 'remote_id') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, identify, option82, option82_auth_type, option82_template, remote_id):
        return tuple.__new__(cls, (id, identify, option82, option82_auth_type, option82_template, remote_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new NasData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 6:
            raise TypeError('Expected 6 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'SwitchData(id=%r, identify=%r, option82=%r, option82_auth_type=%r, option82_template=%r, remote_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field identifys to their values'
        return {'id': t[0], 'identify': t[1], 'option82': t[2], 'option82_auth_type': t[3], 'option82_template': t[4], 'remote_id':t[5]} 

    def _replace(self, **kwds):
        'Return a new SwitchData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'identify', 'option82', 'option82_auth_type', 'option82_template', 'remote_id'), self))
        if kwds:
            raise ValueError('Got unexpected field identifys: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    identify = property(itemgetter(1))
    option82 = property(itemgetter(2))
    option82_auth_type = property(itemgetter(3))
    option82_template = property(itemgetter(4))
    remote_id = property(itemgetter(5))
    
from operator import itemgetter, setitem

class ActiveSessionData(tuple):
    'ActiveSessionData(framed_ip_address, nas_id,  account_id)' 

    __slots__ = () 

    _fields = ('framed_ip_address', 'nas_id', 'account_id') 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new ActiveSessionData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 3:
            raise TypeError('Expected 3 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'ActiveSessionData(framed_ip_address=%r, nas_id=%r, account_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'framed_ip_address':t[0], 'nas_id':t[1], 'account_id':t[2]} 

    def _replace(self, **kwds):
        'Return a new ActiveSessionData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('framed_ip_address', 'nas_id', 'account_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 
    
    framed_ip_address = property(itemgetter(0))
    nas_id = property(itemgetter(1))
    account_id = property(itemgetter(2))

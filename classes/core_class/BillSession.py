from operator import itemgetter, setitem

class BillSession(tuple):
    'BillSession(id, account_id, sessionid, session_time, interrim_update, taccs_id, tarif_id, acctf_id)' 

    __slots__ = () 

    _fields = ('id', 'account_id', 'sessionid', 'session_time', 'interrim_update', 'taccs_id', 'tarif_id', 'acctf_id') 

    def __new__(cls, id, account_id, sessionid, session_time, interrim_update, taccs_id, tarif_id, acctf_id):
        return tuple.__new__(cls, (id, account_id, sessionid, session_time, interrim_update, taccs_id, tarif_id, acctf_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new BillSession object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 8:
            raise TypeError('Expected 8 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'BillSession(id=%r, account_id=%r, sessionid=%r, session_time=%r, interrim_update=%r, taccs_id=%r, tarif_id=%r, acctf_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'account_id': t[1], 'sessionid': t[2], 'session_time': t[3], 'interrim_update': t[4], 'taccs_id': t[5], 'tarif_id': t[6], 'acctf_id': t[7]} 

    def _replace(self, **kwds):
        'Return a new BillSession object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'account_id', 'sessionid', 'session_time', 'interrim_update', 'taccs_id', 'tarif_id', 'acctf_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    account_id = property(itemgetter(1))
    sessionid = property(itemgetter(2))
    session_time = property(itemgetter(3))
    interrim_update = property(itemgetter(4))
    taccs_id = property(itemgetter(5))
    tarif_id = property(itemgetter(6))
    acctf_id = property(itemgetter(7))

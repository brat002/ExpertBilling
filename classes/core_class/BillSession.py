from operator import itemgetter, setitem

class BillSession(tuple):
    'BillSession(id, account_id, sessionid, session_time, bytes_in, bytes_out, interrim_update, date_end, taccs_id, traccs_id, tarif_id, acctf_id, lt_time, lt_bytes_in, lt_bytes_out)' 

    __slots__ = () 

    _fields = ('id', 'account_id', 'sessionid', 'session_time', 'bytes_in', 'bytes_out','interrim_update', 'date_end', 'taccs_id', 'traccs_id','tarif_id', 'acctf_id', 'lt_time', 'lt_bytes_in', 'lt_bytes_out') 

    def __new__(cls, id, account_id, sessionid, session_time, bytes_in, bytes_out, interrim_update, date_end, taccs_id, traccs_id, tarif_id, acctf_id, lt_time, lt_bytes_in, lt_bytes_out):
        return tuple.__new__(cls, (id, account_id, sessionid, session_time, bytes_in, bytes_out, interrim_update, date_end, taccs_id, traccs_id, tarif_id, acctf_id, lt_time, lt_bytes_in, lt_bytes_out)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new BillSession object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 15:
            raise TypeError('Expected 15 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'BillSession(id=%r, account_id=%r, sessionid=%r, session_time=%r,bytes_in=%r, bytes_out=%r, interrim_update=%r, date_end=%r, taccs_id=%r, traccs_id=%r, tarif_id=%r, acctf_id=%r, lt_time=%r, lt_bytes_in=%r, lt_bytes_out=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'account_id': t[1], 'sessionid': t[2], 'session_time': t[3], 'bytes_in':t[4], 'bytes_out':t[5], 'interrim_update': t[6], 'date_end':t[7],'taccs_id': t[8], 'traccs_id':t[9],'tarif_id': t[10], 'acctf_id': t[11], 'lt_time':t[12], 'lt_bytes_in':t[13], 'lt_bytes_out':t[14]} 

    def _replace(self, **kwds):
        'Return a new BillSession object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'account_id', 'sessionid', 'session_time', 'bytes_in', 'bytes_out', 'interrim_update', 'date_end', 'taccs_id', 'traccs_id', 'tarif_id', 'acctf_id', 'lt_time', 'lt_bytes_in', 'lt_bytes_out'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    account_id = property(itemgetter(1))
    sessionid = property(itemgetter(2))
    session_time = property(itemgetter(3))
    bytes_in = property(itemgetter(4))
    bytes_out = property(itemgetter(5))
    interrim_update = property(itemgetter(6))
    date_end = property(itemgetter(7))
    taccs_id = property(itemgetter(8))
    traccs_id = property(itemgetter(9))
    tarif_id = property(itemgetter(10))
    acctf_id = property(itemgetter(11))
    lt_time = property(itemgetter(12))
    lt_bytes_in = property(itemgetter(13))
    lt_bytes_out = property(itemgetter(14))

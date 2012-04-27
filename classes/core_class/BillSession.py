from operator import itemgetter, setitem

class BillSession(tuple):
    'BillSession(id, account_id, sessionid, session_time, bytes_in, bytes_out, interrim_update, date_start, date_end, taccs_id, traccs_id, tarif_id, acctf_id, lt_time, lt_bytes_in, lt_bytes_out,nas_port_id,nas_int_id)' 

    __slots__ = () 

    _fields = ('id', 'account_id', 'sessionid', 'session_time', 'bytes_in', 'bytes_out','interrim_update', 'date_start',  'date_end', 'taccs_id', 'traccs_id','tarif_id', 'acctf_id', 'lt_time', 'lt_bytes_in', 'lt_bytes_out', 'nas_port_id', 'nas_int_id') 

    def __new__(cls, id, account_id, sessionid, session_time, bytes_in, bytes_out, interrim_update, date_start, date_end, taccs_id, traccs_id, tarif_id, acctf_id, lt_time, lt_bytes_in, lt_bytes_out, nas_port_id,nas_int_id):
        return tuple.__new__(cls, (id, account_id, sessionid, session_time, bytes_in, bytes_out, interrim_update, date_start, date_end, taccs_id, traccs_id, tarif_id, acctf_id, lt_time, lt_bytes_in, lt_bytes_out,nas_port_id,nas_int_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new BillSession object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 18:
            raise TypeError('Expected 18 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'BillSession(id=%r, account_id=%r, sessionid=%r, session_time=%r,bytes_in=%r, bytes_out=%r, interrim_update=%r, date_start=%r, date_end=%r, taccs_id=%r, traccs_id=%r, tarif_id=%r, acctf_id=%r, lt_time=%r, lt_bytes_in=%r, lt_bytes_out=%r, nas_port_id=%r, nas_int_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'account_id': t[1], 'sessionid': t[2], 'session_time': t[3], 'bytes_in':t[4], 'bytes_out':t[5], 'interrim_update': t[6], 'date_start': t[7],  'date_end':t[8],'taccs_id': t[9], 'traccs_id':t[10], 'tarif_id': t[11], 'acctf_id': t[12], 'lt_time':t[13], 'lt_bytes_in':t[14], 'lt_bytes_out':t[15], 'nas_port_id':t[16], 'nas_int_id':t[17]} 

    def _replace(self, **kwds):
        'Return a new BillSession object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'account_id', 'sessionid', 'session_time', 'bytes_in', 'bytes_out', 'interrim_update', 'date_start', 'date_end', 'taccs_id', 'traccs_id', 'tarif_id', 'acctf_id', 'lt_time', 'lt_bytes_in', 'lt_bytes_out', 'nas_port_id', 'nas_int_id'), self))
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
    date_start = property(itemgetter(7))
    date_end = property(itemgetter(8))
    taccs_id = property(itemgetter(9))
    traccs_id = property(itemgetter(10))
    tarif_id = property(itemgetter(11))
    acctf_id = property(itemgetter(12))
    lt_time = property(itemgetter(13))
    lt_bytes_in = property(itemgetter(14))
    lt_bytes_out = property(itemgetter(15))
    nas_port_id = property(itemgetter(16))
    nas_int_id = property(itemgetter(17))
    

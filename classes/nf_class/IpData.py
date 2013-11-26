from operator import itemgetter, setitem

class IpData(tuple):
    'IpData(ip, account_id, tariff_id, accounttarif_id)' 

    __slots__ = () 

    _fields = ('ip', 'account_id', 'tariff_id', 'accounttarif_id') 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new IpData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 4:
            raise TypeError('Expected 4 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'ActiveSessionData(ip=%r, account_id=%r, tariff_id=%r, accounttarif_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'ip':t[0], 'account_id':t[1], 'tariff_id':t[2], 'accounttarif_id': t[4]} 

    def _replace(self, **kwds):
        'Return a new IpData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('ip', 'account_id', 'tariff_id', 'accounttarif_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 
    
    ip = property(itemgetter(0))
    account_id = property(itemgetter(1))
    tariff_id = property(itemgetter(2))
    accounttarif_id = property(itemgetter(3))

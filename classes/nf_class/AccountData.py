from operator import itemgetter, setitem

class AccountData(tuple):
    'AccountData(account_id, acctf_id, tarif_id)' 

    __slots__ = () 
    _fields = ('account_id', 'acctf_id', 'tarif_id') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, account_id, acctf_id, tarif_id):
        return tuple.__new__(cls, (account_id, acctf_id, tarif_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new AccountData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 3:
            raise TypeError('Expected 3 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'AccountData(account_id=%r, acctf_id=%r, tarif_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'account_id': t[0], 'acctf_id': t[1], 'tarif_id': t[2]} 

    def _replace(self, **kwds):
        'Return a new AccountData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('account_id', 'acctf_id', 'tarif_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    account_id = property(itemgetter(0))
    acctf_id = property(itemgetter(1))
    tarif_id = property(itemgetter(2))

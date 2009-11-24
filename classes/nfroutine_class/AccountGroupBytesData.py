from operator import itemgetter, setitem

class AccountGroupBytesData(list):
    'AccountGroupBytesData(account_id, tarif_id, acctf_id, datetime, group_bytes, lock)' 

    __slots__ = () 

    _fields = ('account_id', 'tarif_id', 'acctf_id', 'datetime', 'group_bytes', 'lock') 

    def __init__(self, empty=True, account_id=None, tarif_id=None, acctf_id=None, datetime=None, group_bytes=None, lock=None):
        if empty:
            pass
        else:
            self.extend((account_id, tarif_id, acctf_id, datetime, group_bytes, lock)) 
                
    @classmethod
    def _make(cls, iterable):
        'Make a new AccountGroupBytesData object from a sequence or iterable'
        result = cls()
        result.extend(iterable)
        if len(result) < 6:
            result.extend([None for i in xrange(6 - len(result))])
        return result 

    def __repr__(self):
        try:
            return 'AccountGroupBytesData(account_id=%r, tarif_id=%r, acctf_id=%r, datetime=%r, group_bytes=%r, lock=%r)' % tuple(self) 
        except:
            return repr(tuple(self)) 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'account_id': t[0], 'tarif_id': t[1], 'acctf_id': t[2], 'datetime': t[3], 'group_bytes': t[4], 'lock': t[5]} 

    def _replace(self, **kwds):
        'Return a new AccountGroupBytesData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('account_id', 'tarif_id', 'acctf_id', 'datetime', 'group_bytes', 'lock'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    account_id = property(itemgetter(0), lambda self_, value_: setitem(self_, 0, value_))
    tarif_id = property(itemgetter(1), lambda self_, value_: setitem(self_, 1, value_))
    acctf_id = property(itemgetter(2), lambda self_, value_: setitem(self_, 2, value_))
    datetime = property(itemgetter(3), lambda self_, value_: setitem(self_, 3, value_))
    group_bytes = property(itemgetter(4), lambda self_, value_: setitem(self_, 4, value_))
    lock = property(itemgetter(5), lambda self_, value_: setitem(self_, 5, value_))

from operator import itemgetter, setitem

class AccountGroupBytesData(list):
    'AccountGroupBytesData(account_id,)' 

    __slots__ = () 

    _fields = ('account_id',) 

    def __init__(self, empty=True, account_id=None):
        if empty:
            pass
        else:
            self.extend((account_id,)) 
                
    @classmethod
    def _make(cls, iterable):
        'Make a new AccountGroupBytesData object from a sequence or iterable'
        result = cls()
        result.extend(iterable)
        if len(result) < 1:
            result.extend([None for i in xrange(1 - len(result))])
        return result 

    def __repr__(self):
        try:
            return 'AccountGroupBytesData(account_id=%r)' % tuple(self) 
        except:
            return repr(tuple(self)) 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'account_id': t[0]} 

    def _replace(self, **kwds):
        'Return a new AccountGroupBytesData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('account_id',), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    account_id = property(itemgetter(0), lambda self_, value_: setitem(self_, 0, value_))

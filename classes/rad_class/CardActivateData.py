from operator import itemgetter, setitem

class CardActivateData(tuple):
    'CardActivateData(account_id, password, nas_id, tarif_id, account_status, balance_blocked, ballance, disabled_by_limit, tariff_active)' 

    __slots__ = () 

    _fields = ('account_id', 'password', 'nas_id', 'tarif_id', 'account_status', 'balance_blocked', 'ballance', 'disabled_by_limit', 'tariff_active') 

    def __new__(cls, account_id, password, nas_id, tarif_id, account_status, balance_blocked, ballance, disabled_by_limit, tariff_active):
        return tuple.__new__(cls, (account_id, password, nas_id, tarif_id, account_status, balance_blocked, ballance, disabled_by_limit, tariff_active)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new CardActivateData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 9:
            raise TypeError('Expected 9 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'CardActivateData(account_id=%r, password=%r, nas_id=%r, tarif_id=%r, account_status=%r, balance_blocked=%r, ballance=%r, disabled_by_limit=%r, tariff_active=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'account_id': t[0], 'password': t[1], 'nas_id': t[2], 'tarif_id': t[3], 'account_status': t[4], 'balance_blocked': t[5], 'ballance': t[6], 'disabled_by_limit': t[7], 'tariff_active': t[8]} 

    def _replace(self, **kwds):
        'Return a new CardActivateData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('account_id', 'password', 'nas_id', 'tarif_id', 'account_status', 'balance_blocked', 'ballance', 'disabled_by_limit', 'tariff_active'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    account_id = property(itemgetter(0))
    password = property(itemgetter(1))
    nas_id = property(itemgetter(2))
    tarif_id = property(itemgetter(3))
    account_status = property(itemgetter(4))
    balance_blocked = property(itemgetter(5))
    ballance = property(itemgetter(6))
    disabled_by_limit = property(itemgetter(7))
    tariff_active = property(itemgetter(8))

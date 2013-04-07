from operator import itemgetter, setitem

class AddonPeriodicalData(tuple):
    'AddonPeriodicalData(ps_id, ps_name, cost, cash_method, sp_name, time_start, length, length_in, autostart, account_id, created, deactivated, temporary_blocked, last_checkout, addon_id, subaccount_id, tpd)' 

    __slots__ = () 

    _fields = ('ps_id', 'ps_name', 'cost', 'cash_method', 'sp_name', 'time_start', 'length', 'length_in', 'autostart', 'account_id', 'created', 'deactivated', 'temporary_blocked', 'last_checkout', 'addon_id', 'subaccount_id', 'tpd') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, ps_id, ps_name, cost, cash_method, sp_name, time_start, length, length_in, autostart, account_id, created, deactivated, temporary_blocked, last_checkout, addon_id, subaccount_id, tpd):
        return tuple.__new__(cls, (ps_id, ps_name, cost, cash_method, sp_name, time_start, length, length_in, autostart, account_id, created, deactivated, temporary_blocked, last_checkout, addon_id, subaccount_id, tpd)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new AddonPeriodicalData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 17:
            raise TypeError('Expected 17 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'AddonPeriodicalData(ps_id=%r, ps_name=%r, cost=%r, cash_method=%r, sp_name=%r, time_start=%r, length=%r, length_in=%r, autostart=%r, account_id=%r, created=%r, deactivated=%r, temporary_blocked=%r, last_checkout=%r, addon_id=%r, subaccount_id=%r, tpd=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'ps_id': t[0], 'ps_name': t[1], 'cost': t[2], 'cash_method': t[3], 'sp_name': t[4], 'time_start': t[5], 'length': t[6], 'length_in': t[7], 'autostart': t[8], 'account_id': t[9], 'created': t[10], 'deactivated': t[11], 'temporary_blocked': t[12], 'last_checkout': t[13], 'addon_id': t[14], 'subaccount_id':t[15], 'tpd': t[16]} 

    def _replace(self, **kwds):
        'Return a new AddonPeriodicalData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('ps_id', 'ps_name', 'cost', 'cash_method', 'sp_name', 'time_start', 'length', 'length_in', 'autostart', 'account_id', 'created', 'deactivated', 'temporary_blocked', 'last_checkout', 'addon_id', 'subaccount_id', 'tpd'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    ps_id = property(itemgetter(0))
    ps_name = property(itemgetter(1))
    cost = property(itemgetter(2))
    cash_method = property(itemgetter(3))
    sp_name = property(itemgetter(4))
    time_start = property(itemgetter(5))
    length = property(itemgetter(6))
    length_in = property(itemgetter(7))
    autostart = property(itemgetter(8))
    account_id = property(itemgetter(9))
    created = property(itemgetter(10))
    deactivated = property(itemgetter(11))
    temporary_blocked = property(itemgetter(12))
    last_checkout = property(itemgetter(13))
    addon_id = property(itemgetter(14))
    subaccount_id = property(itemgetter(15))
    tpd = property(itemgetter(16))
    

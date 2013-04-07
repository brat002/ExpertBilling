from operator import itemgetter, setitem

class ShedulelogData(tuple):
    'ShedulelogData(id, account_id, ballance_checkout, prepaid_traffic_reset, prepaid_traffic_accrued, prepaid_time_reset, prepaid_time_accrued, prepaid_radius_traffic_reset, prepaid_radius_traffic_accrued, balance_blocked, accounttarif_id)' 

    __slots__ = () 

    _fields = ('id', 'account_id', 'ballance_checkout', 'prepaid_traffic_reset', 'prepaid_traffic_accrued', 'prepaid_time_reset', 'prepaid_time_accrued', 'prepaid_radius_traffic_reset', 'prepaid_radius_traffic_accrued', 'balance_blocked', 'accounttarif_id') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, account_id, ballance_checkout, prepaid_traffic_reset, prepaid_traffic_accrued, prepaid_time_reset, prepaid_time_accrued, prepaid_radius_traffic_reset, prepaid_radius_traffic_accrued, balance_blocked, accounttarif_id):
        return tuple.__new__(cls, (id, account_id, ballance_checkout, prepaid_traffic_reset, prepaid_traffic_accrued, prepaid_time_reset, prepaid_time_accrued, prepaid_radius_traffic_reset, prepaid_radius_traffic_accrued, balance_blocked, accounttarif_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new ShedulelogData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 11:
            raise TypeError('Expected 11 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'ShedulelogData(id=%r, account_id=%r, ballance_checkout=%r, prepaid_traffic_reset=%r, prepaid_traffic_accrued=%r, prepaid_time_reset=%r, prepaid_time_accrued=%r, prepaid_radius_traffic_reset=%r, prepaid_radius_traffic_accrued=%r, balance_blocked=%r, accounttarif_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'account_id': t[1], 'ballance_checkout': t[2], 'prepaid_traffic_reset': t[3], 'prepaid_traffic_accrued': t[4], 'prepaid_time_reset': t[5], 'prepaid_time_accrued': t[6], 'prepaid_radius_traffic_reset':t[7], 'prepaid_radius_traffic_accrued':t[8], 'balance_blocked': t[9], 'accounttarif_id': t[10]} 

    def _replace(self, **kwds):
        'Return a new ShedulelogData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'account_id', 'ballance_checkout', 'prepaid_traffic_reset', 'prepaid_traffic_accrued', 'prepaid_time_reset', 'prepaid_time_accrued', 'prepaid_radius_traffic_reset', 'prepaid_radius_traffic_accrued', 'balance_blocked', 'accounttarif_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    account_id = property(itemgetter(1))
    ballance_checkout = property(itemgetter(2))
    prepaid_traffic_reset = property(itemgetter(3))
    prepaid_traffic_accrued = property(itemgetter(4))
    prepaid_time_reset = property(itemgetter(5))
    prepaid_time_accrued = property(itemgetter(6))
    prepaid_radius_traffic_reset = property(itemgetter(7))
    prepaid_radius_traffic_accrued = property(itemgetter(8))
    balance_blocked = property(itemgetter(9))
    accounttarif_id = property(itemgetter(10))

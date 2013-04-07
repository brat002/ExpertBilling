from operator import itemgetter, setitem

class AccountData(tuple):
    'AccountData(account_id, ballance, credit, datetime, tarif_id, access_parameters_id, time_access_service_id, traffic_transmit_service_id, cost, reset_tarif_cost, settlement_period_id, tarif_active, acctf_id, account_status)' 

    __slots__ = () 

    _fields = ('account_id', 'ballance', 'credit', 'datetime', 'tarif_id', 'access_parameters_id', 'time_access_service_id', 'traffic_transmit_service_id', 'cost', 'reset_tarif_cost', 'settlement_period_id', 'tarif_active', 'acctf_id', 'account_status') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, account_id, ballance, credit, datetime, tarif_id, access_parameters_id, time_access_service_id, traffic_transmit_service_id, cost, reset_tarif_cost, settlement_period_id, tarif_active, acctf_id, account_status):
        return tuple.__new__(cls, (account_id, ballance, credit, datetime, tarif_id, access_parameters_id, time_access_service_id, traffic_transmit_service_id, cost, reset_tarif_cost, settlement_period_id, tarif_active, acctf_id, account_status)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new AccountData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 14:
            raise TypeError('Expected 14 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'AccountData(account_id=%r, ballance=%r, credit=%r, datetime=%r, tarif_id=%r, access_parameters_id=%r, time_access_service_id=%r, traffic_transmit_service_id=%r, cost=%r, reset_tarif_cost=%r, settlement_period_id=%r, tarif_active=%r, acctf_id=%r, account_status=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'account_id': t[0], 'ballance': t[1], 'credit': t[2], 'datetime': t[3], 'tarif_id': t[4], 'access_parameters_id': t[5], 'time_access_service_id': t[6], 'traffic_transmit_service_id': t[7], 'cost': t[8], 'reset_tarif_cost': t[9], 'settlement_period_id': t[10], 'tarif_active': t[11], 'acctf_id': t[12], 'account_status': t[13]} 

    def _replace(self, **kwds):
        'Return a new AccountData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('account_id', 'ballance', 'credit', 'datetime', 'tarif_id', 'access_parameters_id', 'time_access_service_id', 'traffic_transmit_service_id', 'cost', 'reset_tarif_cost', 'settlement_period_id', 'tarif_active', 'acctf_id', 'account_status'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    account_id = property(itemgetter(0))
    ballance = property(itemgetter(1))
    credit = property(itemgetter(2))
    datetime = property(itemgetter(3))
    tarif_id = property(itemgetter(4))
    access_parameters_id = property(itemgetter(5))
    time_access_service_id = property(itemgetter(6))
    traffic_transmit_service_id = property(itemgetter(7))
    cost = property(itemgetter(8))
    reset_tarif_cost = property(itemgetter(9))
    settlement_period_id = property(itemgetter(10))
    tarif_active = property(itemgetter(11))
    acctf_id = property(itemgetter(12))
    account_status = property(itemgetter(13))

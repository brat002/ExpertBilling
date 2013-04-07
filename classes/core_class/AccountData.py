from operator import itemgetter, setitem

class AccountData(list):
    'AccountData(account_id, ballance, credit, datetime, tarif_id, access_parameters_id, time_access_service_id, traffic_transmit_service_id, cost, reset_tarif_cost, settlement_period_id, tarif_active, acctf_id, false_, account_created, disabled_by_limit, balance_blocked, ps_null_ballance_checkout, tarif_deleted, allow_express_pay, account_status, username, password, require_tarif_cost, periodical_billed, current_acctf, end_date,  radius_traffic_transmit_service_id,userblock_max_days)' 

    __slots__ = () 

    _fields = ('account_id', 'ballance', 'credit', 'datetime', 'tarif_id', 'access_parameters_id', 'time_access_service_id', 'traffic_transmit_service_id', 'cost', 'reset_tarif_cost', 'settlement_period_id', 'tarif_active', 'acctf_id', 'false_', 'account_created', 'disabled_by_limit', 'balance_blocked', 'ps_null_ballance_checkout', 'tarif_deleted', 'allow_express_pay', 'account_status', 'username', 'password', 'require_tarif_cost', 'periodical_billed', 'current_acctf', 'end_date', 'radius_traffic_transmit_service_id', 'userblock_max_days') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __init__(self, empty=True, account_id=None, ballance=None, credit=None, datetime=None, tarif_id=None, access_parameters_id=None, time_access_service_id=None, traffic_transmit_service_id=None, cost=None, reset_tarif_cost=None, settlement_period_id=None, tarif_active=None, acctf_id=None, false_=None, account_created=None, disabled_by_limit=None, balance_blocked=None, ps_null_ballance_checkout=None, tarif_deleted=None, allow_express_pay=None, account_status=None, username=None, password=None, require_tarif_cost=None, periodical_billed=None, current_acctf=None, end_date=None, radius_traffic_transmit_service_id=None, userblock_max_days=None):
        if empty:
            pass
        else:
            self.extend((account_id, ballance, credit, datetime, tarif_id, access_parameters_id, time_access_service_id, traffic_transmit_service_id, cost, reset_tarif_cost, settlement_period_id, tarif_active, acctf_id, false_, account_created, disabled_by_limit, balance_blocked,  ps_null_ballance_checkout, tarif_deleted, allow_express_pay, account_status, username, password, require_tarif_cost, periodical_billed, current_acctf, end_date, radius_traffic_transmit_service_id,userblock_max_days)) 
                
    @classmethod
    def _make(cls, iterable):
        'Make a new AccountData object from a sequence or iterable'
        result = cls()
        result.extend(iterable)
        if len(result) != 29:
            result.extend([None for i in xrange(29 - len(result))])
        return result 

    def __repr__(self):
        try:
            return 'AccountData(account_id=%r, ballance=%r, credit=%r, datetime=%r, tarif_id=%r, access_parameters_id=%r, time_access_service_id=%r, traffic_transmit_service_id=%r, cost=%r, reset_tarif_cost=%r, settlement_period_id=%r, tarif_active=%r, acctf_id=%r, false_=%r, account_created=%r, disabled_by_limit=%r, balance_blocked=%r,  ps_null_ballance_checkout=%r, tarif_deleted=%r, allow_express_pay=%r, account_status=%r, username=%r, password=%r, require_tarif_cost=%r, periodical_billed=%r, current_acctf=%r, end_date=%r, radius_traffic_transmit_service_id=%r,userblock_max_days=%r)' % tuple(self) 
        except:
            return repr(tuple(self)) 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'account_id': t[0], 'ballance': t[1], 'credit': t[2], 'datetime': t[3], 'tarif_id': t[4], 'access_parameters_id': t[5], 'time_access_service_id': t[6], 'traffic_transmit_service_id': t[7], 'cost': t[8], 'reset_tarif_cost': t[9], 'settlement_period_id': t[10], 'tarif_active': t[11], 'acctf_id': t[12], 'false_': t[13], 'account_created': t[14], 'disabled_by_limit': t[15], 'balance_blocked': t[16],  'ps_null_ballance_checkout': t[17], 'tarif_deleted': t[18], 'allow_express_pay': t[19], 'account_status': t[20], 'username': t[21], 'password': t[22], 'require_tarif_cost': t[23], 'periodical_billed': t[24], 'current_acctf': t[25], 'end_date': t[26],  'radius_traffic_transmit_service_id':t[27], 'userblock_max_days':t[28]} 

    def _replace(self, **kwds):
        'Return a new AccountData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('account_id', 'ballance', 'credit', 'datetime', 'tarif_id', 'access_parameters_id', 'time_access_service_id', 'traffic_transmit_service_id', 'cost', 'reset_tarif_cost', 'settlement_period_id', 'tarif_active', 'acctf_id', 'false_', 'account_created', 'disabled_by_limit', 'balance_blocked',  'ps_null_ballance_checkout', 'tarif_deleted', 'allow_express_pay', 'account_status', 'username', 'password', 'require_tarif_cost', 'periodical_billed', 'current_acctf', 'end_date', 'radius_traffic_transmit_service_id', 'userblock_max_days'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    account_id = property(itemgetter(0), lambda self_, value_: setitem(self_, 0, value_))
    ballance = property(itemgetter(1), lambda self_, value_: setitem(self_, 1, value_))
    credit = property(itemgetter(2), lambda self_, value_: setitem(self_, 2, value_))
    datetime = property(itemgetter(3), lambda self_, value_: setitem(self_, 3, value_))
    tarif_id = property(itemgetter(4), lambda self_, value_: setitem(self_, 4, value_))
    access_parameters_id = property(itemgetter(5), lambda self_, value_: setitem(self_, 5, value_))
    time_access_service_id = property(itemgetter(6), lambda self_, value_: setitem(self_, 6, value_))
    traffic_transmit_service_id = property(itemgetter(7), lambda self_, value_: setitem(self_, 7, value_))
    cost = property(itemgetter(8), lambda self_, value_: setitem(self_, 8, value_))
    reset_tarif_cost = property(itemgetter(9), lambda self_, value_: setitem(self_, 9, value_))
    settlement_period_id = property(itemgetter(10), lambda self_, value_: setitem(self_, 10, value_))
    tarif_active = property(itemgetter(11), lambda self_, value_: setitem(self_, 11, value_))
    acctf_id = property(itemgetter(12), lambda self_, value_: setitem(self_, 12, value_))
    false_ = property(itemgetter(13), lambda self_, value_: setitem(self_, 13, value_))
    account_created = property(itemgetter(14), lambda self_, value_: setitem(self_, 14, value_))
    disabled_by_limit = property(itemgetter(15), lambda self_, value_: setitem(self_, 15, value_))
    balance_blocked = property(itemgetter(16), lambda self_, value_: setitem(self_, 16, value_))
    ps_null_ballance_checkout = property(itemgetter(17), lambda self_, value_: setitem(self_, 17, value_))
    tarif_deleted = property(itemgetter(18), lambda self_, value_: setitem(self_, 18, value_))
    allow_express_pay = property(itemgetter(19), lambda self_, value_: setitem(self_, 19, value_))
    account_status = property(itemgetter(20), lambda self_, value_: setitem(self_, 20, value_))
    username = property(itemgetter(21), lambda self_, value_: setitem(self_, 21, value_))
    password = property(itemgetter(22), lambda self_, value_: setitem(self_, 22, value_))
    require_tarif_cost = property(itemgetter(23), lambda self_, value_: setitem(self_, 23, value_))
    periodical_billed = property(itemgetter(24), lambda self_, value_: setitem(self_, 24, value_))
    current_acctf = property(itemgetter(25), lambda self_, value_: setitem(self_, 25, value_))
    end_date = property(itemgetter(26), lambda self_, value_: setitem(self_, 26, value_))
    radius_traffic_transmit_service_id = property(itemgetter(27), lambda self_, value_: setitem(self_, 27, value_))
    userblock_max_days = property(itemgetter(28), lambda self_, value_: setitem(self_, 28, value_))
    
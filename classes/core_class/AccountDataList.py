from operator import itemgetter, setitem

class AccountData(list):
    'AccountData(account_id, ballance, credit, datetime, tarif_id, access_parameters_id, time_access_service_id, traffic_transmit_service_id, cost, reset_tarif_cost, settlement_period_id, tarif_active, acctf_id, false_, account_created, disabled_by_limit, balance_blocked, nas_id, vpn_ip_address, ipn_ip_address, ipn_mac_address, assign_ipn_ip_from_dhcp, ipn_status, ipn_speed, vpn_speed, ipn_added, ps_null_ballance_checkout, tarif_deleted, allow_express_pay, account_status, allow_vpn_null, allow_vpn_block, username, password, require_tarif_cost, periodical_billed, current_acctf, end_date)' 

    __slots__ = () 

    _fields = ('account_id', 'ballance', 'credit', 'datetime', 'tarif_id', 'access_parameters_id', 'time_access_service_id', 'traffic_transmit_service_id', 'cost', 'reset_tarif_cost', 'settlement_period_id', 'tarif_active', 'acctf_id', 'false_', 'account_created', 'disabled_by_limit', 'balance_blocked', 'nas_id', 'vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'assign_ipn_ip_from_dhcp', 'ipn_status', 'ipn_speed', 'vpn_speed', 'ipn_added', 'ps_null_ballance_checkout', 'tarif_deleted', 'allow_express_pay', 'account_status', 'allow_vpn_null', 'allow_vpn_block', 'username', 'password', 'require_tarif_cost', 'periodical_billed', 'current_acctf', 'end_date') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __init__(self, empty=True, account_id=None, ballance=None, credit=None, datetime=None, tarif_id=None, access_parameters_id=None, time_access_service_id=None, traffic_transmit_service_id=None, cost=None, reset_tarif_cost=None, settlement_period_id=None, tarif_active=None, acctf_id=None, false_=None, account_created=None, disabled_by_limit=None, balance_blocked=None, nas_id=None, vpn_ip_address=None, ipn_ip_address=None, ipn_mac_address=None, assign_ipn_ip_from_dhcp=None, ipn_status=None, ipn_speed=None, vpn_speed=None, ipn_added=None, ps_null_ballance_checkout=None, tarif_deleted=None, allow_express_pay=None, account_status=None, allow_vpn_null=None, allow_vpn_block=None, username=None, password=None, require_tarif_cost=None, periodical_billed=None, current_acctf=None, end_date=None):
        if empty:
            pass
        else:
            self.extend((account_id, ballance, credit, datetime, tarif_id, access_parameters_id, time_access_service_id, traffic_transmit_service_id, cost, reset_tarif_cost, settlement_period_id, tarif_active, acctf_id, false_, account_created, disabled_by_limit, balance_blocked, nas_id, vpn_ip_address, ipn_ip_address, ipn_mac_address, assign_ipn_ip_from_dhcp, ipn_status, ipn_speed, vpn_speed, ipn_added, ps_null_ballance_checkout, tarif_deleted, allow_express_pay, account_status, allow_vpn_null, allow_vpn_block, username, password, require_tarif_cost, periodical_billed, current_acctf, end_date)) 
                
    @classmethod
    def _make(cls, iterable):
        'Make a new AccountData object from a sequence or iterable'
        result = cls()
        result.extend(iterable)
        if len(result) < 38:
            result.extend([None for i in xrange(38 - len(result))])
        return result 

    def __repr__(self):
        try:
            return 'AccountData(account_id=%r, ballance=%r, credit=%r, datetime=%r, tarif_id=%r, access_parameters_id=%r, time_access_service_id=%r, traffic_transmit_service_id=%r, cost=%r, reset_tarif_cost=%r, settlement_period_id=%r, tarif_active=%r, acctf_id=%r, false_=%r, account_created=%r, disabled_by_limit=%r, balance_blocked=%r, nas_id=%r, vpn_ip_address=%r, ipn_ip_address=%r, ipn_mac_address=%r, assign_ipn_ip_from_dhcp=%r, ipn_status=%r, ipn_speed=%r, vpn_speed=%r, ipn_added=%r, ps_null_ballance_checkout=%r, tarif_deleted=%r, allow_express_pay=%r, account_status=%r, allow_vpn_null=%r, allow_vpn_block=%r, username=%r, password=%r, require_tarif_cost=%r, periodical_billed=%r, current_acctf=%r, end_date=%r)' % tuple(self) 
        except:
            return repr(tuple(self)) 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'account_id': t[0], 'ballance': t[1], 'credit': t[2], 'datetime': t[3], 'tarif_id': t[4], 'access_parameters_id': t[5], 'time_access_service_id': t[6], 'traffic_transmit_service_id': t[7], 'cost': t[8], 'reset_tarif_cost': t[9], 'settlement_period_id': t[10], 'tarif_active': t[11], 'acctf_id': t[12], 'false_': t[13], 'account_created': t[14], 'disabled_by_limit': t[15], 'balance_blocked': t[16], 'nas_id': t[17], 'vpn_ip_address': t[18], 'ipn_ip_address': t[19], 'ipn_mac_address': t[20], 'assign_ipn_ip_from_dhcp': t[21], 'ipn_status': t[22], 'ipn_speed': t[23], 'vpn_speed': t[24], 'ipn_added': t[25], 'ps_null_ballance_checkout': t[26], 'tarif_deleted': t[27], 'allow_express_pay': t[28], 'account_status': t[29], 'allow_vpn_null': t[30], 'allow_vpn_block': t[31], 'username': t[32], 'password': t[33], 'require_tarif_cost': t[34], 'periodical_billed': t[35], 'current_acctf': t[36], 'end_date': t[37]} 

    def _replace(self, **kwds):
        'Return a new AccountData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('account_id', 'ballance', 'credit', 'datetime', 'tarif_id', 'access_parameters_id', 'time_access_service_id', 'traffic_transmit_service_id', 'cost', 'reset_tarif_cost', 'settlement_period_id', 'tarif_active', 'acctf_id', 'false_', 'account_created', 'disabled_by_limit', 'balance_blocked', 'nas_id', 'vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'assign_ipn_ip_from_dhcp', 'ipn_status', 'ipn_speed', 'vpn_speed', 'ipn_added', 'ps_null_ballance_checkout', 'tarif_deleted', 'allow_express_pay', 'account_status', 'allow_vpn_null', 'allow_vpn_block', 'username', 'password', 'require_tarif_cost', 'periodical_billed', 'current_acctf', 'end_date'), self))
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
    nas_id = property(itemgetter(17), lambda self_, value_: setitem(self_, 17, value_))
    vpn_ip_address = property(itemgetter(18), lambda self_, value_: setitem(self_, 18, value_))
    ipn_ip_address = property(itemgetter(19), lambda self_, value_: setitem(self_, 19, value_))
    ipn_mac_address = property(itemgetter(20), lambda self_, value_: setitem(self_, 20, value_))
    assign_ipn_ip_from_dhcp = property(itemgetter(21), lambda self_, value_: setitem(self_, 21, value_))
    ipn_status = property(itemgetter(22), lambda self_, value_: setitem(self_, 22, value_))
    ipn_speed = property(itemgetter(23), lambda self_, value_: setitem(self_, 23, value_))
    vpn_speed = property(itemgetter(24), lambda self_, value_: setitem(self_, 24, value_))
    ipn_added = property(itemgetter(25), lambda self_, value_: setitem(self_, 25, value_))
    ps_null_ballance_checkout = property(itemgetter(26), lambda self_, value_: setitem(self_, 26, value_))
    tarif_deleted = property(itemgetter(27), lambda self_, value_: setitem(self_, 27, value_))
    allow_express_pay = property(itemgetter(28), lambda self_, value_: setitem(self_, 28, value_))
    account_status = property(itemgetter(29), lambda self_, value_: setitem(self_, 29, value_))
    allow_vpn_null = property(itemgetter(30), lambda self_, value_: setitem(self_, 30, value_))
    allow_vpn_block = property(itemgetter(31), lambda self_, value_: setitem(self_, 31, value_))
    username = property(itemgetter(32), lambda self_, value_: setitem(self_, 32, value_))
    password = property(itemgetter(33), lambda self_, value_: setitem(self_, 33, value_))
    require_tarif_cost = property(itemgetter(34), lambda self_, value_: setitem(self_, 34, value_))
    periodical_billed = property(itemgetter(35), lambda self_, value_: setitem(self_, 35, value_))
    current_acctf = property(itemgetter(36), lambda self_, value_: setitem(self_, 36, value_))
    end_date = property(itemgetter(37), lambda self_, value_: setitem(self_, 37, value_))

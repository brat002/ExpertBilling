from operator import itemgetter, setitem

class AccountData(tuple):
    'AccountData(account_id, ballance, credit, datetime, tarif_id, access_parameters_id, time_access_service_id, traffic_transmit_service_id, cost, reset_tarif_cost, settlement_period_id, tarif_active, acctf_id, false_, account_created, disabled_by_limit, balance_blocked, nas_id, vpn_ip_address, ipn_ip_address, ipn_mac_address, assign_ipn_ip_from_dhcp, ipn_status, ipn_speed, vpn_speed, ipn_added, ps_null_ballance_checkout, tarif_deleted, allow_express_pay, account_status, allow_vpn_null, allow_vpn_block, username, password, require_tarif_cost, current_acctf)' 

    __slots__ = () 

    _fields = ('account_id', 'ballance', 'credit', 'datetime', 'tarif_id', 'access_parameters_id', 'time_access_service_id', 'traffic_transmit_service_id', 'cost', 'reset_tarif_cost', 'settlement_period_id', 'tarif_active', 'acctf_id', 'false_', 'account_created', 'disabled_by_limit', 'balance_blocked', 'nas_id', 'vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'assign_ipn_ip_from_dhcp', 'ipn_status', 'ipn_speed', 'vpn_speed', 'ipn_added', 'ps_null_ballance_checkout', 'tarif_deleted', 'allow_express_pay', 'account_status', 'allow_vpn_null', 'allow_vpn_block', 'username', 'password', 'require_tarif_cost', 'current_acctf') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, account_id, ballance, credit, datetime, tarif_id, access_parameters_id, time_access_service_id, traffic_transmit_service_id, cost, reset_tarif_cost, settlement_period_id, tarif_active, acctf_id, false_, account_created, disabled_by_limit, balance_blocked, nas_id, vpn_ip_address, ipn_ip_address, ipn_mac_address, assign_ipn_ip_from_dhcp, ipn_status, ipn_speed, vpn_speed, ipn_added, ps_null_ballance_checkout, tarif_deleted, allow_express_pay, account_status, allow_vpn_null, allow_vpn_block, username, password, require_tarif_cost, current_acctf):
        return tuple.__new__(cls, (account_id, ballance, credit, datetime, tarif_id, access_parameters_id, time_access_service_id, traffic_transmit_service_id, cost, reset_tarif_cost, settlement_period_id, tarif_active, acctf_id, false_, account_created, disabled_by_limit, balance_blocked, nas_id, vpn_ip_address, ipn_ip_address, ipn_mac_address, assign_ipn_ip_from_dhcp, ipn_status, ipn_speed, vpn_speed, ipn_added, ps_null_ballance_checkout, tarif_deleted, allow_express_pay, account_status, allow_vpn_null, allow_vpn_block, username, password, require_tarif_cost, current_acctf)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new AccountData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 36:
            raise TypeError('Expected 36 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'AccountData(account_id=%r, ballance=%r, credit=%r, datetime=%r, tarif_id=%r, access_parameters_id=%r, time_access_service_id=%r, traffic_transmit_service_id=%r, cost=%r, reset_tarif_cost=%r, settlement_period_id=%r, tarif_active=%r, acctf_id=%r, false_=%r, account_created=%r, disabled_by_limit=%r, balance_blocked=%r, nas_id=%r, vpn_ip_address=%r, ipn_ip_address=%r, ipn_mac_address=%r, assign_ipn_ip_from_dhcp=%r, ipn_status=%r, ipn_speed=%r, vpn_speed=%r, ipn_added=%r, ps_null_ballance_checkout=%r, tarif_deleted=%r, allow_express_pay=%r, account_status=%r, allow_vpn_null=%r, allow_vpn_block=%r, username=%r, password=%r, require_tarif_cost=%r, current_acctf=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'account_id': t[0], 'ballance': t[1], 'credit': t[2], 'datetime': t[3], 'tarif_id': t[4], 'access_parameters_id': t[5], 'time_access_service_id': t[6], 'traffic_transmit_service_id': t[7], 'cost': t[8], 'reset_tarif_cost': t[9], 'settlement_period_id': t[10], 'tarif_active': t[11], 'acctf_id': t[12], 'false_': t[13], 'account_created': t[14], 'disabled_by_limit': t[15], 'balance_blocked': t[16], 'nas_id': t[17], 'vpn_ip_address': t[18], 'ipn_ip_address': t[19], 'ipn_mac_address': t[20], 'assign_ipn_ip_from_dhcp': t[21], 'ipn_status': t[22], 'ipn_speed': t[23], 'vpn_speed': t[24], 'ipn_added': t[25], 'ps_null_ballance_checkout': t[26], 'tarif_deleted': t[27], 'allow_express_pay': t[28], 'account_status': t[29], 'allow_vpn_null': t[30], 'allow_vpn_block': t[31], 'username': t[32], 'password': t[33], 'require_tarif_cost': t[34], 'current_acctf': t[35]} 

    def _replace(self, **kwds):
        'Return a new AccountData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('account_id', 'ballance', 'credit', 'datetime', 'tarif_id', 'access_parameters_id', 'time_access_service_id', 'traffic_transmit_service_id', 'cost', 'reset_tarif_cost', 'settlement_period_id', 'tarif_active', 'acctf_id', 'false_', 'account_created', 'disabled_by_limit', 'balance_blocked', 'nas_id', 'vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'assign_ipn_ip_from_dhcp', 'ipn_status', 'ipn_speed', 'vpn_speed', 'ipn_added', 'ps_null_ballance_checkout', 'tarif_deleted', 'allow_express_pay', 'account_status', 'allow_vpn_null', 'allow_vpn_block', 'username', 'password', 'require_tarif_cost', 'current_acctf'), self))
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
    false_ = property(itemgetter(13))
    account_created = property(itemgetter(14))
    disabled_by_limit = property(itemgetter(15))
    balance_blocked = property(itemgetter(16))
    nas_id = property(itemgetter(17))
    vpn_ip_address = property(itemgetter(18))
    ipn_ip_address = property(itemgetter(19))
    ipn_mac_address = property(itemgetter(20))
    assign_ipn_ip_from_dhcp = property(itemgetter(21))
    ipn_status = property(itemgetter(22))
    ipn_speed = property(itemgetter(23))
    vpn_speed = property(itemgetter(24))
    ipn_added = property(itemgetter(25))
    ps_null_ballance_checkout = property(itemgetter(26))
    tarif_deleted = property(itemgetter(27))
    allow_express_pay = property(itemgetter(28))
    account_status = property(itemgetter(29))
    allow_vpn_null = property(itemgetter(30))
    allow_vpn_block = property(itemgetter(31))
    username = property(itemgetter(32))
    password = property(itemgetter(33))
    require_tarif_cost = property(itemgetter(34))
    current_acctf = property(itemgetter(35))

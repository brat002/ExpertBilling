from operator import itemgetter, setitem

class AccountData(tuple):
    'AccountData(account_id, username, time_access_service_id, nas_id, vpn_ip_address, tarif_id, access_type, account_status, balance_blocked, ballance, disabled_by_limit, tariff_active, radius_traffic_transmit_service_id, vpn_ippool_id, vpn_guest_ippool_id, sessionscount)' 

    __slots__ = () 

    _fields = ('account_id', 'username', 'time_access_service_id',  'nas_id', 'vpn_ip_address', 'tarif_id', 'access_type', 'account_status', 'balance_blocked', 'ballance', 'disabled_by_limit', 'tariff_active', 'radius_traffic_transmit_service_id', 'vpn_ippool_id', 'vpn_guest_ippool_id', 'sessionscount') 

    def __new__(cls, account_id, username, time_access_service_id, nas_id, vpn_ip_address, tarif_id, access_type, account_status, balance_blocked, ballance, disabled_by_limit, tariff_active, radius_traffic_transmit_service_id, vpn_ippool_id, vpn_guest_ippool_id, sessionscount):
        return tuple.__new__(cls, (account_id, username, time_access_service_id, nas_id, vpn_ip_address, tarif_id, access_type, account_status, balance_blocked, ballance, disabled_by_limit, tariff_active, radius_traffic_transmit_service_id, vpn_ippool_id, vpn_guest_ippool_id, sessionscount)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new AccountData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 16:
            raise TypeError('Expected 16 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'AccountData(account_id=%r, username=%r, time_access_service_id=%r, nas_id=%r, vpn_ip_address=%r, tarif_id=%r, access_type=%r, account_status=%r, balance_blocked=%r, ballance=%r, disabled_by_limit=%r, tariff_active=%r, radius_traffic_transmit_service_id=%r, vpn_ippool_id=%r, vpn_guest_ippool_id=%r, sessionscount=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'account_id': t[0], 'username': t[1], 'time_access_service_id': t[2],  'nas_id': t[3], 'vpn_ip_address': t[4], 'tarif_id': t[5], 'access_type': t[6], 'account_status': t[7], 'balance_blocked': t[8], 'ballance': t[9], 'disabled_by_limit': t[10], 'tariff_active': t[11], 'radius_traffic_transmit_service_id':t[12], 'vpn_ippool_id':t[13], 'vpn_guest_ippool_id':t[14], 'sessionscount':t[15]} 

    def _replace(self, **kwds):
        'Return a new AccountData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('account_id', 'username', 'time_access_service_id', 'nas_id', 'vpn_ip_address', 'tarif_id', 'access_type', 'account_status', 'balance_blocked', 'ballance', 'disabled_by_limit', 'tariff_active', 'radius_traffic_transmit_service_id', 'vpn_ippool_id','vpn_guest_ippool_id', 'sessionscount'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    account_id = property(itemgetter(0))
    username = property(itemgetter(1))
    time_access_service_id = property(itemgetter(2))
    nas_id = property(itemgetter(3))
    vpn_ip_address = property(itemgetter(4))
    tarif_id = property(itemgetter(5))
    access_type = property(itemgetter(6))
    account_status = property(itemgetter(7))
    balance_blocked = property(itemgetter(8))
    ballance = property(itemgetter(9))
    disabled_by_limit = property(itemgetter(10))
    tariff_active = property(itemgetter(11))
    radius_traffic_transmit_service_id = property(itemgetter(12))
    vpn_ippool_id = property(itemgetter(13))
    vpn_guest_ippool_id = property(itemgetter(14))
    sessionscount = property(itemgetter(15))
    
    
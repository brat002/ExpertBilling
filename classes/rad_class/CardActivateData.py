from operator import itemgetter, setitem

class CardActivateData(tuple):
    'CardActivateData(account_id, subaccount_id, password, nas_id, tarif_id, account_status, balance_blocked, ballance, disabled_by_limit, tariff_active, ipv4_vpn_pool_id, vpn_ippool_id,vpn_ip_address, ipn_ip_address, ipn_mac_address,access_type)' 

    __slots__ = () 

    _fields = ('account_id', 'subaccount_id','password', 'nas_id', 'tarif_id', 'account_status', 'balance_blocked', 'ballance', 'disabled_by_limit', 'tariff_active', 'ipv4_vpn_pool_id', 'vpn_ippool_id','vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'access_type') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, account_id, subaccount_id, password, nas_id, tarif_id, account_status, balance_blocked, ballance, disabled_by_limit, tariff_active, ipv4_vpn_pool_id, vpn_ippool_id,vpn_ip_address, ipn_ip_address, ipn_mac_address,access_type):
        return tuple.__new__(cls, (account_id, subaccount_id, password, nas_id, tarif_id, account_status, balance_blocked, ballance, disabled_by_limit, tariff_active, ipv4_vpn_pool_id, vpn_ippool_id,vpn_ip_address, ipn_ip_address, ipn_mac_address,access_type)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new CardActivateData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 15:
            raise TypeError('Expected 15 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'CardActivateData(account_id=%r, subaccount_id=%r, password=%r, nas_id=%r, tarif_id=%r, account_status=%r, balance_blocked=%r, ballance=%r, disabled_by_limit=%r, tariff_active=%r, ipv4_vpn_pool_id=%r, vpn_ippool_id=%r, vpn_ip_address=%r, ipn_ip_address=%r, ipn_mac_address=%r,access_type=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'account_id': t[0], 'subaccount_id':t[1], 'password': t[2], 'nas_id': t[3], 'tarif_id': t[4], 'account_status': t[5], 'balance_blocked': t[6], 'ballance': t[7], 'disabled_by_limit': t[8], 'tariff_active': t[9],'ipv4_vpn_pool_id':t[10], 'vpn_ippool_id':t[11],'vpn_ip_address':t[12], 'ipn_ip_address':t[13], 'ipn_mac_address':t[14],'access_type':t[15]} 

    def _replace(self, **kwds):
        'Return a new CardActivateData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('account_id', 'subaccount_id', 'password', 'nas_id', 'tarif_id', 'account_status', 'balance_blocked', 'ballance', 'disabled_by_limit', 'tariff_active', 'ipv4_vpn_pool_id', 'vpn_ippool_id', 'vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'access_type'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    account_id = property(itemgetter(0))
    subaccount_id = property(itemgetter(1))
    password = property(itemgetter(2))
    nas_id = property(itemgetter(3))
    tarif_id = property(itemgetter(4))
    account_status = property(itemgetter(5))
    balance_blocked = property(itemgetter(6))
    ballance = property(itemgetter(7))
    disabled_by_limit = property(itemgetter(8))
    tariff_active = property(itemgetter(9))
    ipv4_vpn_pool_id = property(itemgetter(10))
    vpn_ippool_id = property(itemgetter(11))
    vpn_ip_address = property(itemgetter(12))
    ipn_ip_address = property(itemgetter(13))
    ipn_mac_address = property(itemgetter(14))
    access_type = property(itemgetter(15))
    
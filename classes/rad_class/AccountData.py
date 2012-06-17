from operator import itemgetter, setitem

class AccountData(tuple):
    'AccountData(account_id, username, ipn_mac_address, time_access_service_id, password, nas_id, vpn_ip_address, tarif_id, access_type, account_status, balance_blocked, ballance, disabled_by_limit, vpn_speed, tariff_active, allow_vpn_null, allow_vpn_block, ipn_ip_address, ipn_speed, assign_dhcp_null, assign_dhcp_block, radius_traffic_transmit_service_id, vpn_ippool_id, vpn_guest_ippool_id, sessionscount)' 

    __slots__ = () 

    _fields = ('account_id', 'username', 'ipn_mac_address', 'time_access_service_id', 'password', 'nas_id', 'vpn_ip_address', 'tarif_id', 'access_type', 'account_status', 'balance_blocked', 'ballance', 'disabled_by_limit', 'vpn_speed', 'tariff_active', 'allow_vpn_null', 'allow_vpn_block', 'ipn_ip_address', 'netmask', 'ipn_speed', 'assign_dhcp_null', 'assign_dhcp_block', 'associate_pptp_ipn_ip', 'associate_pppoe_mac', 'radius_traffic_transmit_service_id', 'vpn_ippool_id', 'vpn_guest_ippool_id', 'sessionscount') 

    def __new__(cls, account_id, username, ipn_mac_address, time_access_service_id, password, nas_id, vpn_ip_address, tarif_id, access_type, account_status, balance_blocked, ballance, disabled_by_limit, vpn_speed, tariff_active, allow_vpn_null, allow_vpn_block, ipn_ip_address, ipn_speed, assign_dhcp_null, assign_dhcp_block, associate_pptp_ipn_ip, associate_pppoe_mac, radius_traffic_transmit_service_id, vpn_ippool_id, vpn_guest_ippool_id, sessionscount):
        return tuple.__new__(cls, (account_id, username, ipn_mac_address, time_access_service_id, password, nas_id, vpn_ip_address, tarif_id, access_type, account_status, balance_blocked, ballance, disabled_by_limit, vpn_speed, tariff_active, allow_vpn_null, allow_vpn_block, ipn_ip_address, ipn_speed, assign_dhcp_null, assign_dhcp_block, associate_pptp_ipn_ip, associate_pppoe_mac, radius_traffic_transmit_service_id, vpn_ippool_id, vpn_guest_ippool_id, sessionscount)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new AccountData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 27:
            raise TypeError('Expected 27 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'AccountData(account_id=%r, username=%r, ipn_mac_address=%r, time_access_service_id=%r, password=%r, nas_id=%r, vpn_ip_address=%r, tarif_id=%r, access_type=%r, account_status=%r, balance_blocked=%r, ballance=%r, disabled_by_limit=%r, vpn_speed=%r, tariff_active=%r, allow_vpn_null=%r, allow_vpn_block=%r, ipn_ip_address=%r,  ipn_speed=%r, assign_dhcp_null=%r, assign_dhcp_block=%r, associate_pptp_ipn_ip=%r, associate_pppoe_mac=%r, radius_traffic_transmit_service_id=%r, vpn_ippool_id=%r, vpn_guest_ippool_id=%r, sessionscount=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'account_id': t[0], 'username': t[1], 'ipn_mac_address': t[2], 'time_access_service_id': t[3], 'password': t[4], 'nas_id': t[5], 'vpn_ip_address': t[6], 'tarif_id': t[7], 'access_type': t[8], 'account_status': t[9], 'balance_blocked': t[10], 'ballance': t[11], 'disabled_by_limit': t[12], 'vpn_speed': t[13], 'tariff_active': t[14], 'allow_vpn_null': t[15], 'allow_vpn_block': t[16], 'ipn_ip_address': t[17], 'ipn_speed': t[18], 'assign_dhcp_null': t[19], 'assign_dhcp_block': t[20], 'associate_pptp_ipn_ip': t[21], 'associate_pppoe_mac':t[22], 'radius_traffic_transmit_service_id':t[23], 'vpn_ippool_id':t[24], 'vpn_guest_ippool_id':t[25], 'sessionscount':t[26]} 

    def _replace(self, **kwds):
        'Return a new AccountData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('account_id', 'username', 'ipn_mac_address', 'time_access_service_id', 'password', 'nas_id', 'vpn_ip_address', 'tarif_id', 'access_type', 'account_status', 'balance_blocked', 'ballance', 'disabled_by_limit', 'vpn_speed', 'tariff_active', 'allow_vpn_null', 'allow_vpn_block', 'ipn_ip_address', 'ipn_speed', 'assign_dhcp_null', 'assign_dhcp_block', 'associate_pptp_ipn_ip', 'associate_pppoe_mac', 'radius_traffic_transmit_service_id', 'vpn_ippool_id','vpn_guest_ippool_id', 'sessionscount'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    account_id = property(itemgetter(0))
    username = property(itemgetter(1))
    ipn_mac_address = property(itemgetter(2))
    time_access_service_id = property(itemgetter(3))
    password = property(itemgetter(4))
    nas_id = property(itemgetter(5))
    vpn_ip_address = property(itemgetter(6))
    tarif_id = property(itemgetter(7))
    access_type = property(itemgetter(8))
    account_status = property(itemgetter(9))
    balance_blocked = property(itemgetter(10))
    ballance = property(itemgetter(11))
    disabled_by_limit = property(itemgetter(12))
    vpn_speed = property(itemgetter(13))
    tariff_active = property(itemgetter(14))
    allow_vpn_null = property(itemgetter(15))
    allow_vpn_block = property(itemgetter(16))
    ipn_ip_address = property(itemgetter(17))
    ipn_speed = property(itemgetter(18))
    assign_dhcp_null = property(itemgetter(19))
    assign_dhcp_block = property(itemgetter(20))
    associate_pptp_ipn_ip = property(itemgetter(21)) 
    associate_pppoe_mac = property(itemgetter(22))
    radius_traffic_transmit_service_id = property(itemgetter(23))
    vpn_ippool_id = property(itemgetter(24))
    vpn_guest_ippool_id = property(itemgetter(25))
    sessionscount = property(itemgetter(26))
    
    
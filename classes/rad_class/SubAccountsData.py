from operator import itemgetter, setitem

class SubAccountsData(tuple):
    'SubAccountsData(id, account_id, username, password, vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id,  switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip, associate_pppoe_ipn_mac, vpn_speed, vlan,vpn_ipv6_ip_address, ipv4_vpn_pool_id, sessionscount)' 

    __slots__ = () 

    _fields = ('id', 'account_id', 'username', 'password', 'vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'nas_id',  'switch_id', 'switch_port', 'allow_dhcp', 'allow_dhcp_with_null', 'allow_dhcp_with_minus', 'allow_dhcp_with_block', 'allow_vpn_with_null', 'allow_vpn_with_minus', 'allow_vpn_with_block', 'associate_pptp_ipn_ip', 'associate_pppoe_ipn_mac',  'vpn_speed', 'vlan', 'vpn_ipv6_ip_address', 'ipv4_vpn_pool_id', 'sessionscount') 

    def __new__(cls, id, account_id, username, password, vpn_ip_address, ipn_ip_address,  ipn_mac_address, nas_id,  switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip, associate_pppoe_ipn_mac, vpn_speed, vlan,vpn_ipv6_ip_address, ipv4_vpn_pool_id, sessionscount):
        return tuple.__new__(cls, (id, account_id, username, password, vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id,  switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip, associate_pppoe_ipn_mac, vpn_speed, vlan,vpn_ipv6_ip_address, ipv4_vpn_pool_id, sessionscount)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new RadiusAttrsData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 24:
            raise TypeError('Expected 24 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'SubAccountsData(id=%r, account_id=%r, username=%r, password=%r, vpn_ip_address=%r, ipn_ip_address=%r, ipn_mac_address=%r, nas_id=%r,  switch_id=%r, switch_port=%r, allow_dhcp=%r, allow_dhcp_with_null=%r, allow_dhcp_with_minus=%r, allow_dhcp_with_block=%r, allow_vpn_with_null=%r, allow_vpn_with_minus=%r, allow_vpn_with_block=%r, associate_pptp_ipn_ip=%r, associate_pppoe_ipn_mac=%r, vpn_speed=%r, vlan=%r, vpn_ipv6_ip_address=%r, ipv4_vpn_pool_id=%r, sessionscount=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id':t[0], 'account_id':t[1], 'username':t[2], 'password':t[3], 'vpn_ip_address':t[4], 'ipn_ip_address':t[5], 'ipn_mac_address':t[6], 'nas_id':t[7],  'switch_id':t[8], 'switch_port':t[9], 'allow_dhcp':t[10], 'allow_dhcp_with_null':t[11], 'allow_dhcp_with_minus':t[12], 'allow_dhcp_with_block':t[13], 'allow_vpn_with_null':t[14], 'allow_vpn_with_minus':t[15], 'allow_vpn_with_block':t[16], 'associate_pptp_ipn_ip':t[17], 'associate_pppoe_ipn_mac':t[18],  'vpn_speed':t[19], 'vlan':t[20], 'vpn_ipv6_ip_address':t[21], 'ipv4_vpn_pool_id':t[22], 'sessionscount':t[23]} 

    def _replace(self, **kwds):
        'Return a new RadiusAttrsData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'account_id', 'username', 'password', 'vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'nas_id',  'switch_id', 'switch_port', 'allow_dhcp', 'allow_dhcp_with_null', 'allow_dhcp_with_minus', 'allow_dhcp_with_block', 'allow_vpn_with_null', 'allow_vpn_with_minus', 'allow_vpn_with_block', 'associate_pptp_ipn_ip', 'associate_pppoe_ipn_mac',  'vpn_speed', 'vlan', 'vpn_ipv6_ip_address', 'ipv4_vpn_pool_id', 'sessionscount'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 
    
    id = property(itemgetter(0))
    account_id = property(itemgetter(1))
    username = property(itemgetter(2))
    password = property(itemgetter(3))
    vpn_ip_address = property(itemgetter(4))
    ipn_ip_address = property(itemgetter(5))
    ipn_mac_address = property(itemgetter(6))
    nas_id = property(itemgetter(7))
    switch_id = property(itemgetter(8))
    switch_port = property(itemgetter(9))
    allow_dhcp = property(itemgetter(10))
    allow_dhcp_with_null = property(itemgetter(11))
    allow_dhcp_with_minus = property(itemgetter(12))
    allow_dhcp_with_block = property(itemgetter(13))
    allow_vpn_with_null = property(itemgetter(14))
    allow_vpn_with_minus = property(itemgetter(15))
    allow_vpn_with_block = property(itemgetter(16))
    associate_pptp_ipn_ip = property(itemgetter(17))
    associate_pppoe_ipn_mac = property(itemgetter(18))
    vpn_speed = property(itemgetter(19))
    vlan = property(itemgetter(20))
    vpn_ipv6_ip_address = property(itemgetter(21))
    ipv4_vpn_pool_id = property(itemgetter(22))
    sessionscount = property(itemgetter(23))

    
    
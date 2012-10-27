from operator import itemgetter, setitem

class SubAccountData(tuple):
    'SubAccountsData(id, account_id, username, password, vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, ipn_added, ipn_enabled, need_resync, speed, switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip, associate_pppoe_ipn_mac, ipn_speed, vpn_speed, allow_addonservice, allow_ipn_with_null, allow_ipn_with_minus, allow_ipn_with_block, vlan,vpn_ipv6_ip_address, ipv4_ipn_pool_id,ipv4_vpn_pool_id)' 

    __slots__ = () 

    _fields = ('id', 'account_id', 'username', 'password', 'vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'nas_id', 'ipn_added', 'ipn_enabled', 'need_resync', 'speed', 'switch_id', 'switch_port', 'allow_dhcp', 'allow_dhcp_with_null', 'allow_dhcp_with_minus', 'allow_dhcp_with_block', 'allow_vpn_with_null', 'allow_vpn_with_minus', 'allow_vpn_with_block', 'associate_pptp_ipn_ip', 'associate_pppoe_ipn_mac', 'ipn_speed', 'vpn_speed', 'allow_addonservice', 'allow_ipn_with_null', 'allow_ipn_with_minus', 'allow_ipn_with_block', 'vlan', 'vpn_ipv6_ip_address', 'ipv4_ipn_pool_id', 'ipv4_vpn_pool_id') 

    def __new__(cls, id, account_id, username, password, vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, ipn_added, ipn_enabled, need_resync, speed, switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip, associate_pppoe_ipn_mac, ipn_speed, vpn_speed, allow_addonservice, allow_ipn_with_null, allow_ipn_with_minus, allow_ipn_with_block, vlan, vpn_ipv6_ip_address,ipv4_ipn_pool_id,ipv4_vpn_pool_id):
        return tuple.__new__(cls, (id, account_id, username, password, vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, ipn_added, ipn_enabled, need_resync, speed, switch_id, switch_port, allow_dhcp, allow_dhcp_with_null, allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip, associate_pppoe_ipn_mac, ipn_speed, vpn_speed, allow_addonservice, allow_ipn_with_null, allow_ipn_with_minus, allow_ipn_with_block, vlan, vpn_ipv6_ip_address,ipv4_ipn_pool_id,ipv4_vpn_pool_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new RadiusAttrsData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 33:
            raise TypeError('Expected 33 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'SubAccountData(id=%r, account_id=%r, username=%r, password=%r, vpn_ip_address=%r, ipn_ip_address=%r, ipn_mac_address=%r, nas_id=%r, ipn_added=%r, ipn_enabled=%r, need_resync=%r, speed=%r, switch_id=%r, switch_port=%r, allow_dhcp=%r, allow_dhcp_with_null=%r, allow_dhcp_with_minus=%r, allow_dhcp_with_block=%r, allow_vpn_with_null=%r, allow_vpn_with_minus=%r, allow_vpn_with_block=%r, associate_pptp_ipn_ip=%r, associate_pppoe_ipn_mac=%r, ipn_speed=%r, vpn_speed=%r, allow_addonservice=%r, allow_ipn_with_null=%r, allow_ipn_with_minus=%r, allow_ipn_with_block=%r, vlan=%r, vpn_ipv6_ip_address=%r,ipv4_ipn_pool_id=%r,ipv4_vpn_pool_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id':t[0], 'account_id':t[1], 'username':t[2], 'password':t[3], 'vpn_ip_address':t[4], 'ipn_ip_address':t[5], 'ipn_mac_address':t[6], 'nas_id':t[7], 'ipn_added':t[8], 'ipn_enabled':t[9], 'need_resync':t[10], 'speed':t[11], 'switch_id':t[12], 'switch_port':t[13], 'allow_dhcp':t[14], 'allow_dhcp_with_null':t[15], 'allow_dhcp_with_minus':t[16], 'allow_dhcp_with_block':t[17], 'allow_vpn_with_null':t[18], 'allow_vpn_with_minus':t[19], 'allow_vpn_with_block':t[20], 'associate_pptp_ipn_ip':t[21], 'associate_pppoe_ipn_mac':t[22], 'ipn_speed':t[23], 'vpn_speed':t[24], 'allow_addonservice':t[25], 'allow_ipn_with_null':t[26], 'allow_ipn_with_minus':t[27], 'allow_ipn_with_block':t[28], 'vlan':t[29], 'vpn_ipv6_ip_address':t[30], 'ipv4_ipn_pool_id':t[31], 'ipv4_vpn_pool_id':t[32]} 

    def _replace(self, **kwds):
        'Return a new RadiusAttrsData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'account_id', 'username', 'password', 'vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'nas_id', 'ipn_added', 'ipn_enabled', 'need_resync', 'speed', 'switch_id', 'switch_port', 'allow_dhcp', 'allow_dhcp_with_null', 'allow_dhcp_with_minus', 'allow_dhcp_with_block', 'allow_vpn_with_null', 'allow_vpn_with_minus', 'allow_vpn_with_block', 'associate_pptp_ipn_ip', 'associate_pppoe_ipn_mac', 'ipn_speed', 'vpn_speed', 'allow_addonservice', 'allow_ipn_with_null', 'allow_ipn_with_minus', 'allow_ipn_with_block', 'vlan', 'vpn_ipv6_ip_address','ipv4_ipn_pool_id', 'ipv4_vpn_pool_id'), self))
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
    ipn_added = property(itemgetter(8))
    ipn_enabled = property(itemgetter(9))
    need_resync = property(itemgetter(10))
    speed = property(itemgetter(11))
    switch_id = property(itemgetter(12))
    switch_port = property(itemgetter(13))
    allow_dhcp = property(itemgetter(14)) 
    allow_dhcp_with_null = property(itemgetter(15))
    allow_dhcp_with_minus = property(itemgetter(16)) 
    allow_dhcp_with_block = property(itemgetter(17)) 
    allow_vpn_with_null = property(itemgetter(18)) 
    allow_vpn_with_minus = property(itemgetter(19)) 
    allow_vpn_with_block = property(itemgetter(20)) 
    associate_pptp_ipn_ip = property(itemgetter(21)) 
    associate_pppoe_ipn_mac = property(itemgetter(22)) 
    ipn_speed = property(itemgetter(23))
    vpn_speed = property(itemgetter(24))
    allow_addonservice = property(itemgetter(25))
    allow_ipn_with_null = property(itemgetter(26))
    allow_ipn_with_minus = property(itemgetter(27))
    allow_ipn_with_block = property(itemgetter(28))
    vlan = property(itemgetter(29))
    vpn_ipv6_ip_address = property(itemgetter(30))
    ipv4_ipn_pool_id = property(itemgetter(31))
    ipv4_vpn_pool_id = property(itemgetter(32))
    
    
    
from operator import itemgetter, setitem

class SubAccountsData(tuple):
    'SubAccountsData(account_id, username, password, vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, ipn_added, ipn_enabled, need_resync)' 

    __slots__ = () 

    _fields = ('account_id', 'username', 'password', 'vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'nas_id', 'ipn_added', 'ipn_enabled', 'need_resync') 

    def __new__(cls, account_id, username, password, vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, ipn_added, ipn_enabled, need_resync):
        return tuple.__new__(cls, (account_id, username, password, vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, ipn_added, ipn_enabled, need_resync)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new RadiusAttrsData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 10:
            raise TypeError('Expected 10 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'SubAccountsData(account_id=%r, username=%r, password=%r, vpn_ip_address=%r, ipn_ip_address=%r, ipn_mac_address=%r, nas_id=%r, ipn_added=%r, ipn_enabled=%r, need_resync=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'account_id':t[0], 'username':t[1], 'password':t[2], 'vpn_ip_address':t[3], 'ipn_ip_address':t[4], 'ipn_mac_address':t[5], 'nas_id':t[6], 'ipn_added':t[7], 'ipn_enabled':t[8], 'need_resync':t[9]} 

    def _replace(self, **kwds):
        'Return a new RadiusAttrsData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('account_id', 'username', 'password', 'vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'nas_id', 'ipn_added', 'ipn_enabled', 'need_resync'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    account_id = property(itemgetter(0))
    username = property(itemgetter(1))
    password = property(itemgetter(2))
    vpn_ip_address = property(itemgetter(3))
    ipn_ip_address = property(itemgetter(4))
    ipn_mac_address = property(itemgetter(5))
    nas_id = property(itemgetter(6))
    ipn_added = property(itemgetter(7))
    ipn_enabled = property(itemgetter(8))
    need_resync = property(itemgetter(9))

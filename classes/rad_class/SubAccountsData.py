from operator import itemgetter, setitem

class SubAccountsData(tuple):
    'SubAccountsData(id, account_id, username, password, vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, ipn_added, ipn_enabled, need_resync)' 

    __slots__ = () 

    _fields = ('id', 'account_id', 'username', 'password', 'vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'nas_id', 'ipn_added', 'ipn_enabled', 'need_resync') 

    def __new__(cls, id, account_id, username, password, vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, ipn_added, ipn_enabled, need_resync):
        return tuple.__new__(cls, (id, account_id, username, password, vpn_ip_address, ipn_ip_address, ipn_mac_address, nas_id, ipn_added, ipn_enabled, need_resync)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new RadiusAttrsData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 11:
            raise TypeError('Expected 11 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'SubAccountsData(id=%r, account_id=%r, username=%r, password=%r, vpn_ip_address=%r, ipn_ip_address=%r, ipn_mac_address=%r, nas_id=%r, ipn_added=%r, ipn_enabled=%r, need_resync=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id':t[0], 'account_id':t[1], 'username':t[2], 'password':t[3], 'vpn_ip_address':t[4], 'ipn_ip_address':t[5], 'ipn_mac_address':t[6], 'nas_id':t[7], 'ipn_added':t[8], 'ipn_enabled':t[9], 'need_resync':t[10]} 

    def _replace(self, **kwds):
        'Return a new RadiusAttrsData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'account_id', 'username', 'password', 'vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'nas_id', 'ipn_added', 'ipn_enabled', 'need_resync'), self))
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

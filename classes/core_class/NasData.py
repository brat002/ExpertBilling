from operator import itemgetter, setitem

class NasData(tuple):
    'NasData(id, type, name, ipaddress, secret, login, password, allow_pptp, allow_pppoe, allow_ipn, user_add_action, user_enable_action, user_disable_action, user_delete_action, vpn_speed_action, ipn_speed_action, reset_action, confstring, multilink, speed_vendor_1, speed_vendor_2, speed_attr_id1, speed_attr_id2, speed_value1, speed_value2, identify, subacc_add_action, subacc_enable_action, subacc_disable_action,subacc_del_action, subacc_ipn_speed_action, acct_interim_interval)' 

    __slots__ = () 

    _fields = ('id', 'type', 'name', 'ipaddress', 'secret', 'login', 'password', 'allow_pptp', 'allow_pppoe', 'allow_ipn', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'confstring', 'multilink', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'identify', 'subacc_add_action', 'subacc_enable_action', 'subacc_disable_action', 'subacc_del_action', 'subacc_ipn_speed_action', 'acct_interim_interval') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, type, name, ipaddress, secret, login, password, allow_pptp, allow_pppoe, allow_ipn, user_add_action, user_enable_action, user_disable_action, user_delete_action, vpn_speed_action, ipn_speed_action, reset_action, confstring, multilink, speed_vendor_1, speed_vendor_2, speed_attr_id1, speed_attr_id2, speed_value1, speed_value2, identify, subacc_add_action, subacc_enable_action, subacc_disable_action,subacc_del_action, subacc_ipn_speed_action, acct_interim_interval):
        return tuple.__new__(cls, (id, type, name, ipaddress, secret, login, password, allow_pptp, allow_pppoe, allow_ipn, user_add_action, user_enable_action, user_disable_action, user_delete_action, vpn_speed_action, ipn_speed_action, reset_action, confstring, multilink, speed_vendor_1, speed_vendor_2, speed_attr_id1, speed_attr_id2, speed_value1, speed_value2, identify, subacc_add_action, subacc_enable_action, subacc_disable_action,subacc_del_action, subacc_ipn_speed_action, acct_interim_interval)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new NasData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 32:
            raise TypeError('Expected 32 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'NasData(id=%r, type=%r, name=%r, ipaddress=%r, secret=%r, login=%r, password=%r, allow_pptp=%r, allow_pppoe=%r, allow_ipn=%r, user_add_action=%r, user_enable_action=%r, user_disable_action=%r, user_delete_action=%r, vpn_speed_action=%r, ipn_speed_action=%r, reset_action=%r, confstring=%r, multilink=%r, speed_vendor_1=%r, speed_vendor_2=%r, speed_attr_id1=%r, speed_attr_id2=%r, speed_value1=%r, speed_value2=%r, identify=%r, subacc_add_action=%r, subacc_enable_action=%r, subacc_disable_action=%r, subacc_del_action=%r, subacc_ipn_speed_action=%r, acct_interim_interval=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'type': t[1], 'name': t[2], 'ipaddress': t[3], 'secret': t[4], 'login': t[5], 'password': t[6], 'allow_pptp': t[7], 'allow_pppoe': t[8], 'allow_ipn': t[9], 'user_add_action': t[10], 'user_enable_action': t[11], 'user_disable_action': t[12], 'user_delete_action': t[13], 'vpn_speed_action': t[14], 'ipn_speed_action': t[15], 'reset_action': t[16], 'confstring': t[17], 'multilink': t[18], 'speed_vendor_1':t[19], 'speed_vendor_2':t[20], 'speed_attr_id1':t[21], 'speed_attr_id2':t[22], 'speed_value1':t[23], 'speed_value2':t[24], 'identify':t[25], 'subacc_add_action':t[26], 'subacc_enable_action':t[27], 'subacc_disable_action':t[28], 'subacc_del_action':t[29], 'subacc_ipn_speed_action':t[30], 'acct_interim_interval':t[31]} 

    def _replace(self, **kwds):
        'Return a new NasData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'type', 'name', 'ipaddress', 'secret', 'login', 'password', 'allow_pptp', 'allow_pppoe', 'allow_ipn', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'confstring', 'multilink', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'identify', 'subacc_add_action', 'subacc_enable_action', 'subacc_disable_action', 'subacc_del_action', 'subacc_ipn_speed_action', 'acct_interim_interval'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    type = property(itemgetter(1))
    name = property(itemgetter(2))
    ipaddress = property(itemgetter(3))
    secret = property(itemgetter(4))
    login = property(itemgetter(5))
    password = property(itemgetter(6))
    allow_pptp = property(itemgetter(7))
    allow_pppoe = property(itemgetter(8))
    allow_ipn = property(itemgetter(9))
    user_add_action = property(itemgetter(10))
    user_enable_action = property(itemgetter(11))
    user_disable_action = property(itemgetter(12))
    user_delete_action = property(itemgetter(13))
    vpn_speed_action = property(itemgetter(14))
    ipn_speed_action = property(itemgetter(15))
    reset_action = property(itemgetter(16))
    confstring = property(itemgetter(17))
    multilink = property(itemgetter(18))
    speed_vendor_1 = property(itemgetter(19))
    speed_vendor_2 = property(itemgetter(20)) 
    speed_attr_id1 = property(itemgetter(21))
    speed_attr_id2 = property(itemgetter(22))
    speed_value1 = property(itemgetter(23))
    speed_value2 = property(itemgetter(24))
    identify = property(itemgetter(25))
    subacc_add_action = property(itemgetter(26))
    subacc_enable_action = property(itemgetter(27))
    subacc_disable_action = property(itemgetter(28))
    subacc_del_action = property(itemgetter(29))
    subacc_ipn_speed_action = property(itemgetter(30))
    acct_interim_interval = property(itemgetter(31))

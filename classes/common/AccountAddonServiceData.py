from operator import itemgetter, setitem

class AccountAddonServiceData(tuple):
    'AccountAddonServiceData(id, service_id, account_id, activated, deactivated, action_status, speed_status, temporary_blocked, last_checkout)' 

    __slots__ = () 

    _fields = ('id', 'service_id', 'account_id', 'activated', 'deactivated', 'action_status', 'speed_status', 'temporary_blocked', 'last_checkout') 

    def __new__(cls, id, service_id, account_id, activated, deactivated, action_status, speed_status, temporary_blocked, last_checkout):
        return tuple.__new__(cls, (id, service_id, account_id, activated, deactivated, action_status, speed_status, temporary_blocked, last_checkout)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new AccountAddonServiceData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 9:
            raise TypeError('Expected 8 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'AccountAddonServiceData(id=%r, service_id=%r, account_id=%r, activated=%r, deactivated=%r, action_status=%r, speed_status=%r, temporary_blocked=%r, last_checkout=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'service_id': t[1], 'account_id': t[2], 'activated': t[3], 'deactivated': t[4], 'action_status': t[5], 'speed_status': t[6], 'temporary_blocked': t[7], 'last_checkout':t[8]} 

    def _replace(self, **kwds):
        'Return a new AccountAddonServiceData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'service_id', 'account_id', 'activated', 'deactivated', 'action_status', 'speed_status', 'temporary_blocked', 'last_checkout'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    service_id = property(itemgetter(1))
    account_id = property(itemgetter(2))
    activated = property(itemgetter(3))
    deactivated = property(itemgetter(4))
    action_status = property(itemgetter(5))
    speed_status = property(itemgetter(6))
    temporary_blocked = property(itemgetter(7))
    last_checkout = property(itemgetter(9))
    

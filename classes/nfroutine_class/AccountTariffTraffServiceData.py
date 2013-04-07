from operator import itemgetter, setitem

class AccountTariffTraffServiceData(tuple):
    'AccountTariffTraffServiceData(id, account_id, tariff_id,traffic_transmit_service_id)' 

    __slots__ = () 

    _fields = ('id', 'account_id', 'tariff_id', 'traffic_transmit_service_id') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, account_id, tariff_id, traffic_transmit_service_id):
        return tuple.__new__(cls, (id, account_id, tariff_id, traffic_transmit_service_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new AccountTariffTraffServiceData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 4:
            raise TypeError('Expected 4 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'AccountTariffTraffServiceData(id=%r, account_id=%r, tariff_id=%r, traffic_transmit_service_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'account_id': t[1], 'tariff_id':t[2], 'traffic_transmit_service_id': t[3]} 

    def _replace(self, **kwds):
        'Return a new AccountTariffTraffServiceData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'account_id', 'tariff_id', 'traffic_transmit_service_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    
    id = property(itemgetter(0))
    account_id = property(itemgetter(1))
    tariff_id = property(itemgetter(2))
    traffic_transmit_service_id = property(itemgetter(3))

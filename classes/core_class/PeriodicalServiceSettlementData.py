from operator import itemgetter, setitem

class PeriodicalServiceSettlementData(tuple):
    'PeriodicalServiceSettlementData(ps_id, ps_name, cost, cash_method, sp_name, time_start, length, length_in, autostart, tarif_id, condition, created)' 

    __slots__ = () 

    _fields = ('ps_id', 'ps_name', 'cost', 'cash_method', 'sp_name', 'time_start', 'length', 'length_in', 'autostart', 'tarif_id', 'condition', 'created') 

    def __new__(cls, ps_id, ps_name, cost, cash_method, sp_name, time_start, length, length_in, autostart, tarif_id, condition, created):
        return tuple.__new__(cls, (ps_id, ps_name, cost, cash_method, sp_name, time_start, length, length_in, autostart, tarif_id, condition, created)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new PeriodicalServiceSettlementData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 12:
            raise TypeError('Expected 12 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'PeriodicalServiceSettlementData(ps_id=%r, ps_name=%r, cost=%r, cash_method=%r, sp_name=%r, time_start=%r, length=%r, length_in=%r, autostart=%r, tarif_id=%r, condition=%r, created=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'ps_id': t[0], 'ps_name': t[1], 'cost': t[2], 'cash_method': t[3], 'sp_name': t[4], 'time_start': t[5], 'length': t[6], 'length_in': t[7], 'autostart': t[8], 'tarif_id': t[9], 'condition': t[10], 'created': t[11]} 

    def _replace(self, **kwds):
        'Return a new PeriodicalServiceSettlementData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('ps_id', 'ps_name', 'cost', 'cash_method', 'sp_name', 'time_start', 'length', 'length_in', 'autostart', 'tarif_id', 'condition', 'created'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    ps_id = property(itemgetter(0))
    ps_name = property(itemgetter(1))
    cost = property(itemgetter(2))
    cash_method = property(itemgetter(3))
    sp_name = property(itemgetter(4))
    time_start = property(itemgetter(5))
    length = property(itemgetter(6))
    length_in = property(itemgetter(7))
    autostart = property(itemgetter(8))
    tarif_id = property(itemgetter(9))
    condition = property(itemgetter(10))
    created = property(itemgetter(11))

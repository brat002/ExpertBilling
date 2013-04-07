from operator import itemgetter, setitem

class PeriodicalServiceSettlementData(tuple):
    'PeriodicalServiceSettlementData(ps_id, ps_name, cost, cash_method, sp_name, time_start, length, length_in, autostart, tarif_id, condition, condition_summ, created, deactivated, deleted, tpd)' 

    __slots__ = () 

    _fields = ('ps_id', 'ps_name', 'cost', 'cash_method', 'sp_name', 'time_start', 'length', 'length_in', 'autostart', 'tarif_id', 'condition', 'condition_summ', 'created', 'deactivated', 'deleted', 'tpd') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, ps_id, ps_name, cost, cash_method, sp_name, time_start, length, length_in, autostart, tarif_id, condition, condition_summ, created, deactivated, deleted, tpd):
        return tuple.__new__(cls, (ps_id, ps_name, cost, cash_method, sp_name, time_start, length, length_in, autostart, tarif_id, condition, condition_summ, created, deactivated, deleted, tpd)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new PeriodicalServiceSettlementData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 16:
            raise TypeError('Expected 16 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'PeriodicalServiceSettlementData(ps_id=%r, ps_name=%r, cost=%r, cash_method=%r, sp_name=%r, time_start=%r, length=%r, length_in=%r, autostart=%r, tarif_id=%r, condition=%r, condition_summ=%s, created=%r, deactivated=%r, deleted=%r, tpd=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'ps_id': t[0], 'ps_name': t[1], 'cost': t[2], 'cash_method': t[3], 'sp_name': t[4], 'time_start': t[5], 'length': t[6], 'length_in': t[7], 'autostart': t[8], 'tarif_id': t[9], 'condition': t[10], 'condition_summ': t[11],  'created': t[12], 'deactivated':t[13], 'deleted':t[14], 'tpd': t[15]} 

    def _replace(self, **kwds):
        'Return a new PeriodicalServiceSettlementData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('ps_id', 'ps_name', 'cost', 'cash_method', 'sp_name', 'time_start', 'length', 'length_in', 'autostart', 'tarif_id', 'condition', 'condition_summ', 'created', 'deactivated', 'deleted', 'tpd'), self))
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
    condition_summ = property(itemgetter(11))
    created = property(itemgetter(12))
    deactivated = property(itemgetter(13))
    deleted = property(itemgetter(14))
    tpd = property(itemgetter(15))

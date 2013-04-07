from operator import itemgetter, setitem

class AddonServiceData(tuple):
    'AddonServiceData(id, name, allow_activation, service_type, sp_type, sp_period_id, timeperiod_id, cost, cancel_subscription, wyte_period_id, wyte_cost, action, nas_id, service_activation_action, service_deactivation_action, deactivate_service_for_blocked_account, change_speed, change_speed_type, speed_units, max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx, burst_time_tx, burst_time_rx, min_tx, min_rx, priority)' 

    __slots__ = () 

    _fields = ('id', 'name', 'allow_activation', 'service_type', 'sp_type', 'sp_period_id', 'timeperiod_id', 'cost', 'cancel_subscription', 'wyte_period_id', 'wyte_cost', 'action', 'nas_id', 'service_activation_action', 'service_deactivation_action', 'deactivate_service_for_blocked_account', 'change_speed', 'change_speed_type', 'speed_units', 'max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx', 'burst_time_tx', 'burst_time_rx', 'min_tx', 'min_rx', 'priority') 
    def __getstate__(self):
        return tuple(self)
    def __setstate__(self, state):
        return self._make(state)
    def __new__(cls, id, name, allow_activation, service_type, sp_type, sp_period_id, timeperiod_id, cost, cancel_subscription, wyte_period_id, wyte_cost, action, nas_id, service_activation_action, service_deactivation_action, deactivate_service_for_blocked_account, change_speed, change_speed_type, speed_units, max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx, burst_time_tx, burst_time_rx, min_tx, min_rx, priority):
        return tuple.__new__(cls, (id, name, allow_activation, service_type, sp_type, sp_period_id, timeperiod_id, cost, cancel_subscription, wyte_period_id, wyte_cost, action, nas_id, service_activation_action, service_deactivation_action, deactivate_service_for_blocked_account, change_speed, change_speed_type, speed_units, max_tx, max_rx, burst_tx, burst_rx, burst_treshold_tx, burst_treshold_rx, burst_time_tx, burst_time_rx, min_tx, min_rx, priority)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new AddonServiceData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 30:
            raise TypeError('Expected 30 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'AddonServiceData(id=%r, name=%r, allow_activation=%r, service_type=%r, sp_type=%r, sp_period_id=%r, timeperiod_id=%r, cost=%r, cancel_subscription=%r, wyte_period_id=%r, wyte_cost=%r, action=%r, nas_id=%r, service_activation_action=%r, service_deactivation_action=%r, deactivate_service_for_blocked_account=%r, change_speed=%r, change_speed_type=%r, speed_units=%r, max_tx=%r, max_rx=%r, burst_tx=%r, burst_rx=%r, burst_treshold_tx=%r, burst_treshold_rx=%r, burst_time_tx=%r, burst_time_rx=%r, min_tx=%r, min_rx=%r, priority=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'id': t[0], 'name': t[1], 'allow_activation': t[2], 'service_type': t[3], 'sp_type': t[4], 'sp_period_id': t[5], 'timeperiod_id': t[6], 'cost': t[7], 'cancel_subscription': t[8], 'wyte_period_id': t[9], 'wyte_cost': t[10], 'action': t[11], 'nas_id': t[12], 'service_activation_action': t[13], 'service_deactivation_action': t[14], 'deactivate_service_for_blocked_account': t[15], 'change_speed': t[16], 'change_speed_type': t[17], 'speed_units': t[18], 'max_tx': t[19], 'max_rx': t[20], 'burst_tx': t[21], 'burst_rx': t[22], 'burst_treshold_tx': t[23], 'burst_treshold_rx': t[24], 'burst_time_tx': t[25], 'burst_time_rx': t[26], 'min_tx': t[27], 'min_rx': t[28], 'priority': t[29]} 

    def _replace(self, **kwds):
        'Return a new AddonServiceData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('id', 'name', 'allow_activation', 'service_type', 'sp_type', 'sp_period_id', 'timeperiod_id', 'cost', 'cancel_subscription', 'wyte_period_id', 'wyte_cost', 'action', 'nas_id', 'service_activation_action', 'service_deactivation_action', 'deactivate_service_for_blocked_account', 'change_speed', 'change_speed_type', 'speed_units', 'max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx', 'burst_time_tx', 'burst_time_rx', 'min_tx', 'min_rx', 'priority'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    id = property(itemgetter(0))
    name = property(itemgetter(1))
    allow_activation = property(itemgetter(2))
    service_type = property(itemgetter(3))
    sp_type = property(itemgetter(4))
    sp_period_id = property(itemgetter(5))
    timeperiod_id = property(itemgetter(6))
    cost = property(itemgetter(7))
    cancel_subscription = property(itemgetter(8))
    wyte_period_id = property(itemgetter(9))
    wyte_cost = property(itemgetter(10))
    action = property(itemgetter(11))
    nas_id = property(itemgetter(12))
    service_activation_action = property(itemgetter(13))
    service_deactivation_action = property(itemgetter(14))
    deactivate_service_for_blocked_account = property(itemgetter(15))
    change_speed = property(itemgetter(16))
    change_speed_type = property(itemgetter(17))
    speed_units = property(itemgetter(18))
    max_tx = property(itemgetter(19))
    max_rx = property(itemgetter(20))
    burst_tx = property(itemgetter(21))
    burst_rx = property(itemgetter(22))
    burst_treshold_tx = property(itemgetter(23))
    burst_treshold_rx = property(itemgetter(24))
    burst_time_tx = property(itemgetter(25))
    burst_time_rx = property(itemgetter(26))
    min_tx = property(itemgetter(27))
    min_rx = property(itemgetter(28))
    priority = property(itemgetter(29))

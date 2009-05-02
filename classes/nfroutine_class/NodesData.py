from operator import itemgetter, setitem

class NodesData(tuple):
    'NodesData(traffic_node_id, traffic_cost, edge_start, edge_end, time_start, length, repeat_after, group_id, traffic_transmit_service_id)' 

    __slots__ = () 

    _fields = ('traffic_node_id', 'traffic_cost', 'edge_start', 'edge_end', 'time_start', 'length', 'repeat_after', 'group_id', 'traffic_transmit_service_id') 

    def __new__(cls, traffic_node_id, traffic_cost, edge_start, edge_end, time_start, length, repeat_after, group_id, traffic_transmit_service_id):
        return tuple.__new__(cls, (traffic_node_id, traffic_cost, edge_start, edge_end, time_start, length, repeat_after, group_id, traffic_transmit_service_id)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new NodesData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 9:
            raise TypeError('Expected 9 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'NodesData(traffic_node_id=%r, traffic_cost=%r, edge_start=%r, edge_end=%r, time_start=%r, length=%r, repeat_after=%r, group_id=%r, traffic_transmit_service_id=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'traffic_node_id': t[0], 'traffic_cost': t[1], 'edge_start': t[2], 'edge_end': t[3], 'time_start': t[4], 'length': t[5], 'repeat_after': t[6], 'group_id': t[7], 'traffic_transmit_service_id': t[8]} 

    def _replace(self, **kwds):
        'Return a new NodesData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('traffic_node_id', 'traffic_cost', 'edge_start', 'edge_end', 'time_start', 'length', 'repeat_after', 'group_id', 'traffic_transmit_service_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    traffic_node_id = property(itemgetter(0))
    traffic_cost = property(itemgetter(1))
    edge_start = property(itemgetter(2))
    edge_end = property(itemgetter(3))
    time_start = property(itemgetter(4))
    length = property(itemgetter(5))
    repeat_after = property(itemgetter(6))
    group_id = property(itemgetter(7))
    traffic_transmit_service_id = property(itemgetter(8))

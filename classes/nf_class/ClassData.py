from operator import itemgetter, setitem

class ClassData(tuple):
    'ClassData(src_ip, src_mask, dst_ip, dst_mask, next_hop, src_port, dst_port, protocol, passthrough, direction, store, traffic_class_id, weight)' 

    __slots__ = () 

    _fields = ('src_ip', 'src_mask', 'dst_ip', 'dst_mask', 'next_hop', 'src_port', 'dst_port', 'protocol', 'passthrough', 'direction', 'store', 'traffic_class_id', 'weight') 

    def __new__(cls, src_ip, src_mask, dst_ip, dst_mask, next_hop, src_port, dst_port, protocol, passthrough, direction, store, traffic_class_id, weight):
        return tuple.__new__(cls, (src_ip, src_mask, dst_ip, dst_mask, next_hop, src_port, dst_port, protocol, passthrough, direction, store, traffic_class_id, weight)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new ClassData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 13:
            raise TypeError('Expected 13 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'ClassData(src_ip=%r, src_mask=%r, dst_ip=%r, dst_mask=%r, next_hop=%r, src_port=%r, dst_port=%r, protocol=%r, passthrough=%r, direction=%r, store=%r, traffic_class_id=%r, weight=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'src_ip': t[0], 'src_mask': t[1], 'dst_ip': t[2], 'dst_mask': t[3], 'next_hop': t[4], 'src_port': t[5], 'dst_port': t[6], 'protocol': t[7], 'passthrough': t[8], 'direction': t[9], 'store': t[10], 'traffic_class_id': t[11], 'weight': t[12]} 

    def _replace(self, **kwds):
        'Return a new ClassData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('src_ip', 'src_mask', 'dst_ip', 'dst_mask', 'next_hop', 'src_port', 'dst_port', 'protocol', 'passthrough', 'direction', 'store', 'traffic_class_id', 'weight'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    src_ip = property(itemgetter(0))
    src_mask = property(itemgetter(1))
    dst_ip = property(itemgetter(2))
    dst_mask = property(itemgetter(3))
    next_hop = property(itemgetter(4))
    src_port = property(itemgetter(5))
    dst_port = property(itemgetter(6))
    protocol = property(itemgetter(7))
    passthrough = property(itemgetter(8))
    direction = property(itemgetter(9))
    store = property(itemgetter(10))
    traffic_class_id = property(itemgetter(11))
    weight = property(itemgetter(12))

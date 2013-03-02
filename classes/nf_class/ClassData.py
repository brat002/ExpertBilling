from operator import itemgetter, setitem

class ClassData(tuple):
    'ClassData(dst_ip, dst_mask, next_hop, src_port, dst_port, in_index, out_index, src_as, dst_as, protocol, passthrough, traffic_class_id, weight)' 

    __slots__ = () 

    _fields = ('dst_ip', 'dst_mask', 'next_hop', 'src_port', 'dst_port', 'in_index', 'out_index', 'src_as', 'dst_as', 'protocol', 'passthrough', 'traffic_class_id', 'weight') 

    def __new__(cls, dst_ip, dst_mask, next_hop, src_port, dst_port, in_index, out_index, src_as, dst_as, protocol, passthrough,  traffic_class_id, weight):
        return tuple.__new__(cls, (dst_ip, dst_mask, next_hop, src_port, dst_port, in_index, out_index, src_as, dst_as, protocol, passthrough, traffic_class_id, weight)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new ClassData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 13:
            raise TypeError('Expected 13 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'ClassData(dst_ip=%r, dst_mask=%r, next_hop=%r, src_port=%r, dst_port=%r, in_index=%r, out_index=%r, src_as=%r, dst_as=%r, protocol=%r, passthrough=%r, traffic_class_id=%r, weight=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'dst_ip': t[0], 'dst_mask': t[1], 'next_hop': t[2], 'src_port': t[3], 'dst_port': t[4], 'in_index':t[5], 'out_index':t[6], 'src_as':t[7], 'dst_as':t[8], 'protocol': t[9], 'passthrough': t[10], 'traffic_class_id': t[11], 'weight': t[12]} 

    def _replace(self, **kwds):
        'Return a new ClassData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('dst_ip', 'dst_mask', 'next_hop', 'src_port', 'dst_port', 'in_index', 'out_index', 'src_as', 'dst_as', 'protocol', 'passthrough', 'traffic_class_id', 'weight'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self) 

    dst_ip = property(itemgetter(0))
    dst_mask = property(itemgetter(1))
    next_hop = property(itemgetter(2))
    src_port = property(itemgetter(3))
    dst_port = property(itemgetter(4))
    in_index = property(itemgetter(5))
    out_index = property(itemgetter(6))
    src_as = property(itemgetter(7))
    dst_as = property(itemgetter(8))
    protocol = property(itemgetter(9))
    passthrough = property(itemgetter(10))
    traffic_class_id = property(itemgetter(11))
    weight = property(itemgetter(12))

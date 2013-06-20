from operator import itemgetter, setitem

class ClassData(tuple):
    'ClassData(dst_ip, dst_mask, next_hop, src_port, dst_port, in_index, out_index, src_as, dst_as, protocol, passthrough, traffic_class_id, weight, store)' 

    __slots__ = () 

    _fields = ('src_ip', 'src_mask', 'dst_ip', 'dst_mask', 'next_hop', 'src_port', 'dst_port', 'in_index', 'out_index', 'src_as', 'dst_as', 'protocol', 'passthrough', 'traffic_class_id', 'weight' , 'store') 

    def __new__(cls, src_ip, src_mask, dst_ip, dst_mask, next_hop, src_port, dst_port, in_index, out_index, src_as, dst_as, protocol, passthrough,  traffic_class_id, weight, store):
        return tuple.__new__(cls, (src_ip, src_mask, dst_ip, dst_mask, next_hop, src_port, dst_port, in_index, out_index, src_as, dst_as, protocol, passthrough, traffic_class_id, weight, store)) 

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new ClassData object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 16:
            raise TypeError('Expected 16 arguments, got %d' % len(result))
        return result 

    def __repr__(self):
        return 'ClassData(src_ip=%r, src_mask=%r, dst_ip=%r, dst_mask=%r, next_hop=%r, src_port=%r, dst_port=%r, in_index=%r, out_index=%r, src_as=%r, dst_as=%r, protocol=%r, passthrough=%r, traffic_class_id=%r, weight=%r, store=%r)' % self 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'src_ip': t[0], 'src_mask': t[1], 'dst_ip': t[2], 'dst_mask': t[3], 'next_hop': t[4], 'src_port': t[5], 'dst_port': t[6], 'in_index':t[7], 'out_index':t[8], 'src_as':t[9], 'dst_as':t[10], 'protocol': t[11], 'passthrough': t[12], 'traffic_class_id': t[13], 'weight': t[14], 'store': t[15]} 

    def _replace(self, **kwds):
        'Return a new ClassData object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('src_ip', 'src_mask', 'dst_ip', 'dst_mask', 'next_hop', 'src_port', 'dst_port', 'in_index', 'out_index', 'src_as', 'dst_as', 'protocol', 'passthrough', 'traffic_class_id', 'weight', 'store'), self))
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
    in_index = property(itemgetter(7))
    out_index = property(itemgetter(8))
    src_as = property(itemgetter(9))
    dst_as = property(itemgetter(10))
    protocol = property(itemgetter(11))
    passthrough = property(itemgetter(12))
    traffic_class_id = property(itemgetter(13))
    weight = property(itemgetter(14))
    store = property(itemgetter(15))
    
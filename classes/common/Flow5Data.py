from operator import itemgetter, setitem

class Flow5Data(list):
    '''Flow5Data(src_addr, dst_addr, next_hop, in_index, out_index, packets, octets, start, finish, src_port, dst_port, nas_id, tcp_flags, protocol, tos, src_as, dst_as, src_netmask_length, dst_netmask_length, padding, account_id, datetime, class_id, node_direction, class_store, class_passthrough, acctf_id, has_groups, groups) \n
        self.src_addr = self._int_to_ipv4(_ff[0])
        self.dst_addr = self._int_to_ipv4(_ff[1])
        self.next_hop = self._int_to_ipv4(_ff[2])
        self.in_index = _ff[3]
        self.out_index = _ff[4]
        self.packets = _ff[5]
        self.octets = _ff[6]
        self.start = _ff[7]
        self.finish = _ff[8]
        self.src_port = _ff[9]
        self.dst_port = _ff[10]
        [11] - nas_id
        self.tcp_flags = _ff[12]
        self.protocol = _ff[13]
        self.tos = _ff[14]
        self.src_as = _ff[15]
        self.dst_as = _ff[16]
        self.src_netmask_length = _ff[17]
        self.dst_netmask_length = _ff[18]
        [19]- #added_later
        [20] - account_id
        [21] - CURRENT_TIMESTAMP
        [22] - nas_traficclass_id
        [23] - nas_trafficnode.direction
        [24] - nas_trafficclass.store
        [25] - nas.trafficclass.passthrough
        [26] - accounttarif.id
        [27] - hasgroups
        [28] - groups
    ''' 

    __slots__ = () 

    _fields = ('src_addr', 'dst_addr', 'next_hop', 'in_index', 'out_index', 'packets', 'octets', 'start', 'finish', 'src_port', 'dst_port', 'nas_id', 'tcp_flags', 'protocol', 'tos', 'src_as', 'dst_as', 'src_netmask_length', 'dst_netmask_length', 'padding', 'account_id', 'datetime', 'class_id', 'node_direction', 'class_store', 'class_passthrough', 'acctf_id', 'has_groups', 'groups', 'tariff_id') 

    def __init__(self, empty=True, src_addr=None, dst_addr=None, next_hop=None, in_index=None, out_index=None, packets=None, octets=None, start=None, finish=None, src_port=None, dst_port=None, nas_id=None, tcp_flags=None, protocol=None, tos=None, src_as=None, dst_as=None, src_netmask_length=None, dst_netmask_length=None, padding=None, account_id=None, datetime=None, class_id=None, node_direction=None, class_store=None, class_passthrough=None, acctf_id=None, has_groups=None, groups=None, tariff_id=None):
        if empty:
            pass
        else:
            self.extend((src_addr, dst_addr, next_hop, in_index, out_index, packets, octets, start, finish, src_port, dst_port, nas_id, tcp_flags, protocol, tos, src_as, dst_as, src_netmask_length, dst_netmask_length, padding, account_id, datetime, class_id, node_direction, class_store, class_passthrough, acctf_id, has_groups, groups, tariff_id)) 
                
    @classmethod
    def _make(cls, iterable):
        'Make a new Flow5Data object from a sequence or iterable'
        result = cls()
        result.extend(iterable)
        if len(result) < 30:
            result.extend([None for i in xrange(30 - len(result))])
        return result 

    def __repr__(self):
        try:
            return 'Flow5Data(src_addr=%r, dst_addr=%r, next_hop=%r, in_index=%r, out_index=%r, packets=%r, octets=%r, start=%r, finish=%r, src_port=%r, dst_port=%r, nas_id=%r, tcp_flags=%r, protocol=%r, tos=%r, src_as=%r, dst_as=%r, src_netmask_length=%r, dst_netmask_length=%r, padding=%r, account_id=%r, datetime=%r, class_id=%r, node_direction=%r, class_store=%r, class_passthrough=%r, acctf_id=%r, has_groups=%r, groups=%r, tariff_id=%r)' % tuple(self) 
        except:
            return repr(tuple(self)) 

    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {'src_addr': t[0], 'dst_addr': t[1], 'next_hop': t[2], 'in_index': t[3], 'out_index': t[4], 'packets': t[5], 'octets': t[6], 'start': t[7], 'finish': t[8], 'src_port': t[9], 'dst_port': t[10], 'nas_id': t[11], 'tcp_flags': t[12], 'protocol': t[13], 'tos': t[14], 'src_as': t[15], 'dst_as': t[16], 'src_netmask_length': t[17], 'dst_netmask_length': t[18], 'padding': t[19], 'account_id': t[20], 'datetime': t[21], 'class_id': t[22], 'node_direction': t[23], 'class_store': t[24], 'class_passthrough': t[25], 'acctf_id': t[26], 'has_groups': t[27], 'groups': t[28], 'tariff_id': t[29]} 

    def _replace(self, **kwds):
        'Return a new Flow5Data object replacing specified fields with new values'
        result = self._make(map(kwds.pop, ('src_addr', 'dst_addr', 'next_hop', 'in_index', 'out_index', 'packets', 'octets', 'start', 'finish', 'src_port', 'dst_port', 'nas_id', 'tcp_flags', 'protocol', 'tos', 'src_as', 'dst_as', 'src_netmask_length', 'dst_netmask_length', 'padding', 'account_id', 'datetime', 'class_id', 'node_direction', 'class_store', 'class_passthrough', 'acctf_id', 'has_groups', 'groups', 'tariff_id'), self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result 

    def __getnewargs__(self):
        return tuple(self)
    
    def getBaseSlice(self):
        return self.__getslice__(3,30)
    
    def getAddrSlice(self):
        return self.__getslice__(0,3)
    
    src_addr = property(itemgetter(0), lambda self_, value_: setitem(self_, 0, value_))
    dst_addr = property(itemgetter(1), lambda self_, value_: setitem(self_, 1, value_))
    next_hop = property(itemgetter(2), lambda self_, value_: setitem(self_, 2, value_))
    in_index = property(itemgetter(3), lambda self_, value_: setitem(self_, 3, value_))
    out_index = property(itemgetter(4), lambda self_, value_: setitem(self_, 4, value_))
    packets = property(itemgetter(5), lambda self_, value_: setitem(self_, 5, value_))
    octets = property(itemgetter(6), lambda self_, value_: setitem(self_, 6, value_))
    start = property(itemgetter(7), lambda self_, value_: setitem(self_, 7, value_))
    finish = property(itemgetter(8), lambda self_, value_: setitem(self_, 8, value_))
    src_port = property(itemgetter(9), lambda self_, value_: setitem(self_, 9, value_))
    dst_port = property(itemgetter(10), lambda self_, value_: setitem(self_, 10, value_))
    nas_id = property(itemgetter(11), lambda self_, value_: setitem(self_, 11, value_))
    tcp_flags = property(itemgetter(12), lambda self_, value_: setitem(self_, 12, value_))
    protocol = property(itemgetter(13), lambda self_, value_: setitem(self_, 13, value_))
    tos = property(itemgetter(14), lambda self_, value_: setitem(self_, 14, value_))
    src_as = property(itemgetter(15), lambda self_, value_: setitem(self_, 15, value_))
    dst_as = property(itemgetter(16), lambda self_, value_: setitem(self_, 16, value_))
    src_netmask_length = property(itemgetter(17), lambda self_, value_: setitem(self_, 17, value_))
    dst_netmask_length = property(itemgetter(18), lambda self_, value_: setitem(self_, 18, value_))
    padding = property(itemgetter(19), lambda self_, value_: setitem(self_, 19, value_))
    account_id = property(itemgetter(20), lambda self_, value_: setitem(self_, 20, value_))
    datetime = property(itemgetter(21), lambda self_, value_: setitem(self_, 21, value_))
    class_id = property(itemgetter(22), lambda self_, value_: setitem(self_, 22, value_))
    node_direction = property(itemgetter(23), lambda self_, value_: setitem(self_, 23, value_))
    class_store = property(itemgetter(24), lambda self_, value_: setitem(self_, 24, value_))
    class_passthrough = property(itemgetter(25), lambda self_, value_: setitem(self_, 25, value_))
    acctf_id = property(itemgetter(26), lambda self_, value_: setitem(self_, 26, value_))
    has_groups = property(itemgetter(27), lambda self_, value_: setitem(self_, 27, value_))
    groups = property(itemgetter(28), lambda self_, value_: setitem(self_, 28, value_))
    tariff_id = property(itemgetter(29), lambda self_, value_: setitem(self_, 29, value_))

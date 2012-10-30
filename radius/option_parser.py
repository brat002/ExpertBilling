import struct
def parse(nas_type, remote_id, circuit_id):
    identify, vlan, module, port=None,None,None,None
    
    if nas_type=='dlink_35xx':
        port = struct.unpack("!B",circuit_id[-1])[0]
        
        length=struct.unpack("!B",remote_id[3])
        identify=struct.unpack("!%ss" % length,remote_id[4:])[0]
        
    return identify, vlan, module, port
        
        
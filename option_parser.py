import struct

def parse(nas_type, remote_id, circuit_id):
    identify, vlan, module, port=None,None,None,None
    
    if nas_type=='dlink-32xx':
        port = struct.unpack("!B",circuit_id[-1])[0]
        
        length=struct.unpack("!B",remote_id[1])[0]
        identify=remote_id[0:].encode('hex')
        
    return identify, vlan, module, port
        
        
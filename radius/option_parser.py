def parse(nas_type, agent_id, circuit_id):
    identify, vlan, module, port=None,None,None,None
    
    if nas_type=='dlink_35xx':
        port = struct.unpack("!B",agent_id[-1])
        
        length=struct.unpack("!B",circuit_id[3])
        identify=struct.unpack("!%ss" % length,circuit_id[4:])
        
    return identify, vlan, module, port
        
        
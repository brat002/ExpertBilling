def parse(nas_type, agent_id, circuit_id):
    identify, vlan, module, port=None,None,None,None
    
    if nas_type=='dlink_35xx':
        vlan, module,port = struct.unpack("!BBHBB",agent_id)
        
        length=struct.unpack("!B",circuit_id[2:3])[0]
        identify=struct.unpack("!%ss" % length*2,circuit_id[4:4+length*2])
        
    return identify, vlan, module, port
        
        
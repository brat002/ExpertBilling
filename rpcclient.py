import Pyro.core
from mdi.orm.models import Nas
    
# you have to change the URI below to match your own host/port.
connection = Pyro.core.getProxyForURI("PYROLOC://localhost:7766/rpc")
nas=Nas()


#print connection.get(nas, 'all', limit=[0, 10])      

#print connection.get(nas, 'filter', where="id>0", order="id DESC")  
try:
    #a=connection.get(nas, 'update', name="Mikrotik", where="id=1")
    result = connection.sql("SELECT * FROM nas_nas")
    print result['name']
    #print a
    #print a.name
except Exception, x:
    print ''.join(Pyro.util.getPyroTraceback(x))

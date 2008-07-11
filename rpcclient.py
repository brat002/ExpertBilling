import Pyro.core

connection = Pyro.core.getProxyForURI("PYROLOC://localhost:7766/rpc")


class Object(object):
    def __init__(self, result):
        print result
        for key in result:
            print key, result[key]
            setattr(self, key, result[key])
            
    def count(self):
        return len(result)

try:

    result = connection.get("SELECT * FROM nas_nas")

except Exception, x:
    print ''.join(Pyro.util.getPyroTraceback(x))

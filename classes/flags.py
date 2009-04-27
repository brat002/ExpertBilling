from threading import Lock

class Flags(object):
    __slots__ = ('cacheFlag', 'cacheLock')
    def __init__(self):
        self.cacheFlag = False
        self.cacheLock = Lock()
        
class CoreFlags(Flags):
    __slots__ = ()
    def __init__(self):
        super(CoreFlags, self).__init__()
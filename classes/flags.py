from threading import Lock

class Flags(object):
    __slots__ = ('cacheFlag', 'cacheLock', 'writeProf', 'allowedUsersCheck')
    def __init__(self):
        self.cacheFlag = False
        self.cacheLock = Lock()
        self.writeProf = False
        self.allowedUsersCheck = False
        
class CoreFlags(Flags):
    __slots__ = ()
    def __init__(self):
        super(CoreFlags, self).__init__()
        
class NfFlags(Flags):
    __slots__ = ()
    def __init__(self):
        super(NfFlags, self).__init__()
        
class NfrFlags(Flags):
    __slots__ = ()
    def __init__(self):
        super(NfrFlags, self).__init__()
   
class RadFlags(Flags):
    __slots__ = ()
    def __init__(self):
        super(RadFlags, self).__init__()

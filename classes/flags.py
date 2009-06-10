from threading import Lock

class Flags(object):
    __slots__ = ('cacheFlag', 'cacheLock', 'writeProf', 'recover')
    def __init__(self):
        self.cacheFlag = False
        self.cacheLock = Lock()
        self.writeProf = False
        self.recover   = True
        
class CoreFlags(Flags):
    __slots__ = ()
    def __init__(self):
        super(CoreFlags, self).__init__()
        
class NfFlags(Flags):
    __slots__ = ('recover_dumped', 'recoverprev', 'checkClasses')
    def __init__(self):
        super(NfFlags, self).__init__()
        self.recover_dumped, self.recoverprev, self.checkClasses = False, False, False
        
class NfrFlags(Flags):
    __slots__ = ('store_na_tarif', 'store_na_account')
    def __init__(self):
        super(NfrFlags, self).__init__()
        self.store_na_tarif, self.store_na_account = False, False
   
class RadFlags(Flags):
    __slots__ = ('common_vpn', 'ignore_nas_for_vpn')
    def __init__(self):
        super(RadFlags, self).__init__()
        self.common_vpn, self.ignore_nas_for_vpn = False, False

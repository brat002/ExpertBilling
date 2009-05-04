import struct
from collections import deque
from threading import Lock

class NfVars(object):
    """('clientHost', 'clientPort', 'clientAddr', 'sockTimeout', 'saveDir', 'aggrTime', 'aggrNum',\
                 'FLOW_TYPES', 'flowLENGTH', 'headerLENGTH', 'dumpDir')"""
    __slots__ = ('clientHost', 'clientPort', 'clientAddr', 'sockTimeout', 'saveDir', 'aggrTime', 'aggrNum',\
                 'FLOW_TYPES', 'flowLENGTH', 'headerLENGTH', 'dumpDir')
    def __init__(self):
        self.clientHost, self.clientPort, self.clientAddr, self.sockTimeout, self.saveDir = (None,)*5
        self.aggrTime, self.aggrNum = 120, 667
        self.FLOW_TYPES = {5 : (None, None)}
        self.flowLENGTH   = struct.calcsize("!LLLHHIIIIHHBBBBHHBBH")
        self.headerLENGTH = struct.calcsize("!HHIIIIBBH")
        self.dumpDir = '.'
        
class NfQueues(object):
    """('nfFlowCache', 'dcache','dcacheLock', 'flowQueue','fqueueLock',\
                 'databaseQueue','dbLock', 'fnameQueue','fnameLock', 'nfQueue', 'nfqLock')"""
    __slots__ = ('nfFlowCache', 'dcache','dcacheLock', 'flowQueue','fqueueLock',\
                 'databaseQueue','dbLock', 'fnameQueue','fnameLock', 'nfQueue', 'nfqLock')
    def __init__(self):
        self.nfFlowCache = None
        self.dcache, self.dcacheLock = {}, Lock()
        self.flowQueue, self.fqueueLock = deque(), Lock()
        self.databaseQueue, self.dbLock = deque(), Lock()
        self.fnameQueue, self.fnameLock = deque(), Lock()
        self.nfQueue, self.nfqLock = deque(), Lock()

class NfrVars(object):
    __slots__ = ('host', 'port', 'addr', 'sendFlag', 'saveDir', 'groupAggrTime', 'statAggrTime')
    
    def __init__(self):
        self.host, self.port = '127.0.0.1', 9997
        self.addr = (self.host, self.port)
        self.sendFlag = ''
        self.savedir = '.'
        self.groupAggrTime = 300    
        self.statAggrTime  = 1800
        
class NfrQueues(object):
    __slots__ = ('nfIncomingQueue', 'nfQueueLock', 'groupAggrDict', 'statAggrDict', \
                 'groupDeque', 'groupLock', 'statDeque', 'statLock', 'depickerQueue', 'depickerLock', \
                 'picker', 'pickerLock', 'pickerTime')
    def __init__(self):
        self.nfIncomingQueue = deque(); self.nfQueueLock = Lock()
        self.groupAggrDict = {}; self.statAggrDict = {}
        self.groupAggrLock = Lock(); self.statAggrLock = Lock()
        self.groupDeque = deque(); self.groupLock = Lock()
        self.statDeque =  deque(); self.statLock = Lock()
        self.depickerQueue = deque(); self.depickerLock = Lock()
        self.picker = None; self.pickerLock = Lock(); self.pickerTime = 0
        
        
class RadVars(object):
    __slots__ = ('session_timeout', 'gigaword', 'dict')
    
    def __init__(self):
        self.session_timeout = 86400
        self.gigaword = 4294967296
        self.dict = None
    
class RadQueues(object):
    __slots__ = ('account_timeaccess_cache', 'account_timeaccess_cache_count')
    def __init__(self):
        self.account_timeaccess_cache = {}
        self.account_timeaccess_cache_count = 0
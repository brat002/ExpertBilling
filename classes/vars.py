import struct
import psycopg2
from collections import deque
from threading import Lock


class Vars(object):
    __slots__ = ('name', 'piddir', 'db_errors', 'db_dsn', 'db_session')
    def __init__(self):
        self.name = ''
        self.piddir = 'pid'
        self.db_errors = [psycopg2.DatabaseError, psycopg2.OperationalError, psycopg2.InterfaceError, psycopg2.InternalError]
        self.db_dsn = ''
        self.db_session = []

class NfVars(Vars):
    """('clientHost', 'clientPort', 'clientAddr', 'sockTimeout', 'saveDir', 'aggrTime', 'aggrNum',\
                 'FLOW_TYPES', 'flowLENGTH', 'headerLENGTH', 'dumpDir')"""
    __slots__ = ('port', 'host', 'clientHost', 'clientPort', 'clientAddr', 'sockTimeout', 'saveDir', 'aggrTime', 'aggrNum',\
                 'FLOW_TYPES', 'flowLENGTH', 'headerLENGTH', 'dumpDir', 'cacheDicts')
    def __init__(self):
        super(NfVars, self).__init__()
        self.name = 'nf'
        self.clientHost, self.clientPort, self.clientAddr, self.sockTimeout, self.saveDir = (None,)*5
        self.aggrTime, self.aggrNum = 120, 667
        self.FLOW_TYPES = {5 : (None, None)}
        self.flowLENGTH   = struct.calcsize("!LLLHHIIIIHHBBBBHHBBH")
        self.headerLENGTH = struct.calcsize("!HHIIIIBBH")
        self.dumpDir = '.'
        self.cacheDicts = 10
        self.port = 9996
        self.host = '0.0.0.0'
        
class NfQueues(object):
    """('nfFlowCache', 'dcaches','dcacheLocks', 'flowQueue','fqueueLock',\
                 'databaseQueue','dbLock', 'fnameQueue','fnameLock', 'nfQueue', 'nfqLock')"""
    __slots__ = ('nfFlowCache', 'dcaches','dcacheLocks', 'flowQueue','fqueueLock',\
                 'databaseQueue','dbLock', 'fnameQueue','fnameLock', 'nfQueue', 'nfqLock')
    def __init__(self, dcacheNum = 10):
        self.nfFlowCache = None
        self.dcaches = [{}]*dcacheNum; self.dcacheLocks = [Lock()]*dcacheNum
        self.flowQueue = deque(); self.fqueueLock = Lock()
        self.databaseQueue = deque(); self.dbLock = Lock()
        self.fnameQueue = deque(); self.fnameLock = Lock()
        self.nfQueue = deque(); self.nfqLock = Lock()

class NfrVars(Vars):
    __slots__ = ('nfr_session', 'host', 'port', 'addr', 'sendFlag', 'saveDir', 'groupAggrTime', 'statAggrTime', 'statDicts', 'groupDicts')
    
    def __init__(self):
        super(NfrVars, self).__init__()
        self.name = 'nfroutine'
        self.host, self.port = '127.0.0.1', 9997
        self.nfr_session = ["SET synchronous_commit TO OFF;"]
        self.addr = (self.host, self.port)
        self.sendFlag = ''
        self.saveDir = '.'
        self.groupAggrTime = 300    
        self.statAggrTime  = 1800
        self.statDicts  = 10
        self.groupDicts = 10
        
class NfrQueues(object):
    __slots__ = ('nfIncomingQueue', 'nfQueueLock', 'groupAggrDicts', 'statAggrDicts', 'groupAggrLocks', 'statAggrLocks', \
                 'groupDeque', 'groupLock', 'statDeque', 'statLock', 'depickerQueue', 'depickerLock', \
                 'picker', 'pickerLock', 'pickerTime')
    def __init__(self, groupDicts = 10, statDicts = 10):
        self.nfIncomingQueue = deque(); self.nfQueueLock = Lock()
        self.groupAggrDicts = [{}]*groupDicts;     self.statAggrDicts = [{}]*statDicts
        self.groupAggrLocks = [Lock()]*groupDicts; self.statAggrLocks = [Lock()]*statDicts
        self.groupDeque = deque(); self.groupLock = Lock()
        self.statDeque =  deque(); self.statLock = Lock()
        self.depickerQueue = deque(); self.depickerLock = Lock()
        self.picker = None; self.pickerLock = Lock(); self.pickerTime = 0
        
        
class RadVars(Vars):
    __slots__ = ('session_timeout', 'gigaword', 'dict')
    
    def __init__(self):
        super(RadVars, self).__init__()
        self.name = 'rad'
        self.session_timeout = 86400
        self.gigaword = 4294967296
        self.dict = None
    
class RadQueues(object):
    __slots__ = ('account_timeaccess_cache', 'account_timeaccess_cache_count')
    def __init__(self):
        self.account_timeaccess_cache = {}
        self.account_timeaccess_cache_count = 0
        
class CoreVars(Vars):
    __slots__ = ()
    
    def __init__(self):
        super(CoreVars, self).__init__()
        self.name = 'core'
        
class RpcVars(Vars):
    __slots__ = ('pids', 'piddate', 'pidLock')
    
    def __init__(self):
        super(RpcVars, self).__init__()
        self.name = 'rpc'
        self.pids = []
        self.piddate = 0
        self.pidLock = Lock()
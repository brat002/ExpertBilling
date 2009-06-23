import struct
import psycopg2
from collections import deque
from threading import Lock


class Vars(object):
    __slots__ = ('cache_time', 'name', 'piddir', 'db_errors', 'db_dsn', 'db_session', 'log_type', 'log_ident', 'log_level', 'log_file', 'log_format', 'log_filemode', 'log_maxsize', 'log_rotate', 'types')
    def __init__(self):
        self.cache_time = 60
        self.name = ''
        self.piddir = 'pid'
        self.db_errors = (psycopg2.DatabaseError, psycopg2.OperationalError, psycopg2.InterfaceError, psycopg2.InternalError)
        self.db_dsn = ''
        self.db_session = []
        self.log_type = None; self.log_ident = 'ebs'
        self.log_level = 0
        self.log_file = None
        self.log_format = '%(asctime)s %(levelname)-8s %(message)s'
        self.log_filemode = 'a+'
        self.log_maxsize = 10485760
        self.log_rotate = 3
        self.types = {'cache': ('cache_time', ), 'name': ('name',), 'db_errors': ('db_errors',), 'db': ('db_dsn', 'db_session'),\
                      'pid': ('piddir',), 'log_level': ('log_level',), 'log': ('log_type','log_ident','log_file','log_format','log_filemode','log_maxsize','log_rotate')}
        
    def get_dynamic(self, **kwargs):
        config = kwargs['config']
        name = kwargs['name']
        db_name = kwargs['db_name']
        if config.has_option(name, 'cache_time'): self.cache_time = config.getint(name, 'cache_time')
        if config.has_option(name, 'name'): self.name = config.get(name, 'name')
        if config.has_option(name, 'piddir'): self.piddir = config.get(name, 'piddir')
        self.db_dsn = "dbname='%s' user='%s' host='%s' password='%s'" % (config.get(db_name, "name"), config.get(db_name, "username"),
                                                                         config.get(db_name, "host"), config.get(db_name, "password"))
        if config.has_option(db_name, 'session'): self.db_session = config.get(db_name, 'session').split(',')
        self.log_type = config.get(name, "log_type")
        if config.has_option(name, 'log_ident'): self.log_ident = config.get(name, 'log_ident')
        if config.has_option(name, 'log_level'): self.log_level = config.getint(name, 'log_level')
        if config.has_option(name, 'log_file'): self.log_file = config.get(name, 'log_file')
        if config.has_option(name, 'log_format'): self.log_format = config.get(name, 'log_format')
        if config.has_option(name, 'log_filemode'): self.log_filemode = config.get(name, 'log_filemode')
        if config.has_option(name, 'log_maxsize'): self.log_maxsize = config.getint(name, 'log_maxsize')
        if config.has_option(name, 'log_rotate'): self.log_rotate = config.getint(name, 'log_rotate')
        
    def get_static(self, **kwargs):
        pass
        
    def get_vars(self, **kwargs):
        self.get_dynamic(**kwargs)
        self.get_static(**kwargs)
        
    def changed(self, aVars):
        assert isinstance(aVars, Vars)
        changed = set()
        for field in self.slots:
            if getattr(self, field, None) != getattr(aVars, field, None):
                for key, values in self.types.iteritems():
                    if field in values:
                        changed.add(field)
                        break
        return changed
    
    def get_changed(self, aVars):
        return self.changed(aVars)
                
        
    def __repr__(self):
        return ' ;'.join((field + ': ' + repr(getattr(self,field)) for field in self.__slots__))
        
        
        
        

class NfVars(Vars):
    """('clientHost', 'clientPort', 'clientAddr', 'sockTimeout', 'saveDir', 'aggrTime', 'aggrNum',\
                 'FLOW_TYPES', 'flowLENGTH', 'headerLENGTH', 'dumpDir')"""
    __slots__ = ('port', 'host', 'nfrHost', 'nfrPort', 'nfrAddr', 'sockTimeout', 'saveDir', 'readDir', 'prefix', 'aggrTime', 'aggrNum',\
                 'FLOW_TYPES', 'flowLENGTH', 'headerLENGTH', 'dumpDir', 'cacheDicts', 'sock_type', 'file_pack', 'check_classes', 'max_datagram_len')
    def __init__(self):
        super(NfVars, self).__init__()
        self.name = 'nf'
        self.nfrHost, self.nfrPort, self.nfrAddr, self.sockTimeout = (None,)*4
        self.aggrTime, self.aggrNum = 120, 667
        self.FLOW_TYPES = {5 : (None, None)}
        self.flowLENGTH   = struct.calcsize("!LLLHHIIIIHHBBBBHHBBH")
        self.headerLENGTH = struct.calcsize("!HHIIIIBBH")
        self.dumpDir = '.'
        self.saveDir = '.'
        self.readDir = '.'
        self.prefix = 'nf_'
        self.cacheDicts = 10
        self.port = 9996
        self.host = '0.0.0.0'
        self.sock_type = 0
        self.file_pack = 300
        self.check_classes = 0
        self.max_datagram_len = 8192
        self.types.update({'addr': ('host', 'port'), 'nfraddr': ('sock_type', 'nfrHost', 'nfrPort'),\
                           'cachedicts': ('cacheDicts',), 'filepack': ('file_pack',), 'checkclasses': ('check_classes',), 'prefix': ('prefix',), 'aggr':('aggrTime', 'aggrNum'),\
                           'savedir': ('saveDir',), 'readdir': ('readDir',), 'dumpdir': ('dumpDir',)})
    
    def get_dynamic(self, **kwargs):
        super(NfVars, self).get_dynamic(**kwargs)
        config = kwargs['config']
        name = kwargs['name']
        net_name = kwargs['net_name']
        if config.has_option(name, 'cachedicts'): self.cacheDicts = config.getint(name, 'cachedicts')
        if config.has_option(name, 'port'): self.port = config.getint(name, 'port')
        if config.has_option(name, 'host'): self.host = config.get(name, 'host')
        self.sock_type = config.getint(net_name, "usock")
        if self.sock_type == 0:
            self.nfrHost = config.get(net_name + "_inet", "host")
            self.nfrPort = config.getint(net_name + "_inet", "port")
            self.nfrAddr = (self.nfrHost, self.nfrPort)
        elif self.sock_type == 1:
            self.nfrHost = config.get(net_name + "_unix", "host")
            self.nfrPort = None
            self.nfrAddr = self.nfrHost
        if config.has_option(name, 'sock_timeout'): self.sockTimeout = config.getint(name, 'sock_timeout')
        if config.has_option(name, 'aggrtime'): self.aggrTime = config.getint(name, 'aggrtime')
        if config.has_option(name, 'aggrnum'): self.aggrNum = config.getint(name, 'aggrnum')
        if config.has_option(name, 'checkclasses'): self.check_classes = config.getint(name, 'checkclasses')
        if config.has_option(name, 'file_pack'): self.file_pack = config.getint(name, 'file_pack')
        if config.has_option(name, 'prefix'): self.prefix = config.get(name, 'prefix')
        if config.has_option(name, 'dump_dir'): self.dumpDir = config.get(name, 'dump_dir')
        self.readDir = config.get(name, 'read_dir') if config.has_option(name, 'read_dir') else self.dumpDir
        if config.has_option(name, 'save_dir'): self.saveDir = config.get(name, 'save_dir')
        if config.has_option(name, 'max_datagram_len'): self.saveDir = config.getint(name, 'max_datagram_len')
            
    def get_static(self, **kwargs):
        super(NfVars, self).get_static(**kwargs)
        
    def changed(self, aVars):
        assert isinstance(aVars, NfVars)
        
    def __repr__(self):
        return super(NfVars, self).__repr__() + ' '+ ' ;'.join((field + ': ' + repr(getattr(self,field)) for field in self.__slots__))

        
        
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
    __slots__ = ('nfr_session', 'host', 'port', 'addr', 'sendFlag', 'saveDir', 'groupAggrTime', 'statAggrTime', 'statDicts', 'groupDicts', 'sock_type')
    
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
        self.sock_type = 0
        
class NfrQueues(object):
    __slots__ = ('nfIncomingQueue', 'nfQueueLock', 'groupAggrDicts', 'statAggrDicts', 'groupAggrLocks', 'statAggrLocks', \
                 'groupDeque', 'groupLock', 'statDeque', 'statLock', 'depickerQueue', 'depickerLock', \
                 'picker', 'pickerLock', 'pickerTime', 'prepaidLock')
    def __init__(self, groupDicts = 10, statDicts = 10):
        self.nfIncomingQueue = deque(); self.nfQueueLock = Lock()
        self.groupAggrDicts = [{}]*groupDicts;     self.statAggrDicts = [{}]*statDicts
        self.groupAggrLocks = [Lock()]*groupDicts; self.statAggrLocks = [Lock()]*statDicts
        self.groupDeque = deque(); self.groupLock = Lock()
        self.statDeque =  deque(); self.statLock = Lock()
        self.depickerQueue = deque(); self.depickerLock = Lock()
        self.picker = None; self.pickerLock = Lock(); self.pickerTime = 0
        self.prepaidLock = Lock()
        
        
class RadVars(Vars):
    __slots__ = ('session_timeout', 'gigaword', 'dict')
    
    def __init__(self):
        super(RadVars, self).__init__()
        self.name = 'rad'
        self.session_timeout = 86400
        self.gigaword = 4294967296
        self.dict = None
    
class RadQueues(object):
    __slots__ = ('account_timeaccess_cache', 'account_timeaccess_cache_count', 'eap_md5_ch', 'eap_md5_lock')
    def __init__(self):
        self.account_timeaccess_cache = {}
        self.account_timeaccess_cache_count = 0
        self.eap_md5_ch = {}
        self.eap_md5_lock = Lock()
        
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
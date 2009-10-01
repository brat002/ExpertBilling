import struct
import psycopg2
from collections import deque, defaultdict
from threading import Lock
import dictionary
from operator import itemgetter
from system.PersistentQueues import FileSaveDeque
logger = None

def install_logger(lgr):
    global logger
    logger = lgr
    
class Vars(object):
    __slots__ = ('RECOVER', 'CACHE_TIME', 'name', 'piddir', 'db_errors', 'db_dsn', 'db_session', 'log_type', 'log_ident', 'log_level', 'log_file', 'log_format', 'log_filemode', 'log_maxsize', 'log_rotate', 'types')
    def __init__(self):
        self.RECOVER = True
        self.CACHE_TIME = 60
        self.name = ''
        self.piddir = 'pid'
        self.db_errors = (psycopg2.DatabaseError, psycopg2.OperationalError, psycopg2.InterfaceError, psycopg2.InternalError)
        self.db_dsn = ''
        self.db_session = []
        self.log_type = 'logging'; self.log_ident = 'ebs'
        self.log_level = 0
        self.log_file = self.name + '_log'
        self.log_format = '%(asctime)s %(levelname)-8s %(message)s'
        self.log_filemode = 'a+'
        self.log_maxsize = 10485760
        self.log_rotate = 3
        self.types = {'cache': ('CACHE_TIME', ), 'name': ('name',), 'db_errors': ('db_errors',), 'db': ('db_dsn', 'db_session'),\
                      'pid': ('piddir',), 'log_level': ('log_level',), 'log': ('log_type','log_ident','log_file','log_format','log_filemode','log_maxsize','log_rotate')}
        
    def get_dynamic(self, **kwargs):
        config = kwargs['config']
        name = kwargs['name']
        db_name = kwargs['db_name']
        if config.has_option(name, 'recover'):
            self.RECOVER = False if config.get(name, 'recover').lower() in ('false', '0') else True
        if config.has_option(name, 'cache_time'): self.CACHE_TIME = config.getint(name, 'cache_time')
        if config.has_option(name, 'name'): self.name = config.get(name, 'name')
        if config.has_option(name, 'piddir'): self.piddir = config.get(name, 'piddir')
        self.db_dsn = "dbname='%s' user='%s' host='%s' password='%s'" % (config.get(db_name, "name"), config.get(db_name, "username"),
                                                                         config.get(db_name, "host"), config.get(db_name, "password"))
        if config.has_option(db_name, 'session'): self.db_session = config.get(db_name, 'session').split(',')
        if config.has_option(name, 'log_type'): self.log_type = config.get(name, "log_type")
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
        for field in self.__slots__:
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
    __slots__ = ('HOST', 'PORT', 'NFR_HOST', 'NFR_PORT', 'NFR_ADDR', 'SOCK_TIMEOUT', 'SAVE_DIR', 'READ_DIR', 'PREFIX', 'AGGR_TIME', 'AGGR_NUM',\
                 'FLOW_TYPES', 'flowLENGTH', 'headerLENGTH', 'DUMP_DIR', 'CACHE_DICTS', 'SOCK_TYPE', 'FILE_PACK', 'PACKET_PACK', 'CHECK_CLASSES', 'MAX_DATAGRAM_LEN', 'RECOVER_DUMP', 'NF_TIME_MOD',\
                 'MAX_SENDBUF_LEN', 'NFR_DELIMITER')
    def __init__(self):
        super(NfVars, self).__init__()
        self.name = 'nf'
        self.NFR_HOST = '127.0.0.1'
        self.NFR_PORT = 36577
        self.NFR_ADDR = (self.NFR_HOST, self.NFR_PORT)
        self.SOCK_TIMEOUT = 5
        self.AGGR_TIME, self.AGGR_NUM = 120, 200
        self.RECOVER_DUMP = True
        self.FLOW_TYPES = {5 : (None, None)}
        self.flowLENGTH   = struct.calcsize("!LLLHHIIIIHHBBBBHHBBH")
        self.headerLENGTH = struct.calcsize("!HHIIIIBBH")
        self.DUMP_DIR = '.'
        self.SAVE_DIR = '.'
        self.READ_DIR = '.'
        self.PREFIX = self.name + '_'
        self.CACHE_DICTS = 10
        self.PORT = 9996
        self.HOST = '0.0.0.0'
        self.SOCK_TYPE = 0
        self.FILE_PACK = 2000 #300!
        self.PACKET_PACK = 32
        self.CHECK_CLASSES = 0
        self.MAX_DATAGRAM_LEN = 8192
        self.NF_TIME_MOD = 20
        self.MAX_SENDBUF_LEN = 20000 #10000!
        self.NFR_DELIMITER = '--NFRP--'
        self.types.update({'addr': ('HOST', 'PORT'), 'nfraddr': ('NFR_HOST', 'NFR_PORT', 'SOCK_TIMEOUT'),\
                           'cachedicts': ('CACHE_DICTS',), 'filepack': ('FILE_PACK',), 'checkclasses': ('CHECK_CLASSES',), 'prefix': ('PREFIX',), 'aggr':('AGGR_TIME', 'AGGR_NUM'),\
                           'savedir': ('SAVE_DIR',), 'readdir': ('READ_DIR',), 'dumpdir': ('DUMP_DIR',)})
    
    def get_dynamic(self, **kwargs):
        super(NfVars, self).get_dynamic(**kwargs)
        config = kwargs['config']
        name = kwargs['name']
        net_name = kwargs['net_name']
        if config.has_option(name, 'cachedicts'): self.CACHE_DICTS = config.getint(name, 'cachedicts')
        if config.has_option(name, 'port'): self.PORT = config.getint(name, 'port')
        if config.has_option(name, 'host'): self.HOST = config.get(name, 'host')
        self.SOCK_TYPE = config.getint(net_name, "sock_type")
        if self.SOCK_TYPE == 0:
            if config.has_option(net_name + "_inet", "nfr_host"): self.NFR_HOST = config.get(net_name + "_inet", "nfr_host")
            if config.has_option(net_name + "_inet", "nfr_port"): self.NFR_PORT = config.getint(net_name + "_inet", "nfr_port")
            self.NFR_ADDR = (self.NFR_HOST, self.NFR_PORT)
        elif self.SOCK_TYPE == 1:
            if config.has_option(net_name + "_unix", "nfr_host"): self.NFR_HOST = config.get(net_name + "_unix", "nfr_host")
            self.NFR_PORT = None
            self.NFR_ADDR = self.NFR_HOST
        if config.has_option(name, 'recover_dump'):
            self.RECOVER_DUMP = False if config.get(name, 'recover_dump').lower() in ('false', '0') else True
        if config.has_option(name, 'sock_timeout'): self.SOCK_TIMEOUT = config.getint(name, 'sock_timeout')
        if config.has_option(name, 'aggrtime'):     self.AGGR_TIME = config.getint(name, 'aggrtime')
        if config.has_option(name, 'aggrnum'):      self.AGGR_NUM = config.getint(name, 'aggrnum') % 500
        if config.has_option(name, 'checkclasses'): self.CHECK_CLASSES = config.getint(name, 'checkclasses')
        if config.has_option(name, 'file_pack'):    self.FILE_PACK = config.getint(name, 'file_pack')
        if config.has_option(name, 'packet_pack'):  self.PACKET_PACK = config.getint(name, 'packet_pack')
        if config.has_option(name, 'prefix'):       self.PREFIX = config.get(name, 'prefix')
        if config.has_option(name, 'dump_dir'):     self.DUMP_DIR = config.get(name, 'dump_dir')
        self.READ_DIR = config.get(name, 'read_dir') if config.has_option(name, 'read_dir') else self.DUMP_DIR
        if config.has_option(name, 'save_dir'):         self.SAVE_DIR = config.get(name, 'save_dir')
        if config.has_option(name, 'max_datagram_len'): self.MAX_DATAGRAM_LEN = config.getint(name, 'max_datagram_len')
        if config.has_option(name, 'nf_time_mod'): self.NF_TIME_MOD = config.getint(name, 'nf_time_mod')
            
    def get_static(self, **kwargs):
        super(NfVars, self).get_static(**kwargs)
        
    def changed(self, aVars):
        assert isinstance(aVars, NfVars)
        
    def __repr__(self):
        return '; '.join((field + ': ' + repr(getattr(self,field)) for field in super(NfVars, self).__slots__ + self.__slots__))

        
        
class NfQueues(object):
    """('nfFlowCache', 'dcaches','dcacheLocks', 'flowQueue','fqueueLock',\
                 'databaseQueue','dbLock', 'fnameQueue','fnameLock', 'nfQueue', 'nfqLock')"""
    __slots__ = ('nfFlowCache', 'dcaches','dcacheLocks', 'flowQueue','fqueueLock',\
                 'databaseQueue','dbLock', 'fnameQueue','fnameLock', 'nfQueue', 'nfqLock', 'packetIndex', 'packetIndexLock')
    def __init__(self, dcacheNum = 10):
        self.nfFlowCache = None
        self.dcaches = [{} for i in xrange(dcacheNum)]; self.dcacheLocks = [Lock() for i in xrange(dcacheNum)]
        self.flowQueue = deque(); self.fqueueLock = Lock()
        #self.databaseQueue = deque(); self.dbLock = Lock()
        self.dbLock = Lock()
        #self.databaseQueue = FileSaveDeque(fsd_name, fsd_dumpdir, fsd_prefix, fsd_filepack, fsd_maxlen, self.dbLock, fsd_logger)
        self.databaseQueue = FileSaveDeque()
        self.fnameQueue = deque(); self.fnameLock = Lock()
        self.nfQueue = deque(); self.nfqLock = Lock()
        self.packetIndex = 0; self.packetIndexLock = Lock()
        
    

class NfrVars(Vars):
    __slots__ = ('NFR_SESSION', 'HOST', 'PORT', 'ADDR', 'sendFlag', 'SAVE_DIR', 'GROUP_AGGR_TIME', 'STAT_AGGR_TIME',\
                 'STAT_DICTS', 'GROUP_DICTS', 'SOCK_TYPE', 'STORE_NA_TARIF', 'STORE_NA_ACCOUNT', 'MAX_DATAGRAM_LEN',\
                 'PICKER_AGGR_TIME', 'ROUTINE_THREADS', 'GROUPSTAT_THREADS', 'GLOBALSTAT_THREADS', 'BILL_THREADS',\
                 'ALLOWED_NF_IP_LIST', 'NFR_DELIMITER')
    
    def __init__(self):
        super(NfrVars, self).__init__()
        self.name = 'nfroutine'
        self.HOST, self.PORT = '0.0.0.0', 36577
        self.NFR_SESSION = ["SET synchronous_commit TO OFF;"]
        self.ADDR = (self.HOST, self.PORT)
        self.sendFlag = ''
        self.SAVE_DIR = '.'
        self.GROUP_AGGR_TIME = 300    
        self.STAT_AGGR_TIME  = 1800
        self.STAT_DICTS  = 10
        self.GROUP_DICTS = 10
        self.SOCK_TYPE = 0
        self.STORE_NA_TARIF   = False
        self.STORE_NA_ACCOUNT = False
        self.MAX_DATAGRAM_LEN = 32687
        self.PICKER_AGGR_TIME = 300.0
        self.ROUTINE_THREADS = 4
        self.GROUPSTAT_THREADS  = 1
        self.GLOBALSTAT_THREADS = 1
        self.BILL_THREADS = 1
        self.ALLOWED_NF_IP_LIST = ['127.0.0.1']
        self.NFR_DELIMITER = '--NFRP--'
        
    def get_dynamic(self, **kwargs):
        super(NfrVars, self).get_dynamic(**kwargs)
        config = kwargs['config']
        name = kwargs['name']
        net_name = kwargs['net_name']
        db_name = kwargs['db_name']
        if config.has_option(name, 'statdicts'): self.STAT_DICTS = config.getint(name, 'statdicts')
        if config.has_option(name, 'groupdicts'): self.GROUP_DICTS = config.getint(name, 'groupdicts')
        self.SOCK_TYPE = config.getint(net_name, "sock_type")
        if self.SOCK_TYPE == 0:
            if config.has_option(net_name + "_inet", "nfr_host"): self.HOST = config.get(net_name + "_inet", "nfr_host")
            if config.has_option(net_name + "_inet", "nfr_port"): self.PORT = config.getint(net_name + "_inet", "nfr_port")
            self.ADDR = (self.HOST, self.PORT)
        elif self.SOCK_TYPE == 1:
            if config.has_option(net_name + "_unix", "nfr_host"): self.HOST = config.get(net_name + "_unix", "nfr_host")
            self.PORT = None
            self.ADDR = self.HOST

        if config.has_option(db_name, 'nfr_session'): self.NFR_SESSION = config.get(db_name, 'nfr_session').split(',')
        if config.has_option(name, 'save_dir'):         self.SAVE_DIR = config.get(name, 'save_dir')
        if config.has_option(name, 'group_aggr_time'): self.GROUP_AGGR_TIME = config.getint(name, 'group_aggr_time')
        if config.has_option(name, 'stat_aggr_time'):  self.STAT_AGGR_TIME  = config.getint(name, 'stat_aggr_time')
        if config.has_option(name, 'picker_aggr_time'):  self.PICKER_AGGR_TIME  = config.getint(name, 'picker_aggr_time')
        if config.has_option(name, 'store_na_tarif'):
            self.STORE_NA_TARIF   = False if config.get(name, 'store_na_tarif').lower()   in ('false', '0') else True
        if config.has_option(name, 'store_na_account'):
            self.STORE_NA_ACCOUNT = False if config.get(name, 'store_na_account').lower() in ('false', '0') else True
        if config.has_option(name, 'max_datagram_len'): self.MAX_DATAGRAM_LEN = config.getint(name, 'max_datagram_len')
        if config.has_option(name, 'routine_threads'):    self.ROUTINE_THREADS = config.getint(name, 'routine_threads')
        if config.has_option(name, 'groupstat_threads'):  self.GROUPSTAT_THREADS = config.getint(name, 'groupstat_threads')
        if config.has_option(name, 'globalstat_threads'): self.GLOBALSTAT_THREADS = config.getint(name, 'globalstat_threads')
        if config.has_option(name, 'bill_threads'):       self.BILL_THREADS = config.getint(name, 'bill_threads')
        if config.has_option(name, 'allowed_nf_ip_list'): self.ALLOWED_NF_IP_LIST = config.get(name, 'allowed_nf_ip_list').split(',')
            
    def get_static(self, **kwargs):
        super(NfrVars, self).get_static(**kwargs)
        
    def changed(self, aVars):
        assert isinstance(aVars, NfrVars)
        
    def __repr__(self):
        return '; '.join((field + ': ' + repr(getattr(self,field)) for field in super(NfrVars, self).__slots__ + self.__slots__))
        
class NfrQueues(object):
    __slots__ = ('nfIncomingQueue', 'nfQueueLock', 'groupAggrDicts', 'statAggrDicts', 'groupAggrLocks', 'statAggrLocks', \
                 'groupDeque', 'groupLock', 'statDeque', 'statLock', 'depickerQueue', 'depickerLock', \
                 'picker', 'pickerLock', 'pickerTime', 'prepaidLock', 'lastPacketInfo')
    def __init__(self, groupDicts = 10, statDicts = 10):
        self.nfIncomingQueue = deque(); self.nfQueueLock = Lock()
        #[(1,2,3)][0][4]['INPUT']
        #[(1,2, )][1] = group info
        #lambda: [defaultdict(lambda: {'INPUT':0, 'OUTPUT':0}), None])
        self.groupAggrDicts = [{} for i in xrange(groupDicts)];     self.statAggrDicts = [{} for i in xrange(statDicts)]
        self.groupAggrLocks = [Lock() for i in xrange(groupDicts)]; self.statAggrLocks = [Lock() for i in xrange(statDicts)]
        self.groupDeque = deque(); self.groupLock = Lock()
        self.statDeque =  deque(); self.statLock = Lock()
        self.depickerQueue = deque(); self.depickerLock = Lock()
        self.picker = None; self.pickerLock = Lock(); self.pickerTime = 0
        self.prepaidLock = Lock()
        self.lastPacketInfo = defaultdict(lambda: (None,0))
        
        
class RadVars(Vars):
    __slots__ = ('SESSION_TIMEOUT', 'GIGAWORD', 'DICT_LIST', 'DICT', 'COMMON_VPN', 'IGNORE_NAS_FOR_VPN',\
                 'MAX_DATAGRAM_LEN', 'AUTH_PORT', 'ACCT_PORT', 'AUTH_SOCK_TIMEOUT', 'ACCT_SOCK_TIMEOUT',\
                 'AUTH_THREAD_NUM', 'ACCT_THREAD_NUM', 'LISTEN_THREAD_NUM', 'EAP_ID_TYPE', 'POLL_TIMEOUT','EAP_ACCESS_TYPES')
    
    def __init__(self):
        super(RadVars, self).__init__()
        self.name = 'rad'        
        self.GIGAWORD = 4294967296
        self.SESSION_TIMEOUT = 86400
        self.DICT_LIST = ("dicts/dictionary","dicts/dictionary.microsoft", 'dicts/dictionary.mikrotik')
        self.DICT = None
        self.COMMON_VPN = False
        self.IGNORE_NAS_FOR_VPN = False
        self.MAX_DATAGRAM_LEN = 4096
        self.AUTH_PORT = 1812
        self.ACCT_PORT = 1813
        self.AUTH_SOCK_TIMEOUT = 5
        self.ACCT_SOCK_TIMEOUT = 5
        self.AUTH_THREAD_NUM = 2
        self.ACCT_THREAD_NUM = 3
        self.LISTEN_THREAD_NUM = 2
        self.EAP_ID_TYPE = 'eap-md5'
        self.EAP_ACCESS_TYPES = {'802.1x':'eap-tls', 'PPTP':'eap-md5', 'PPPOE':'eap-md5'}
        self.POLL_TIMEOUT = 500
        
    def get_dynamic(self, **kwargs):
        super(RadVars, self).get_dynamic(**kwargs)
        config = kwargs['config']
        name = kwargs['name']
        if config.has_option(name, 'session_timeout'): self.SESSION_TIMEOUT = config.getint(name, 'session_timeout')
        if config.has_option(name, 'common_vpn'):
            self.COMMON_VPN = False if config.get(name, 'common_vpn').lower() in ('false', '0') else True
        if config.has_option(name, 'ignore_nas_for_vpn'):
            self.IGNORE_NAS_FOR_VPN = False if config.get(name, 'ignore_nas_for_vpn').lower() in ('false', '0') else True
        if config.has_option(name, 'dict_list'):
            self.DICT_LIST = config.get(name, 'dict_list').split(',')
        self.DICT = dictionary.Dictionary(*self.DICT_LIST)
        if config.has_option(name, 'max_datagram_length'): self.MAX_DATAGRAM_LEN = config.getint(name, 'max_datagram_length')
        if config.has_option(name, 'auth_port'): self.AUTH_PORT = config.getint(name, 'auth_port')
        if config.has_option(name, 'acct_port'): self.ACCT_PORT = config.getint(name, 'acct_port')
        if config.has_option(name, 'auth_sock_timeout'): self.AUTH_SOCK_TIMEOUT = config.getint(name, 'auth_sock_timeout')
        if config.has_option(name, 'acct_sock_timeout'): self.ACCT_SOCK_TIMEOUT = config.getint(name, 'acct_sock_timeout')
        if config.has_option(name, 'auth_thread_num'): self.AUTH_THREAD_NUM = config.getint(name, 'auth_thread_num')
        if config.has_option(name, 'acct_thread_num'): self.ACCT_THREAD_NUM = config.getint(name, 'acct_thread_num')
        if config.has_option(name, 'listen_thread_num'): self.LISTEN_THREAD_NUM = config.getint(name, 'listen_thread_num')
        if config.has_option(name, 'poll_timeout'): self.POLL_TIMEOUT = config.getint(name, 'poll_timeout')
        if config.has_option(name, 'eap_id_type'):
            self.EAP_ID_TYPE = config.get(name, 'eap_id_type').lower()
        if config.has_option(name, 'eap_access_type'):
            self.EAP_ACCESS_TYPE = dict((apply(lambda lst: (lst[0], lst[1].lower()), (fst.split(':'),)) for fst in config.get(name, 'eap_access_type').split(',')))
    def __repr__(self):
        return '; '.join((field + ': ' + repr(getattr(self,field)) for field in super(RadVars, self).__slots__ + self.__slots__))


    
class RadQueues(object):
    __slots__ = ('account_timeaccess_cache', 'account_timeaccess_cache_count', 'eap_auth_chs', 'eap_auth_locks',\
                 'rad_server', 'challenges', 'sessions', 'sessions_lock')
    def __init__(self):
        self.account_timeaccess_cache = {}
        self.account_timeaccess_cache_count = 0
        self.eap_auth_chs = {}
        self.eap_auth_locks = {}
        self.challenges = {}
        self.rad_server = None
        self.sessions = None
        self.sessions_lock = Lock()
        
class CoreVars(Vars):
    __slots__ = ('TRANSACTIONS_PER_DAY', 'VPN_SLEEP', 'IPN_SLEEP', 'PERIODICAL_SLEEP', 'TIMEACCESS_SLEEP', 'LIMIT_SLEEP', 'SETTLEMENT_PERIOD_SLEEP',\
                 'DICT_LIST', 'DICT')
    
    def __init__(self):
        super(CoreVars, self).__init__()
        self.name = 'core'
        self.TRANSACTIONS_PER_DAY = 24
        self.VPN_SLEEP = 60
        self.PERIODICAL_SLEEP = 180
        self.TIMEACCESS_SLEEP = 60
        self.LIMIT_SLEEP = 110
        self.SETTLEMENT_PERIOD_SLEEP = 120
        self.IPN_SLEEP = 120
        self.DICT_LIST = ("dicts/dictionary", "dicts/dictionary.microsoft","dicts/dictionary.mikrotik","dicts/dictionary.rfc3576")
        self.DICT = None
        
    def get_dynamic(self, **kwargs):
        super(CoreVars, self).get_dynamic(**kwargs)
        config = kwargs['config']
        name = kwargs['name']
        if config.has_option(name, 'transactions_per_day'): self.TRANSACTIONS_PER_DAY = config.getint(name, 'transactions_per_day')
        if config.has_option(name, 'vpn_sleep'): self.VPN_SLEEP = config.getint(name, 'vpn_sleep')
        if config.has_option(name, 'periodical_sleep'): self.PERIODICAL_SLEEP = config.getint(name, 'periodical_sleep')
        if config.has_option(name, 'limit_sleep'): self.LIMIT_SLEEP = config.getint(name, 'limit_sleep')
        if config.has_option(name, 'timeaccess_sleep'): self.TIMEACCESS_SLEEP = config.getint(name, 'timeaccess_sleep')
        if config.has_option(name, 'settlement_period_sleep'): self.SETTLEMENT_PERIOD_SLEEP = config.getint(name, 'settlement_period_sleep')
        if config.has_option(name, 'ipn_sleep'): self.IPN_SLEEP = config.getint(name, 'ipn_sleep')

        if config.has_option(name, 'dict_list'):
            self.DICT_LIST = config.get(name, 'dict_list').split(',')
        self.DICT = dictionary.Dictionary(*self.DICT_LIST)
        
    def __repr__(self):
        return '; '.join((field + ': ' + repr(getattr(self,field)) for field in super(CoreVars, self).__slots__ + self.__slots__))

        
class RpcVars(Vars):
    __slots__ = ('pids', 'piddate', 'pidLock', 'db_connection', 'db_connection_lock', 'graph_connection', 'graph_connection_lock', 'LISTEN_PORT')
    
    def __init__(self):
        super(RpcVars, self).__init__()
        self.name = 'rpc'
        self.pids = []
        self.piddate = 0
        self.pidLock = Lock()
        self.db_connection_lock = Lock()
        self.db_connection = None
        self.graph_connection_lock = Lock()
        self.graph_connection = None
        self.LISTEN_PORT = 7771
       
    def get_dynamic(self, **kwargs):
        super(RpcVars, self).get_dynamic(**kwargs)
        config = kwargs['config']
        name = kwargs['name']
        if config.has_option(name, 'listen_port'): self.LISTEN_PORT = config.getint(name, 'listen_port')
        
    def __repr__(self):
        return '; '.join((field + ': ' + repr(getattr(self,field)) for field in super(RpcVars, self).__slots__ + self.__slots__))

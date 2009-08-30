'''
Syslog/Logging wrapper
'''
import logging
from logging import handlers
try: import syslog
except ImportError, ipe: import syslog_dummy as syslog

import threading
from threading import Lock


dateDelim = "."
strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"

LG_DEBUG    = 0
LG_INFO     = 1
LG_WARNING  = 2
LG_ERROR    = 3
LG_CRITICAL = 4

loggingLevels = {0: logging.DEBUG, 1: logging.INFO, 2: logging.WARNING, 3: logging.ERROR, 4: logging.CRITICAL}
syslogLevels  = {0: syslog.LOG_DEBUG, 1: syslog.LOG_INFO, 2: syslog.LOG_WARNING, 3: syslog.LOG_ERR, 4 : syslog.LOG_CRIT} 

loggingFormat = '%(asctime)s %(levelname)-8s %(message)s'

class isdlogger(object):
    def __init__ (self, ltype, loglevel=0, ident=None, filename=None, format=loggingFormat, filemode='a+', maxBytes=10485760, backupCount=3):
        self.loggingLevel = loglevel
        self.ident  = ident
        if ltype == 'syslog':
            self.log_ = self.syslogLog
            self.levels = syslogLevels
            if not ident: self.ident = 'isdlogger'
            syslog.openlog(self.ident)
        elif ltype == 'logging':
            self.log_ = self.loggingLog
            self.levels = loggingLevels
            #self.fflush = fflush
            #if not format: self.loggingFormat = loggingFormat
            #else: self.loggingFormat = format
            #if not filemode: self.filemode = 'a+'
            #else: self.filemode = filemode
            if not filename : raise Exception('Please specify the filename!')
            #else: self.filename = filename
            #logging.config
            logging.root.setLevel(self.levels[loglevel])
            rtHdlr = handlers.RotatingFileHandler(filename, mode=filemode, maxBytes=maxBytes, backupCount=backupCount)
            rtHdlr.setFormatter(logging.Formatter(format))
            logging.root.addHandler(rtHdlr)
            #logging.basicConfig(level=self.levels[loglevel], format=self.loggingFormat, filename=self.filename, filemode=self.filemode)
        else:
            raise Exception('Unknown logger type!')
        
    '''generic logging method'''
    def log(self, level, message, vars):
        if level >= self.loggingLevel:
            self.log_(self.levels[level], message % vars)
            
    """quick method with 'repr'"""
    def reprl(self, level, obj, message='%s'):
        if level >= self.loggingLevel:
            self.log_(self.levels[level], message % repr(obj))
            
    '''print a message with 'INFO' level'''
    def lprint(self, message):
        if 1 >= self.loggingLevel:
            self.log_(self.levels[1], message)
            
    '''for log adapter'''
    def log_adapt(self, message, level):
        if level >= self.loggingLevel:
            self.log_(self.levels[level], message)        
            
    '''syslog log method'''
    def syslogLog(self, level, message):
        syslog.syslog(level, message)
        
    '''logging log method'''
    def loggingLog(self, level, message):
        logging.log(level, message)
            
    '''set logging level'''
    def setLevel(self, level):
        self.loggingLevel = level
        
    def setNewLevel(self, level):
        if self.loggingLevel != level:
            self.loggingLevel = level
            '''if self.ltype == 'logging':
                logging.root.setLevel(self.levels[level])'''
        
    def debug(self, message, vars):
        self.log(0, message, vars)
        
    def debugfun(self, message, fun, vars):
        self.log(0, message, fun(*vars))
        
    def info(self, message, vars):
        self.log(1, message, vars)
        
    def warning(self, message, vars):
        self.log(2, message, vars)
        
    def error(self, message, vars):
        self.log(3, message, vars)
        
    def critical(self, message, vars):
        self.log(4, message, vars)
        
    '''predicate - whether level <= INFO level'''
    def writeInfoP(self):
        return self.loggingLevel <= 1
    
#logger compatible with PYRO
class pyrologger(isdlogger):
    def __init__(self, *args, **kwargs):
        super(pyrologger, self).__init__(*args, **kwargs)
        self.trace_on = kwargs.get('trace_on', False)
	#self.lock = Lock()
        
    def _checkTraceLevel(self, level):
	return self.trace_on
    
    def _logfile(self):
	return 'pyro_log'
    
    def msg(self,source,*args):
	self._trace(LG_INFO,source, args)
    def warn(self,source,*args):
	self._trace(LG_WARNING,source, args)
    def error(self,source,*args):
	self._trace(LG_ERROR,source, args)
    def raw(self,str):
	self.log_(self.levels[LG_WARNING], str)
    def _trace(self, level, source, arglist):
	pass
        '''
	if level >= self.loggingLevel:
	    thread_name = 'NA'
	    try:
		thread_name = threading.currentThread().getName()
	    except: pass
	    
        try:
	    self.log_(self.levels[level],  ' | '.join(('PYRO_LOG:', thread_name, str(source), \
						       reduce(lambda x,y: str(x)+' '+str(y),arglist))))
        except:
            self.log_(self.levels[level],str(arglist))
	 '''


    
    
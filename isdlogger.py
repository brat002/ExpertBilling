import logging
try: import syslog
except ImportError, ipe: import syslog_dummy as syslog

dateDelim = "."
strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"

loggingLevels = {0: logging.DEBUG, 1: logging.INFO, 2: logging.WARNING, 3: logging.ERROR, 4: logging.CRITICAL}
syslogLevels  = {0: syslog.LOG_DEBUG, 1: syslog.LOG_INFO, 2: syslog.LOG_WARNING, 3: syslog.LOG_ERR, 4 : syslog.LOG_CRIT} 

loggingFormat = '%(asctime)s %(levelname)-8s %(message)s'
class isdlogger(object):
    def __init__ (self, ltype, loglevel=0, ident=None, filename=None, format=None, filemode=None, fflush=True):
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
            self.fflush = fflush
            if not format: self.loggingFormat = loggingFormat
            else: self.loggingFormat = format
            if not filemode: self.filemode = 'w'
            else: self.filemode = filemode
            if not filename : raise Exception('Please specify the filename!')
            else: self.filename = filename
            logging.basicConfig(level=self.levels[loglevel], format=self.loggingFormat, filename=self.filename, filemode=self.filemode)
        else:
            raise Exception('Unknown logger type!')
        
    def log(self, level, message, vars):
        if level >= self.loggingLevel:
            self.log_(self.levels[level], message % vars)
            
    def reprl(self, level, obj, message='%s'):
        if level >= self.loggingLevel:
            self.log_(self.levels[level], message % repr(obj))
            
    def lprint(self, message):
        if 1 >= self.loggingLevel:
            self.log_(self.levels[1], message)
            
    def syslogLog(self, level, message):
        syslog.syslog(level, message)
        
    def loggingLog(self, level, message):
        logging.log(level, message)
        '''if self.fflush:
            logging._handlerList[0].flush()'''
            #logging.Handler.flush()
    def setLevel(self, level):
        self.loggingLevel = level
        
    def debug(self, message, vars):
        self.log(0, message, vars)
        
    def info(self, message, vars):
        self.log(1, message, vars)
        
    def warning(self, message, vars):
        self.log(2, message, vars)
        
    def error(self, message, vars):
        self.log(3, message, vars)
        
    def critical(self, message, vars):
        self.log(4, message, vars)
        
    def writeInfoP(self):
        return self.loggingLevel <= 1
    
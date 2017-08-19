"""
Syslog/Logging wrapper
"""

import logging
import syslog
from logging import handlers


LG_DEBUG = 0
LG_INFO = 1
LG_WARNING = 2
LG_ERROR = 3
LG_CRITICAL = 4

dateDelim = '.'
strftimeFormat = '%d' + dateDelim + '%m' + dateDelim + '%Y %H:%M:%S'

loggingLevels = {
    0: logging.DEBUG,
    1: logging.INFO,
    2: logging.WARNING,
    3: logging.ERROR,
    4: logging.CRITICAL
}
syslogLevels = {
    0: syslog.LOG_DEBUG,
    1: syslog.LOG_INFO,
    2: syslog.LOG_WARNING,
    3: syslog.LOG_ERR,
    4: syslog.LOG_CRIT
}

loggingFormat = '%(asctime)s %(levelname)-8s %(message)s'


class isdlogger(object):

    def __init__(self, ltype, loglevel=0, ident=None, filename=None,
                 format=loggingFormat, filemode='a+', maxBytes=10485760,
                 backupCount=3):
        self.loggingLevel = loglevel
        self.ident = ident
        if ltype == 'syslog':
            self.log_ = self.syslogLog
            self.levels = syslogLevels
            if not ident:
                self.ident = 'isdlogger'
            syslog.openlog(self.ident)
        elif ltype == 'logging':
            self.log_ = self.loggingLog
            self.levels = loggingLevels
            if not filename:
                raise Exception('Please specify the filename!')
            logging.root.setLevel(self.levels[loglevel])
            rtHdlr = handlers.RotatingFileHandler(
                filename,
                mode=filemode,
                maxBytes=maxBytes,
                backupCount=backupCount
            )
            rtHdlr.setFormatter(logging.Formatter(format))
            logging.root.addHandler(rtHdlr)
        else:
            raise Exception('Unknown logger type!')

    def log(self, level, message, vars):
        """generic logging method"""
        if level >= self.loggingLevel:
            self.log_(self.levels[level], message % vars)

    def reprl(self, level, obj, message='%s'):
        """quick method with 'repr'"""
        if level >= self.loggingLevel:
            self.log_(self.levels[level], message % repr(obj))

    def lprint(self, message):
        """print a message with 'INFO' level"""
        if 1 >= self.loggingLevel:
            self.log_(self.levels[1], message)

    def log_adapt(self, message, level):
        """for log adapter"""
        if level >= self.loggingLevel:
            self.log_(self.levels[level], message)

    def syslogLog(self, level, message):
        """syslog log method"""
        syslog.syslog(level, message)

    def loggingLog(self, level, message):
        """logging log method"""
        logging.log(level, message)

    def setLevel(self, level):
        """set logging level"""
        self.loggingLevel = level

    def setNewLevel(self, level):
        if self.loggingLevel != level:
            self.loggingLevel = level

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

    def writeInfoP(self):
        """predicate - whether level <= INFO level"""
        return self.loggingLevel <= 1


class pyrologger(isdlogger):
    """logger compatible with PYRO"""

    def __init__(self, *args, **kwargs):
        super(pyrologger, self).__init__(*args, **kwargs)
        self.trace_on = kwargs.get('trace_on', False)

    def _checkTraceLevel(self, level):
        return self.trace_on

    def _logfile(self):
        return 'pyro_log'

    def msg(self, source, *args):
        self._trace(LG_INFO, source, args)

    def warn(self, source, *args):
        self._trace(LG_WARNING, source, args)

    def error(self, source, *args):
        self._trace(LG_ERROR, source, args)

    def raw(self, str):
        self.log_(self.levels[LG_WARNING], str)

    def _trace(self, level, source, arglist):
        pass

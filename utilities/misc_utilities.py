from __future__ import with_statement

import sys

class PseudoLogger(object):
    def _pass(self, *args, **kwargs):
        pass
    
    def __getattr__(self, *args, **kwargs):
        return self._pass
    
def install_logger(lgr):
    global logger
    logger = lgr
    
class ExecuteAtomically(object):
    """To be used with `with` statement.
       Atomically executes a block of code,
       disabling thread switches."""
    def __init__(self):
        self.checkinterval = 100
    
    def __enter__(self):
        self.checkinterval = sys.getcheckinterval()
        sys.setcheckinterval(sys.maxint)
        
    def __exit__(self, type, value, tb):
        sys.setcheckinterval(self.checkinterval)
        
class ExecuteAtomicallySimple(object):
    """To be used with `with` statement.
       Atomically executes a block of code,
       disabling thread switches.
       Uses default checkinterval."""
    
    @classmethod
    def __enter__(cls):
        sys.setcheckinterval(sys.maxint)
        
    @classmethod
    def __exit__(cls, type, value, tb):
        sys.setcheckinterval(100)


    
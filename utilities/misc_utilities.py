from __future__ import with_statement

class PseudoLogger(object):
    def _pass(self, *args, **kwargs):
        pass
    
    def __getattr__(self, *args, **kwargs):
        return self._pass
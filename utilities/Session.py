from data_utilities import *

class Session(object):
    __slots__ = ('base',)
    
    def __init__(self):
        self.base = None
        
    def pop(self, key=-1):
        pass
    
    def has_hey(self, key):
        pass
    
    def __setitem__(self, key, item):
        pass
    
    def __getitem__(self, key):
        pass
    
    def set_data(self):
        pass
    
    def clean(self):
        pass
    
    
class DictSession(dict):
    __slots__ = ('get_data_fn', 'index_fn')
    
    def __init__(self, get_data_fn, index_fn):
        super(DictSession, self).__init__()
        self.get_data_fn = get_data_fn_opts
        self.index_fn = index_fn_opts
        
    def get_data(self, get_data_fn_opts, index_fn_opts):
        data = []
        try:
            data = self.get_data_fn(*get_data_fn_opts)
            super(DictSession, self).__init__(self.index_fn(data, *index_fn_opts))
        except Exception, ex:
            raise "Exception in DictSession.get_data: %s \n data: %s get_data_fn: %s index_fn: %s" % \
                  (repr(ex), data, repr(self.get_data_fn) + ' | ' + repr(get_data_fn_opts), repr(self.index_fn) + ' | ' + repr(index_fn_opts))
            
        
    
    
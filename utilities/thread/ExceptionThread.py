from __future__ import with_statement

from threading import Thread, Event
import os, sys, traceback
import datetime

sys.path.append(os.path.abspath('../../'))

from utilities.misc_utilities import PseudoLogger, install_logger


class ExceptionPack(object):
    __slots__ = ('exception_classes', 'callback_fn', 'exception_flags')
    
    def __init__(self):
        self.exception_classes = ()
        self.callback_fn = None
        self.exception_flags = []
        
class PermanentExceptionThread(Thread):
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None, 
                 exception_packs=[], run_fn_args=(), run_fn_kwargs={},
                 logger=PseudoLogger(), stop_event=Event(), cleanup_callback=None):
        
        super(self, Thread).__init__(group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None)
        
        self.exception_packs = exception_packs
        self.run_fn_args = run_fn_args
        self.run_fn_kwargs = run_fn_kwargs
        self.logger = logger
        self.stop_event = stopEvent
        self.cleanup_callback = cleanup_callback
        
        self.checkpoint = '__init__'
        
        
        
    def run_fn(self, *args, **kwargs):
        '''Used instead of run()
           Definitely override!'''
        pass
    
    def set_checkpoint(self, info_string):
        self.checkpoint = info_string
        
    def run(self):
        while True:
            
            if self.stop_event.isSet():
                if self.cleanup_callback:
                    self.cleanup_callback(self)
                self.set_checkpoint('Stopping: ' + datetime.datetime.now().isoformat())
                break
        try:
            self.run_fn(self.run_fn_args, self.run_fn_kwargs)
            
        except Exception, ex:
            for exPack in self.exception_packs:
                if 0: assert isinstance( exPack, ExceptionPack )
                if isinstance(ex, exPack.exception_classes):
                    if exPack.callback_fn:
                        exPack.callback_fn(self, ex)
                        
                    if 'break' in exPack.exception_flags:
                        break
            else:
                self.logger.error('%s: unhandled exception at checkpoint %s: %s | %s',
                                  self.getName(), self.checkpoint, repr(ex), traceback.format_exc())
                
                
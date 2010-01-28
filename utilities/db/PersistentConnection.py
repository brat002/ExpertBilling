from __future__ import with_statement


from threading import Thread, Lock, Event
from twisted.protocols.basic import implements, interfaces, defer, Int32StringReceiver
from twisted.internet.protocol import Factory
from collections import deque
import sys, os, time, traceback, datetime
import socket

sys.path.append(os.path.abspath('../../'))

from utilities.misc_utilities import PseudoLogger, install_logger
from utilities import logger 

class DBDisconnectException(Exception):
    pass

class DBFailException(Exception):
    pass

class PersistentDBConnection(object):
    
    def __init__(self, driver, dsn, cursor_factory = None, encoding = 'UTF8'):
        self.driver = driver
        self.dsn = dsn
        self.connected = None
        self.connection = None
        self.cursor_ = None
        self.encoding = encoding
        self.cursor_factory = cursor_factory
        
    def connect(self):
        try:
            self.connection = self.driver.connect(self.dsn)
            self.connection.set_client_encoding('UTF8')
            if self.cursor_factory:
                self.cursor_ = self.connection.cursor(cursor_factory=self.cursor_factory)
            else:
                self.cursor_ = self.connection.cursor()
            self.connected = True
        except Exception, ex:
            self.connected = False
            logger.error('Database connect failed: %s', (repr(ex),))
            raise DBDisconnectException(str(ex))
        
    def execute(self, query, args = ()):
        if not self.connected or self.connection.closed:
            self.connect()
            
        if args:
            self.cursor_.execute(query, args)
        else:
            self.cursor_.execute(query)
        
    def fetchone(self):
        return self.cursor_.fetchone()
    
    def fetchall(self):
        return self.cursor_.fetchall()
    
    def commit(self):
        self.connection.commit()
        
    def rollback(self):
        self.connection.rollback()
        
    def cursor(self):
        return self.connection.cursor()
       
    def close_(self):
        self.connected = False
        self.connection.close()
        
    def close(self):
        pass
    
#-*-coding=utf-8-*-

from __future__ import with_statement
import site

site.addsitedir('/opt/ebs/venv/lib/python2.6/site-packages')
site.addsitedir('/opt/ebs/venv/lib/python2.7/site-packages')
import sys
sys.path.insert(0, "modules")
sys.path.append("cmodules")
import gc
import copy

import signal
import os, sys
import marshal
#import psycopg2ct
#os.sys.modules['psycopg2']=psycopg2ct
import threading
import traceback
import ConfigParser
import socket, select, struct, datetime, time
import string, glob, types
import utilites

try:
    import codecs
except ImportError:
    codecs = None

import isdlogger
import saver
import IPy

from threading import Thread, Lock, Event
from IPy import IP, IPint, parseAddress
from collections import deque, defaultdict
from saver import graceful_loader, graceful_saver
import logging
from logging.handlers import TimedRotatingFileHandler, BaseRotatingHandler, _MIDNIGHT


from classes.nf_cache import *
from classes.common.Flow5Data import Flow5Data
from classes.cacheutils import CacheMaster
from classes.flags import NfFlags
from classes.vars import NfFilterVars, NfQueues, install_logger
from utilites import savepid, rempid, get_connection, getpid, check_running

#from dirq.QueueSimple import QueueSimple
#from saver import RedisQueue

from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu.utils import kwdict, reprcall
from kombu import Connection
from kombu.common import maybe_declare
from kombu.pools import producers

from queues import nf_write, task_exchange



NAME = 'nf'
DB_NAME = 'db'
FLOW_NAME = 'flow'

WRITE_OK = 1


class Worker(ConsumerMixin):

    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=nf_write,
                         callbacks=[self.process_task])]

    def process_task(self, body, message):
        body = body['data']

        
        try:
            for flow in body:
                ips = map(lambda ip: IPy.intToIp(ip, 4), flow[0:3])
    #            ips = map(lambda ip: IPy.intToIp(ip, 4), flow.getAddrSlice())
                queues.flowSynchroBox.appendData(list(ips) + list(flow[3:]))
            queues.flowSynchroBox.checkData()
        except Exception, ex:
            logger.error("NFWriter exception: %s \n %s", (repr(ex), traceback.format_exc()))

        message.ack()


        
                    
class nfDequeThread(Thread):
    '''Thread that gets packets received by the server from nfQueue queue and puts them onto the conveyour
    that gets flows and caches them.'''
    
    def __init__(self):
        self.tname = self.__class__.__name__
        Thread.__init__(self)
        
    def run(self):
        
        while True:
            try:
                with Connection(vars.kombu_dsn) as conn:
                    Worker(conn).run()

            except IndexError, err:
                time.sleep(3); continue  
            except Exception, ex:
                logger.error("NFF exception: %s \n %s", (repr(ex), traceback.format_exc()))


    

def ungraceful_save():
    global suicideCondition
    global cacheThr, threads, suicideCondition, vars

    suicideCondition[cacheThr.tname] = True
    for key in suicideCondition.iterkeys():
        suicideCondition[key] = True
    rempid(vars.piddir, vars.name)
    print "NF Writer: exiting"
    logger.lprint("NF Writer exiting.")
    sys.exit()
    

class MyTimedRotatingFileHandler(BaseRotatingHandler):
    """
    Handler for logging to a file, rotating the log file at certain timed
    intervals.

    If backupCount is > 0, when rollover is done, no more than backupCount
    files are kept - the oldest ones are deleted.
    """
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None):
        global vars
        self.when = string.upper(when)
        self.backupCount = backupCount
        
        currentTime = int(time.time())
        if self.when == 'S':
            self.interval = 1 # one second
            self.suffix = "%Y-%m-%d_%H-%M-%S"
        elif self.when == 'M':
            self.interval = 60 # one minute
            self.suffix = "%Y-%m-%d_%H-%M"
        elif self.when == 'H':
            self.interval = 60 * 60 # one hour
            self.suffix = "%Y-%m-%d_%H"
        elif self.when == 'D' or self.when == 'MIDNIGHT':
            self.interval = 60 * 60 * 24 # one day
            self.suffix = "%Y-%m-%d"
        elif self.when.startswith('W'):
            self.interval = 60 * 60 * 24 * 7 # one week
            if len(self.when) != 2:
                raise ValueError("You must specify a day for weekly rollover from 0 to 6 (0 is Monday): %s" % self.when)
            if self.when[1] < '0' or self.when[1] > '6':
                raise ValueError("Invalid day specified for weekly rollover: %s" % self.when)
            self.dayOfWeek = int(self.when[1])
            self.suffix = "%Y-%m-%d"
        else:
            raise ValueError("Invalid rollover interval specified: %s" % self.when)

        self.interval = self.interval * interval # multiply by units requested
        self.rolloverAt = currentTime - (currentTime % self.interval) + self.interval
        if self.when == 'MIDNIGHT' or self.when.startswith('W'):
            # This could be done with less code, but I wanted it to be clear
            t = time.localtime(currentTime)
            currentHour = t[3]
            currentMinute = t[4]
            currentSecond = t[5]
            # r is the number of seconds left between now and midnight
            r = _MIDNIGHT - ((currentHour * 60 + currentMinute) * 60 +
                    currentSecond)
            self.rolloverAt = currentTime + r
            if when.startswith('W'):
                day = t[6] # 0 is Monday
                if day != self.dayOfWeek:
                    if day < self.dayOfWeek:
                        daysToWait = self.dayOfWeek - day
                    else:
                        daysToWait = 6 - day + self.dayOfWeek + 1
                    self.rolloverAt = self.rolloverAt + (daysToWait * (60 * 60 * 24))
        t = self.rolloverAt - self.interval
        timeTuple = time.localtime(t)
        folder = os.path.abspath(os.path.join(vars.FLOW_DIR,time.strftime('%Y-%m-%d', timeTuple)))
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        #open_fname = os.path.join(folder, filename + "." + time.strftime(self.suffix, timeTuple))      
        open_fname = os.path.join(folder, time.strftime(self.suffix, timeTuple))
           
        BaseRotatingHandler.__init__(self, open_fname, 'a', encoding)
        open_fname = os.path.join(folder, time.strftime(self.suffix, timeTuple))
        self.baseFilename = os.path.abspath(open_fname)
        



        #print "Will rollover at %d, %d seconds from now" % (self.rolloverAt, self.rolloverAt - currentTime)

    def shouldRollover(self, record):
        """
        Determine if rollover should occur

        record is not used, as we are just comparing times, but it is needed so
        the method siguratures are the same
        """
        t = int(time.time())
        if t >= self.rolloverAt:
            return 1
        #print "No need to rollover: %d, %d" % (t, self.rolloverAt)
        return 0

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        self.stream.close()
        # get the time that this sequence started at and make it a TimeTuple
        '''
        t = self.rolloverAt - self.interval
        timeTuple = time.localtime(t)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        
        if os.path.exists(dfn):
            os.remove(dfn)
        os.rename(self.baseFilename, dfn)
        '''
        t = self.rolloverAt
        timeTuple = time.localtime(t)
        
        t = self.rolloverAt
        timeTuple = time.localtime(t)
        folder = os.path.abspath(os.path.join(vars.FLOW_DIR,time.strftime('%Y-%m-%d', timeTuple)))
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        #open_fname = os.path.join(folder, filename + "." + time.strftime(self.suffix, timeTuple))      
        open_fname = os.path.join(folder, time.strftime(self.suffix, timeTuple))
           
        self.baseFilename = os.path.abspath(open_fname)
        
        dfn = self.baseFilename #self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        if self.backupCount > 0:
            # find the oldest log file and delete it
            s = glob.glob(self.baseFilename + ".20*")
            if len(s) > self.backupCount:
                s.sort()
                os.remove(s[0])
        #print "%s -> %s" % (self.baseFilename, dfn)
        if self.encoding:
            self.stream = codecs.open(dfn, 'a', self.encoding)
        else:
            self.stream = open(dfn, 'a')
        self.rolloverAt = self.rolloverAt + self.interval



class SynchroPacket(object):
    __slots__ = ('getDataPLZ', 'gotDataKTX', 'dataList', 'maxCount', 'maxTimeout',\
                  'dataCount', 'dataTime', 'SYNCHRO')
    
    def __init__(self, count = 1, timeout = 5):
        self.getDataPLZ = Event()
        self.gotDataKTX = Event()
        self.dataList = []
        self.maxCount = count
        self.maxTimeout = timeout
        self.dataCount = 0
        self.dataTime = 0
        self.SYNCHRO = True if self.dataCount == 1 else False
            
    def checkData(self):
        if (self.dataCount >= self.maxCount or (time.clock() - self.dataTime) > self.maxTimeout)\
          and not self.isDataEmpty() and self.gotDataKTX.isSet() == False:
            self.getDataPLZ.set()
            
    def isDataEmpty(self):
        return not bool(self.dataList)
    
    def waitForData(self):
        self.gotDataKTX.clear()
        #maybe timeout here?
        self.getDataPLZ.wait()
        #sys.setcheckinterval(0)
        data = self.dataList if not self.SYNCHRO else self.dataList[0]
        self.dataList = []
        self.dataTime = time.clock()
        self.getDataPLZ.clear()
        self.gotDataKTX.set()
        #sys.setcheckinterval(1000)
        return data
        
        
    def appendData(self, data):
        self.dataList.append(data)
        self.dataCount += 1
        if self.SYNCHRO:
            self.getDataPLZ.set()
            self.gotDataKTX.wait()

def simpleCSV(csvList):
    return ','.join([str(csvV) for csvV in csvList])

class FlowLoggerThread(Thread):
    def __init__(self, errorLogger, synchroBox, dieCondition, dataTransformer, fHandler, fVars):
        Thread.__init__(self)
        self.tname = self.__class__.__name__
        #create notifier
        self.synchroBox = synchroBox
        self.dieCondition = dieCondition
        self.errorLogger = errorLogger
        self.dataTranformer = dataTransformer
        self.fVars = fVars
        try:
            self.fileLogger = logging.getLogger('filelogger')
            self.fileLogger.setLevel(logging.DEBUG)
            #flHdlr = TimedRotatingFileHandler('/'.join((fVars.FLOW_DIR, fVars.FLOW_PREFIX)), when = fVars.FLOW_WHEN, interval = fVars.FLOW_INTERVAL)
            #currentTime = int(time.time())
            #flHdlr.rolloverAt = currentTime - (currentTime % flHdlr.interval) + flHdlr.interval
            flHdlr = fHandler(fVars.FLOW_PREFIX, when = fVars.FLOW_WHEN, interval = fVars.FLOW_INTERVAL)
            flHdlr.setFormatter(logging.Formatter("%(message)s"))
            self.fileLogger.addHandler(flHdlr)
        except Exception, ex:
            self.errorLogger.error("Flowlogger creation exception: %s %s | %s", (self.getName(), repr(ex), traceback.format_exc()))
            print "Flowlogger creation exception: flow logging didn't start. See log."
            self.notifyError("Flowlogger creation exception: %s %s | %s" % (self.getName(), repr(ex), traceback.format_exc()))
    
    def notifyError(self, error):
        #maybe e-mail?
        pass
    
    def heuristics(self):
        pass
    
    def statistics(self):
        pass
    
    def run(self):
        #base on events
        while True:
            if self.dieCondition[self.__class__.__name__]:
                try:
                    for handler in self.fileLogger.handlers:
                        handler.flush()
                        handler.close()
                    self.errorLogger.info('Flowlogger terminated without errors.', ())
                except Exception, ex:
                    self.errorLogger.error("Flowlogger close exception: %s %s | %s", (self.getName(), repr(ex), traceback.format_exc()))
                break
            
            data = self.synchroBox.waitForData()
            try:
                for dataPiece in data:
                    dataString = self.dataTranformer(dataPiece)
                    self.fileLogger.log(logging.INFO, dataString)
                #heuristics
                #statistics
                for handler in self.fileLogger.handlers:
                    handler.flush()
            except Exception, ex:
                #write exception
                self.errorLogger.error("Flowlogger write exception: %s %s | %s", (self.getName(), repr(ex), traceback.format_exc()))
                #heuristics
                if self.fVars.FLOW_MAIL_WARNING:
                    self.notifyError(ex)
                    


def SIGTERM_handler(signum, frame):
    logger.lprint("SIGTERM recieved")
    graceful_save()

def SIGINT_handler(signum, frame):
    logger.lprint("SIGINT recieved")
    graceful_save()
    
def SIGHUP_handler(signum, frame):
    global config
    logger.lprint("SIGHUP recieved")
    try:
        config.read("ebs_config.ini")
        logger.setNewLevel(int(config.get("nf", "log_level")))
        flags.writeProf = logger.writeInfoP()
    except Exception, ex:
        logger.error("SIGHUP config reread error: %s", repr(ex))
    else:
        logger.lprint("SIGHUP config reread OK")

def SIGUSR1_handler(signum, frame):
    global flags
    logger.lprint("SIGUSR1 recieved")

    
def graceful_save():
    global cacheThr, threads, suicideCondition, vars


    logger.lprint("About to stop gracefully.")
    #pool.close()


    rempid(vars.piddir, vars.name)
    logger.lprint(vars.name + " stopping gracefully.")

    sys.exit()
        
class Watcher:
    """this class solves two problems with multithreaded
    programs in Python, (1) a signal might be delivered
    to any thread (which is just a malfeature) and (2) if
    the thread that gets the signal is waiting, the signal
    is ignored (which is a bug).

    The watcher is a concurrent process (not thread) that
    waits for a signal and the process that contains the
    threads.  See Appendix A of The Little Book of Semaphores.
    http://greenteapress.com/semaphores/

    I have only tested this on Linux.  I would expect it to
    work on the Macintosh and not work on Windows.
    """
    
    def __init__(self):
        """ Creates a child thread, which returns.  The parent
            thread waits for a KeyboardInterrupt and then kills
            the child thread.
        """
        self.child = os.fork()
        if self.child == 0:
            return
        else:
            self.watch()

    def watch(self):
        try:
            os.wait()
        except KeyboardInterrupt:
            # I put the capital B in KeyBoardInterrupt so I can
            # tell when the Watcher gets the SIGINT
            print 'KeyBoardInterrupt'
            self.kill()
        sys.exit()

    def kill(self):
        try:
            os.kill(self.child, signal.SIGKILL)
        except OSError: pass
        
def main ():        
    global flags, queues, cacheMaster, threads, cacheThr, caches, script

    threads = []
    

    threads = []

    Watcher()
    
    thrnames = [(nfDequeThread, 'nfDequeThread'),]
    for thClass, thName in thrnames:
        threads.append(thClass())
        threads[-1].setName(thName)
    
    if vars.WRITE_FLOW:
        flowWriterThr = FlowLoggerThread(logger, queues.flowSynchroBox, suicideCondition, simpleCSV, MyTimedRotatingFileHandler, vars)
        flowWriterThr.setName('FlowWriter')
        threads.append(flowWriterThr)
    #-----

        

    try:
        signal.signal(signal.SIGHUP, SIGHUP_handler)
    except: logger.lprint('NO SIGHUP!')
    try:
        signal.signal(signal.SIGUSR1, SIGUSR1_handler)
    except: logger.lprint('NO SIGUSR1!')
    
    try:
        signal.signal(signal.SIGTERM, SIGTERM_handler)
    except: logger.lprint('NO SIGTERM!')

    try:
        signal.signal(signal.SIGINT, SIGINT_handler)
    except:
        print "nosigint" 
        logger.lprint('NO SIGINT!')
    
    for th in threads:
        suicideCondition[th.__class__.__name__] = False
        th.start()
        time.sleep(0.5)

    
    #
    savepid(vars.piddir, vars.name)
    print "ebs: nfwriter: started"    
    

    
    


if __name__=='__main__':
        
    flags = NfFlags()
    vars  = NfFilterVars()
    
   
    config = ConfigParser.ConfigParser()
    config.read("ebs_config.ini")

    try:
        
        import psyco
        psyco.full(memory=100)
        psyco.profile(0.05, memory=100)
        psyco.profile(0.2)
    except:
        print "Can`t optimize"
        
    try:
        vars.get_vars(config=config, name=NAME, db_name=DB_NAME, flow_name=FLOW_NAME)

        
        logger = isdlogger.isdlogger(vars.log_type, loglevel=vars.log_level, ident=vars.log_ident, filename=vars.log_file) 
        saver.log_adapt = logger.log_adapt
        utilites.log_adapt = logger.log_adapt
        install_logger(logger)
        queues = NfQueues(dcacheNum=vars.CACHE_DICTS)
        queues.flowSynchroBox = SynchroPacket(vars.FLOW_COUNT, vars.FLOW_TIME)
        logger.lprint('Nf Writer start')
        if check_running(getpid(vars.piddir, 'nfwriter'), 'nfwriter'): raise Exception ('%s already running, exiting' % 'nfwriter')
        
        out_connection = Connection(vars.kombu_dsn)
        
        
        #write profiling info predicate
        flags.writeProf = logger.writeInfoP()
        #file_test(vars.DUMP_DIR, vars.PREFIX)
        if vars.WRITE_FLOW:
            try:
                os.mkdir(vars.FILE_DIR)
            except: pass

            
        suicideCondition = {}    
        #vars.FLOW_TYPES = {5 : (header5, flow5)}        


        #-------------------
        #print "ebs: nfwriter: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in nfwriter, exiting: ', repr(ex)
        #print "Exception in nffilter, exiting: %s \n %s'" % (repr(ex), traceback.format_exc())
    
    
    

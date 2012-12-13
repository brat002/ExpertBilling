#-*-coding=utf-8-*-

from __future__ import with_statement
import site
site.addsitedir('/opt/ebs/venv/lib/python2.6/site-packages')
site.addsitedir('/opt/ebs/venv/lib/python2.7/site-packages')
import sys
sys.path.insert(0, "modules")
sys.path.append("cmodules")

import signal
import os, sys
import utilites

import traceback
import ConfigParser
import socket, time
import glob


try:
    import codecs
except ImportError:
    codecs = None

import isdlogger
import saver


from collections import deque
from saver import graceful_loader, graceful_saver
from threading import Thread

from twisted.internet.protocol import DatagramProtocol


try:
    from twisted.internet import epollreactor
    epollreactor.install()
except:
    print 'No poll(). Using select() instead.'
from twisted.internet import reactor


from classes.flags import NfFlags
from classes.vars import NfVars, install_logger
from utilites import savepid, rempid, getpid, check_running
                     

#from dirq.QueueSimple import QueueSimple
#from saver import RedisQueue



from kombu.common import maybe_declare
from kombu.pools import producers
from kombu import Connection

from queues import task_exchange



def send_as_task(connection, data, routing_key):
    payload = {'data': data}


    with producers[connection].acquire(block=True) as producer:
        maybe_declare(task_exchange, producer.channel)
        producer.publish(payload, 
                         serializer='pickle',
                         #         compression='bzip2',
                                  exchange=task_exchange, 
                                  routing_key=routing_key)



NAME = 'nf'
DB_NAME = 'db'
NET_NAME = 'nfroutine_nf'
FLOW_NAME = 'flow'


class Reception_UDP(DatagramProtocol):
    '''
    Twisted Asynchronous server that recieves datagrams with NetFlow packets
    and appends them to 'nfQueue' queue.
    '''

        
    def datagramReceived(self, data, addrport):
        global FTT
        if len(data) <= vars.MAX_DATAGRAM_LEN:
            message = '%s|<>|%s' % (data, addrport[0])
            FTT.buffer.appendleft(message)
            #send_as_task(in_dirq, message, 'nf_in')
            
        else:
            logger.error("NF server exception: packet %s <= %s", (len(data), vars.MAX_DATAGRAM_LEN))

class FlowToQueueThread(Thread):
    def __init__(self):
        self.tname = self.__class__.__name__
        Thread.__init__(self)
        self.buffer = deque()
        
    def run(self):
        last_time = time.time()
        global suicideCondition
        while not suicideCondition:
            
            if len(self.buffer)>=50 or time.time()-last_time>10 and self.buffer:
                #in_dirq.put("_|_|_".join(self.buffer))
                
                r = []
                n=0
                while n<50:
                    try:
                        r.append(self.buffer.pop())
                    except IndexError, e:
                        break
                    n+=1
                if r:
                    data = "_|_|_".join(r)
                    send_as_task(in_dirq, data, 'nf_in')
                    last_time = time.time()
            else:
                
                time.sleep(0.1)
        

def ungraceful_save():
    global suicideCondition
    global cacheThr, threads, suicideCondition, vars
    from twisted.internet import reactor
    reactor.callFromThread(reactor.disconnectAll)
    reactor.callFromThread(reactor.stop)
    reactor._started = False
    rempid(vars.piddir, vars.name)
    print "NF: exiting"
    logger.lprint("NF exiting.")
    sys.exit()
    

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
    with flags.cacheLock: flags.cacheFlag = True
    
def graceful_save():
    global cacheThr, threads, suicideCondition, vars
    from twisted.internet import reactor
    reactor.callFromThread(reactor.disconnectAll)
    reactor.callFromThread(reactor.stop)
    reactor._started = False
    reactor.stop()
    suicideCondition = True
    logger.lprint("About to stop gracefully.")
    time.sleep(1)
    #pool.close()
    #time.sleep(1)
    

    
    rempid(vars.piddir, vars.name)
    logger.lprint(vars.name + " stopping gracefully.")
    print vars.name + " stopping gracefully."


def main ():        
    global flags, queues, cacheMaster, FTT, cacheThr, caches, script

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
    except: logger.lprint('NO SIGINT!')


    #add "listenunixdatagram!"
    #listenUNIXDatagram(self, address, protocol, maxPacketSize=8192,
    
    FTT = FlowToQueueThread()
    FTT.start()

    reactor.listenUDP(vars.PORT, Reception_UDP())
    
    #
    savepid(vars.piddir, vars.name)
    print "ebs: nf: started"    
    
    reactor.run(installSignalHandlers=False)
    
    


if __name__=='__main__':
        
    flags = NfFlags()
    vars  = NfVars()

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
        vars.get_vars(config=config, name=NAME, db_name=DB_NAME, net_name=NET_NAME, flow_name=FLOW_NAME)
        #print repr(vars)
        #in_dirq = QueueSimple(vars.QUEUE_IN)
        #in_dirq = RedisQueue("in_queue", host=vars.REDIS_HOST, port=vars.REDIS_PORT, db=vars.REDIS_DB)
        
        in_dirq = Connection(vars.kombu_dsn)
        
        suicideCondition = False
        logger = isdlogger.isdlogger(vars.log_type, loglevel=vars.log_level, ident=vars.log_ident, filename=vars.log_file) 
        saver.log_adapt = logger.log_adapt
        utilites.log_adapt = logger.log_adapt
        install_logger(logger)
        logger.info("Config variables: %s", repr(vars))
        logger.lprint('Nf start')
        if check_running(getpid(vars.piddir, vars.name), vars.name): raise Exception ('%s already running, exiting' % vars.name)

        #-------------------
        print "ebs: nf: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in nf, exiting: ', repr(ex)
        print "Exception in nf, exiting: %s \n %s'" % (repr(ex), traceback.format_exc())
    
    
    

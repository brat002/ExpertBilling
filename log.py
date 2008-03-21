# -*- coding:utf-8 -*-

import settings

from time import strftime


class simple_log(object):
    
    def __init__(self,message=None, packet=None):
        if settings.LOG:
            print 'called', message
            try:
                
                log_file = file(settings.LOG_LOCATION + 'log.txt','a+')
                log_file.write('*********** ' + strftime("%Y-%m-%d %H:%M:%S") + ' ***********\n')
                log_file.write('\n')
                if message:
                    log_file.write(str(message))
                if packet:
                    for key,value in packet.items():
                        log_file.write('%s %s\n' % (packet._DecodeKey(key),packet[packet._DecodeKey(key)][0]))
                        
                log_file.write('\n')
                log_file.write('*********** * ***********\n')
                log_file.close()
                print 'write Ok'
            except Exception, e:
                pass
            
            del self
    
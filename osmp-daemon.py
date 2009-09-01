# -*- coding=utf-8 -*-
import  datetime
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from payment_systems import osmp_routine
from payment_systems import payment_misc

import isdlogger, ConfigParser
from classes.vars import Vars
import utilites
from IPy import parseAddress

NAME = 'osmp_daemon'
DB_NAME = 'db'

def main():
    try:
        server = HTTPServer(('', 8080), osmp_routine.MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    config.read("ebs_config.ini")
    try:
        vars = Vars()
        vars.get_vars(config=config, name=NAME, db_name=DB_NAME)  
        logger = isdlogger.isdlogger(vars.log_type, loglevel=vars.log_level, ident=vars.log_ident, filename='log/'+NAME+'_log') 
        osmp_routine.vars = vars
        osmp_routine.logger = logger
        osmp_routine.get_connection = utilites.get_connection
        osmp_routine.parseAddress = parseAddress
        osmp_routine.db_connection = utilites.get_connection(vars.db_dsn)
        osmp_routine.checker = payment_misc.ByFlatIPNIPCheck()
    except Exception, ex:
        print 'Exception in %s, exiting: ' % NAME, repr(ex)
        logger.error('Exception in %s, exiting: %s \n %s', (NAME, repr(ex), traceback.format_exc()))
    main()
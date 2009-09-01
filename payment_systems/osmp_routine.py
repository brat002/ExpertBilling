from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import asyncore, urllib, urlparse, datetime, decimal
import psycopg2
import psycopg2.extras


logger = None
vars   = None
get_connection = None
parseAddress = None
NAME = 'osmp_routine'
db_connection = None
checker = None

#MIN_ADDRESS = 1334710272
#MAX_ADDRESS = 1334714367

MIN_ADDRESS = 2130706432 #- test - local
MAX_ADDRESS = 2130706687

#MIN_ADDRESS = 168427776 #- test - local network
#MAX_ADDRESS = 168428031

STATE_OK   = 0    
TEMP_ERROR = 1  
WRONG_ACCOUNT_ID_FORMAT = 4 #fatal
ACCOUNT_ID_NOT_FOUND    = 5  #fatal
TRANSACTIONS_DISABLED_BY_ISP      = 7 #fatal
TRANSACTIONS_DISABLED_MAINTENANCE = 8 #fatal
ACCOUNT_NOT_ACTIVE = 79 #fatal
TRANSACTION_NOT_COMPLETED_YET = 90  
AMOUNT_TOO_SMALL   = 241 #fatal
AMOUNT_TOO_BIG     = 242 #fatal
ACCOUNT_CHECK_FAIL = 243 #fatal
OTHER_ISP_ERROR    = 300 #fatal

USER_OK = 1
NO_USER = 2
DB_FAIL = 3

MINUS_ONE = decimal.Decimal(-1)

PAY_RESPONSE = \
u"""<?xml version="1.0" encoding="UTF-8"?>
    <response>
        <osmp_txn_id>%s</osmp_txn_id>
        <prv_txn>%s</prv_txn>
        <sum>%s</sum>
        <result>%s</result>
        %s
    </response>""" 


CHECK_RESPONSE = \
u"""<?xml version="1.0" encoding="UTF-8"?>
    <response>
        <osmp_txn_id>%s</osmp_txn_id>
        <result>%s</result>
        %s
   </response>"""

def urldecode(query):
    d = {}
    a = query.split('&')
    for s in a:
        if s.find('='):
            k,v = map(urllib.unquote, s.split('='))
            try:
                d[k].append(v)
            except KeyError:
                d[k] = [v]
    return d

class MyHandler(BaseHTTPRequestHandler):

    check_fields = ['command', 'txn_id', 'account', 'sum', ]
    pay_fields = ['command', 'txn_id', 'txn_date', 'account', 'sum', ]
    
    def get_fields(self, c_type = None):
        parsed_path = urlparse.urlparse(self.path)
        parsed_query = urldecode(parsed_path.query)
        rs = {}
        if c_type == 'check':
            fls = self.check_fields
        elif c_type == 'pay':
            fls = self.pay_fields
        else:
            fls = self.check_fields
        for f in fls:
            try:
                rs[f] = parsed_query[f][0]
            except KeyError:
                return False
        return rs
    
    def send404(self):
        self.send_error(404,'File Not Found: %s' % self.path)

    def send_check(self, fs, result, comment = None):
        self.send_response(200)
        self.send_header('Content-type', 'text/xml')
        self.end_headers()
        cmt = """<comment>%s</comment>""" % comment if comment else ''
        rs = CHECK_RESPONSE % (fs['txn_id'], result, cmt)

        self.wfile.write(rs)
        return True
    
    def send_c(self, c_type, fs, result, comment = None):
        if c_type == 'check':
            self.send_check(fs, result, comment)
        elif c_type == 'pay':
            fs.update({'prv_txn': ''})
            self.send_pay(fs, result, comment)
        else:
            self.send404()
            
    def send_pay(self, fs, result, comment = None):
        try:
            prv_txn = fs['prv_txn']
        except KeyError:
            fs.update({'prv_txn': ''})
        self.send_response(200)
        self.send_header('Content-type', 'text/xml')
        self.end_headers()
        cmt = """<comment>%s</comment>""" % comment if comment else ''
        rs = PAY_RESPONSE % (fs['txn_id'], fs['prv_txn'], fs['sum'], result, cmt)        
        self.wfile.write(rs)
        return True
    
    def db_connect(self):
        global db_connection
        try:
            db_connection = get_connection(vars.db_dsn)
        except Exception, ex:
            logger.error("%s: database connection error: %s", (NAME, repr(ex)))
            
            '''
            if c_type == 'check':
                self.send_check(fs, TEMP_ERROR, 'Unable to connect to database')
            elif c_type == 'pay':
                fs.update({'prv_txn': ''})
                self.send_pay(fs, TEMP_ERROR, 'Unable to connect to database')
            else:
                self.send404()
            return False'''
            return False

        #self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  
        return True
    def serve_check(self, fs):
        try:
            uname = str(fs['account'])
        except Exception, ex:
            logger.error("%s serve check account error: %s", (NAME, repr(ex)))
            self.send_check(fs, WRONG_ACCOUNT_ID_FORMAT)
            return
            
        if not checker.pre_check(uname):
            logger.warning("%s wrong account name", (NAME,))
            self.send_check(fs, WRONG_ACCOUNT_ID_FORMAT)
            return
        status, err = checker.check_db(uname, db_connection)
        if status == DB_FAIL:
            logger.error("%s check database fail: %s", (NAME, repr(ex)))
            try: 
                self.db_connect()
            except Exception, ex:
                logger.error("%s check database fail: %s", (NAME, repr(ex)))
                self.send_check(fs, TEMP_ERROR, "Database failure")
                return
            status, err = checker.check_db(uname, db_connection)
        if status == DB_FAIL:
            self.send_check(fs, TEMP_ERROR, "Database failure")
            return
        elif status == NO_USER:
            self.send_check(fs, ACCOUNT_ID_NOT_FOUND)
            return
        else:
            self.send_check(fs, STATE_OK)
            return
        
    def serve_pay(self, fs):
        try:
            try:
                uname = str(fs['account'])
            except Exception, ex:
                logger.error("%s serve pay account error: %s", (NAME, repr(ex)))
                self.send_pay(fs, WRONG_ACCOUNT_ID_FORMAT)
                return
                
            if not checker.pre_check(uname):
                logger.warning("%s wrong account name", (NAME,))
                self.send_pay(fs, WRONG_ACCOUNT_ID_FORMAT)
                return
            
            tx_datetime = fs.get('txn_date')
            
            if not tx_datetime: 
                tx_datetime = datetime.datetime.now()
            else:
                tx_datetime = datetime.datetime.strptime(tx_datetime, '%Y%m%d%H%M%S')
                
            pay_summ = decimal.Decimal(fs['sum']) * MINUS_ONE
            status, data = checker.get_db(uname, db_connection, tx_datetime)
            if status == DB_FAIL:
                logger.error("%s check database fail: %s", (NAME, repr(data)))
                try: 
                    self.db_connect()
                except Exception, ex:
                    logger.error("%s check database fail: %s", (NAME, repr(ex)))
                    self.send_pay(fs, TEMP_ERROR, "Database failure")
                    return
                status, data = checker.get_db(uname, db_connection, tx_datetime)
            if status == DB_FAIL:
                logger.error("%s check database fail: %s", (NAME, repr(data)))
                self.send_pay(fs, TEMP_ERROR, "Database failure")
                return
            elif status == NO_USER:
                self.send_pay(fs, ACCOUNT_ID_NOT_FOUND)
                return
            (account_id, acctf_id, tarif_id) = data
            status, data = checker.pay_db(db_connection, account_id, acctf_id, tarif_id, pay_summ, tx_datetime)
            if status == DB_FAIL:
                logger.error("%s check database fail: %s", (NAME, repr(data)))
                self.send_pay(fs, TEMP_ERROR, "Database failure")
                return
            elif status == NO_USER:
                self.send_pay(fs, ACCOUNT_ID_NOT_FOUND)
                return
            fs.update({'prv_txn': str(data)})
            self.send_pay(fs, STATE_OK)
        except Exception, ex:
            logger.error("%s PAY FAIL: %s", (NAME, repr(ex)))
            self.send_pay(fs, OTHER_ISP_ERROR)
            
    def check_ip(self, ip):
        try:
            ip_int = parseAddress(ip)[0]
        except Exception, ex:
            logger.error('Wrong ip: %s, %s', (ip, repr(ex)))
            return False
        if ip_int >= MIN_ADDRESS and ip_int <= MAX_ADDRESS:
            return True
        else:
            logger.warning('CLIENT IP NOT IN RANGE: %s', (ip,))
            
    def do_GET(self):
        global db_connection
        ip_status = self.check_ip(self.client_address[0])
        if not ip_status:
            self.send404(); return
        cfs = ''
        try:
            cfs = self.get_fields('check')
            if not cfs: raise Exception('WRONG CFS')
        except Exception, ex:
            logger.error('%s: wrong check fields: %s', (NAME, repr(ex)))
            self.send404(); return
        command = cfs.get('command', 'no_command')
        if command not in ('pay', 'check'):
            logger.error('%s: wrong command: %s', (NAME, command))
            self.send404(); return
        if command == 'check':
            self.serve_check(cfs)
        else:
            try:
                cfs = self.get_fields('pay')
                if not cfs: raise Exception('WRONG CFS')
            except Exception, ex:
                logger.error('%s: wrong pay fields: %s', (NAME, repr(ex)))
                self.send404(); return
                
            self.serve_pay(cfs)

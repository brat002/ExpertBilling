# -*- coding=utf-8 -*-
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import asyncore, urllib, urlparse, datetime

import psycopg2
import psycopg2.extras

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
        rs = u"""<?xml version="1.0" encoding="UTF-8"?>
<response>
  <id>%s</id>
  <result>%s</result>
              """ % (fs['txn_id'], result)
        if comment is not None:
            rs += u"""
  <comment>%s</comment>""" % comment
        rs += u"""
</response>"""
        
        self.wfile.write(rs)
        return True
    
    def send_pay(self, fs, result, comment = None):
        try:
            prv_txn = fs['prv_txn']
        except KeyError:
            fs.update({'prv_txn': ''})
        self.send_response(200)
        self.send_header('Content-type', 'text/xml')
        self.end_headers()
        rs = u"""<?xml version="1.0" encoding="UTF-8"?>
<response>
  <id>%s</id>
  <prv_txn>%s</prv_txn>
  <sum>%s</sum>
  <result>%s</result>""" % (fs['txn_id'], fs['prv_txn'], fs['sum'], result)
        if comment is not None:
            rs += u"""
  <comment>%s</comment>""" % comment
        rs += u"""
</response>"""
        
        self.wfile.write(rs)
        return True
    
    def db_connect(self, c_type, fs):
        try:
            self.conn = psycopg2.connect("dbname='ebs_ref_sql' user='mikrobill' host='10.10.1.1' password='1234'");
        except:
            if c_type == 'check':
                self.send_check(fs, 1, 'I am unable to connect to the database')
            elif c_type == 'pay':
                fs.update({'prv_txn': ''})
                self.send_pay(fs, 1, 'I am unable to connect to the database')
            else:
                self.send404()
            return False
        self.conn.set_client_encoding('UTF8')
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  
        return True
        
    
    def do_GET(self):
        if self.client_address[0] == '82.195.26.130':
            try:
                cfs = self.get_fields('check')
                if cfs:
                    if cfs['command'] == 'check':
                        fs = self.get_fields('check')
                        if fs:
                            if not self.db_connect('check', fs):
                                return
                            q = "SELECT 1 FROM public.billservice_account WHERE username = %s"
                            self.cursor.execute(q, (fs['account'],))
                            f = self.cursor.fetchone()
                            if f is not None:
                                self.send_check(fs, 0)
                            else:
                                self.send_check(fs, 1, 'User account not found')
                            self.cursor.close()
                            self.conn.close()
                            return
                        else:
                            self.send404()
                    elif cfs['command'] == 'pay':
                        fs = self.get_fields('pay')
                        if fs:
                            if not self.db_connect('pay', fs):
                                return                            
                            q = "SELECT id FROM public.billservice_account WHERE username = %s"
                            self.cursor.execute(q, (fs['account'],))
                            f = self.cursor.fetchone()
                            if f is not None:
                                q = "SELECT nextval('public.billservice_transaction_id_seq') as _id"
                                self.cursor.execute(q)
                                _id = self.cursor.fetchone()['_id']
                                q = """INSERT INTO public.billservice_transaction(id, bill, account_id, type_id, approved, tarif_id, summ, description, created)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                                fs.update({'prv_txn': _id})
                                try:
                                    self.cursor.execute(q, 
                                        (int(_id), '', int(f['id']), 'OSMP_BILL', True, None, float(fs['sum']), '', datetime.datetime.now(),)
                                    )
                                    self.conn.commit()
                                    self.send_pay(fs, 0)
                                except:
                                    self.send_pay(fs, 1, 'Error during query execution')
                            else:
                                self.send_pay(fs, 1, 'User account not found')
                            self.cursor.close()
                            self.conn.close()                                
                            return
                        else:
                            self.send404()
                    else:
                        self.send404()
                else:
                    self.send404()
            except IOError:
                self.send404()
        else:
            self.send404()


def main():
    try:
        server = HTTPServer(('', 8080), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()
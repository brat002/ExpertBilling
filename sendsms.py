#-*-coding=utf-8-*-

import os, sys
"""
http://howto.gumph.org/content/send-sms-messages-from-linux/
"""

sys.path.append("/opt/ebs/data/modules")
command='sms_client smscenter:'
SEND_IF_LESS=5000

import  datetime, time

import psycopg2, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
import ConfigParser
from DBUtils.PooledDB import PooledDB
from mako.template import Template
import commands

class Object(object):
    def __init__(self, result=[], *args, **kwargs):
        for key in result:
            setattr(self, key, result[key])

        for key in kwargs:
            setattr(self, key, kwargs[key])  


#from mail.mail import send_mail

def send_balance_notice():
    connection = pool.connection()
    connection._con._con.set_client_encoding('UTF8')       
    cur = connection.cursor()
    cur = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cur.execute("SELECT body FROM billservice_template as template WHERE type_id=8;")
    try:
        body = cur.fetchone()["body"]
    except Exception, ex:
        print "Sendsms : Template body with type_id=8. internal exception: %s" % (repr(ex),)
        return
    #print body   
    
    cur.execute("SELECT * FROM billservice_account ORDER BY id ASC;")
    connection.commit()
    
    accounts = map(Object, cur.fetchall()) 
    
    cur.execute("SELECT * FROM billservice_operator ORDER BY id ASC LIMIT 1;")
    connection.commit()
    
    try:
        operator = map(Object, cur.fetchall())[0]        
        connection.commit()
    except Exception, ex:
        print "Sendsms : Operator info not found or dublicate record. internal exception: %s" % (repr(ex),)

    templ = Template(body, input_encoding='utf-8')
    for account in accounts:
        
        if float(account.ballance)>SEND_IF_LESS or not account.phone_m : continue
        print "Sending sms for %s" % account.username
        data=templ.render_unicode(account=account, operator = operator)
        d={'phone':account.phone_m,'message':data}
        print commands.getstatusoutput("%s%(phone)s %(message)s" % (command,d))


      
                
def main (): 
    send_balance_notice()       


if __name__=='__main__':

    config = ConfigParser.ConfigParser()
    config.read("/opt/ebs/data/ebs_config.ini")

    
    pool = PooledDB(
    mincached=1,  maxcached=9,
    blocking=True,creator=psycopg2,
    dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"), config.get("db", "username"),
                                                           config.get("db", "host"), config.get("db", "password")))
    print "ebs: Sendmail: configs read, about to start"
    main()

    

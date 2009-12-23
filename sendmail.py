#-*-coding=utf-8-*-

import os, sys

sys.path.insert(0, "modules")

import  datetime, time

import psycopg2, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
import ConfigParser
from DBUtils.PooledDB import PooledDB
from mako.template import Template

class Object(object):
    def __init__(self, result=[], *args, **kwargs):
        for key in result:
            setattr(self, key, result[key])

        for key in kwargs:
            setattr(self, key, kwargs[key])  


from mail.mail import send_mail

def send_balance_notice():
    connection = pool.connection()
    connection._con._con.set_client_encoding('UTF8')       
    cur = connection.cursor()
    cur = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cur.execute("SELECT body FROM billservice_template as template WHERE type_id=8;")
    try:
        body = cur.fetchone()["body"]
    except Exception, ex:
        print "Sendmail : Template body with type_id=8. internal exception: %s" % (repr(ex),)
        return
    #print body   
    
    cur.execute("SELECT * FROM billservice_account ORDER BY id ASC LIMIT 2;")
    connection.commit()
    
    accounts = map(Object, cur.fetchall()) 
    
    cur.execute("SELECT * FROM billservice_operator ORDER BY id ASC LIMIT 1;")
    connection.commit()
    
    try:
        operator = map(Object, cur.fetchall())[0]        
        connection.commit()
    except Exception, ex:
        print "Sendmail : Operator info not found or dublicate record. internal exception: %s" % (repr(ex),)

    templ = Template(body, input_encoding='utf-8')
    for account in accounts:
        print "Sending mail for %s" % account.username
        if float(account.ballance)>SEND_IF_LESS: continue
        data=templ.render_unicode(account=account, operator = operator)
        send_mail(subject=EMAIL_SUBJECT, message=data, from_email=EMAIL_FROM, recipient_list=[account.email,], fail_silently=EMAIL_FAIL_SILENTLY, auth_user=EMAIL_HOST_USER,\
                  auth_password=EMAIL_HOST_PASSWORD, host=EMAIL_HOST, port=EMAIL_PORT, use_tls=EMAIL_USE_TLS)


      
                
def main (): 
    send_balance_notice()       


if __name__=='__main__':

    config = ConfigParser.ConfigParser()
    config.read("ebs_config.ini")

    
    pool = PooledDB(
    mincached=1,  maxcached=9,
    blocking=True,creator=psycopg2,
    dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"), config.get("db", "username"),
                                                           config.get("db", "host"), config.get("db", "password")))

        
    EMAIL_SUBJECT = config.get("sendmail", "subject") or 'Provider information'
    
    EMAIL_USE_TLS = True if config.get("sendmail", "use_tls") == "True" else False
    
    EMAIL_HOST = config.get("sendmail", "host") or 'localhost'
    
    EMAIL_HOST_USER = config.get("sendmail", "host_user") or ''
    EMAIL_HOST_PASSWORD = config.get("sendmail", "host_password") or ''
    EMAIL_PORT = config.get("sendmail", "port") or 25
    EMAIL_FROM = config.get("sendmail", "email_from") or 'info@provider.com'
    EMAIL_FAIL_SILENTLY = True if config.get("sendmail", "fail_silently") == "True" else False

    SEND_IF_LESS = float(config.get("sendmail", "send_if_less")) or 0
    print "ebs: Sendmail: configs read, about to start"
    main()

    

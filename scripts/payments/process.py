#-*-coding= utf-8 -*-

import os, sys
import ConfigParser
import datetime, time
import fnmatch
import shutil
import time
import psycopg2

config = ConfigParser.ConfigParser()
billing_config = ConfigParser.ConfigParser()
billing_config.read("/opt/ebs/data/ebs_config.ini")
#billing_config.read("d:/projects/mikrobill/ebs_config.ini")
#########################
host = billing_config.get("db", "host")
port = billing_config.getint('db', 'port')
database = billing_config.get('db', 'name')
user = billing_config.get('db', 'username')
password = billing_config.get('db', 'password')
try:
    connection = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (database, user, host, password, port));
except Exception, e:
    print "I am unable to connect to the database"
    print e
    sys.exit()

connection.set_isolation_level(1)
cur = connection.cursor()
transaction_pattern=u"""
INSERT INTO billservice_transaction(
            account_id, type_id, approved, summ,
            created)
    VALUES (%(ACC_ID)s, '%(PAYMENT_TYPE)s', True, (-1)*%(SUM)s,  '%(DATETIME)s');

"""
curdir='/opt/ebs/data/scripts/payments/'
#curdir='d:/projects/mikrobill/scripts/payments/'
config.read(curdir+"pattern.ini")
def make_dict(lst, fields_list, datetime_fmt, encoding='utf-8', time_fmt='', ):
    result_dict={}
    i=0
    dt_field='DATETIME'
    for field in fields_list:
        if field=='DATETIME':
            d=datetime.datetime(*time.strptime(lst[i],datetime_fmt)[0:5])
            dt_field=field
            result_dict[field]=d
        else:
            if encoding!='utf-8':
                result_dict[field]=str(lst[i].decode(encoding, 'utf-8')).strip()
            else:
                result_dict[field]=str(lst[i]).strip()

        i+=1

    if result_dict.has_key('TIME'):
        f_time = time.strptime(result_dict.get('TIME'), time_fmt)
        #print f_time, result_dict[dt_field]
        result_dict['DATETIME']=datetime.datetime(year=d.year,month=d.month,day=d.day,hour=f_time.tm_hour,minute=f_time.tm_min,second=f_time.tm_sec)
        #result_dict[dt_field].hour=f_time.tm_hour
        #result_dict[dt_field].minute=f_time.tm_min
        #result_dict[dt_field].second=f_time.tm_sec

    return result_dict

if __name__=='__main__':
    payment_system = sys.argv[1]
    if config.has_section(payment_system):
        fields=config.get(payment_system, 'fieldnames')
        if not fields:
            print "Fieldnames declaration for payment system %s not found" % payment_system
            sys.exit()

        delimeter = config.get(payment_system, 'separator')
        payment_type = unicode(config.get(payment_system, 'payment_type').decode('utf-8'))
        fields_list=fields.split(delimeter)
        datetime_fmt = config.get(payment_system, 'datetime_fmt')
        time_fmt = config.get(payment_system, 'time_fmt')
        text_encoding = config.get(payment_system, 'encoding')
        active = config.get(payment_system, 'active')
        file_mask = config.get(payment_system, 'file_mask')
        exclude_mask = config.get(payment_system, 'exclude_mask')
        folder_in, folder_out, folder_err = config.get(payment_system, 'folder_in'),config.get(payment_system, 'folder_out'),config.get(payment_system, 'folder_err')
        #print folder_in
        for file in os.listdir(curdir+folder_in):
            print "processing file", file
            buffer=[]
            if not (fnmatch.fnmatch(file, file_mask) and not fnmatch.fnmatch(file, exclude_mask) and not file=='.svn'): print "skip"; continue

            for line in open(curdir+folder_in+file,'r'):
                lst=line.split(delimeter)
                res_dict = make_dict(lst, fields_list, datetime_fmt, text_encoding,  time_fmt)
                res_dict['PAYMENT_TYPE']=payment_type
                #print res_dict
                try:
                    cur.execute("SELECT id FROM billservice_account WHERE contract='%s'" % res_dict.get('ACC'))
                    acc_id=cur.fetchone()
                    if acc_id:
                       acc_id=acc_id[0]
                    else:
                       print "Account for contract %s not found. Skip" % res_dict.get('ACC')
                       print "*"*10
                       buffer.append(line)
                       continue
                    res_dict['ACC_ID']=acc_id
                    s=transaction_pattern % res_dict
                    print "INSERT\n"
                    print "*"*10
                    cur.execute(s)
                    connection.commit()
                    print "*"*10
                except Exception, e:
                    print 'ERROR',e
                    connection.rollback()

                    buffer.append(line)

            if buffer:
                f=open(curdir+folder_err+file,'w')

                f.write('\n'.join(buffer))
                f.close()


            shutil.move(curdir+folder_in+file, curdir+folder_out+file)

        #    process_file(payment_system)


cur.close()
connection.close()

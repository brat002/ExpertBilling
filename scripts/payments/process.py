#-*-coding= utf-8 -*-

import os, sys
import ConfigParser
import datetime, time

config = ConfigParser.ConfigParser()

transaction_pattern=u""" 
INSERT INTO billservice_transaction(
            account_id, type_id, approved, summ, description, 
            created)
    VALUES (%(ACC)s, 'MANUAL_TRANSACTION', True, %(SUM)s, %(DESCR)s, '%(DATETIME)s');

"""
curdir='/opt/ebs/data/scripts/payments/'
curdir='d:/projects/mikrobill/scripts/payments/'
config.read(curdir+"pattern.ini")
def make_dict(lst, fields_list, datetime_fmt, date_ftm='',time_fmt=''):
    result_dict={}
    i=0
    for field in fields_list:
        if field=='DATETIME':
            d=datetime.datetime(*time.strptime(lst[i],datetime_fmt)[0:5])
        result_dict[field]=lst[i]
        i+=1
        
    return result_dict
if __name__=='__main__':
    payment_system = sys.argv[1]
    if config.has_section(payment_system):
        fields=config.get(payment_system, 'fieldnames')
        if not fields:
            print "Fieldnames declaration for payment system %s not found" % payment_system
            sys.exit()
            
        delimeter = config.get(payment_system, 'separator')
        comment = unicode(config.get(payment_system, 'comment').decode('utf-8'))
        fields_list=fields.split(delimeter)
        datetime_fmt = config.get(payment_system, 'datetime_fmt')
        text_encoding = config.get(payment_system, 'encoding')
        active = config.get(payment_system, 'active')
        folder_in, folder_out, folder_err = config.get(payment_system, 'folder_in'),config.get(payment_system, 'folder_out'),config.get(payment_system, 'folder_err')
        print folder_in
        for file in os.listdir(curdir+folder_in):
            for line in open(curdir+folder_in+file):
                lst=line.split(delimeter)
                res_dict = make_dict(lst, fields_list, datetime_fmt)
                res_dict['DESCR']=comment
                print res_dict
                print transaction_pattern % res_dict
        #    process_file(payment_system)

        
        
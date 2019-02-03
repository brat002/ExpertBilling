# -*- coding: utf-8 -*-
"""
This product released under GPL2 license and is part a ExpertBilling system (http://www.expertbilling.ru).
For any questions please visit http://forum.expertbilling.ru
04.12.2010 Aleksandr Kuzmitskij
"""
"""
/opt/ebs/data/acledit/ - корневая папка

acl_config_template - шаблон конфига. Использован шаблонизатор mako, который позволяет делать конфиг абсолютно любого формата и вида (http://www.google.com/url?sa=t&source=web&cd=1&v

acl_md5 - md5 хэш последнего конфига. Если хэш нового сгенерированного конфига совпадает со старым - ничего не происходит

aclexec.py -  непосредственно скрипт

Внутри файла aclexec.py 2 секции настроек. Первая секция - настройки подключения к базе данных
Вторая секция - пути и прочие настройки вроде IP адресов и путей

Важным параметром является переменная ids_addonservices - здесь через запятую указаны id подключаемых услуг. Если в списке 1 элемент - запятая за ним обязательна, а лучше ставить её

path_to_config - путь к сгенерированному файлу конфига.
Пропишите в кроне, чтобы скрипт выполнялся каждых пару минут

"""
import psycopg2
import psycopg2.extras
import hashlib
from mako.template import Template
import sys
import commands
#import getopt

##### Database opts #####
host = '127.0.0.1'
port = '5433'
database = 'ebs_new'
user = 'ebs'
password = 'ebspassword'

##### Internal script opts #####
ids_addonservices = (1,2,3,4,5,6,7,8,9,10,11,12,13)
path_to_config = 'active-config'
path_to_template = 'acl_config_template'
path_to_md5_summ = 'acl_md5'
nas_ip = ('10.1.1.1',)
tftp_ip = '10.2.2.2'
snmp_community = 'write'
################################

def get_md5(path_to_config):
    md5 = hashlib.md5()
    with open(path_to_config,'rb') as f: 
        for chunk in iter(lambda: f.read(8192), ''): 
             md5.update(chunk)
    return md5.hexdigest()    


def check_md5(new_md5, md5_file):
    md5_f = open(md5_file,'r')
    old_md5=md5_f.read()
    md5_f.close()
    if old_md5!=new_md5:
        md5_f = open(md5_file, 'w')
        md5_f.write(new_md5)
        md5_f.close()
        return True
    return False
    

def main():
    try:
        conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (database, user, host, password, port));
    except:
        print "I am unable to connect to the database"
        sys.exit()
    
    conn.set_isolation_level(0)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cur.execute("SELECT * FROM billservice_account  WHERE ballance+credit>0 and balance_blocked=False and status=1 and disabled_by_limit=False and id in (SELECT account_id FROM billservice_accountaddonservice WHERE service_id IN %s and deactivated is Null)", (ids_addonservices,))
    
    result = cur.fetchall()
    cur.close()
    conn.close()
    #for r in result:
    #    print r
    mytemplate = Template(filename=path_to_template, input_encoding='utf-8')
    rendered_result = mytemplate.render(result=result)
    k=open(path_to_config, 'w')
    k.write(rendered_result)
    k.close()
    md5_rendered = get_md5(path_to_config)
    if check_md5(md5_rendered, path_to_md5_summ)==True:
        """
        Если файлы отличаются
        """
        for nas in nas_ip:
            print "status=%s, output=%s" % commands.getoutput("snmpset -v 2c -t 60 -c %s %s .1.3.6.1.4.1.9.2.1.53.%s s %s" % (snmp_community, nas, tftp_ip, path_to_config, ))
    
    
if __name__ == "__main__":
    main()

    
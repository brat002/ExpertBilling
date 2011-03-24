#!/usr/bin/env python
#coding=utf-8

import os
import sys
import shutil
from hashlib import md5
import datetime
import commands
import ConfigParser
import datetime
import psycopg2

DIST_PATH=os.path.abspath('.')
SQL_UPGRADE_PATH = DIST_PATH+'/sql/upgrade/' 
BILLING_PATH = '/opt/ebs/data'
WEBCAB_PATH = '/opt/ebs/web/'
BACKUP_DIR = '/opt/ebs/backups/'
LAST_SQL = '/opt/ebs/data/sql/last_sql.dont_remove' 
exclude_files=(
'/opt/ebs/data/ebs_config.ini',
'/opt/ebs/data/ebs_config_runtime.ini',
'/opt/ebs/web/ebscab/settings.py',
'/opt/ebs/web/ebscab/upgrade.py',
)
curdate = datetime.datetime.now().strftime('%d-%m-%y_%H_%M_%S')
config = ConfigParser.ConfigParser()
config.read(BILLING_PATH+"/ebs_config.ini") 

try:
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (config.get('db', 'name'), config.get('db', 'username'),config.get('db', 'host'),config.get('db', 'password'), config.get('db', 'port')));
    cur=conn.cursor()
except Exception, e:
    print "I am unable to connect to the database"
    print e
    sys.exit()
        
def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

def md5gen(file_path):
    f = open(file_path,'rb')
    
    data=f.read()
    f.close()
    return md5(data).digest()

def stop_processes():
    print '*'*80
    print 'Stopping billing processes'
    commands.getstatusoutput('/etc/init.d/ebs_core stop')
    commands.getstatusoutput('/etc/init.d/ebs_nf stop')
    commands.getstatusoutput('/etc/init.d/ebs_rad stop')
    commands.getstatusoutput('/etc/init.d/ebs_rpc stop')
    commands.getstatusoutput('/etc/init.d/ebs_nfroutine stop')
    print '*'*80
    print 'Stopping complete'

def start_processes():
    print '*'*80
    print 'Starting billing processes'
    commands.getstatusoutput('/etc/init.d/ebs_core start')
    commands.getstatusoutput('/etc/init.d/ebs_nf start')
    commands.getstatusoutput('/etc/init.d/ebs_rad start')
    commands.getstatusoutput('/etc/init.d/ebs_rpc start')
    commands.getstatusoutput('/etc/init.d/ebs_nfroutine start')
    print '*'*80
    print 'Running complete'

    
def allow_continue(phrase=''):
    a=True
    while a:
        print '*'*80
        if not phrase:
            output = raw_input("\nWe have error. Continue? (y/n)")
        else:
            output = raw_input("\n%s. Continue? (y/n)" % phrase)
        if output in ['n', 'N', 'No', 'Not']:
            sys.exit()
        elif output in ['y', 'Y', 'Yes']:
            a=False
            
def make_archive(name,path):
    return commands.getstatusoutput('tar -cvzf %s.tar.gz %s' % (name, path,))
    
def get_last_sql():
    pass

def pre_upgrade():
    status, output = make_archive('%sdata_%s' % (BACKUP_DIR,curdate), BILLING_PATH)
    if status!=0:
        print "Can not create 'data' backup %s" % output
        allow_continue()
    status, output = make_archive('%swebcab_%s' % (BACKUP_DIR,curdate), WEBCAB_PATH)
    
    if status!=0:
        print "Can not create 'webcab' backup %s" % output
        allow_continue()
    

def files_for_copy():
    to_copy=[]
    for root,dirs,files in os.walk(DIST_PATH):
     
        for f in files:
            to_file = "%s/%s" % (root.replace(DIST_PATH,BILLING_PATH), f)
            from_file = '%s/%s' % (root,f) 
            #print to_file, from_file
            if to_file in exclude_files:continue
            if os.path.exists(to_file):
                if md5gen(from_file)!=md5gen(to_file):
                    #print "%s copy to %s" % (('%s/%s' % (root,f)),"%s/%s" % (root.replace(DIST_PATH,BILLING_PATH), f))
                    to_copy.append((from_file, to_file))
                #else:
                #    print 'DUBLICATE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            else:
                to_copy.append((from_file, to_file))
    print '\n'.join(["%s->%s" % (x,y) for x,y in  to_copy])
    return to_copy
      
def backup_db():

    print "*"*80  
    print "Please, enter password for database user %s.\nYou can see right password in file /opt/ebs/data/ebs_config.ini" % (config.get('db', 'username'),)
    status, output = commands.getstatusoutput('pg_dump -W -h %s -p %s -U %s -F p -b -S ebs --disable-triggers -f %s %s' % (config.get('db', 'host'),config.get('db', 'port'),config.get('db', 'username'),"%s%s_db.sql" % (BACKUP_DIR, curdate), config.get('db', 'name')))
    if status!=0:
        print "We have error on database backup operation. %s" % output
        allow_continue()
    print "Backup database completed."
    print "*"*80
        
def upgrade_db():
    
    first_time=False
    if not os.path.exists(LAST_SQL):
        first_time=True
        las_sql_id=0
    

    if not first_time:
        f = open(LAST_SQL, 'r')
        last = f.read()
        f.close()
    
        try:
            las_sql_id = int(last.strip())
        except Exception, e:
            print "Last SQL id in file %s have incorrect format" % LAST_SQL 
            sys.exit()
    else:
        las_sql_id=0
        
    available_files=[int(x.replace(".sql", '')) for x in os.listdir(SQL_UPGRADE_PATH)]
    
    for id in xrange(las_sql_id+1, max(available_files)+1):
        not_write = False
        upgrade_sql="%s%s.sql" % (SQL_UPGRADE_PATH, id)
        if not os.path.exists(upgrade_sql):
            print "cannot find file %s" % upgrade_sql
            allow_continue('Do you want to continue upgrade of EBS database?')
            continue
            
        sql_file = open(upgrade_sql, 'r')
        sql = sql_file.read()
        sql_file.close()
        
        try:
            cur.execute(sql)
            not_write = False
        except Exception, e:
            conn.rollback()
            print "Error, while importing sql: %s" % sql
            allow_continue('Continue is not recommended. Do you want to continue upgrade of EBS database?')
            not_write=True
            
        if not not_write:
            f = open(LAST_SQL, 'w')
            f.write(id)
            f.close()
        conn.commit()


def copy_files(files):
    files_copied=[]
    for src, dst in files:
        try:
            shutil.copy(src, dst)
            files_copied.append((src,dst))
        except IOError,e:
            print "I/O Exception %s" % str(e)
            allow_continue()

def post_upgrade():
    pass

def fromchanges():
    
    to_db=[]
    changes_start=False
    changes_date = datetime.datetime.now()-datetime.timedelta(days=-1000)
    for line in open(DIST_PATH+'/sql/changes.sql'):
        if line.startswith('--') and not changes_start:
            print line
            try:
                changes_date = datetime.datetime.strptime(line.strip(), "--%d.%m.%Y")
            except Exception, e:
                print e
                continue
            
        if changes_date>=installation_date:
            changes_start=True
            to_db.append(line)
             
    print '\n'.join(to_db)   
    try:
        cur.execute('\n'.join(to_db))
        conn.commit()
    except Exception, e:
        print e 
        conn.rollback()
        print "*"*80
        print "Error First stage upgrading DB"
        allow_continue()

installation_date = modification_date(BILLING_PATH+'/license.lic')
print installation_date
stop_processes()
pre_upgrade()
files=files_for_copy()
if not files:
    print '*'*80
    print 'No files copy needed'
    allow_continue('Do you want to upgrade EBS database?')

copy_files(files)  
backup_db()
if not os.path.exists(LAST_SQL):
    fromchanges()
upgrade_db()
#start_processes()

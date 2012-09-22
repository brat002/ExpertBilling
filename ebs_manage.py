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
import psycopg2.extras
import tarfile
import pexpect
import optparse

DIST_PATH='/tmp/ebs_upgrade'
SQL_UPGRADE_PATH = DIST_PATH+'/sql/upgrade/' 
BILLING_PATH = '/opt/ebs/data'
WEBCAB_PATH = '/opt/ebs/web/'
BACKUP_DIR = '/opt/ebs/backups/'
LAST_SQL = '/opt/ebs/data/etc/install.ini'
FIRST_TIME_LAST_SQL='/tmp/ebs_upgrade/etc/install.ini' 
exclude_files_upgrade=(
'/opt/ebs/data/ebs_config.ini',
'/opt/ebs/data/ebs_config_runtime.ini',
'/opt/ebs/web/ebscab/settings.py',
'/opt/ebs/web/ebscab/upgrade.py',
)

exclude_folders_upgrade =(
'/opt/ebs/data/scripts/',
                          )
curdate = datetime.datetime.now().strftime('%d-%m-%y_%H_%M_%S')
config = ConfigParser.ConfigParser()
config.read(BILLING_PATH+"/ebs_config.ini") 
install_config = ConfigParser.ConfigParser()
"""
try:
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (config.get('db', 'name'), config.get('db', 'username'),config.get('db', 'host'),config.get('db', 'password'), config.get('db', 'port')));
    cur=conn.cursor()
except Exception, e:
    print "I am unable to connect to the database"
    print e
    print "Please, enter correct database parameters in %s/ebs_config.ini" % BILLING_PATH
    sys.exit()
"""  

     
def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

def md5gen(file_path):
    if os.path.exists(file_path):
        f = open(file_path,'rb')
        data=f.read()
        f.close()
        return md5(data).digest()
    else:
        return 

def stop_processes():
    print '*'*80
    print 'Stopping billing processes'
    commands.getstatusoutput('/etc/init.d/ebs_core stop')
    commands.getstatusoutput('/etc/init.d/ebs_nf stop')
    commands.getstatusoutput('/etc/init.d/ebs_rad stop')
    #commands.getstatusoutput('/etc/init.d/ebs_rpc stop')
    commands.getstatusoutput('/etc/init.d/ebs_nfroutine stop')
    print '*'*80
    print 'Stopping complete'

def start_processes():
    print '*'*80
    print 'Please, start manually billing processess and see logs in /opt/ebs/data/log/'
    print """
    /etc/init.d/ebs_core start
    /etc/init.d/ebs_nf start
    /etc/init.d/ebs_rad start
    /etc/init.d/ebs_nfroutine start
    """
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
            cleanup()
            sys.exit()
        elif output in ['y', 'Y', 'Yes']:
            a=False
            
def make_archive(name,path):
    return commands.getstatusoutput('tar -cvzf %s.tar.gz %s' % (name, path,))
    
def get_last_sql():
    pass

def create_folders():
    if not os.path.exists('/opt/ebs'): os.mkdir('/opt/ebs/')
    if not os.path.exists('/opt/ebs/backups'): os.mkdir('/opt/ebs/backups')
    if not os.path.exists('/opt/ebs/data'): os.mkdir('/opt/ebs/data')
    if not os.path.exists(DIST_PATH): os.mkdir(DIST_PATH)
    if not os.path.exists('/opt/ebs/stats'): os.mkdir('/opt/ebs/stats')
    if not os.path.exists('/opt/ebs/web'): os.mkdir('/opt/ebs/web')
    
    
def unpack_archive(archive_name):
    try:
        tar=tarfile.open(archive_name)
    except Exception, e:
        print "Fatal error, Can not read archive %s" % str(e)
        sys.exit()
    tar.extractall(path=DIST_PATH)
    tar.close()
        
def cleanup():
    try:
        shutil.rmtree(DIST_PATH)
    except:
        pass
    
def dbconnect():
    global dbhost,dbname,dbuser,dbpassword, conn, cur
    try:
        conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (dbname, dbuser,dbhost,dbpassword, 5432));
        conn.set_client_encoding('UTF8')
        cur=conn.cursor()
    except Exception, e:
        print "I am unable to connect to the database"
        print e
        print "Please, enter correct database parameters"
        sys.exit()
            
def pre_upgrade():
    #unpack files to temp folder
    print "Creating archive of billing dir /opt/ebs/."
    print "*"*80
    status, output = make_archive('%sdata_%s' % (BACKUP_DIR,curdate), BILLING_PATH)
    if status!=0:
        print "Can not create 'data' backup %s" % output
        allow_continue()
    status, output = make_archive('%swebcab_%s' % (BACKUP_DIR,curdate), WEBCAB_PATH)
    
    if status!=0:
        print "Can not create 'webcab' backup %s" % output
        allow_continue()
        

    

def files_for_copy(first_time=False):
    to_copy=[]
    for root,dirs,files in os.walk(DIST_PATH):
        for d in dirs:
            to_dir = os.path.join(root.replace(DIST_PATH,BILLING_PATH), d)
            if to_dir in exclude_folders_upgrade and first_time==False:continue
            if not os.path.exists(to_dir):
                to_copy.append((None, to_dir))
        for f in files:
            to_file = "%s/%s" % (root.replace(DIST_PATH,BILLING_PATH), f)
            from_file = '%s/%s' % (root,f) 
            #print to_file, from_file
            if to_file in exclude_files_upgrade and first_time==False:continue
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
    global dbhost,dbname,dbuser,dbpassword
    print "*"*80  
    print "Backup database"
    print "Please, enter password for DB user %s.\nYou can see right password in file /opt/ebs/data/ebs_config.ini" % (dbuser,)
    status, output = commands.getstatusoutput('pg_dump -W -h %s -p %s -U %s -F p -b -S ebs --disable-triggers -f %s %s' % (dbhost,5432,dbuser,"%s%s_db.sql" % (BACKUP_DIR, curdate), dbname))
    if status!=0:
        print "We have error on database backup operation. %s" % output
        allow_continue()
    else:
        print "Backup database completed."
    print "*"*80
        

def auto_backup_db():
   
    print "*"*80  
    print "Backuping database from config /opt/ebs/data/ebs_config.ini" 
    status, output = commands.getstatusoutput('su ebs -c "pg_dump -W -h %s -p %s -U %s -F p -b -S ebs --disable-triggers -f %s %s"' % (config.get('db', 'host'),config.getint('db', 'port'),config.get('db', 'username'),"%s%s_db.sql" % (BACKUP_DIR, curdate), config.get('db', 'name')))
    print "Backup database completed.See %s" % BACKUP_DIR
    print "*"*80
    
def upgrade_db():
    global cur, conn
    print "*"*80
    print "Upgrading DB from sql/upgrade/*.sql files"
    first_time=False
    if not os.path.exists(LAST_SQL):
        first_time=True
        last_sql_id=0
    
    if first_time==True:
        install_config.read(FIRST_TIME_LAST_SQL)
        if not install_config.has_section('sql'):
            install_config.add_section('sql') 
    else:
        install_config.read(LAST_SQL) 
        last_sql_id=install_config.getint('sql', 'last_id')
                
        
    available_files=[int(x.replace(".sql", '')) for x in os.listdir(SQL_UPGRADE_PATH)]
    
    for id in xrange(last_sql_id+1, max(available_files)+1):
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
            install_config.set('sql','last_id',id)
            
        conn.commit()
        
    if first_time==True:
        with open(FIRST_TIME_LAST_SQL, 'wb') as configfile:
            install_config.write(configfile)
    else:
        with open(LAST_SQL, 'wb') as configfile:
            install_config.write(configfile)
                

def modifydb():
    global cur, conn
    print "*"*80    
    print "Modifying DB. Creating triggers"
    
    l=[]
    for x in xrange(9,13):
        for i in xrange(1,13):
            print "%.2i%.2i" % (x,i)
            l.append("""DROP TRIGGER acc_psh_trg ON psh20%.2i%.2i01;""" % (x,i,))
            l.append("""CREATE TRIGGER acc_psh_trg
              AFTER INSERT OR UPDATE OR DELETE
              ON psh20%.2i%.2i01
              FOR EACH ROW
              EXECUTE PROCEDURE account_transaction_trg_fn(); """ % ( x,i))

    for x in xrange(9,13):
        for i in xrange(1,13):
            print "%.2i%.2i" % (x,i)
            l.append("""DROP TRIGGER acc_tftrans_trg ON traftrans20%.2i%.2i01;""" % (x,i,))
            l.append("""CREATE TRIGGER acc_tftrans_trg
              AFTER INSERT OR UPDATE OR DELETE
              ON traftrans20%.2i%.2i01
              FOR EACH ROW
              EXECUTE PROCEDURE account_transaction_trg_fn(); """ % (x,i))
            
    for sql in l:
        try:
            cur.execute(sql)
            conn.commit()
        except Exception, e:
            conn.rollback()
            print "Skip. Not worry.Its Ok."
    print "Delteing triggers complete"
    print "*"*80
        
def copy_files(files):
    files_copied=[]
    for src, dst in files:
        print src,'->>', dst
        try:
            
            if src==None:
                os.makedirs(dst)
            else:
                shutil.copy(src, dst)
            files_copied.append((src,dst))
        except IOError,e:
            print "I/O Exception %s" % str(e)
            allow_continue()

def setup_init():
    print "*"*80  
    print "Copying init scripts to /etc/init.d/"
    shutil.copy(os.path.join(DIST_PATH,'init.d/ebs_core'), '/etc/init.d/ebs_core')
    shutil.copy(os.path.join(DIST_PATH,'init.d/ebs_rad'), '/etc/init.d/ebs_rad')
    shutil.copy(os.path.join(DIST_PATH,'init.d/ebs_nf'), '/etc/init.d/ebs_nf')
    shutil.copy(os.path.join(DIST_PATH,'init.d/ebs_nfroutine'), '/etc/init.d/ebs_nfroutine')
    #shutil.copy(os.path.join(DIST_PATH,'init.d/ebs_rpc'), '/etc/init.d/ebs_rpc')
    print "*"*80  
    status, output = commands.getstatusoutput('update-rc.d ebs_nfroutine defaults')
    status, output = commands.getstatusoutput('update-rc.d ebs_nf defaults')
    status, output = commands.getstatusoutput('update-rc.d ebs_rad defaults')
    status, output = commands.getstatusoutput('update-rc.d ebs_core defaults')
    #status, output = commands.getstatusoutput('update-rc.d ebs_rpc defaults')
    if status!=0:
        print "We have error on init scripts setup. %s" % output
        allow_continue()
    else:
        print "Init scripts setup was succefull."
    print "*"*80    


    print "Copying manage script(billing) to /usr/sbin/"
    shutil.copy(os.path.join(DIST_PATH,'soft/billing'), '/usr/sbin/')
    print "*"*80  
    
def setup_config():
    global dbhost,dbname,dbuser,dbpassword
    print "*"*80 
    print "Write database parameters to config file /opt/ebs/data/ebs_config.ini"
    print "*"*80
    config.read(BILLING_PATH+"/ebs_config.ini") 
    config.set('db', 'name', dbname)
    config.set('db', 'username', dbuser)
    config.set('db', 'password', dbpassword)
    config.set('db', 'host', dbhost)
    config.set('db', 'port', 5432)
    #config.write(BILLING_PATH+"/ebs_config.ini")
    with open(os.path.join(BILLING_PATH+"/ebs_config.ini_new"), 'wb') as configfile:
        config.write(configfile)
    shutil.move(BILLING_PATH+'/ebs_config.ini_new', BILLING_PATH+'/ebs_config.ini')
    
def setup_webcab():
    print "*"*80
    print "Webcab install"
    #shutil.copytree(BILLING_PATH+'/ebscab/', '/opt/ebs/web/')
    output=commands.getoutput('cp -r %s %s' % (os.path.join(BILLING_PATH,'ebscab/*'), '/opt/ebs/web/'))
    #print output
    shutil.copy(os.path.join(DIST_PATH,'ebscab/default'), '/etc/apache2/sites-available/')
    shutil.copy(os.path.join(DIST_PATH,'ebscab/blankpage_config'), '/etc/apache2/sites-available/')
    output=commands.getoutput('a2ensite blankpage_config')
    output=commands.getoutput('echo > %s' % ('/opt/ebs/web/ebscab/log/django.log'))
    output=commands.getoutput('chmod 0777 %s' % ('/opt/ebs/web/ebscab/log/django.log'))
 
    output=commands.getoutput('echo > %s' % ('/opt/ebs/web/ebscab/log/webcab_log'))
    output=commands.getoutput('chmod 0777 %s' % ('/opt/ebs/web/ebscab/log/webcab_log'))
       
     
    print "Please, set correct database access parameters and your timezone in /opt/ebs/web/ebscab/settings.py, restart apache and enjoy!."
    print "*"*80    
 
    
def post_upgrade():
    pass

def upgrade_from_13():
    global conn, cur
    print "*"*80
    print "Migrating accounts from 1.3 to 1.4"
    print "*"*80
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cur.execute("""
    SELECT id, username, "password", fullname, email, address, nas_id, vpn_ip_address, 
           assign_ipn_ip_from_dhcp, ipn_ip_address, ipn_mac_address, ipn_status, 
           status, suspended, created, ballance, credit, disabled_by_limit, 
           balance_blocked, ipn_speed, vpn_speed, ipn_added, city, 
           postcode, region, street, house, house_bulk, entrance, room, 
           vlan, allow_webcab, allow_expresscards, assign_dhcp_null, assign_dhcp_block, 
           allow_vpn_null, allow_vpn_block, passport, passport_date, passport_given, 
           phone_h, phone_m, vpn_ipinuse_id, ipn_ipinuse_id, associate_pptp_ipn_ip, associate_pppoe_mac
      FROM billservice_account;
    """)
    accounts = cur.fetchall()
    
    for account in accounts:
        cur.execute(""" 
        INSERT INTO billservice_subaccount(
                account_id, username, "password", vpn_ip_address, ipn_ip_address, 
                ipn_mac_address, nas_id, ipn_added, ipn_enabled, 
                allow_dhcp, allow_dhcp_with_null, 
                allow_dhcp_with_minus, allow_dhcp_with_block, allow_vpn_with_null, 
                allow_vpn_with_minus, allow_vpn_with_block, associate_pptp_ipn_ip, 
                associate_pppoe_ipn_mac, ipn_speed, vpn_speed, allow_addonservice, 
                vpn_ipinuse_id, ipn_ipinuse_id, allow_ipn_with_null, 
                allow_ipn_with_minus, allow_ipn_with_block)
        VALUES (%s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, %s, 
                %s);    
        """, (account['id'],account['username'],account['password'],account['vpn_ip_address'],account['ipn_ip_address'],
              account['ipn_mac_address'],account['nas_id'],account['ipn_added'],account['ipn_status'],
              account['assign_ipn_ip_from_dhcp'],account['assign_dhcp_null'],
              account['assign_dhcp_null'],account['assign_dhcp_block'],account['allow_vpn_null'],
              account['allow_vpn_null'],account['allow_vpn_block'],account['associate_pptp_ipn_ip'],
              account['associate_pppoe_mac'],account['ipn_speed'],account['vpn_speed'],True,
              account['vpn_ipinuse_id'],account['ipn_ipinuse_id'], False, False, False, 
              ))
    
    cur.execute("UPDATE billservice_accountaddonservice as accs SET account_id=Null, subaccount_id=(SELECT id FROM billservice_subaccount  WHERE account_id=accs.account_id LIMIT 1) WHERE accs.deactivated is Null")
    cur.execute("UPDATE billservice_account set nas_id = Null")
    conn.commit()
    print '*'*80
    print "Migration completed"
    
def prompt_db_access():
    global dbhost,dbname,dbuser,dbpassword
    dbhost = raw_input("Enter database host [127.0.0.1]: ") or '127.0.0.1'
    dbname = raw_input("Enter database name [ebs]: ") or 'ebs'
    dbuser = raw_input("Enter database user (strongly recommended default)[ebs]: ") or 'ebs'
    dbpassword = raw_input("Enter database password [ebspassword]: ") or 'ebspassword'
    

    
def import_dump():
    global dbhost,dbname,dbuser,dbpassword
    print "*"*80
    print "Importing main database dump. Enter database password for user %s" % dbuser
    print "*"*80
    status, output = commands.getstatusoutput('psql -W -h %s -p %s -U %s %s -f %s' % (dbhost,5432,dbuser, dbname, DIST_PATH+'/sql/ebs_dump.sql'))
    
    if status!=0:
        allow_continue("We get error when importing initial dump. %s" % output)
        
def import_initial_changes():       
    global dbhost,dbname,dbuser,dbpassword
    print "*"*80
    print "Importing changes dump. Enter database password for user %s" % dbuser
    print "*"*80
    status, output = commands.getstatusoutput('psql -W -h %s -p %s -U %s %s -f %s' % (dbhost,5432,dbuser, dbname, DIST_PATH+'/sql/changes.sql'))
    
    if status!=0:
        allow_continue("We get error when importing initial dump. %s" % output)  
           
def fromchanges(changes_start=False):
    global conn, cur
    
    to_db=[]
    
    changes_date = datetime.datetime.now()-datetime.timedelta(days=-1000)
    for line in open(DIST_PATH+'/sql/changes.sql'):
        #print line
        if line.startswith('--') and not changes_start:
            #print line
            try:
                changes_date = datetime.datetime.strptime(line.strip(), "--%d.%m.%Y")
            except Exception, e:
                print e
                continue
        print installation_date, changes_date    
        if installation_date and changes_date>=installation_date:
            changes_start=True
        
        if changes_start==True:
            #print "changes_start==True"
            print line
            to_db.append(line)
             
    #print '\n'.join(to_db)   
    try:
        cur.execute('\n'.join(to_db))
        conn.commit()
    except Exception, e:
        print e
    
        #print e 
        #conn.rollback()
    print "*"*80
        #print "Error First stage upgrading DB"
        #allow_continue()
    print 'First stage DB upgrading was completed'
    conn.commit()

def create_user():
    commands.getoutput('adduser --system --no-create-home --disabled-password ebs')
    
if __name__=='__main__':
    p = optparse.OptionParser()
    p = optparse.OptionParser(description='ExpertBilling manage utility',
                              prog='ebs_manage.py',
                              version='0.1',
                              usage= 'python %prog <install|upgrade|migrate> path_to_ebs_archive ')
    options, arguments = p.parse_args()
    #if len(arguments) == 3:
    if True:
        prompt_db_access()
        dbconnect()
        installation_date=None
        
        if 'install' in sys.argv:
            if not len(sys.argv)==3:  
                print "*"*80
                print 'Please define archive path and name (example: upgrade.py install /opt/12345678901234567890.tar.gz)'
                sys.exit()   
                
            if os.path.exists(BILLING_PATH):
                print "You cant`t install billing on existing installation"
                sys.exit() 
            create_folders()
            create_user()    
            unpack_archive(sys.argv[2])
            import_dump()
            import_initial_changes()
            #fromchanges(changes_start=True)
            upgrade_db()
            files=files_for_copy(first_time=True)
            if files:
                copy_files(files)
                        
            setup_init()
            setup_config()
            start_processes()
            setup_webcab()
            commands.getoutput("ln -sf /opt/ebs/web/django /opt/ebs/web/ebscab/django")
            print "*"*80
            print "   CONGRATULATIONS!!! Your ExpertBilling copy was sucefully installed!"
            print "   Default admin username/password: admin/admin"
            print "   Please, read manual, refer to forum.expertbilling.ru and wiki.expertbilling.ru for detail information about system"
            print "   Contacts: ICQ: 162460666, e-mail: brat002@gmail.com"
            print "*"*80
            
        if  'upgrade' in sys.argv:
            installation_date = modification_date(BILLING_PATH+'/license.lic')
            print installation_date
            if not len(sys.argv)==3:  
                print "*"*80
                print 'Please define archive path and name (example: upgrade.py upgrade /opt/12345678901234567890.tar.gz)'
                sys.exit()
            create_folders()
            stop_processes()    
            unpack_archive(sys.argv[2])
            
            
            pre_upgrade()
            
            backup_db()
            #fromchanges()
            upgrade_db()
            modifydb()
            files=files_for_copy()
            if files:
                copy_files(files)
            else:
                print '*'*80
                print 'Files copying dont need'
            
            
            #commands.getoutput("cd  /opt/ebs/web/ebscab/ && python manage.py syncdb --noinput")
            #commands.getoutput("python manage.py syncdb")
            allow_continue('Do you want to setup EBS webcab?')
            setup_webcab()
            commands.getoutput("ln -sf /opt/ebs/web/django /opt/ebs/web/ebscab/django")
            print "*"*80
            print "   CONGRATULATIONS!!! Your ExpertBilling copy was upgraded!"
            print "   Now start billing processes by running 'billing start' command!"            
            print "   Please, check for all running!"
            print "   Please, read manual, refer to forum.expertbilling.ru and wiki.expertbilling.ru for detail information about system"
            print "   Contacts: ICQ: 162460666, e-mail: brat002@gmail.com"
            print "*"*80
            
        if  'upgrade1.3' in sys.argv:
            installation_date = modification_date(BILLING_PATH+'/license.lic')
            print installation_date
            if not len(sys.argv)==3:  
                print "*"*80
                print 'Please define archive path and name (example: upgrade.py upgrade /opt/12345678901234567890.tar.gz)'
                sys.exit()
            create_folders()
            stop_processes()    
            unpack_archive(sys.argv[2])
            
            
            pre_upgrade()
            
            backup_db()
            fromchanges()
            upgrade_db()
            modifydb()
            files=files_for_copy()
            if files:
                copy_files(files)
            else:
                print '*'*80
                print 'Files copying dont need'
            allow_continue('Do you want to setup EBS webcab?')
            setup_webcab()
            print "*"*80
            print "   CONGRATULATIONS!!! Your ExpertBilling copy was upgraded frmo 1.3 to 1.4 version!"
            print "   Now start billing processes by running 'billing start' command!"            
            print "   Please, check for all running!"
            print "   Please, read manual, refer to forum.expertbilling.ru and wiki.expertbilling.ru for detail information about system"
            print "   Contacts: ICQ: 162460666, e-mail: brat002@gmail.com"
            print "*"*80
            
        if 'migrate' in sys.argv:
            allow_continue('Do you want to migrate your accounts database from 1.3 to 1.4 EBS version?')
            backup_db()
            upgrade_db()
            upgrade_from_13()
            
        if 'backupdb' in sys.argv:
            create_folders()
            #allow_continue('Do you want to migrate your accounts database from 1.3 to 1.4 EBS version?')
            auto_backup_db()     
        cleanup()
        #start_processes()
    else:
        p.print_help()


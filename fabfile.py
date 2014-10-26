#-*-coding=utf-8-*-
from __future__ import with_statement
from fabric.api import local
from fabric.api import local, settings, abort
from fabric.contrib.console import confirm
from fabric.colors import green,red,yellow
from fabric.api import lcd
from fabric.context_managers import  prefix
import os, sys
import tempfile
import ConfigParser
import datetime
import importlib

BILLING_ROOT_PATH = '/opt/ebs/'
BILLING_PATH = '/opt/ebs/data'
WEBCAB_ROOT_PATH = '/opt/ebs/web/'
WEBCAB_PATH = '/opt/ebs/web/ebscab/'
BACKUP_DIR = '/opt/ebs/backups/'
LAST_SQL = '/opt/ebs/data/etc/install.ini'

DEPLOYMENT_DIR = '/opt/ebs/deploy/'
BACKUP_DIR = '/opt/ebs/backups'
curdate = datetime.datetime.now().strftime('%d-%m-%y_%H_%M_%S')

def get_tempdir():
    return tempfile.mkdtemp()

def prepare_deploy():
    
    #local('echo "deb http://www.rabbitmq.com/debian/ testing main" >/etc/apt/sources.list.d/rabbitmq.list')
    
    local('apt-get  update && apt-get -y install python-software-properties wget psmisc')
    #local('wget http://www.rabbitmq.com/rabbitmq-signing-key-public.asc && apt-key add rabbitmq-signing-key-public.asc')
    #local('apt-get update')
    #local('apt-get -y install g++ postgresql-9.1 postgresql-contrib-9.1 postgresql-server-dev-9.1 htop mc python-dev mc openssh-server openssl python-paramiko python-crypto libapache2-mod-wsgi python-simplejson rrdtool snmp python-pexpect python-pip python-virtualenv rabbitmq-server ')
    local('apt-get  -y --force-yes  install libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev g++ postgresql postgresql-contrib postgresql-server-dev-all htop mc python-dev mc openssh-server openssl python-paramiko python-crypto libapache2-mod-wsgi python-simplejson rrdtool snmp python-pexpect python-pip python-virtualenv redis-server rabbitmq-server libmemcached-dev memcached libjpeg-dev libfreetype6-dev zlib1g-dev')
    local('pip install psycopg2')

def configure_rabbit():
    with settings(warn_only=True):
        local("rabbitmqctl add_user ebs ebspassword")
        local("rabbitmqctl add_vhost /ebs")
        local("rabbitmqctl change_password ebs ebspassword")
        local("rabbitmqctl set_permissions -p /ebs ebs '.*' '.*' '.*'")

    
def requirements():
    
    with settings(warn_only=True):
        local("sudo ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/")
        local("sudo ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/")
        local("sudo ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/")
        
        
    with settings(warn_only=True):
        with prefix('. /opt/ebs/venv/bin/activate'):
            local('pip install -U setuptools')
            
            
    with settings(warn_only=True):
        with prefix('. /opt/ebs/venv/bin/activate'):
            local("for line in `cat /opt/ebs/data/soft/del_requirements.txt`; do pip uninstall -y -q $line; done")
            
    with prefix('. /opt/ebs/venv/bin/activate'):
        local('pip install -U -r /opt/ebs/data/soft/requirements.txt')
    
def virtualenv():
    with lcd('/opt/ebs/'):
        local('virtualenv venv')
        
def congratulations():
    print("*"*80)
    print(green("CONGRATULATIONS!!! Your ExpertBilling 1.5 was succesfully installed!"))
    print(" Now you ExpertBilling include next new daemons in your system:")
    print(""" * core (/etc/init.d/ebs_core) - ExpertBilling core
 * nf (/etc/init.d/ebs_nf) - NetFlow collector
 * nffilter (/etc/init.d/ebs_nffilter) - NetFlow filter
 * nfroutine (/etc/init.d/ebs_nfroutine) - NetFlow tarificator
 * nfwriter (/etc/init.d/ebs_nfwriter) - NetFlow to disk writer daemon
 * rad_auth (/etc/init.d/ebs_rad_auth) - RADIUS authentication daemon
 * rad_acct (/etc/init.d/ebs_rad_acct) - RADIUS accounting daemon
 * celery (/etc/init.d/ebs_celery) - Asynchronous mechanism for executing tasks
 * rabbitmq (/etc/init.d/rabbitmq-server) - AMQP server. ExpertBilling use rabbitmq server for storing arrived NetFlow statistics!!!
 * postgresql (/etc/init.d/postgresql) - Database server
 * apache2 (/etc/init.d/apache2) - web-server""")
    print("""
 For manage your server, please, use command "billing"
 examples:
 * billing start
 * billing stop
 * billing force-stop

 or restart services manually
    """)
    print("   Now go to http://your.server.ip , login as admin and configure it!")
    print(red( "   It is alpha version ExpertBilling. For any error report to our forum."))
    print( "   Default admin username/password: admin/admin")
    print( "   Please, read manual, refer to forum.expertbilling.ru and wiki.expertbilling.ru for detail information about system")
    print( "   Contacts: ICQ: 162460666, e-mail: brat002@gmail.com")
    print( "*"*80)


def layout():
    print(green('Preparing layout'))
    if not os.path.exists('/opt/ebs'): local('mkdir -p /opt/ebs/')
    
    if not os.path.exists('/opt/ebs/backups'): local('mkdir -p /opt/ebs/backups')
    local("chmod a+w /opt/ebs/backups")
    if not os.path.exists('/opt/ebs/data'): local('mkdir -p /opt/ebs/data')
    if not os.path.exists('/opt/ebs/stats'): local('mkdir -p /opt/ebs/stats')
    if not os.path.exists('/opt/ebs/web'): local('mkdir -p /opt/ebs/web')
    if not os.path.exists('/opt/ebs/deploy'): local('mkdir -p /opt/ebs/deploy')

def unpack(tarfile):
    print(green('Unpack archive to /opt/ebs/ directory'))
    if not os.path.exists(tarfile):
        print('File %s not found. Enter correct expert billing archive path to argument. ' % tarfile)
        sys.exit()
        
    local('rm -rf /opt/ebs/deploy/')
    local('mkdir -p /opt/ebs/deploy/')
    local('tar -xvzf %s -C /opt/ebs/deploy/' % tarfile)
    with lcd('/opt/ebs/deploy'):
        local('tar -xvzf ebs.tar.gz -C %s' % BILLING_ROOT_PATH)
        local('tar -xvzf web.tar.gz -C %s' % BILLING_ROOT_PATH)
    
def postconf():
    print(green('Renaming ebs_config.ini.tmpl to ebs_config.ini'))
    local('mv /opt/ebs/data/ebs_config.ini.tmpl /opt/ebs/data/ebs_config.ini')
    
    
def setup_webcab():
    print(green('Setuping webcab'))
    if not os.path.exists(os.path.join(WEBCAB_PATH, 'settings_local.py')):
        with lcd(WEBCAB_PATH):
            local('cp settings_local.py.tmpl settings_local.py')


    apache_ver = local('apache2 -v | head -n 1', True)
    
    if 'Apache/2.4' in apache_ver:
        local('ln -sf %s /etc/apache2/sites-enabled/ebs.conf ' % os.path.join(WEBCAB_ROOT_PATH, 'default2.4'))
    else:
        local('ln -sf %s /etc/apache2/sites-enabled/ebs.conf ' % os.path.join(WEBCAB_ROOT_PATH, 'default'))
    
    local('ln -sf  %s /etc/apache2/sites-enabled/ebs_blankpage.conf'  % os.path.join(WEBCAB_ROOT_PATH, 'blankpage_config'))
    with settings(warn_only=True):
        local('a2dissite default')
        local('a2dissite 000-default')
    local('a2enmod rewrite')
    

    local('/etc/init.d/apache2 restart')
    with settings(warn_only=True):
        local(''' su postgres -c 'psql ebs -c "ALTER TABLE billservice_account ALTER COLUMN fullname TYPE varchar(2000);"' ''')
        local(''' su postgres -c 'psql ebs -c "ALTER TABLE auth_user ALTER COLUMN first_name TYPE varchar(2000);"' ''')

    with prefix('. /opt/ebs/venv/bin/activate'):
        with lcd(WEBCAB_PATH):
            local("touch /opt/ebs/web/ebscab/templates/site_verify_codes.html")
            local('mkdir -p /opt/ebs/web/ebscab/log/')
            
            local('touch /opt/ebs/web/ebscab/log/django.log')
            local('chmod -R 0777 /opt/ebs/web/ebscab/log/')
            local('python manage.py syncdb --noinput')
            local('python manage.py collectstatic --noinput')



        
def deploy(tarfile):
    print('Installing expert billing system')
    if os.path.exists(os.path.join(BILLING_PATH, 'ebs_config.ini')):
        print "You cant`t install billing on existing installation"
        print "Remove /opt/ebs and try again (rm -rf /opt/ebs)"
        sys.exit() 
    
    
    layout()
    with settings(warn_only=True):
        local('adduser --disabled-password ebs')
    prepare_deploy()
    configure_rabbit()
    virtualenv()
    
    unpack(tarfile)
    requirements()
    #backup settings before deploy, restore settings after deploy
    postconf()
    db_install()
    db_upgrade()
    
    setup_webcab()
    init_scripts()
    
    restart()
    congratulations()
    

def upgrade_14(tarfile):
    print('Upgrading expert billing system from 1.4.1 version')
    stop()
    layout()
    with settings(warn_only=True):
        local('adduser --disabled-password ebs')
    prepare_deploy()
    configure_rabbit()
    virtualenv()
    
    db_backup()
    stop()
    data_backup()
    webcab_backup()
    cleanup_14()
    layout()
    unpack(tarfile)
    requirements()
    #backup settings before deploy, restore settings after deploy
    
    #db_install()
    postconf()
    db_upgrade()
    
    setup_webcab()
    init_scripts()
    
    restart()
    congratulations()
    
def upgrade(tarfile):
    print('Upgrading expert billing system')
    

    
    db_backup()
    stop()
    data_backup()
    webcab_backup()

    layout()
    with settings(warn_only=True):
        local('adduser --disabled-password ebs')
    prepare_deploy()
    configure_rabbit()
    
    virtualenv()
    


    unpack(tarfile)
    requirements()
    #backup settings before deploy, restore settings after deploy
    
    #db_install()
    db_upgrade()
    setup_webcab()
    
    init_scripts()
    #postconf()
    restart()
    congratulations()
    

def cleanup_14():
    print(green('Cneaning directory /opt/ebs/data /opt/ebs/web'))
    local('mkdir -p %s' % os.path.join(BACKUP_DIR, 'pre15', 'data/'))
    local('mkdir -p %s' % os.path.join(BACKUP_DIR, 'pre15', 'webcab/'))
    local('tar -cvzf %s/data.tar.gz %s' % (os.path.join(BACKUP_DIR, 'pre15', ), BILLING_PATH,) )
    local('tar -cvzf %s/web.tar.gz %s' % (os.path.join(BACKUP_DIR, 'pre15'), os.path.join(BILLING_ROOT_PATH, 'web/'),) )
    local('rm -rf %s' % BILLING_PATH)
    local('rm -rf %s' % os.path.join(BILLING_ROOT_PATH, 'web/'))
    
def restart():
    with settings(warn_only=True):
        print(green('Restarting processes'))
        local("billing restart")

def stop():
    print(green('Stopping processes'))
    with settings(warn_only=True):
        local("billing force-stop")
        local("billing force-stop")
        local("/etc/init.d/apache2 stop")
        local("killall -9 python")


def init_scripts():
    print(green('Installing init script'))
    local('cp -f %s /etc/init.d/' % (os.path.join(BILLING_PATH,'init.d/*')))
    local('update-rc.d ebs_celery defaults')
    local('update-rc.d ebs_nfroutine defaults')
    local('update-rc.d ebs_nf defaults')
    local('update-rc.d ebs_nffilter defaults')
    local('update-rc.d ebs_rad_auth defaults')
    local('update-rc.d ebs_rad_acct defaults')
    local('update-rc.d ebs_core defaults')
    local('cp -f /opt/ebs/data/soft/celeryd /etc/default/')
    local('cp -f /opt/ebs/data/soft/billing /usr/sbin/')
    local('chmod +x /usr/sbin/billing')

def db_backup():
    print(green('Database backup'))
    local("""su postgres -c 'pg_dump ebs | gzip >%s'"""  % (os.path.join(BACKUP_DIR, 'database_%s.gz' % curdate)))

def data_backup():
    print(green('/opt/ebs/data folder backup'))
    with lcd(BILLING_PATH):
        local('tar -cvzf %s .' % os.path.join(BACKUP_DIR, 'data_%s.tar.gz' % curdate))
        

def webcab_backup():
    print(green('Webcab backup'))
    with lcd(BILLING_ROOT_PATH):
        local('tar -cvzf %s web' % os.path.join(BACKUP_DIR, 'web_%s.tar.gz' % curdate))
        
def db_install():
    print(green('Installing initial databaes scheme'))
    with lcd('/opt/ebs/data/'):
        local("""su postgres -c 'psql ebs -f sql/ebs_dump.sql'""")
        local("""su postgres -c 'psql ebs -f sql/changes.sql'""")

def db_upgrade():
    print("*"*80)
    print(green("Upgrading DB from sql/upgrade/*.sql files"))
    SQL_UPGRADE_PATH = os.path.join(BILLING_PATH, 'sql/upgrade')
    
    sys.path.append(os.path.join(BILLING_PATH, 'migrations'))
    install_config = ConfigParser.ConfigParser()
    first_time=False
    if not os.path.exists(LAST_SQL):
        first_time=True
        last_sql_id=0
    
    if first_time==True:
        install_config.read(LAST_SQL)
        if not install_config.has_section('sql'):
            install_config.add_section('sql') 
    else:
        install_config.read(LAST_SQL) 
        last_sql_id=install_config.getint('sql', 'last_id')
                
        
    available_files=[int(x.replace(".sql", '')) for x in os.listdir(SQL_UPGRADE_PATH)]
    
    for id in xrange(last_sql_id+1, max(available_files)+1):
        upgrade_sql="%s/%s.sql" % (SQL_UPGRADE_PATH, id)
        if not os.path.exists(upgrade_sql):
            print "cannot find file %s" % upgrade_sql
            continue
        if os.path.exists(os.path.join(BILLING_PATH, 'migrations', 'migration_%s.py' % id)):
            worker = importlib.import_module('migration_%s' % id)
            worker.pre_migrate()
        local("""su postgres -c 'psql ebs -f %s'""" % (upgrade_sql,))
        if os.path.exists(os.path.join(BILLING_PATH, 'migrations', 'migration_%s.py' % id)):
            worker.post_migrate()

            

        install_config.set('sql','last_id',id)
            
        
    if first_time==True:
        with open(LAST_SQL, 'wb') as configfile:
            install_config.write(configfile)
    else:
        with open(LAST_SQL, 'wb') as configfile:
            install_config.write(configfile)





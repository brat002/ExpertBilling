#-*-coding=utf-8-*-
from __future__ import with_statement
from fabric.api import local
from fabric.api import local, settings, abort
from fabric.contrib.console import confirm
from fabric.api import lcd
from fabric.context_managers import  prefix
import os, sys
import tempfile
import ConfigParser
import datetime

BILLING_ROOT_PATH = '/opt/ebs/'
BILLING_PATH = '/opt/ebs/data'
WEBCAB_PATH = '/opt/ebs/data/ebscab/'
BACKUP_DIR = '/opt/ebs/backups/'
LAST_SQL = '/opt/ebs/data/etc/install.ini'
FIRST_TIME_LAST_SQL='/opt/ebs/deploy/billing/etc/install.ini'
DEPLOYMENT_DIR = '/opt/ebs/deploy/'
BACKUP_DIR = '/opt/ebs/backups'
curdate = datetime.datetime.now().strftime('%d-%m-%y_%H_%M_%S')

def get_tempdir():
    return tempfile.mkdtemp()

def prepare_deploy():
    local('apt-get update')
    local('apt-get install postgresql postgresql-contrib mc openssh-server openssl python-paramiko python-crypto libapache2-mod-wsgi python-simplejson rrdtool snmp python-pexpect python-pip python-virtualenv')

    
def requirements():
    with prefix('source /opt/ebs/venv/bin/activate'):
        local('pip install -U -r /opt/ebs/data/soft/requirements.txt')
    
def virtualenv():
    with lcd('/opt/ebs/'):
        local('virtualenv venv')
        

def layout():
    if not os.path.exists('/opt/ebs'): local('mkdir -p /opt/ebs/')
    if not os.path.exists('/opt/ebs/backups'): local('mkdir -p /opt/ebs/backups')
    if not os.path.exists('/opt/ebs/data'): local('mkdir -p /opt/ebs/data')
    if not os.path.exists('/opt/ebs/stats'): local('mkdir -p /opt/ebs/stats')
    if not os.path.exists('/opt/ebs/web'): local('mkdir -p /opt/ebs/web')
    if not os.path.exists('/opt/ebs/deploy'): local('mkdir -p /opt/ebs/deploy')

def unpack(tarfile):
    local('tar -xvzf %s -C /opt/ebs/deploy/' % tarfile)
    with lcd('/opt/ebs/deploy'):
        local('tar -xvzf ebs.tar.gz -C %s' % BILLING_ROOT_PATH)
        local('tar -xvzf web.tar.gz -C %s' % BILLING_ROOT_PATH)
    
def update_src():
    #local('cp -rf /opt/ebs/deploy/billing/data/* /opt/ebs/data/')
    pass
    
def setup_webcab():
    with lcd(WEBCAB_PATH):
        local('cp ebscab/settings_local.py.tmpl ebscab/settings_local.py')
        local('ln -sf default /etc/init.d/apache2/sites-enabled/ebs')
        local('a2dissite default')
        
def deploy(tarfile):
    print('Installing expert billing system')
    if os.path.exists(os.path.join(BILLING_PATH, 'ebs_config.ini')):
        print "You cant`t install billing on existing installation"
        sys.exit() 
    
    print('Preparing layout')
    layout()
    local('adduser --system --no-create-home --disabled-password ebs')
    prepare_deploy()
    virtualenv()
    unpack(tarfile)
    update_src()#backup settings before deploy, restore settings after deploy
    db_install()
    db_upgrade()
    requirements()
    setup_webcab()

def upgrade():
    pass

def init_scripts():
    local('cp -f %s /etc/init.d/' % (os.path.join(BILLING_PATH,'init.d/')))
    local('update-rc.d ebs_celery defaults')
    local('update-rc.d ebs_nfroutine defaults')
    local('update-rc.d ebs_nf defaults')
    local('update-rc.d ebs_nffilter defaults')
    local('update-rc.d ebs_rad_auth defaults')
    local('update-rc.d ebs_rad_acct defaults')
    local('update-rc.d ebs_core defaults')

def db_backup():
    local("""su postgres -c 'pg_dump ebs | gzip >%s'""", (os.path.join(BACKUP_DIR, 'database_%s.gz' % curdate)))

def db_install():
    with lcd('/opt/ebs/data/'):
        local("""su postgres -c 'psql ebs -f sql/ebs_dump.sql'""")
        local("""su postgres -c 'psql ebs -f sql/changes.sql'""")

def db_upgrade():
    print("*"*80)
    print("Upgrading DB from sql/upgrade/*.sql files")
    SQL_UPGRADE_PATH = os.path.join(BILLING_PATH, '/sql/upgrade')
    install_config = ConfigParser.ConfigParser()
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
        upgrade_sql="%s%s.sql" % (SQL_UPGRADE_PATH, id)
        if not os.path.exists(upgrade_sql):
            print "cannot find file %s" % upgrade_sql
            continue
            
        local("""su postgres -c 'psql ebs -f %s'""" % (upgrade_sql,))


            

        install_config.set('sql','last_id',id)
            
        
    if first_time==True:
        with open(FIRST_TIME_LAST_SQL, 'wb') as configfile:
            install_config.write(configfile)
    else:
        with open(LAST_SQL, 'wb') as configfile:
            install_config.write(configfile)





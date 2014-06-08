from fabric.api import local
from fabric.api import settings
from fabric.api import run
from fabric.api import cd
from fabric.api import env
from fabric.api import task
from fabric.api import hosts
from fabric.operations import sudo


@hosts(['brat002@m4.diggit.ru', 'brat002@m8.diggit.ru'])
def build(key=None, users=200, name=''):
    with cd('mikrobill'):
        run('git pull')
        run('sh build_all.sh %s %s %s' % (key if key else name or 'demo1.5_`uname -i`', users, key if key else ''))
        run('scp builds/%s.tar.gz brat002@m3.diggit.ru:/opt/ebs/media/builds/' % (key if key else 'demo1.5_`uname -i`'))
       
       
@hosts(['brat002@m4.diggit.ru', ])
def build_x64(key=None, users=200, name=''):
    with cd('mikrobill'):
        run('git pull')
        run('sh build_all.sh %s %s %s' % (key if key else name or 'demo1.5_`uname -i`', users, key if key else ''))
        run('scp builds/%s.tar.gz brat002@m3.diggit.ru:/opt/ebs/media/builds/' % (key if key else 'demo1.5_`uname -i`'))
        
@hosts(['brat002@m8.diggit.ru', ])
def build_x32(key=None, users=200, name=''):
    with cd('mikrobill'):
        run('git pull')
        run('sh build_all.sh %s %s %s' % (key if key else name or 'demo1.5_`uname -i`', users, key if key else ''))
        run('scp builds/%s.tar.gz brat002@m3.diggit.ru:/opt/ebs/media/builds/' % (key if key else 'demo1.5_`uname -i`'))
        
        
@hosts(['brat002@m4.diggit.ru'])
def update_demo():
    with cd('mikrobill'):
        run('cp builds/demo1.5_`uname -i`.tar.gz ../')
    run('tar -xvzf demo1.5_`uname -i`.tar.gz fabfile.py')
    sudo('echo >/opt/ebs/web/ebscab/log/django.log')
    sudo('fab upgrade:demo1.5_`uname -i`.tar.gz')
    
    
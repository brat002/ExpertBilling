from fabric.api import local
from fabric.api import settings
from fabric.api import run
from fabric.api import cd
from fabric.api import env
from fabric.api import task


env.hosts = ['brat002@m4.diggit.ru', 'brat002@m8.diggit.ru']

def build(key=None, users=200):
    with cd('mikrobill'):
        run('git pull')
        run('sh build_all.sh %s %s %s' % (key if key else 'demo1.5_`uname -i`', users, key if key else ''))
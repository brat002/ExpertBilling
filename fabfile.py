# -*- coding=utf-8 -*-
from fabric.contrib.project import rsync_project
from fabric.api import env, cd, run
RSYNC_EXCLUDE = ['eggs', 'bin', '*.out', '*.log', '*.db',
                 '*.pyc', '*.so', '*.recs', '*.dump', '*.pyo', 'logs', '_trial_temp*'
                 '*.sh.*', '*.log.*', '*.so.*', '*.cfg', ".svn", 
                 'develop-eggs', 'parts', '#*', '*~', 'settings_*', '*build*']
ENV_DIR = "~/ebscab"
SRC_DIR = "ebscab"

env.hosts = ['webchemist@188.40.89.38']

def ls():
    with cd("~"):
        run("ls -la")

def make_env():
    '''Making virtual env'''
    run("virtualenv %s"%ENV_DIR)
    with cd(ENV_DIR):
        run("source ./bin/activate")
        run("./bin/pip install django==1.1")
        run("mkdir ./%s"%SRC_DIR)

def restart():
    with cd("%s/%s" % (ENV_DIR, SRC_DIR)):
        run("./daemon.sh restart")

def status():
    with cd("%s/%s" % (ENV_DIR, SRC_DIR)):
        run("./daemon.sh status")
    
def sync(do_restart=False):
    rsync_project("%s/%s" % (ENV_DIR, SRC_DIR), "./*", exclude=RSYNC_EXCLUDE)
    if do_restart:
        restart()

# -*- coding=utf-8 -*-
import os, sys
import logging

DEBUG = True
DEBUG_SQL=True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'ebs_nofkeys'             # Or path to database file if using sqlite3.
DATABASE_USER = 'ebs'             # Not used with sqlite3.
DATABASE_PASSWORD = 'ebspassword'         # Not used with sqlite3.
DATABASE_HOST = '127.0.0.1'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '5432'             # Set to empty string for default. Not used with sqlite3.

# system time zone.
TIME_ZONE = 'Europe/Minsk'
LANGUAGE_CODE = 'ru-Ru'
SITE_ID = 1

USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = '/opt/ebs/web/ebscab/media'
MEDIA_ROOT = os.path.abspath('./media')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '%!a5^gik_4lgzt+k)vyo6)y68_3!u^*j(ujks7(=6f2j89d=x&'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'notification.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'notification.context_processors.footer',
    'notification.context_processors.notices',
    'notification.context_processors.setCurrency',
    'lib.context_processors.default_current_view_name',
    'notify.context_processors.notifications',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'lib.threadlocals.ThreadLocalsMiddleware',
    'notify.middleware.NotificationsMiddleware',
    'billservice.middleware.UrlFilter'

)

ROOT_URLCONF = 'ebscab.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/opt/ebs/web/ebscab/templates',
    #'/opt/ebs/web/ebscab/helpdesk/templates',
    os.path.abspath('./templates'),
    #os.path.abspath('./helpdesk/templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sitemaps',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'radius',
    'nas',
    'billservice',
    'lib',
    'service_monitor',
    'testcases',
    'statistics',
    'webmoney',
    'paymentgateways.qiwi',
    'helpdesk',
    'notify'
)

AUTHENTICATION_BACKENDS = (
    #'helpdesk.backend.LoginSystemUserBackend',
    'billservice.backend.LoginUserBackend',
)

RPC_ADDRESS = '127.0.0.1'
RPC_PORT = 7771
RPC_USER = 'webadmin'
RPC_PASSWORD = 'RPCwebadmin'

LOG_LEVEL = 0

CACHE_BACKEND = 'locmem:///'

BLOCKED_TIME = 30*60
ACTIVATION_COUNT=5
SESSION_EXPIRE_AT_BROWSER_CLOSE=True

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/login/'

ALLOW_PROMISE = True
MAX_PROMISE_SUM = 100000
MIN_BALLANCE_FOR_PROMISE=-1000
LEFT_PROMISE_DAYS = 7

ALLOW_WEBMONEY = False
ALLOW_QIWI = True
WEBCAB_LOG = '/opt/ebs/web/ebscab/log/webcab_log'
#WEBCAB_LOG = os.path.abspath('log/webcab_log')

CURRENCY = '$'

TEST_RUNNER = 'testcases.test_runner.run_tests'
PERSONAL_AREA_STAFF_MENU = [
    ('helpdesk_dashboard', u"Панель"),
    ('helpdesk_list', u"Поддержка"),
    ('helpdesk_submit', u"Создать запрос"),
    ('helpdesk_report_index', u"Статистика"),
    ('/helpdesk/admin/', u"Настройки"),
    ('account_logout', u'Выход'),
]

# load local_settings
try:
    from settings_local import *
except:
    pass
# load host dependent settings
try:
    import socket
    import imp
    HOST = str(socket.gethostname()).lower()
    fp, pathname, description = imp.find_module('%s_settings' % HOST)
    imp.load_module('_host_settings', fp, pathname, description)
    from _host_settings import *
except (ImportError, IOError), e:
    pass

# define logging
if DEBUG:
    LEVEL = logging.DEBUG
else:
    LEVEL = logging.INFO
PROJECT_DIR = os.path.dirname(__file__)
logging.basicConfig(level=LEVEL,
     format='%(asctime)s %(name)s %(levelname)s %(message)s',
     filename=os.path.join(PROJECT_DIR, 'log/django.log'),
     filemode='a+')
root = logging.basicConfig()

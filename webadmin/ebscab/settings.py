
# Django settings for ebscab project.
import os, sys
DEBUG = True
DEBUG_SQL=True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'ebs_new'             # Or path to database file if using sqlite3.
DATABASE_USER = 'ebs'             # Not used with sqlite3.
DATABASE_PASSWORD = 'ebspassword'         # Not used with sqlite3.
DATABASE_HOST = '127.0.0.1'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '5432'             # Set to empty string for default. Not used with sqlite3.





# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Minsk'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'ru-Ru'
#AUTHENTICATION_BACKENDS=(
#    'django.contrib.auth.backends.ModelBackend',
#    'ebscab.authbackend.ModelBackend',
#)

#LOGIN_REDIRECT_URL='/account/'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
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
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'lib.threadlocals.ThreadLocalsMiddleware',

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
    #'helpdesk',
    'radius',
    'nas',
    'billservice',
    'lib',
    'service_monitor',
    'testcases',
    'statistics',
    'webmoney',
    'paymentgateways.qiwi'
    #'helpdesk',
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
LEFT_PROMISE_DAYS = 7

WEBCAB_LOG = '/opt/ebs/web/ebscab/log/webcab_log'
WEBCAB_LOG = os.path.abspath('log/webcab_log')

CURRENCY = '$'

TEST_RUNNER = 'testcases.test_runner.run_tests'

try:
    from settings_local import *
except:
    pass

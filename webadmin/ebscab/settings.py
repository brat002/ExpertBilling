# -*- coding=utf-8 -*-
import os, sys
import logging
sys.path.append('/opt/ebs/data/workers/')
DEBUG = True
DEBUG_SQL=False
TEMPLATE_DEBUG = DEBUG
USE_TZ = False

ADMINS = (
     #('Your Name', 'your_email@domain.com'),
)


MANAGERS = ADMINS

DATABASES = {
    'default': {
        'NAME': 'ebs',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'ebs',
        'PASSWORD': 'ebspassword',
        'HOST': "127.0.0.1",
        'PORT':5432,
    },

}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'localmem',
        'TIMEOUT': 60
    }
}

# system time zone.
TIME_ZONE = None # This will use system timezone. Don`t touch this.

LANGUAGE_CODE = 'ru-RU'
SITE_ID = 1

USE_I18N = True

USE_l10N = True

MEDIA_URL = '/media/'

DATETIME_FORMAT = "d.m.Y H:i:s"
SHORT_DATETIME_FORMAT = "d.m.Y H:i:s"

STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/admin_media/'
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

# Make this unique, and don't share it with anybody.
SECRET_KEY = '%!a5^gik_4lgzt+k)vyo6)y68_3!u^*j(ujks7(=6f2j89d=x&'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '#g7(r6=^+7+h6x2_sb)mqydjk6c_!m*d%#na=qtkca$05tx#$8'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
     'django.contrib.auth.context_processors.auth',
    'notification.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'lib.context_processors.default_current_view_name',
    
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    #'lib.threadlocals.ThreadLocalsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
    #'billservice.middleware.UrlFilter'

)

ROOT_URLCONF = 'ebscab.urls'

TEMPLATE_DIRS = (

    '/opt/ebs/web/ebscab/templates',
    #'/opt/ebs/web/ebscab/helpdesk/templates',
    '%s/templates/' % os.path.abspath('.'),

)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'radius',
    'nas',
    'billservice',
    'lib',
    'statistics',
    'paymentgateways.webmoney',
    'helpdesk',
    'object_log',
    'django_tables2',
    'crispy_forms',
    'dynamicmodel',
    'ajax_select',
    'ebsadmin',
    'django_tables2_reports',
    'getpaid',
    'sendsms',
    'django_select2',
)


AJAX_LOOKUP_CHANNELS = {
    #   pass a dict with the model and the field to search against
    'account_fts'  : ('billservice.lookups', 'AccountFTSLookup'),
    'account_fullname'  : ('billservice.lookups', 'AccountFullnameLookup'),
    'account_username'  : ('billservice.lookups', 'AccountUsernameLookup'),
    'account_contract': ('billservice.lookups', 'AccountContractLookup'),
    'account_contactperson': ('billservice.lookups', 'AccountContactPersonLookup'),
    'city_name': ('billservice.lookups', 'CityLookup'),
    'street_name': ('billservice.lookups', 'StreetLookup'),
    'house_name': ('billservice.lookups', 'HouseLookup'),
    'hardware_fts': ('billservice.lookups', 'HardwareLookup'),
    'organization_name': ("billservice.lookups", "OrganizationLookup"),
    'subaccount_fts': ('billservice.lookups', 'SubAccountFTSLookup')
    
    
}

AJAX_SELECT_BOOTSTRAP = False
AJAX_SELECT_INLINES = 'inline'

AUTHENTICATION_BACKENDS = (
    #'helpdesk.backend.LoginSystemUserBackend',
    'billservice.backend.LoginUserBackend',
)

#credentials generation rules
LOGIN_LENGTH=8
PASSWORD_LENGTH=8
LOGIN_CONTAIN_LETTERS=True
LOGIN_CONTAIN_DIGITS=True
PASSWORD_CONTAIN_LETTERS=False
PASSWORD_CONTAIN_DIGITS=True

PGCRYPTO_VALID_CIPHERS = ('AES', )
PGCRYPTO_DEFAULT_CIPHER = 'AES'
PGCRYPTO_DEFAULT_KEY = 'ebscryptkeytest'

LOG_LEVEL = 0

CACHE_BACKEND = 'locmem:///'

SESSION_EXPIRE_AT_BROWSER_CLOSE=True

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/login/'

ALLOW_PROMISE = True
MAX_PROMISE_SUM = 10000
MIN_BALLANCE_FOR_PROMISE=-1000
LEFT_PROMISE_DAYS = 7

ALLOW_WEBMONEY = True
ALLOW_QIWI = True
QIWI_MIN_SUMM=30

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'user@gmail.com'
EMAIL_HOST_PASSWORD = 'userpassword'


CURRENCY = u' руб'

#GETPAID_BACKENDS = ('getpaid.backends.easypay',
#                    )

GETPAID_BACKENDS_SETTINGS = {
    # Please provide your settings for backends
    'payments.liqpay' : {
         'TYPE': 'frontend', 
        'DEFAULT_CURRENCY' : 'UAH',
        'MERCHANT_ID': '',
        'MERCHANT_SIGNATURE': '',
        'PAY_WAY': ('card', 'liqpay', 'delayed'),
        'EXPIRE_TIME': 36,

    },

    'payments.easypay' : {
                          'TYPE': 'backend', 
        'DEFAULT_CURRENCY' : 'UAH',
        'SERVICE_ID' : '1',
        'allowed_ip': ('93.183.196.28', '93.183.196.26'),

    },
    'payments.ru_sberbank' : {
                          'TYPE': 'backend', 
        'DEFAULT_CURRENCY' : 'RUB',
        'PASSWORD' : '12345',
        'allowed_ip': ('93.183.196.28', '93.183.196.26'),

    }
}

SENDSMS_BACKENDS = (
                    ('sendsms.backends.websms.SmsBackend', 'websms.ru'),
                    ('sendsms.backends.smsru.SmsBackend', 'sms.ru'),
                    ('sendsms.backends.smspilotru.SmsBackend', 'smspilot.ru'),
                    )

SENDSMS_BACKENDS_SETTINGS = {
                             'sendsms.backends.websms': {
                                                         'FROM_NAME': '', # http://websms.ru/FromName.asp
                                                         'USERNAME': '',
                                                         'PASSWORD': '',
                                                         },
                             'sendsms.backends.smsru': {
                                                         'FROM_NAME': '', 
                                                         'API_ID': '',
                                                         'TRANSLIT': '1',
                                                         'TEST': '0',
                                                         'PARTNER_ID': '',
                                                         },
                             'sendsms.backends.smspilotru': {
                                                         'FROM_NAME': '', 
                                                         'API_ID': '',
                                                         }
                             }

SENDSMS_IF_BALLANCE_AMOUNT = 0
SENDSMS_DEFAULT_BACKEND = 'sendsms.backends.websms.SmsBackend'

SENDSMS_DEFAULT_FROM_PHONE = '+11111111111'

TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner'
#TEST_RUNNER = 'testrunner.NoDbTestRunner'

PERSONAL_AREA_STAFF_MENU = [
    ('helpdesk_dashboard', u"Сводка"),
    ('helpdesk_list', u"Заявки"),
    ('helpdesk_submit', u"Создать заявку"),
    ('helpdesk_kb_index', u"База знаний"),
    ('helpdesk_report_index', u"Статистика"),
    ('helpdesk_user_settings', u"Ваши настройки"),
    ('/admin/', u"Конфигурация"),
    ('account_logout', u'Выход'),
]



# load local_settings
try:
    from settings_local import *
    import settings_local
    INSTALLED_APPS += settings_local.GETPAID_BACKENDS if 'GETPAID_BACKENDS' in settings_local.__dict__  else ()
except Exception, ex:
    print ex


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


    
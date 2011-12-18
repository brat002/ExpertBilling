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
MEDIA_ROOT = '/opt/ebs/web/ebscab/media'
#MEDIA_ROOT = os.path.abspath('./media')

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
    #'billservice.middleware.UrlFilter'

)

ROOT_URLCONF = 'ebscab.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/opt/ebs/web/ebscab/templates',
    #'/opt/ebs/web/ebscab/helpdesk/templates',
    os.path.abspath('./templates'),
    os.path.abspath('./extjs/templates'),
    
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
    'statistics',
    'paymentgateways.webmoney',
    'paymentgateways.qiwi',
    'helpdesk',
    'compress',
    
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

ALLOW_WEBMONEY = True
ALLOW_QIWI = True
WEBCAB_LOG = '/opt/ebs/web/ebscab/log/webcab_log'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'user@gmail.com'
EMAIL_HOST_PASSWORD = 'userpassword'


CURRENCY = '$'

TEST_RUNNER = 'testcases.test_runner.run_tests'
PERSONAL_AREA_STAFF_MENU = [
    ('helpdesk_dashboard', u"Сводка"),
    ('helpdesk_list', u"Заявки"),
    ('helpdesk_submit', u"Создать заявку"),
    ('helpdesk_kb_index', u"База знаний"),
    ('helpdesk_report_index', u"Статистика"),
    ('helpdesk_user_settings', u"Ваши настройки"),
    ('/helpdesk/admin/', u"Конфигурация"),
    ('account_logout', u'Выход'),
]

COMPRESS = False
COMPRESS_AUTO = False
COMPRESS_VERSION = False
COMPRESS_YUI_BINARY = 'java -jar lib/yuicompressor-2.4.2.jar'

#CSSTIDY_BINARY = 'd:/projects/django_project/lib/csstidy.exe' # windows

CSSTIDY_ARGUMENTS = "--template=highest --remove_last_;=true --allow_html_in_templates=false --compress_colors=true --compress_font-weight=true --lowercase_s=true --sort_properties=true"
# --preserve_css=true --remove_last_;=true
#--discard_invalid_properties=false
#--remove_bslash=false
#--sort_selectors=false
#--timestamp=false
#--merge_selectors=[2|1|0] |
#--case_properties=[0|1|2] |
#--optimise_shorthands=[1|2|0] |


# aptitude install csstidy
COMPRESS_CSS_FILTERS = ( 'compress.filters.csstidy.CSSTidyFilter', )
#COMPRESS_JS_FILTERS = ('compress.filters.jsmin.JSMinFilter',)
# ## or 
COMPRESS_JS_FILTERS = ("compress.filters.yui.YUICompressorFilter",)

# packed files stored to MEDIA/p folder




COMPRESS_CSS = {
    'screen_css': {
        'source_filenames': (
            "ext/resources/css/ext-all.css",

            #Default ExtJS theme
            "ext/resources/css/xtheme-blue.css",
#            "ext/resources/css/reset-min.css",

            "ext/ebs/styles.css",
            "css/style.css",
            "css/MultiSelect.css",
            
            ),
        'output_filename': 'p/screen.?.css',
        'extra_context': { 'media': 'screen,projection',},
    },
#    'screen_css_ie7': {
#        'source_filenames': (
#                'ext/ebs/styles-ie7.css',
#                ),
#        'output_filename': 'p/ie7.?.css',
#        'extra_context': {'media': 'screen,projection',},
#    }
#    'print_css': {
#        'source_filenames': (
#                'css/print.css',
#                ),
#        'output_filename': 'p/print.?.css',
#        'extra_context': {'media': 'print',},
#    },


}


COMPRESS_JS = {
    #EXTJS Debug
     #EXTJS Production
    'scripts_js_ext': {
        'source_filenames': (
            "ext/adapter/ext/ext-base.js",
            "ext/ext-all-debug.js"
        ),
        'output_filename': 'p/ext.?.js',
    },

    'scripts_js_ux': {
        'source_filenames': (
        "ext/ux/gridfilters/menu/RangeMenu.js",

        "ext/ux/gridfilters/menu/ListMenu.js",

        "ext/ux/gridfilters/GridFilters.js",
        "ext/ux/gridfilters/filter/Filter.js",
        "ext/ux/gridfilters/filter/StringFilter.js",
        "ext/ux/gridfilters/filter/DateFilter.js",
        "ext/ux/gridfilters/filter/ListFilter.js",
        "ext/ux/BufferView.js",

        "ext/ux/gridfilters/filter/NumericFilter.js",
        "ext/ux/gridfilters/filter/BooleanFilter.js",

        "ext/ux/Ext.ux.Printer.js",
        #"ext/ux/print/Printer.js",
        #"ext/ux/print/renderers/Base.js",
        #"ext/ux/print/renderers/GridPanel.js",
        
        "ext/ux/MultiSelect.js",
        "ext/ux/ItemSelector.js",
        "ext/ux/Ext.ux.grid.Search.js",
        "ext/ux/CenterLayout.js",
        
        

        #All grid navigation  plugin support
        "ext/ux/SlidingPager.js",

        #Main window tabs plugin support
        "ext/ux/TabScrollerMenu.js",
        "ext/ux/Ext.ux.util.js",
        
        "ext/ebs/plugins/msgbus.js",
        "ext/ebs/plugins/Ext.ux.form.LovCombo.js",
        "ext/ebs/plugins/Ext.ux.grid.RowActions.js",
        "ext/ebs/plugins/Ext.ux.plugin.PagingToolbarResizer.js",
        
        
        "ext/ux/Ext.ux.HtmlEditor.Plugins-all-debug.js",
        #"ext/ebs/plugins/date.js",
        
        #plugins
        
        ),
        'output_filename': 'p/ux.?.js',
    },

#     'scripts_js_direct': {
#        'source_filenames': (
#           "/extjs/remoting/provider_js",
#           "/extjs/remoting/api/"
#            ),
#        'output_filename': 'p/direct.ux.?.js',
#    },
    'scripts_js_ebs_user_group_0': {
        'source_filenames': (
    # Describe application
            u"ext/ebs/application.js",
            u"ext/ebs/base_components.js",
            
            u"ext/ebs/locale/" + LANGUAGE_CODE + u".js",
            u"ext/ebs/locale/main_menu." + LANGUAGE_CODE + u".0.js",
            
            u"ext/ebs/datastore.js",
    # Application components
            u"ext/ebs/components/admin_accounts_list.js",
            u"ext/ebs/components/admin_nasses_list.js",
            u"ext/ebs/components/admin_sessionmonitor.js",
            u"ext/ebs/components/admin_transactionreport.js",
            #u"ext/ebs/components/admin_session_monitor_list.js",
            #u"ext/ebs/components/admin_settlement_period_list.js",
    # Main run script
            u"ext/ebs/run.js"
        ),
         'output_filename': 'p/ebs.%s.%d?.js' % (LANGUAGE_CODE, 0),
    },

    'scripts_js_ebs_user_group_1': {
        'source_filenames': (
    # Describe application
            u"ext/ebs/locale/" + LANGUAGE_CODE + u".js",
            u"ext/ebs/locale/main_menu." + LANGUAGE_CODE + u".0.js",
            u"ext/ebs/base_components.js",
            u"ext/ebs/application.js",
            u"ext/ebs/datastore.js", # TODO: other storage
    # Application components
            u"ext/ebs/components/admin_nasses_list.js",
    # Main run script
            u"ext/ebs/run.js"
        ),
         'output_filename': 'p/ebs.%s.%d?.js' % (LANGUAGE_CODE, 1),
    },


}

# load local_settings
try:
    from settings_local import *
except:
    pass
#    print "tratata"
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

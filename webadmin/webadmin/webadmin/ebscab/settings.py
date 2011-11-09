
# Django settings for ebscab project.
#import os, sys
from os import path

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
MEDIA_ROOT = path.abspath('./media')

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
    '/opt/ebs/web/ebscab/helpdesk/templates',
    path.abspath('./templates'),
    path.abspath('./helpdesk/templates'),
    path.abspath('./extjs/templates'),
)


INSTALLED_APPS = (
    'django.contrib.auth',
    #'django.contrib.contenttypes',
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
    'compress',
    'ebsadmin'
    #'extdjango'
)

AUTHENTICATION_BACKENDS = (
    'helpdesk.backend.LoginSystemUserBackend',
    'billservice.backend.LoginUserBackend',
)

RPC_ADDRESS = '127.0.0.1'
RPC_PORT = 7771
RPC_USER = 'webadmin'
RPC_PASSWORD = 'RPCwebadmin'

LOG_LEVEL = 0

#CACHE_BACKEND = 'locmem:///'

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

CURRENCY = '$'

TEST_RUNNER = 'testcases.test_runner.run_tests'


# ExtJs Direct
SERIALIZATION_MODULES = {
    "extdirect" : "extdirect.django.serializer"        
}
#path.abspath('./extjs/templates'),
 
try:
    from settings_local import *
except:
    pass




# Django settings for ebscab project.


RPC_ADDRESS = '127.0.0.1'
RPC_PORT = 7771
RPC_USER = 'webadmin'
RPC_PASSWORD = 'RPCwebadmin'

LOG_LEVEL = 0



CURRENCY = '$'

TEST_RUNNER = 'testcases.test_runner.run_tests'


SERIALIZATION_MODULES = { 
                            'extdirect' : 'extdirect.django.serializer'
                        }


# Compress media

COMPRESS = False
COMPRESS_AUTO = False
COMPRESS_VERSION = False
#COMPRESS_CSS_FILTERS = None

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

            "ext/ebs/styles.css",
            "css/style.css",
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
            "ext/resources/adapter/ext/ext-base.js",
            "ext/resources/ext-all-debug.js"
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

        "ext/ux/gridfilters/filter/NumericFilter.js",
        "ext/ux/gridfilters/filter/BooleanFilter.js",

        "ext/ux/print/Printer.js",
        "ext/ux/print/renderers/Base.js",

        #All grid navigation  plugin support
        "ext/ux/SlidingPager.js",

        #Main window tabs plugin support
        "ext/ux/TabScrollerMenu.js"
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
            u"ext/ebs/locale/" + LANGUAGE_CODE + u".js",
            u"ext/ebs/locale/main_menu." + LANGUAGE_CODE + u".0.js",
            u"ext/ebs/base_components.js",
            u"ext/ebs/application.js",
            u"ext/ebs/datastore.js",
    # Application components
            u"ext/ebs/components/admin_accounts_list.js",
            u"ext/ebs/components/admin_nasses_list.js",
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



try:
    from settings_local import *
except ImportError:
    pass
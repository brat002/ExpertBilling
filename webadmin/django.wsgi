import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'ebscab.settings'
#path = '/opt/local/django'
#if path not in sys.path:
sys.path.append('/opt/ebs/web/')
sys.path.append('/opt/ebs/web/ebscab/')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

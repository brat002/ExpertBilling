import os
import sys

sys.stdout = sys.stderr

import site
site.addsitedir('/opt/ebs/venv/lib/python2.6/site-packages')
site.addsitedir('/opt/ebs/venv/lib/python2.7/site-packages')


os.environ['DJANGO_SETTINGS_MODULE'] = 'ebscab.settings'
#path = '/opt/local/django'
#if path not in sys.path:
sys.path.append('/opt/ebs/web/')
sys.path.append('/opt/ebs/web/ebscab/')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

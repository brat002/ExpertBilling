"""
WSGI config for inline_radio_select project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import site
import sys

from django.core.wsgi import get_wsgi_application

sys.stdout = sys.stderr

sys.path.append('/opt/ebs/web/')
sys.path.append('/opt/ebs/web/ebscab/')
sys.path.append('/opt/ebs/data/workers/')

site.addsitedir('/opt/ebs/venv/lib/python2.6/site-packages')
site.addsitedir('/opt/ebs/venv/lib/python2.7/site-packages')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inline_radio_select.settings")

application = get_wsgi_application()

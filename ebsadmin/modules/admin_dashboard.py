# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2.config import RequestConfig
from object_log.models import LogItem


from billservice.models import Account

log = LogItem.objects.log_action

    
@login_required
@render_to('ebsadmin/admin_dashboard.html')
def admin_dashboard(request):
 
    accounts_count = Account.objects.count()
    return { 'accounts_count':accounts_count, } 


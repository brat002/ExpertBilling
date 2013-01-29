# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem
from django.contrib import messages

from billservice.models import Account
from billservice.helpers import systemuser_required
log = LogItem.objects.log_action

    
@systemuser_required
@render_to('ebsadmin/admin_dashboard.html')
def admin_dashboard(request):
 
    accounts_count = Account.objects.count()
    return { 'accounts_count':accounts_count, } 


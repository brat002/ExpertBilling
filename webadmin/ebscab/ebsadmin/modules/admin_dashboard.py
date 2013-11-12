# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem
from django.contrib import messages

from billservice.models import Account, SystemUser, Transaction, RegistrationRequest
from billservice.helpers import systemuser_required
from ebsadmin.tables import CommentTable
from ebsadmin.models import Comment
from radius.models import ActiveSession
from django.db.models import Q
log = LogItem.objects.log_action
import datetime
    
@systemuser_required
@render_to('ebsadmin/admin_dashboard.html')
def admin_dashboard(request):
 
    accounts_count = Account.objects.count()
    res = Comment.objects.all().order_by('-created')
    table = CommentTable(res)

    table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else True).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    
    sessions_count = ActiveSession.objects.filter(session_status='ACTIVE').count()
    systemusers_count = SystemUser.objects.all().count()
    
    accounts_today = Account.objects.filter(created__gte=datetime.datetime.now()-datetime.timedelta(seconds=86400)).count()
    transactions_today = Transaction.objects.filter(created__gte=datetime.datetime.now()-datetime.timedelta(seconds=86400)).count()
    
    accounts_minus = Account.objects.filter(ballance__lte=0).count()
    accounts_plus = Account.objects.filter(ballance__gt=0).count()
    
    accounts_inactive = Account.objects.filter(~Q(status = 1)).count()
    
    registrationrequest_count= RegistrationRequest.objects.all().count()
    
    return { 'accounts_count':accounts_count, 
            'comment_table': table, 
            'sessions_count': sessions_count, 
            'systemusers_count': systemusers_count,
            'accounts_today': accounts_today,
            'transactions_today': transactions_today,
            'accounts_minus': accounts_minus,
            'accounts_plus': accounts_plus,
            'accounts_inactive': accounts_inactive,
            'registrationrequest_count': registrationrequest_count
            } 


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
from ebsadmin.tables import CommentTable
from ebsadmin.models import Comment

log = LogItem.objects.log_action

    
@systemuser_required
@render_to('ebsadmin/admin_dashboard.html')
def admin_dashboard(request):
 
    accounts_count = Comment.objects.count()
    res = Comment.objects.all().order_by('-created')
    table = CommentTable(res)

    table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else True).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    
    return { 'accounts_count':accounts_count, 'comment_table': table} 


# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem
from django.db.models import Sum, Min, Max
from ebsadmin.tables import MessageTable
from billservice.forms import SearchSmsForm
from sendsms.models import Message
from django.contrib import messages
log = LogItem.objects.log_action
from billservice.helpers import systemuser_required
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _

@systemuser_required
@render_to('ebsadmin/sms_list.html')
def sms(request):
        
    if  not (request.user.account.has_perm('billservice.view_news')):
        messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')


    if request.GET: 
        data = request.GET

        #pageitems = 100
        form = SearchSmsForm(data)
        if data and form.is_valid():
            
            phone = form.cleaned_data.get('phone')
            accounts = form.cleaned_data.get('accounts')
            backend = form.cleaned_data.get('backend')
            publish_date = form.cleaned_data.get('publish_date')
            
            sended_from = form.cleaned_data.get('sended_from')
            sended_to = form.cleaned_data.get('sended_to')

            
            
            query = Message.objects.all()
            
            if phone:
                query = query.filter(to__istartswith=phone)

            if accounts:
                query = query.filter(account__in=accounts)

            if backend:
                query = query.filter(backend=backend)

            if publish_date:
                query = query.filter(publish_date=publish_date)
                
            if sended_from:
                query = query.filter(sended=sended_from)

            if sended_to:
                query = query.filter(sended=sended_to)

            res = query
            table = MessageTable(res)
            table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else {"per_page": request.COOKIES.get("ebs_per_page")}).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)
            
            return {"table": table,  'form':form, 'resultTab':True}   
    
        else:
            return {'status':False, 'form':form}
    else:
        form = SearchSmsForm()
        return { 'form':form}   

@ajax_request
@systemuser_required
def sms_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_news')):
        return {'status':False, 'message': _(u'У вас нет прав на удаление новостей')}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = Message.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": _(u"Указанное сообщение не найдено %s") % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "SMS not found"} 
    
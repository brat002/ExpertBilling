# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import AccountPrepaysTraficTable
from billservice.forms import AccountPrepaysTraficSearchForm, AccountPrepaysTraficForm
from billservice.models import AccountPrepaysTrafic
from django.contrib import messages
log = LogItem.objects.log_action
from billservice.helpers import systemuser_required



@systemuser_required
@render_to('ebsadmin/accountprepaystraffic_list.html')
def accountprepaystraffic(request):
        
    if  not (request.user.account.has_perm('billservice.view_accountprepaystraffic')):
        messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    
    if request.method=='GET' and request.GET: 
        data = request.GET

        #pageitems = 100
        form = AccountPrepaysTraficSearchForm(data)
        if form.is_valid():
            
            account = form.cleaned_data.get('account')
            group = form.cleaned_data.get('group')
            current = form.cleaned_data.get('current')
            tariff = form.cleaned_data.get('tariff')
            date_start = form.cleaned_data.get('date_start')
            date_end = form.cleaned_data.get('date_end')

            res = AccountPrepaysTrafic.objects.all().order_by('account_tarif__account', 'current')
            if account:
                res = res.filter(account_tarif__account__id__in=account)

            if group:
                res = res.filter(prepaid_traffic__group__in=group)

            if tariff:
                res = res.filter(account_tarif__tarif__in=tariff)
                
            if current:
                res = res.filter(current=current)
                
            if date_start:
                res = res.filter(datetime__gte=date_start)
            if date_end:
                res = res.filter(datetime__lte=date_end)
                
            table = AccountPrepaysTraficTable(res)
            table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else {"per_page": request.COOKIES.get("ebs_per_page")}).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)
            
            return {"table": table,  'form':form, 'resultTab':True}   
    
        else:
            return {'status':False, 'form':form}
    else:
        form = AccountPrepaysTraficSearchForm()
        return { 'form':form}   

@systemuser_required
@render_to('ebsadmin/accountprepaystraffic_edit.html')
def accountprepaystraffic_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 

        if id:
            model = AccountPrepaysTrafic.objects.get(id=id)
            form = AccountPrepaysTraficForm(request.POST, instance=model) 
            if  not (request.user.account.has_perm('billservice.change_accountprepaystraffic')):
                messages.error(request, u'У вас нет прав на редактирование предоплаченного трафика', extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = AccountPrepaysTraficForm(request.POST) 
            if  not (request.user.account.has_perm('billservice.add_accountprepaystraffic')):
                messages.error(request, u'У вас нет прав на добавление предоплаченного трафика', extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)



        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.account.has_perm('billservice.view_accountprepaystraffic')):
                messages.error(request, u'У вас нет прав на доступ в этот раздел.', extra_tags='alert-danger')
                return {}

            item = AccountPrepaysTrafic.objects.get(id=id)
            
            form = AccountPrepaysTraficForm(instance=item)
        else:
            form = AccountPrepaysTraficForm()

    return { 'form':form, 'status': False} 

@ajax_request
@systemuser_required
def accountprepaystraffic_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_accountprepaystrafic')):
        return {'status':False, 'message': u'У вас нет прав на удаление предоплаченного NetFlow трафика'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = AccountPrepaysTrafic.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная запись не найдена %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "AccountPrepaysTrafic not found"} 
    
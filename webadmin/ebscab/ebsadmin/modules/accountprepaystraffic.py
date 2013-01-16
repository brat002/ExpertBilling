# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import AccountPrepaysTraficTable
from billservice.forms import AccountPrepaysTraficSearchForm, AccountPrepaysTraficForm
from billservice.models import AccountPrepaysTrafic

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/accountprepaystraffic_list.html')
def accountprepaystraffic(request):
        
    if  not (request.user.account.has_perm('billservice.delete_accountprepaystime')):
        return {'status': False}
    
    if request.method=='GET' and request.GET: 
        data = request.GET

        #pageitems = 100
        form = AccountPrepaysTraficSearchForm(data)
        if form.is_valid():
            
            account = form.cleaned_data.get('account')
            group = form.cleaned_data.get('group')
            current = form.cleaned_data.get('current')
            tariff = form.cleaned_data.get('tariff')
            daterange = form.cleaned_data.get('daterange') or []
            start_date, end_date = None, None
            if daterange:
                start_date = daterange[0]
                end_date = daterange[1]
            
            
            
            res = AccountPrepaysTrafic.objects.all().order_by('account_tarif__account', 'current')
            if account:
                res = res.filter(account_tarif__account__id__in=account)

            if group:
                res = res.filter(prepaid_traffic__group__in=group)

            if tariff:
                res = res.filter(account_tarif__tarif__in=tariff)
                
            if current:
                res = res.filter(current=current)
                
            if start_date:
                res = res.filter(datetime__gte=start_date)
            if end_date:
                res = res.filter(datetime__lte=end_date)
                
            table = AccountPrepaysTraficTable(res)
            table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)
            
            return {"table": table,  'form':form, 'resultTab':True}   
    
        else:
            return {'status':False, 'form':form}
    else:
        form = AccountPrepaysTraficSearchForm()
        return { 'form':form}   

@login_required
@render_to('ebsadmin/accountprepaystraffic_edit.html')
def accountprepaystraffic_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 

        if id:
            model = AccountPrepaysTrafic.objects.get(id=id)
            form = AccountPrepaysTraficForm(request.POST, instance=model) 
            if  not (request.user.account.has_perm('billservice.change_accountprepaystraffic')):
                return {'status':False, 'message': u'У вас нет прав на редактирование предоплаченного времени'}
        else:
            form = AccountPrepaysTraficForm(request.POST) 
        if  not (request.user.account.has_perm('billservice.add_accountprepaystraffic')):
            return {'status':False, 'message': u'У вас нет прав на добавление предоплаченного времени'}


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
            if  not (request.user.has_perm('billservice.view_accountprepaystraffic')):
                return {'status':False}

            item = AccountPrepaysTrafic.objects.get(id=id)
            
            form = AccountPrepaysTraficForm(instance=item)
        else:
            form = AccountPrepaysTraficForm()

    return { 'form':form, 'status': False} 

@ajax_request
@login_required
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
    
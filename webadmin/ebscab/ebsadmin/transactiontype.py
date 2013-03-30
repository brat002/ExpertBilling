# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from billservice.helpers import systemuser_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from tables import TransactionTypeTable

from billservice.forms import TransactionTypeForm
from billservice.models import TransactionType
from django.contrib import messages
log = LogItem.objects.log_action
from django.utils.translation import ugettext_lazy as _


@systemuser_required
@render_to('ebsadmin/transactiontype_list.html')
def transactiontype(request):
    if  not (request.user.account.has_perm('billservice.view_transactiontype')):
        messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    res = TransactionType.objects.all()
    table = TransactionTypeTable(res)
    table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else {"per_page": request.COOKIES.get("ebs_per_page")}).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    return {"table": table} 
    
@systemuser_required
@render_to('ebsadmin/transactiontype_edit.html')
def transactiontype_edit(request):

    id = request.GET.get("id")
    item = None
    if request.method == 'POST': 
        if id:
            if  not (request.user.account.has_perm('billservice.change_transactiontype')):
                messages.error(request, _(u'У вас нет прав на редактирование типов проводок'), extra_tags='alert-danger')
                return {}

            item = TransactionType.objects.get(id=id)
            form = TransactionTypeForm(request.POST, instance=item)
        else:
            if  not (request.user.account.has_perm('billservice.add_transactiontype')):
                messages.error(request, _(u'У вас нет прав на создание типов проводок'), extra_tags='alert-danger')
                return {}
            form = TransactionTypeForm(request.POST)

            


        
        if form.is_valid():
 
            model = form.save(commit=False)
            model.save()
            form.save_m2m()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, _(u'Тип проводки успешно сохранён.'), extra_tags='alert-success')
            return HttpResponseRedirect(reverse("transactiontype"))
        else:
            messages.error(request, _(u'Ошибка при сохранении типа проводки.'), extra_tags='alert-danger')
            return {'form':form,  'item': item} 
    else:
        id = request.GET.get("id")
        if  not (request.user.account.has_perm('billservice.view_transactiontype')):
            messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
            return HttpResponseRedirect(reverse("transactiontype"))

        if id:
            item = TransactionType.objects.get(id=id)
            form = TransactionTypeForm(instance=item)
        else:
            form = TransactionTypeForm()
   
    return { 'form':form, 'item': item} 

@ajax_request
@systemuser_required
def transactiontype_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_transactiontype')):
        return {'status':False, 'message': _(u'У вас нет прав на удаление типов проводок')}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = TransactionType.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": _(u"Указанный тип не найден %s") % str(e)}
        if item.is_deletable==False:
            return {"status": False, "message": _(u"Выбранный тип списания не может быть удалён")}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, _(u'Тип проводки успешно удалён.'), extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, _(u'Ошибка при удалении типа проводки.'), extra_tags='alert-danger')
        return {"status": False, "message": "TransactionType not found"} 
    
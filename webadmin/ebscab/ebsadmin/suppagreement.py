# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from tables import SuppAgreementTable

from billservice.forms import SuppAgreementForm
from billservice.models import SuppAgreement
from django.contrib import messages
log = LogItem.objects.log_action
from billservice.helpers import systemuser_required
from django.utils.translation import ugettext_lazy as _

@systemuser_required
@render_to('ebsadmin/suppagreement_list.html')
def suppagreement(request):
    if  not (request.user.account.has_perm('billservice.view_suppagreement')):
        messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    
    res = SuppAgreement.objects.all().extra(select={'accounts_count':'SELECT count(*) FROM billservice_accountsuppagreement WHERE suppagreement_id=billservice_suppagreement.id'})
    table = SuppAgreementTable(res)
    table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else True).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    return {"table": table} 
    
@systemuser_required
@render_to('ebsadmin/suppagreement_edit.html')
def suppagreement_edit(request):

    id = request.GET.get("id")
    item = None
    if request.method == 'POST': 
        if id:
            item = SuppAgreement.objects.get(id=id)
            form = SuppAgreementForm(request.POST, instance=item)
        else:
            form = SuppAgreementForm(request.POST)
        if id:
            if  not (request.user.account.has_perm('billservice.edit_suppagreement')):
                messages.error(request, _(u'У вас нет прав на редактирование видов дополнительных соглашений'), extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            
            if  not (request.user.account.has_perm('billservice.edit_suppagreement')):
                messages.error(request, _(u'У вас нет прав на создание видов дополнительных соглашений'), extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)


        
        if form.is_valid():
 
            model = form.save(commit=False)
            model.save()
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, _(u'Вид дополнительного соглашения сохранён.'), extra_tags='alert-success')
            return HttpResponseRedirect(reverse("suppagreement"))
        else:
            messages.error(request, _(u'Ошибка при сохранении.'), extra_tags='alert-danger')
            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")
        if  not (request.user.account.has_perm('billservice.view_suppagreement')):
            messages.error(request, _(u'У вас нет прав на доступ в этот раздел.'), extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        if id:
            item = SuppAgreement.objects.get(id=id)
            form = SuppAgreementForm(instance=item)
        else:
            form = SuppAgreementForm()
   
    return { 'form':form, 'item': item} 

@ajax_request
@systemuser_required
def suppagreement_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_suppagreement')):
        return {'status':False, 'message': _(u'У вас нет прав на удаление видов доп. соглащений')}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = SuppAgreement.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": _(u"Указанная запись не найдена %s") % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, _(u'Запись успешно удалена.'), extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, _(u'Ошибка при удалении записи.'), extra_tags='alert-danger')
        return {"status": False, "message": "SuppAgreement not found"} 
    
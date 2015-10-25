# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem

from ebsadmin.tables import RegistrationRequestTable

from billservice.models import RegistrationRequest
from django.contrib import messages
log = LogItem.objects.log_action
from billservice.helpers import systemuser_required
from django.utils.translation import ugettext_lazy as _

@systemuser_required
@render_to('ebsadmin/common/list.html')
def registrationrequest(request):

    if  not (request.user.account.has_perm('billservice.view_registrationrequest')):
        messages.error(request, _(u'У вас нет прав на просмотр запросов на подключение.'), extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    res = RegistrationRequest.objects.all()
    table = RegistrationRequestTable(res)
    table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else True).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
            
    return {
        "list_url": reverse('registrationrequest'),
        "list_header": _(u'Запросы на подключение'),
        "table": table
    }
    


@ajax_request
@systemuser_required
def registrationrequest_delete(request):
    if  not (request.user.account.has_perm('billservice.delete_registrationrequest')):
        return {'status':False, 'message': _(u'У вас нет прав на удаление запросов на подключение')}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = RegistrationRequest.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": _(u"Указанный запрос на регистрацию не найден %s") % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request, _(u'Запрос на регистрацию успешно удалён.'), extra_tags='alert-success')
        return {"status": True}
    else:
        messages.error(request, _(u'При удалении запроса на регистрацию возникли ошибки.'), extra_tags='alert-danger')
        return {"status": False, "message": "RegistrationRequest not found"} 
    
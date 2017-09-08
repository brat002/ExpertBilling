# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import IPPoolForm
from billservice.utils import systemuser_required
from billservice.models import IPPool
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.utils.decorators import render_to, ajax_request
from object_log.models import LogItem

from ebsadmin.tables import IPPoolTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/common/list.html')
def ippool(request):
    if not (request.user.account.has_perm('billservice.view_ippool')):
        messages.error(
            request,
            _(u'У вас нет прав на доступ в этот раздел.'),
            extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    res = IPPool.objects.all()
    table = IPPoolTable(res)
    table_to_report = RequestConfig(
        request,
        paginate=False if request.GET.get('paginate') == 'False' else True)
    table_to_report = table_to_report.configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    return {
        "list_url": reverse('ippool'),
        "list_header": _(u'IP пул'),
        "add_btn_url": reverse('ippool_edit'),
        "table": table
    }


@systemuser_required
@render_to('ebsadmin/common/edit_form.html')
def ippool_edit(request):
    id = request.GET.get("id")
    item = None
    if request.method == 'POST':
        if id:
            item = IPPool.objects.get(id=id)
            form = IPPoolForm(request.POST, instance=item)
        else:
            form = IPPoolForm(request.POST)
        if id:
            if not (request.user.account.has_perm('billservice.change_ippool')):
                messages.error(
                    request,
                    _(u'У вас нет прав на редактирование IP пулов'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:

            if not (request.user.account.has_perm('billservice.add_ippool')):
                messages.error(
                    request,
                    _(u'У вас нет прав на создание IP пулов'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        if form.is_valid():

            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(request,
                             _(u'IP пул сохранён.'),
                             extra_tags='alert-success')
            return HttpResponseRedirect(reverse("ippool"))
        else:
            messages.error(request,
                           _(u'Ошибка при сохранении IP пула.'),
                           extra_tags='alert-danger')
            return {
                'form': form,
                'status': False
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm('billservice.view_ippool')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        if id:
            item = IPPool.objects.get(id=id)
            form = IPPoolForm(instance=item)
        else:
            form = IPPoolForm()

    return {
        'form': form,
        'item': item,
        'list_url': reverse('ippool'),
        'list_label': _(u'IP пулы'),
        'form_action_url': reverse('ippool_edit'),
        'form_legend': _(u'Параметры IP пула')
    }


@ajax_request
@systemuser_required
def ippool_delete(request):
    if not (request.user.account.has_perm('billservice.delete_ippool')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление IP пулов')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = IPPool.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанный пул не найден %s") % str(e)
            }

        log('DELETE', request.user, item)

        item.delete()
        messages.success(request,
                         _(u'IP пул успешно удалён.'),
                         extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(request,
                       _(u'Ошибка при удалении IP пула.'),
                       extra_tags='alert-danger')
        return {
            "status": False,
            "message": "IPPool not found"
        }

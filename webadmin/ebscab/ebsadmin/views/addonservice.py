# -*-coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import AddonServiceForm
from billservice.utils import systemuser_required
from billservice.models import AddonService
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import render_to, ajax_request
from object_log.models import LogItem

from ebsadmin.tables import AddonServiceTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/common/list.html')
def addonservice(request):
    if not (request.user.account.has_perm('billservice.view_addonservice')):
        messages.error(
            request,
            _(u'У вас нет прав на доступ в этот раздел.'),
            extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    res = AddonService.objects.all()
    table = AddonServiceTable(res)
    table_to_report = RequestConfig(
        request,
        paginate=False if request.GET.get('paginate') == 'False' else True)
    table_to_report = table_to_report.configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    return {
        "list_url": reverse('addonservice'),
        "list_header": _(u'Подключаемые услуги'),
        "add_btn_url": reverse('addonservice_edit'),
        "table": table
    }


@systemuser_required
@render_to('ebsadmin/addonservice/edit.html')
def addonservice_edit(request):
    account = None
    id = request.GET.get("id")
    item = None
    if request.method == 'POST':
        if id:
            item = AddonService.objects.get(id=id)
            form = AddonServiceForm(request.POST, instance=item)
        else:
            form = AddonServiceForm(request.POST)

        if id:
            if not (request.user.account.has_perm(
                    'billservice.change_addonservice')):
                messages.error(
                    request,
                    _(u'У вас нет прав на редактирование подключаемых услуг'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        if not (request.user.account.has_perm('billservice.add_addonservice')):
            messages.error(
                request,
                _(u'У вас нет прав на создание подключаемых услуг'),
                extra_tags='alert-danger')
            return HttpResponseRedirect(request.path)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)

            messages.success(
                request,
                _(u'Подключаемая услуга сохранена.'),
                extra_tags='alert-success')
            return HttpResponseRedirect(reverse("addonservice"))
        else:
            messages.error(
                request,
                _(u'Ошибка при сохранении подключаемой услуги.'),
                extra_tags='alert-danger')
            return {
                'form': form,
                'item': item
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm(
                'billservice.view_addonservice')):
            messages.error(
                request,
                _(u'У вас нет прав на доступ в этот раздел.'),
                extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        if id:
            item = AddonService.objects.get(id=id)
            form = AddonServiceForm(instance=item)
        else:
            form = AddonServiceForm()  # An unbound form
    return {
        'form': form,
        'item': item
    }


@ajax_request
@systemuser_required
def addonservice_delete(request):
    if not (request.user.account.has_perm('billservice.delete_addonservice')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление подключаемых услуг')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = AddonService.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанная услуга не найдена %s") % str(e)
            }

        log('DELETE', request.user, item)

        item.delete()
        messages.success(
            request,
            _(u'Подключаемая услуга удалена.'),
            extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(
            request,
            _(u'Ошибка при удалении подключаемой услуги.'),
            extra_tags='alert-danger')
        return {
            "status": False,
            "message": "TransactionType not found"
        }

# -*- coding: utf-8 -*-

import datetime

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import (
    AccessParametersForm,
    AccessParametersTariffForm,
    TariffForm
)
from billservice.helpers import systemuser_required
from billservice.models import Tariff
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import ajax_request, render_to
from object_log.models import LogItem

from ebsadmin.tables import TariffTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/tariff_list.html')
def tariff(request):
    if not (request.user.account.has_perm('billservice.view_tariff')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    res = Tariff.objects.all().extra(
        select={
            'accounts_count': '''\
SELECT count(*) FROM billservice_accounttarif
WHERE tarif_id=billservice_tariff.id AND id in (SELECT max(id) \
FROM billservice_accounttarif WHERE  datetime<now() GROUP BY account_id \
HAVING max(datetime)<now())'''
        })
    table = TariffTable(res)
    table_to_report = RequestConfig(
        request,
        paginate=False if request.GET.get('paginate') == 'False' else True)
    table_to_report = table_to_report.configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)

    return {
        "table": table
    }


@systemuser_required
@render_to('ebsadmin/tariff_edit_general.html')
def tariff_edit(request):
    item = None
    tariff = None
    if request.method == 'POST':
        id = request.POST.get("id")
        ap_id = request.POST.get("ap-id")
        if id:
            tariff = Tariff.objects.get(id=id)
            form = TariffForm(request.POST, instance=tariff)
            accessparameters_form = AccessParametersTariffForm(
                request.POST, instance=tariff.access_parameters, prefix="ap")
        else:
            form = TariffForm(request.POST)
            accessparameters_form = AccessParametersTariffForm(
                request.POST, prefix="ap")

        if id:
            if not (request.user.account.has_perm(
                    'billservice.change_tariff')):
                messages.error(
                    request,
                    _(u'У вас нет прав на редактирование тарифных планов'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        else:
            if not (request.user.account.has_perm('billservice.add_tariff')):
                messages.error(
                    request,
                    _(u'У вас нет прав на создание тарифных планов'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        if form.is_valid() and accessparameters_form.is_valid():
            ap = accessparameters_form.save(commit=False)
            ap.save()
            model = form.save(commit=False)
            model.access_parameters = ap
            model.save()
            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(request,
                             _(u'Тарифный план сохранён.'),
                             extra_tags='alert-success')
            return HttpResponseRedirect(
                "%s?id=%s" % (reverse("tariff_edit"), model.id))
        else:
            messages.error(
                request,
                _(u'Во время сохранения тарифного плана возникли ошибки.'),
                extra_tags='alert-danger')
            return {
                'form': form,
                "access_parameters": accessparameters_form,
                'status': False
            }
    else:
        id = request.GET.get("id")
        if id:
            if not (request.user.account.has_perm('billservice.view_tariff')):
                return {
                    'status': True
                }

            tariff = Tariff.objects.get(id=id)
            form = TariffForm(instance=tariff)
            accessparameters_form = AccessParametersForm(
                instance=tariff.access_parameters, prefix="ap")
        else:
            form = TariffForm()
            accessparameters_form = AccessParametersForm(prefix="ap")

    return {
        'form': form,
        'tariff': tariff,
        "access_parameters": accessparameters_form,
        'active': 'general'
    }


@ajax_request
@systemuser_required
def tariff_delete(request):
    if not (request.user.account.has_perm('billservice.delete_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление тарифных планов')
        }

    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = Tariff.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанный тарифный план не найден %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request,
                         _(u'Тарифный план удалён.'),
                         extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(request,
                       _(u'При удалении тарифного плана произошла ошибка.'),
                       extra_tags='alert-danger')
        return {
            "status": False,
            "message": "tariff not found"
        }


@ajax_request
@systemuser_required
def tariff_hide(request):
    if not (request.user.account.has_perm('billservice.delete_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление тарифных планов')
        }

    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = Tariff.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанная запись не найдена %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.deleted = datetime.datetime.now()
        item.save()
        messages.success(request,
                         _(u'Запись успешно скрыта.'),
                         extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(request,
                       _(u'Ошибка при сокрытии записи.'),
                       extra_tags='alert-danger')
        return {
            "status": False,
            "message": "Tariff not found"
        }

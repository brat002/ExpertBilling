# -*- coding: utf-8 -*-

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import TrafficLimitForm
from billservice.utils import systemuser_required
from billservice.models import Tariff, TrafficLimit
from ebscab.lib.decorators import ajax_request, render_to
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from object_log.models import LogItem

from ebsadmin.tables import TrafficLimitTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/tariff_trafficlimit.html')
def trafficlimit(request):
    if not (request.user.account.has_perm('billservice.view_tariff')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    item = None
    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    items = TrafficLimit.objects.filter(tarif__id=tariff_id)
    tariff = Tariff.objects.get(id=tariff_id)
    if items:
        table = TrafficLimitTable(items)
        RequestConfig(request, paginate=False).configure(table)
    else:
        table = TrafficLimitTable({})

    return {
        'formset': None,
        'table': table,
        'tariff': tariff,
        'active': 'trafficlimit'
    }


@systemuser_required
@render_to('ebsadmin/trafficlimit_edit.html')
def trafficlimit_edit(request):
    item = None
    if request.method == 'POST':
        if not (request.user.account.has_perm('billservice.change_tariff')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на редактирование тарифного плана')
            }
        id = request.POST.get("id")
        if id:
            model = TrafficLimit.objects.get(id=id)
            form = TrafficLimitForm(request.POST, instance=model)
        else:
            form = TrafficLimitForm(request.POST)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(request,
                             _(u'Лимит трафика успешно сохранён.'),
                             extra_tags='alert-success')
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(
                request,
                _(u'При сохранении лимита трафика возникли ошибки.'),
                extra_tags='alert-danger')
            return {
                'form': form,
                'status': False
            }
    else:
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        if id:
            if not (request.user.account.has_perm('billservice.view_tariff')):
                messages.error(request,
                               _(u'У вас нет прав на доступ в этот раздел.'),
                               extra_tags='alert-danger')
                return {}

            item = TrafficLimit.objects.get(id=id)
            form = TrafficLimitForm(instance=item)
        else:
            form = TrafficLimitForm(initial={'tarif': tariff_id})

    return {
        'formset': None,
        'form': form
    }


@ajax_request
@systemuser_required
def trafficlimit_delete(request):
    if not (request.user.account.has_perm('billservice.change_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на редактирование '
                         u'тарифного плана')
        }

    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = TrafficLimit.objects.get(id=id)
            item.speedlimit.delete()
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанное правило не найдено %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request,
                         _(u'Лимит трафика удален.'),
                         extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(request,
                       _(u'При удалении лимита трафика произошла ошибка.'),
                       extra_tags='alert-danger')
        return {
            "status": False,
            "message": "TrafficLimit not found"
        }

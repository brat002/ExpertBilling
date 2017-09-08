# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import (
    TrafficTransmitNodeForm,
    TrafficTransmitServiceForm
)
from billservice.utils import systemuser_required
from billservice.models import (
    PrepaidTraffic,
    Tariff,
    TrafficTransmitNodes,
    TrafficTransmitService
)
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from ebscab.utils.decorators import ajax_request, render_to
from object_log.models import LogItem

from ebsadmin.tables import PrepaidTrafficTable, TrafficTransmitNodesTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/tariff_traffictransmitservice.html')
def traffictransmitservice(request):
    if not (request.user.account.has_perm('billservice.view_tariff')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    item = None
    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    tariff = Tariff.objects.get(id=tariff_id)
    prepaidtable = None

    if tariff_id:
        if request.method == 'POST':
            if not (request.user.account.has_perm(
                    'billservice.change_tariff')):
                return {
                    'status': False,
                    'message': _(u'У вас нет прав на редактирование '
                                 u'тарифного плана')
                }
            id = request.POST.get("id")
            if id:
                model = TrafficTransmitService.objects.get(id=id)
                form = TrafficTransmitServiceForm(request.POST, instance=model)
            else:
                form = TrafficTransmitServiceForm(request.POST)

            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                item = model
                tariff.traffic_transmit_service = model
                tariff.save()

                if id:
                    log('EDIT', request.user, model)
                else:
                    log('CREATE', request.user, model)
                messages.success(
                    request,
                    _(u'Услуга тарификации трафика успешно сохранена.'),
                    extra_tags='alert-success')
                return HttpResponseRedirect(
                    "%s?tariff_id=%s" %
                    (reverse("tariff_traffictransmitservice"), tariff.id))
            else:
                messages.error(
                    request,
                    _(u'При сохранении услуги тарификации трафика '
                      u'произошла ошибка.'),
                    extra_tags='alert-danger')
        else:
            item = tariff.traffic_transmit_service

        form = TrafficTransmitServiceForm(instance=item)
        items = TrafficTransmitNodes.objects.filter(
            traffic_transmit_service=item)
        table = TrafficTransmitNodesTable(items)
        RequestConfig(request, paginate=False).configure(table)
        prepaidtable = PrepaidTrafficTable(
            PrepaidTraffic.objects.filter(traffic_transmit_service=item))
        RequestConfig(request, paginate=False).configure(prepaidtable)
    else:
        form = TrafficTransmitServiceForm()

    return {
        'formset': None,
        'table': table,
        'tariff': tariff,
        'item': item,
        'form': form,
        'prepaidtraffic_table': prepaidtable,
        'active': 'tts'
    }


@ajax_request
@systemuser_required
def traffictransmitservice_delete(request):
    if not (request.user.account.has_perm('billservice.change_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на редактирование '
                         u'тарифного плана')
        }

    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = TrafficTransmitService.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанная услуга не найдена %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request,
                         _(u'Услуга NetFlow тарификации трафика удалена.'),
                         extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(request,
                       _(u'При удалении NetFlow тарификации трафика произошла ошибка.'),
                       extra_tags='alert-danger')
        return {
            "status": False,
            "message": "TrafficTransmitService not found"
        }


@ajax_request
@systemuser_required
def traffictransmitnode_delete(request):
    if not (request.user.account.has_perm('billservice.change_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на редактирование '
                         u'тарифного плана')
        }

    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = TrafficTransmitNodes.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанное правило не найдено %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        messages.success(
            request,
            _(u'Настройка NetFlow тарификации трафика удалёна.'),
            extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(
            request,
            _(u'При удалении настройки NetFlow тарификации трафика '
              u'произошла ошибка.'),
            extra_tags='alert-danger')
        return {
            "status": False,
            "message": "TrafficTransmitNodes not found"
        }


@systemuser_required
@render_to('ebsadmin/tariff_traffictransmitnode_edit.html')
def traffictransmitnode_edit(request):
    item = None
    if request.method == 'POST':
        if not (request.user.account.has_perm('billservice.change_tariff')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на редактирование '
                             u'тарифного плана')
            }

        id = request.POST.get("id")
        if id:
            model = TrafficTransmitNodes.objects.get(id=id)
            form = TrafficTransmitNodeForm(request.POST, instance=model)
        else:
            form = TrafficTransmitNodeForm(request.POST)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(
                request,
                _(u'Настройки NetFlow тарификации трафика успешно сохранены.'),
                extra_tags='alert-success')
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(
                request,
                _(u'При сохранении настроек NetFlow тарификации трафика '
                  u'произошла ошибка.'),
                extra_tags='alert-danger')
            return {
                'form': form,
                'status': False
            }
    else:
        if not (request.user.account.has_perm('billservice.view_tariff')):
            return {
                'status': False
            }
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        tts = None

        if tariff_id:
            tts = Tariff.objects.get(id=tariff_id).traffic_transmit_service

        if id:
            item = TrafficTransmitNodes.objects.get(id=id)
            form = TrafficTransmitNodeForm(instance=item)
        elif tts:
            form = TrafficTransmitNodeForm(
                initial={"traffic_transmit_service": tts})

        else:
            form = TrafficTransmitNodeForm(
                initial={"traffic_transmit_service": tts})

    return {
        'formset': None,
        'form': form
    }

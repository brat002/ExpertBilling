# -*- coding: utf-8 -*-

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import (
    RadiusTrafficForm,
    TimeAccessNodeForm,
    TimeAccessServiceForm
)
from billservice.utils import systemuser_required
from billservice.models import Tariff, TimeAccessNode, TimeAccessService
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from ebscab.utils.decorators import ajax_request, render_to
from object_log.models import LogItem

from ebsadmin.tables import TimeAccessNodeTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/tariff_timeaccessnode_edit.html')
def timeaccessnode_edit(request):
    item = None
    if request.method == 'POST':
        id = request.POST.get("id")
        if not (request.user.account.has_perm('billservice.change_tariff')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на редактирование '
                             u'тарифного плана')
            }

        if id:
            model = TimeAccessNode.objects.get(id=id)
            form = TimeAccessNodeForm(request.POST, instance=model)
        else:
            form = TimeAccessNodeForm(request.POST)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            item = model
            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(
                request,
                _(u'Правило тарификации времени успешно сохранено.'),
                extra_tags='alert-success')
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(
                request,
                _(u'При сохранении правила тарификации времени '
                  u'произошла ошибка.'),
                extra_tags='alert-danger')
            return {
                'form': form,
                'status': False
            }
    else:
        if not (request.user.account.has_perm('billservice.view_tariff')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return {}
        id = request.GET.get("id")
        tariff_id = request.GET.get("tariff_id")
        time_access_service_id = request.GET.get("time_access_service_id")
        tts = None
        if time_access_service_id:
            tas = TimeAccessService.objects.get(id=time_access_service_id)
        if id:

            item = TimeAccessNode.objects.get(id=id)
            form = TimeAccessNodeForm(instance=item)
        elif tts:
            form = TimeAccessNodeForm(initial={"time_access_service": tas})

        else:
            form = TimeAccessNodeForm(initial={"time_access_service": tas})

    return {
        'item': item,
        'form': form
    }


@ajax_request
@systemuser_required
def timeaccessnode_delete(request):
    if not (request.user.account.has_perm('billservice.change_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на редактирование '
                         u'тарифного плана')
        }

    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = TimeAccessNode.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанное правило не найдено %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request,
                         _(u'Настройка тарификации времени удалена.'),
                         extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(
            request,
            _(u'При удалении настройки тарификации времени произошла ошибка.'),
            extra_tags='alert-danger')
        return {
            "status": False,
            "message": "TimeAccessNode not found"
        }


@systemuser_required
@render_to('ebsadmin/tariff_timeaccessservice.html')
def timeaccessservice(request):
    if not (request.user.account.has_perm('billservice.view_tariff')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    item = None
    id = request.GET.get("id")
    tariff_id = request.GET.get("tariff_id")
    tariff = Tariff.objects.get(id=tariff_id)
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
                model = TimeAccessService.objects.get(id=id)
                form = TimeAccessServiceForm(request.POST, instance=model)
            else:
                form = TimeAccessServiceForm(request.POST)

            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                item = model

                if id:
                    log('EDIT', request.user, model)
                else:
                    log('CREATE', request.user, model)

                tariff.time_access_service = item
                tariff.save()
                messages.success(
                    request,
                    _(u'Услуга RADIUS тарификации времени успешно сохранена.'),
                    extra_tags='alert-success')
            else:
                item = model
                messages.error(
                    request,
                    _(u'При сохранении услуги RADIUS тарификации времени '
                      u'произошла ошибка.'),
                    extra_tags='alert-danger')
        else:
            item = tariff.time_access_service
            form = TimeAccessServiceForm(instance=item)

        items = TimeAccessNode.objects.filter(time_access_service=item)
        table = TimeAccessNodeTable(items)
        RequestConfig(request, paginate=False).configure(table)

    else:
        form = RadiusTrafficForm()

    return {
        'table': table,
        'tariff': tariff,
        'item': item,
        'form': form,
        'active': 'timeaccess'
    }


@ajax_request
@systemuser_required
def timeaccessservice_delete(request):
    if not (request.user.account.has_perm('billservice.change_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на редактирование '
                         u'тарифного плана')
        }

    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = TimeAccessService.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанная услуга не найдена %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        messages.success(
            request,
            _(u'Услуга RADIUS тарификации времени удалена.'),
            extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(
            request,
            _(u'При удалении RADIUS тарификации времени произошла ошибка.'),
            extra_tags='alert-danger')
        return {
            "status": False,
            "message": "TimeAccessService not found"
        }

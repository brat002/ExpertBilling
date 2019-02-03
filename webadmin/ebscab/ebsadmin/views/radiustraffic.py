# -*- coding: utf-8 -*-

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import RadiusTrafficForm, RadiusTrafficNodeForm
from billservice.utils import systemuser_required
from billservice.models import RadiusTraffic, RadiusTrafficNode, Tariff
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from ebscab.utils.decorators import ajax_request, render_to
from object_log.models import LogItem

from ebsadmin.tables import RadiusTrafficNodeTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/tariff_radiustraffic.html')
def radiustraffic(request):
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
        if not (request.user.account.has_perm('billservice.tariff_view')):
            return {
                'status': True
            }

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
                model = RadiusTraffic.objects.get(id=id)
                form = RadiusTrafficForm(request.POST, instance=model)
            else:
                form = RadiusTrafficForm(request.POST)

            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                item = model

                if id:
                    log('EDIT', request.user, model)
                else:
                    log('CREATE', request.user, model)

                tariff.radius_traffic_transmit_service = item
                tariff.save()
                messages.success(
                    request,
                    _(u'Услуга RADIUS тарификации трафика успешно '
                      u'сохранена.'),
                    extra_tags='alert-success')
            else:
                item = model
                messages.error(
                    request,
                    _(u'При сохранении услуги RADIUS тарификации трафика '
                      u'произошла ошибка.'),
                    extra_tags='alert-danger')
        else:
            item = tariff.radius_traffic_transmit_service
            form = RadiusTrafficForm(instance=item)

        items = RadiusTrafficNode.objects.filter(radiustraffic=item)
        form = RadiusTrafficForm(instance=item)
        table = RadiusTrafficNodeTable(items)
        RequestConfig(request, paginate=False).configure(table)
    else:
        form = RadiusTrafficForm()

    return {
        'formset': None,
        'table': table,
        'tariff': tariff,
        'item': item,
        'form': form,
        'active': 'rts'
    }


@systemuser_required
@render_to('ebsadmin/tariff_radiustrafficnode_edit.html')
def radiustrafficnode_edit(request):
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
            model = RadiusTrafficNode.objects.get(id=id)
            form = RadiusTrafficNodeForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'billservice.change_radiustrafficnode')):
                return {
                    'status': False,
                    'message': _(u'У вас нет прав на редактирование '
                                 u'правил тарификации RADIUS трафика')
                }
        else:
            form = RadiusTrafficNodeForm(request.POST)
        if not (request.user.is_staff == True and
                request.user.account.has_perm(
                    'billservice.add_radiustrafficnode')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на добавление правил '
                             u'тарификации RADIUS трафика')
            }

        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(
                request,
                _(u'Правило RADIUS тарификации трафика успешно сохранены.'),
                extra_tags='alert-success')
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(
                request,
                _(u'При сохранении настроек RADIUS тарификации трафика '
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
        radius_traffic_id = request.GET.get("radius_traffic_id")
        tts = None
        if radius_traffic_id:
            tts = RadiusTraffic.objects.get(id=radius_traffic_id)
        if id:
            if not (request.user.account.has_perm('billservice.tariff_view')):
                return {
                    'status': True
                }

            item = RadiusTrafficNode.objects.get(id=id)
            form = RadiusTrafficNodeForm(instance=item)
        elif tts:
            form = RadiusTrafficNodeForm(initial={"radiustraffic": tts})
        else:
            form = RadiusTrafficNodeForm(initial={"radiustraffic": tts})

    return {
        'formset': None,
        'form': form
    }


@ajax_request
@systemuser_required
def radiustrafficnode_delete(request):
    if not (request.user.account.has_perm('billservice.change_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на редактирование '
                         u'тарифного плана')
        }

    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = RadiusTrafficNode.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанное правило не найдено %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        messages.success(
            request,
            _(u'Настройка RADIUS тарификации трафика удалена.'),
            extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(
            request,
            _(u'При удалении настройки RADIUS тарификации трафика '
              u'произошла ошибка.'),
            extra_tags='alert-danger')
        return {
            "status": False,
            "message": _(u'RadiusTrafficNode not found')
        }


@ajax_request
@systemuser_required
def radiustrafficservice_delete(request):
    if not (request.user.account.has_perm('billservice.change_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на редактирование '
                         u'тарифного плана')
        }

    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = RadiusTraffic.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанная услуга не найдена %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        messages.success(
            request,
            _(u'Услуга RADIUS тарификации трафика удалена.'),
            extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(
            request,
            _(u'При удалении RADIUS тарификации трафика произошла ошибка.'),
            extra_tags='alert-danger')
        return {
            "status": False,
            "message": _(u'RadiusTraffic not found')
        }

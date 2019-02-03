# -*- coding: utf-8 -*-

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from billservice.forms import PrepaidTrafficForm
from billservice.utils import systemuser_required
from billservice.models import PrepaidTraffic, Tariff
from ebscab.utils.decorators import ajax_request, render_to
from object_log.models import LogItem


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/tariff_prepaidtraffic_edit.html')
def prepaidtraffic_edit(request):
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
            model = PrepaidTraffic.objects.get(id=id)
            form = PrepaidTrafficForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'billservice.change_prepaidtraffic')):
                return {
                    'status': False,
                    'message': _(u'У вас нет прав на редактирование правил '
                                 u'начисления предоплаченного трафика')
                }
        else:
            form = PrepaidTrafficForm(request.POST)
        if not (request.user.account.has_perm(
                'billservice.add_prepaidtraffic')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на добавление правил '
                             u'начисления предоплаченного трафика')
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
                _(u'Настройки предоплаченного трафика успешно сохранены.'),
                extra_tags='alert-success')
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(
                request,
                _(u'При сохранении настроек предоплаченного трафика '
                  u'произошла ошибка.'),
                extra_tags='alert-danger')
            return {
                'form': form,
                'status': False
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm('billservice.view_tariff')):
            return {
                'status': False
            }

        if id:
            item = PrepaidTraffic.objects.get(id=id)
            form = PrepaidTrafficForm(instance=item)
        else:
            tariff_id = request.GET.get("tariff_id")
            tariff = Tariff.objects.get(id=tariff_id)
            form = PrepaidTrafficForm(initial={
                'traffic_transmit_service': tariff.traffic_transmit_service
            })

    return {
        'formset': None,
        'form': form
    }


@ajax_request
@systemuser_required
def prepaidtraffic_delete(request):
    if not (request.user.account.has_perm('billservice.change_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на редактирование '
                         u'тарифного плана')
        }

    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = PrepaidTraffic.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанная запись не найдена %s") % str(e)
            }

        log('DELETE', request.user, item)

        item.delete()
        messages.success(request,
                         _(u'Предоплаченный трафик удалён.'),
                         extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(
            request,
            _(u'При удалении предоплаченного трафика произошла ошибка.'),
            extra_tags='alert-danger')
        return {
            "status": False,
            "message": _(u'AddonServiceTarif not found')
        }

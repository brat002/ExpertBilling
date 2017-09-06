# -*- coding: utf-8 -*-

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from billservice.forms import TimeSpeedForm
from billservice.utils import systemuser_required
from billservice.models import AccessParameters, TimeSpeed
from ebscab.lib.decorators import ajax_request, render_to
from object_log.models import LogItem


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/tariff_timespeed_edit.html')
def timespeed_edit(request):
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
            model = TimeSpeed.objects.get(id=id)
            form = TimeSpeedForm(request.POST, instance=model)
        else:
            form = TimeSpeedForm(request.POST)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(request,
                             _(u'Настройки скорости успешно сохранены.'),
                             extra_tags='alert-success')
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(
                request,
                _(u'При сохранении параметров скорости произошла ошибка.'),
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
        if id:
            item = TimeSpeed.objects.get(id=id)
            form = TimeSpeedForm(instance=item)
        else:
            access_parameters = request.GET.get("access_parameters")
            ap = AccessParameters.objects.get(id=access_parameters)
            form = TimeSpeedForm({"access_parameters": ap})

    return {
        'formset': None,
        'form': form
    }


@ajax_request
@systemuser_required
def timespeed_delete(request):
    if not (request.user.account.has_perm('billservice.change_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на редактирование '
                         u'тарифного плана')
        }

    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = TimeSpeed.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанное правило не найдено %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request,
                         _(u'Настройка скорости удалёна.'),
                         extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(
            request,
            _(u'При удалении настройки скорости произошла ошибка.'),
            extra_tags='alert-danger')
        return {
            "status": False,
            "message": "TimeSpeed not found"
        }

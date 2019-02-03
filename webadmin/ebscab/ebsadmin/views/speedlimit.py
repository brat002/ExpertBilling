# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from billservice.forms import SpeedLimitForm
from billservice.utils import systemuser_required
from billservice.models import SpeedLimit, TrafficLimit
from ebscab.utils.decorators import ajax_request, render_to
from object_log.models import LogItem


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/speedlimit_edit.html')
def speedlimit_edit(request):
    item = None
    trafficlimit_id = request.GET.get("trafficlimit_id")
    trafficlimit = TrafficLimit.objects.get(id=trafficlimit_id)
    if request.method == 'POST':
        if not (request.user.account.has_perm('billservice.change_tariff')):
            return {
                'status': False,
                'message': _(u'У вас нет прав на редактирование '
                             u'тарифного плана')
            }
        id = request.POST.get("id")
        if id:
            model = SpeedLimit.objects.get(id=id)
            form = SpeedLimitForm(request.POST, instance=model)
        else:
            form = SpeedLimitForm(request.POST)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            item = model
            trafficlimit.speedlimit = model
            trafficlimit.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            return {
                'form': form,
                'status': True
            }
        else:
            return {
                'form': form,
                'trafficlimit': trafficlimit,
                'status': False
            }
    else:
        if not (request.user.account.has_perm('billservice.view_tariff')):
            return {
                'status': False
            }

        id = request.GET.get("id")
        trafficlimit_id = request.GET.get("trafficlimit_id")
        trafficlimit = TrafficLimit.objects.get(id=trafficlimit_id)
        if trafficlimit:
            item = trafficlimit.speedlimit
            form = SpeedLimitForm(instance=item)
        else:
            form = SpeedLimitForm()

    return {
        'trafficlimit': trafficlimit,
        'form': form,
        'item': item
    }


@ajax_request
@systemuser_required
def speedlimit_delete(request):
    if not (request.user.account.has_perm('billservice.change_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на редактирование '
                         u'тарифного плана')
        }

    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = SpeedLimit.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанное правило не найдено %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "message": _(u'SpeedLimit not found')
        }

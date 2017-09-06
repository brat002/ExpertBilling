# -*- coding: utf-8 -*-

import datetime

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from billservice.utils import systemuser_required
from billservice.models import AccountTarif
from ebscab.lib.decorators import ajax_request
from object_log.models import LogItem


log = LogItem.objects.log_action


@ajax_request
@systemuser_required
def accounttariff_delete(request):
    if not (request.user.account.has_perm('billservice.delete_accounttarif')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление связки тарифа')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = AccountTarif.objects.get(id=id)
        except Exception, e:
            return {
                'status': False,
                'message': _(u"Указанный тарифный план не найден "
                             u"тарифный план %s") % str(e)
            }
        if item.datetime < datetime.datetime.now():
            return {
                'status': False,
                'message': _(u"Невозможно удалить вступивший в силу "
                             u"тарифный план")
            }

        log('DELETE', request.user, item)

        item.delete()
        messages.success(request,
                         _(u'Тарифный план применён.'),
                         extra_tags='alert-success')
        return {
            'status': True
        }
    else:
        messages.error(request,
                       _(u'Ошибка при изменении тарифного плана.'),
                       extra_tags='alert-danger')
        return {
            'status': False,
            'message': "AccountTarif not found"
        }

# -*- coding: utf-8 -*-

import datetime

from django.utils.translation import ugettext as _

from billservice.utils import systemuser_required
from ebscab.lib.decorators import ajax_request
from radius.models import ActiveSession
from tasks import cred, rosClient, rosExecute, PoD

from ebscab.utils import instance_dict


@ajax_request
@systemuser_required
def session_reset(request):
    if not request.user.account.has_perm('radius.reset_activesession'):
        return {
            'status': False,
            'message': _(u'У вас нет прав на сброс сессии')
        }

    id = request.POST.get('id', None)
    res = False
    if id and id != 'None':
        session = ActiveSession.objects.get(id=id)
        if not session:
            return {
                'status': False,
                'message': 'Session item with id=%s not found' % (id,)
            }

        n = session.nas_int
        nas = instance_dict(n)
        acc = instance_dict(session.account)
        subacc = instance_dict(session.subaccount)
        res = PoD.delay(acc,
                        subacc,
                        nas,
                        access_type=session.framed_protocol,
                        session_id=str(session.sessionid),
                        vpn_ip_address=session.framed_ip_address,
                        caller_id=str(session.caller_id),
                        format_string=str(n.reset_action))
        return {
            'status': True,
            'message': _(u'Сессия поставлена в очередь на сброс.')
        }

    return {
        "message": _(u"Данная функция временно не реализована"),
        'status': False
    }


@ajax_request
@systemuser_required
def session_hardreset(request):
    if not request.user.account.has_perm('radius.reset_activesession'):
        return {
            'status': False,
            'message': _(u'У вас нет прав на сброс сессии')
        }

    id = request.POST.get('id', None)
    res = False
    if id and id != 'None':
        session = ActiveSession.objects.get(id=id)
        if not session:
            return {
                'status': False,
                'message': 'Session item with id=%s not found' % (id, )
            }

        n = session.nas_int
        nas = instance_dict(n)
        acc = instance_dict(session.account)
        subacc = instance_dict(session.subaccount)
        res = PoD.delay(acc,
                        subacc,
                        nas,
                        access_type=session.framed_protocol,
                        session_id=str(session.sessionid),
                        vpn_ip_address=session.framed_ip_address,
                        caller_id=str(session.caller_id),
                        format_string=str(n.reset_action))
        session.session_status = 'ACK'
        session.save()
        try:
            if session.ipinuse:
                ipin = session.ipinuse
                ipin.disabled = datetime.datetime.now()
                ipin.save()
        except:
            pass

        return {
            'status': True,
            'message': _(u'Сессия поставлена в очередь на сброс, IP '
                         u'адрес освобождён')
        }

    return {
        "message": _(u"Данная функция временно не реализована"),
        'status': False
    }

# -*- coding: utf-8 -*-

import IPy
from django.utils.translation import ugettext as _

from billservice.utils import systemuser_required
from ebscab.lib.decorators import ajax_request
from nas.models import Nas
from tasks import rosClient, rosExecute


@ajax_request
@systemuser_required
def get_mac_for_ip(request):
    if not (request.user.account.has_perm('subaccount.getmacforip')):
        return {
            'status': False,
            'message': _(u'Недостаточно прав для выполнения операции')
        }

    nas_id = request.POST.get('nas_id', None)
    if not nas_id:
        return {
            'status': False,
            'message': _(u'Сервер доступа не указан')
        }
    ipn_ip_address = request.POST.get('ipn_ip_address')

    try:
        nas = Nas.objects.get(id=nas_id)
    except Exception, e:
        return {
            'status': False,
            'message': str(e)
        }

    try:
        IPy.IP(ipn_ip_address)
    except Exception, e:
        return {
            'status': False,
            'message': str(e)
        }

    try:
        apiros = rosClient(nas.ipaddress, nas.login, nas.password)
        command = '/ping =address=%s =count=1' % ipn_ip_address
        rosExecute(apiros, command)
        command = '/ip/arp/print ?address=%s' % ipn_ip_address
        mac = rosExecute(apiros, command).get('mac-address', '')
        apiros.close()
    except Exception, e:
        return {
            'success': False,
            'message': str(e)
        }

    return {
        'success': True,
        'mac': mac
    }

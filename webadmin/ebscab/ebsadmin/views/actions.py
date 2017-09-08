# -*- coding: utf-8 -*-

from billservice.helpers import systemuser_required
from billservice.models import SubAccount
from ebscab.lib.decorators import ajax_request
from object_log.models import LogItem
from tasks import cred

from ebsadmin.lib import instance_dict


log = LogItem.objects.log_action


@ajax_request
@systemuser_required
def actions_set(request):
    if not (request.user.account.has_perm('billservice.actions_set')):
        return {
            'status': False,
            'message': u'У вас нет прав на управление состоянием субаккаунтов'
        }

    subaccount = request.POST.get('subaccount_id')
    action = request.POST.get('action')
    if subaccount:
        sa = SubAccount.objects.get(id=subaccount)
        if action == 'ipn_disable':
            sa.ipn_sleep = False
            sa.save()
            return {
                'status': True,
                'message': 'Ok'
            }
        if action == 'ipn_enable':
            sa.ipn_sleep = True
            sa.save()
            return {
                'status': True,
                'message': 'Ok'
            }

        subacc = instance_dict(SubAccount.objects.get(id=subaccount))
        acc = instance_dict(sa.account)
        acc['account_id'] = acc['id']

        try:
            n = sa.nas
            nas = instance_dict(n)
        except Exception, e:
            return {
                'status': False,
                'message': u'Не указан или не найден указанный сервер доступа'
            }

        if action == 'disable':
            command = n.subacc_disable_action
        elif action == 'enable':
            command = n.subacc_enable_action
        elif action == 'create':
            command = n.subacc_add_action
        elif action == 'delete':
            command = n.subacc_delete_action

        sended = cred(account=acc,
                      subacc=subacc,
                      access_type='ipn',
                      nas=nas,
                      format_string=command)
        sended.wait()

        if action == 'create' and sended == True:
            sa.ipn_added = True
            sa.speed = ''
            sa.save()
            log('EDIT', request.user, sa)
            # TODO: IPN Actions action

        if action == 'delete' and sended == True:
            sa.ipn_enabled = False
            sa.ipn_added = False
            sa.speed = ''
            sa.save()
            log('EDIT', request.user, sa)
            # TODO: IPN Actions action

        if action == 'disable' and sended == True:
            sa.ipn_enabled = False
            sa.save()
            log('EDIT', request.user, sa)
            # TODO: IPN Actions action

        if action == 'enable' and sended == True:
            sa.ipn_enabled = True
            sa.save()
            log('EDIT', request.user, sa)
            # TODO: IPN Actions action

        return {
            'status': sended,
            'message': 'Ok'
        }
    return {
        'status': False,
        'message': 'Ok'
    }

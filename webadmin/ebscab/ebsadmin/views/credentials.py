# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _

from billservice.utils import systemuser_required
from ebscab.lib.decorators import ajax_request
from ebscab.lib.ssh_paramiko import ssh_client

from ebsadmin.utils.credentials import (
    GenPasswd as GenPasswd2,
    GenUsername as nameGen
)


@ajax_request
@systemuser_required
def generate_credentials(request):
    action = request.POST.get('action') or request.GET.get('action')
    if action == 'login':
        return {
            'success': True,
            'generated': nameGen()
        }
    if action == 'password':
        return {
            'success': True,
            'generated': GenPasswd2()
        }
    return {
        'success': False
    }


@systemuser_required
@ajax_request
def testCredentials(request):
    if not (request.user.account.has_perm('billservice.testcredentials')):
        return {
            'status': False,
            'message': _(u'У вас нет на тестирование подключения')
        }
    host, login, password = (request.POST.get('host'),
                             request.POST.get('login'),
                             request.POST.get('password'))
    try:
        print host, login, password
        a = ssh_client(host, login, password, '')
    except Exception, e:

        return {
            'status': False,
            'message': str(e)
        }
    return {
        'status': True
    }

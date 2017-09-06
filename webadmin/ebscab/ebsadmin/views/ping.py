# -*- coding: utf-8 -*-

import subprocess

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from billservice.utils import systemuser_required
from ebscab.utils.decorators import render_to


@systemuser_required
@render_to('ebsadmin/ping_check.html')
def tools_ping(request):
    if request.GET:
        if not (request.user.account.has_perm('billservice.view_account')):
            messages.error(request,
                           _(u'У вас нет прав на просмотр данных аккаунта'),
                           extra_tags='alert-danger')
            return {}

        ip = request.GET.get('ip')
        if ip:
            cmd = ['ping', '-c', '3', ip]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            output = ''
            for line in p.stdout:
                output += line
            p.wait()
            print p.returncode
            return {
                'output': output,
                'status': True
            }

    return {
        'status': False
    }

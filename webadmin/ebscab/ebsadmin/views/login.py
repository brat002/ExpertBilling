# -*- coding: utf-8 -*-

import datetime

import IPy
from django.contrib.auth import authenticate, login as log_in
from django.utils.translation import ugettext as _

from billservice.forms import LoginForm
from billservice.models import SystemUser
from ebscab.lib.decorators import ajax_request


@ajax_request
def simple_login(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        try:
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if isinstance(user.account, SystemUser):
                if user.account.host != '0.0.0.0/0':
                    try:
                        if not (IPy.IP(request.META.get("REMOTE_ADDR")) in
                                IPy.IP(user.account.host)):
                            return {
                                "status": False,
                                "message": _(u"Access for your IP address "
                                             u"forbidden")
                            }
                    except Exception, e:
                        return {
                            "status": False,
                            "message": _("Login error. May be systemuser "
                                         "host syntax error")
                        }
                log_in(request, user)
                user.account.last_login = datetime.datetime.now()
                user.account.last_ip = request.META.get("REMOTE_ADDR")
                user.account.save()
                return {
                    "status": True,
                    "message": _("Login succeful")
                }
            else:
                return {
                    "status": False,
                    "message": _("Login forbidden to this action")
                }
        except Exception, e:
            return {
                "status": False,
                "message": _("Login can`t be authenticated")
            }

    return {
        "status": False,
        "message": "Login not found"
    }

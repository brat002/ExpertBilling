# -*- coding: utf-8 -*-

import datetime

import IPy
from django.contrib.auth import (
    authenticate,
    login as log_in,
    logout as log_out
)
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from ebscab.utils.decorators import ajax_request, render_to

from billservice.forms import LoginForm, RegisterForm
from billservice.models import Account, SystemUser


@render_to('login_base.html')
def login(request):
    error_message = True

    if request.method == 'POST':
        register_form = RegisterForm(prefix='register')
        login_form = LoginForm(request.POST, prefix='login')

        if login_form.is_valid():

            user = authenticate(username=login_form.cleaned_data['username'],
                                password=login_form.cleaned_data['password'])
            if user and isinstance(user.account, Account) and not \
                    user.account.allow_webcab:
                message = _(u'У вас нет прав на вход в веб-кабинет')
                return {
                    'message': message,
                    'login_form': login_form,
                    'register_form': RegisterForm(prefix='register')
                }

            elif user:
                log_in(request, user)

                if isinstance(user.account, SystemUser):
                    try:
                        if not (IPy.IP(request.META.get("REMOTE_ADDR")) in
                                IPy.IP(user.account.host)):
                            return {
                                'message': _(u'Access for your ip is forbidden'),
                                'login_form': login_form,
                                'register_form': RegisterForm(prefix='register'),
                            }

                    except Exception, e:
                        return {
                            'message': _(u'Error in access rule for your account'),
                            'login_form': login_form,
                            'register_form': RegisterForm(prefix='register')
                        }

                    user.account.last_login = datetime.datetime.now()
                    user.account.last_ip = request.META.get("REMOTE_ADDR")
                    user.account.save()
                    if user.account.permissiongroup and \
                            user.account.permissiongroup.role and \
                            user.account.permissiongroup.role == 'CASHIER':
                        return HttpResponseRedirect(reverse("cashier_index"))

                    if request.META.get("HTTP_REFERER"):
                        if len(request.META
                               .get("HTTP_REFERER")
                               .split('?next=')) == 2:
                            return HttpResponseRedirect(request.META
                                                        .get("HTTP_REFERER")
                                                        .split('?next=')[1])
                    return HttpResponseRedirect(reverse("admin_dashboard"))

                tariff = user.account.get_account_tariff()
                if tariff and tariff.allow_express_pay:
                    request.session['express_pay'] = True
                request.session.modified = True
                return HttpResponseRedirect('/')
            else:
                message = _(u'Проверьте введенные данные')
                return {
                    'message': message,
                    'login_form': login_form,
                    'register_form': RegisterForm(prefix='register')
                }

        else:
            message = _(u'Проверьте введенные данные')
            return {
                'message': message,
                'login_form': login_form,
                'register_form': RegisterForm(prefix='register')
            }
    else:
        register_form = RegisterForm(prefix='register')
        form = LoginForm(prefix='login')

    return {
        'login_form': form,
        'register_form': register_form
    }


@render_to('login_base.html')
def register(request):
    error_message = True

    if request.method == 'POST':
        register_form = RegisterForm(request.POST, prefix='register')
        login_form = LoginForm(prefix='login')

        if register_form.is_valid():
            register_form.save()
            register_form = RegisterForm(prefix='register')
            return {
                'login_form': login_form,
                'register_form': register_form,
                'message': _(u'Ваша заявка успешно подана. Ожидайте пока '
                             u'с вами свяжется наш менеджер.')}
        else:
            message = _(u'Ошибка регистрации')
            return {
                'message': message,
                'login_form': login_form,
                'register_form': register_form
            }

    else:
        register_form = RegisterForm(prefix='register')
        form = LoginForm(prefix='login')

    return {
        'login_form': form,
        'register_form': register_form
    }


@ajax_request
def simple_login(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        try:
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])

            log_in(request, user)

            return {
                "status": 1,
                "fullname": user.account.fullname,
                "tariff_name": user.account.get_account_tariff().name,
                "message": _(u'Login succeful')
            }
        except:
            return {
                "status": 0,
                "fullname": '',
                'tariff_name': '',
                "message": _(u'User not found')
            }
    return {
        "status": 0,
        "message": _(u'User not found')
    }


def login_out(request):
    log_out(request)
    return HttpResponseRedirect('/')

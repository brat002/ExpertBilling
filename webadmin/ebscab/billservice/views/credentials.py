# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

from ebscab.utils.decorators import render_to, ajax_request

from billservice.forms import EmailForm, PasswordForm, SimplePasswordForm
from billservice.models import SubAccount


@render_to('accounts/change_password.html')
@login_required
def password_form(request):
    return {
        'password_form': PasswordForm(),
        'email_form': EmailForm(),
    }


@render_to('accounts/subaccount_change_password.html')
@login_required
def subaccount_password_form(request, subaccount_id):
    subaccount = SubAccount.objects.get(id=subaccount_id)
    return {
        'form': SimplePasswordForm(),
        'subaccount': subaccount
    }


@ajax_request
@login_required
def subaccount_change_password(request):
    if request.method == 'POST':
        form = SimplePasswordForm(request.POST)
        if form.is_valid():
            try:
                user = request.user.account
                subaccount_id = request.POST.get("subaccount_id", 0)
                if subaccount_id:
                    try:
                        subaccount = (SubAccount.objects
                                      .get(id=subaccount_id,
                                           account=request.user.account))
                    except Exception, e:
                        return {
                            'error_message': _(u'Обнаружена попытка взлома.')
                        }
                else:
                    return {
                        'error_message': _(u'Обнаружена попытка взлома.')
                    }

                if form.cleaned_data['new_password'] == \
                        form.cleaned_data['repeat_password'] and \
                        subaccount.password != '':
                    subaccount.password = form.cleaned_data['new_password']
                    subaccount.save()
                    return {
                        'error_message': _(u'Пароль успешно изменен')
                    }
                else:
                    return {
                        'error_message': _(u'Пароли не совпадают')
                    }
            except Exception, e:
                return {
                    'error_message': _(u'Возникла ошибка. Обратитесь к '
                                       u'администратору.')
                }
        else:
            return {
                'error_message': _(u'Одно из полей не заполнено')
            }
    else:
        return {
            'error_message': _(u'Не предвиденная ошибка')
        }


@ajax_request
@login_required
def change_password(request):
    if request.method == 'POST':
        user = request.user.account
        form = PasswordForm(request.POST)
        if form.is_valid():
            try:
                if user.password == form.cleaned_data['old_password'] and \
                        form.cleaned_data['new_password'] == \
                        form.cleaned_data['repeat_password']:
                    user.password = form.cleaned_data['new_password']
                    user.save()
                    return {
                        'error_message': _(u'Пароль успешно изменен')
                    }
                else:
                    return {
                        'error_message': _(u'Проверьте пароль. ')
                    }
            except Exception, e:
                return {
                    'error_message': _(u'Возникла ошибка. Обратитесь к '
                                       u'администратору.')
                }
        else:
            return {
                'error_message': _(u'Проверьте введенные данные')
            }
    else:
        return {
            'error_message': _(u'Не предвиденная ошибка')
        }


@ajax_request
@login_required
def change_email(request):
    if request.method == 'POST':
        user = request.user.account
        form = EmailForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['new_email'] and \
                form.cleaned_data['repeat_email'] and \
                    form.cleaned_data['new_email'] == \
                    form.cleaned_data['repeat_email']:
                user.email = form.cleaned_data['new_email']
                user.save()
                return {
                    'error_message': _(u'E-mail успешно изменен'),
                    'ok': 'ok'
                }
            else:
                return {
                    'error_message': _(u'Введённые e-mail не совпадают')
                }

        else:
            return {
                'error_message': _(u'Проверьте введенные данные')
            }

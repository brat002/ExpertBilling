# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _


class PayForm(forms.Form):
    username = forms.CharField(
        label=_(u"Имя администратора или кассира"),
        required=True,
        error_messages={
            'required': _(u'Вы не ввели имя администратора или кассира')
        }
    )
    password = forms.CharField(
        label=_(u"Пароль"),
        widget=forms.PasswordInput,
        required=True,
        error_messages={
            'required': _(u'Вы не ввели пароль администратора или кассира')
        }
    )
    account_username = forms.CharField(
        label=_(u"Имя аккаунта"),
        required=True,
        error_messages={
            'required': _(u'Вы не ввели имя аккаунта')
        }
    )
    summ = forms.DecimalField(
        label=_(u"Сумма"),
        required=True,
        error_messages={
            'required': _(u'Вы не ввели сумму')
        }
    )
    description = forms.CharField(label=_(u"Комментарий"), required=False)
    promise = forms.BooleanField(label=_(u"Обещанный платёж"), required=False)

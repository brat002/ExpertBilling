# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings


class QiwiPaymentRequestForm(forms.Form):
    phone = forms.CharField(label=u"Номер телефона в QIWI")
    password = forms.CharField(
        label=u"Пароль в QIWI", required=False, widget=forms.PasswordInput)
    summ = forms.DecimalField(
        max_digits=7, decimal_places=2, label=u'%s' % settings.CURRENCY)
    autoaccept = forms.BooleanField(required=False)

#-*-coding:utf-8 -*-

from django import forms

from django.conf import settings

class QiwiPaymentRequestForm(forms.Form):
    phone = forms.CharField(label=u"Номер телефона в qiwi")
    summ = forms.DecimalField(max_digits=7, decimal_places=2, label=u'%s' % settings.CURRENCY)
    
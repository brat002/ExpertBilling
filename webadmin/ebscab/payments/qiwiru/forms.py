# -*- coding: utf-8 -*-

from django import forms

from getpaid.models import Order


class AdditionalFieldsForm(forms.Form):
    phone = forms.CharField(
        required=True, label=u'Номер телефона в формате +7XXXXXXXXXX')
    summ = forms.FloatField(label=u'Сумма')
    order = forms.ModelChoiceField(
        widget=forms.widgets.HiddenInput,
        required=False,
        queryset=Order.objects.all())
    backend = forms.CharField(
        initial='payments.qiwiru', widget=forms.widgets.HiddenInput)


class PostBackForm(forms.Form):
    bill_id = forms.CharField(required=True)
    status = forms.CharField(required=True)
    error = forms.CharField()
    amount = forms.FloatField(required=True)
    user = forms.CharField(required=True)
    prv_name = forms.CharField()
    ccy = forms.CharField()
    comment = forms.CharField()
    command = forms.CharField(required=True)

# -*- coding: utf-8 -*-

from django import forms

from getpaid.models import Order


class AdditionalFieldsForm(forms.Form):
    # FIXME: translation
    summ = forms.FloatField(label=u'Сумма')
    order = forms.ModelChoiceField(
        widget=forms.widgets.HiddenInput,
        required=False,
        queryset=Order.objects.all()
    )
    backend = forms.CharField(
        initial='payments.liqpay', widget=forms.widgets.HiddenInput)

# -*- coding: utf-8 -*-

from django import forms

from getpaid.models import Order


class AdditionalFieldsForm(forms.Form):
    summ = forms.FloatField(label=u'Сумма')
    order = forms.ModelChoiceField(
        widget=forms.widgets.HiddenInput, required=False, queryset=Order.objects.all())
    backend = forms.CharField(
        initial='payments.privat24', widget=forms.widgets.HiddenInput)

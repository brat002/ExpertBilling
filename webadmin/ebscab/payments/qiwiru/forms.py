# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from getpaid.models import Order


class AdditionalFieldsForm(forms.Form):
    phone = forms.CharField(
        required=True, label=_(u'Номер телефона в формате +7XXXXXXXXXX'))
    summ = forms.FloatField(label=_(u'Сумма'))
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


class CheckAdditionalFieldsForm(AdditionalFieldsForm):

    def clean_summ(self):
        from payments.qiwiru.backend import PaymentProcessor  # avoid cyclic import

        summ = self.cleaned_data['summ']
        if summ < PaymentProcessor.get_backend_setting(
                'MIN_SUM', PaymentProcessor.MIN_SUM):
            raise forms.ValidationError(_(u'Сумма должна быть не меньше %s' %
                                          PaymentProcessor.get_backend_setting(
                                              'MIN_SUM', PaymentProcessor.MIN_SUM)))

        return summ

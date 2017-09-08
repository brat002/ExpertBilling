# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _

from getpaid.models import Payment


class PromiseForm(forms.Form):
    sum = forms.FloatField(
        label=_(u"Сумма"),
        required=True,
        error_messages={
            'required': _(u'Вы не указали размер платежа!')
        }
    )


class PaymentForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['account'].widget = forms.widgets.HiddenInput()
        self.fields['order'].widget = forms.widgets.HiddenInput()
        self.fields['paid_on'].widget = \
            forms.widgets.DateTimeInput(attrs={'class': 'datepicker'})

    class Meta:
        model = Payment
        fields = '__all__'

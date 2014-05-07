# -*- coding: utf-8 -*-
from django import  forms
from django.forms.fields import ChoiceField
from django.utils.translation import ugettext as _
from getpaid.utils import get_backend_choices
from getpaid.models import Order

class AdditionalFieldsForm(forms.Form):
    #phone = forms.CharField(label=u'Номер телефона', help_text=u'В междунарождном формате (например +370221234567)', required=False)
    summ = forms.FloatField(label=u'Сумма')
    order = forms.ModelChoiceField(widget=forms.widgets.HiddenInput, required=False, queryset=Order.objects.all())
    backend = forms.CharField(initial='payments.privat24', widget=forms.widgets.HiddenInput)
# -*- encoding: utf-8 -*-
from django import forms
from nas.models import Nas
from ajax_select.fields import AutoCompleteSelectMultipleField
from billservice.forms import SplitDateTimeWidget
from billservice.models import City
from django.utils.translation import ugettext_lazy as _


class SessionFilterForm(forms.Form):
    account = AutoCompleteSelectMultipleField( 'account_fts', required = False) 
    nas = forms.ModelMultipleChoiceField(label=_(u"Сервер доступа субаккаунта"), queryset=Nas.objects.all(), required=False)
    id = forms.IntegerField(required=False)
    city = forms.ModelChoiceField(label=_(u'Город'), queryset=City.objects.all(), required=False)
    street = forms.CharField(label=_(u'Улица'), required=False)
    house = forms.CharField(label=_(u'Дом'), required=False)
    date_start = forms.DateTimeField(label = _(u'С даты'), required=False, widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    date_end = forms.DateTimeField(label = _(u'По дату'), required=False, widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    only_active = forms.BooleanField(label = _(u'Только активные'), widget = forms.widgets.CheckboxInput, required=False)
#-*- coding: utf-8 -*-
from django import forms
from ajax_select.fields import AutoCompleteSelectMultipleField
from billservice.widgets import SplitDateTimeWidget
from billservice.models import SystemUser, TransactionType, Switch

from django.utils.translation import ugettext_lazy as _


import datetime

class AccountBallanceForm(forms.Form):
    date_start = forms.DateTimeField(label=u'C', required = True, widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    date_end = forms.DateTimeField(label=u'По', required = False, widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    accounts = AutoCompleteSelectMultipleField( 'account_username', label=u'Аккаунты', required = False)


class CachierReportForm(forms.Form):
    date_start = forms.DateField(label=u'C', initial=datetime.datetime.now(), required = False, widget = forms.widgets.DateInput(attrs={'class':'dateonlypicker'}))
    date_end = forms.DateField(label=u'По', initial=datetime.datetime.now(), required = False, widget = forms.widgets.DateInput(attrs={'class':'dateonlypicker'}))
    systemuser = forms.ModelChoiceField(SystemUser.objects.all(), required=False)
    
    
class ReportForm(forms.Form):
    date_start = forms.DateField(label=u'C', initial=datetime.datetime.now(), required = False, widget = forms.widgets.DateInput(attrs={'class':'dateonlypicker'}))
    date_end = forms.DateField(label=u'По', initial=datetime.datetime.now(), required = False, widget = forms.widgets.DateInput(attrs={'class':'dateonlypicker'}))
    transactiontype = forms.ModelMultipleChoiceField(label = _(u'Тип операции'), queryset = TransactionType.objects.all(), required=False, widget = forms.widgets.SelectMultiple(attrs={'size': 20}))
    
class SwitchReportForm(forms.Form):
    switch = forms.ModelMultipleChoiceField(label = _('Switch'), queryset = Switch.objects.all().order_by('name'), required=False, widget = forms.widgets.SelectMultiple(attrs={'size': 20}))
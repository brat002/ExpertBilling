#-*- coding: utf-8 -*-
from django import forms
from ajax_select.fields import AutoCompleteSelectMultipleField
from billservice.widgets import SplitDateTimeWidget
from billservice.models import SystemUser

class AccountBallanceForm(forms.Form):
    date_start = forms.DateTimeField(label=u'C', required = True, widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    date_end = forms.DateTimeField(label=u'По', required = True, widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    accounts = AutoCompleteSelectMultipleField( 'account_username', label=u'Аккаунты', required = False)


class CachierReportForm(forms.Form):
    date_start = forms.DateField(label=u'C', required = False, widget = forms.widgets.DateInput(attrs={'class':'dateonlypicker'}))
    date_end = forms.DateField(label=u'По', required = False, widget = forms.widgets.DateInput(attrs={'class':'dateonlypicker'}))
    systemuser = forms.ModelChoiceField(SystemUser.objects.all(), required=False)
    
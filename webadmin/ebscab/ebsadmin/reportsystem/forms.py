#-*- coding: utf-8 -*-
from django import forms
from ajax_select.fields import AutoCompleteSelectMultipleField
from billservice.widgets import SplitDateTimeWidget

class AccountBallanceForm(forms.Form):
    date_start = forms.DateTimeField(label=u'C', required = True, widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    date_end = forms.DateTimeField(label=u'По', required = True, widget = forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    accounts = AutoCompleteSelectMultipleField( 'account_username', label=u'Аккаунты', required = False)

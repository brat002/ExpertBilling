#-*- coding: utf-8 -*-
from django import forms
from ajax_select.fields import AutoCompleteSelectMultipleField
from billservice.widgets import SplitDateTimeWidget

class AccountBallanceForm(forms.Form):
    date_start = forms.DateTimeField(label=u'C', required = False, widget=SplitDateTimeWidget(date_attrs={'class':'input-small datepicker'}, time_attrs={'class':'input-small timepicker'}))
    date_end = forms.DateTimeField(label=u'По', required = False, widget=SplitDateTimeWidget(date_attrs={'class':'input-small datepicker'}, time_attrs={'class':'input-small timepicker'}))
    accounts = AutoCompleteSelectMultipleField( 'account_username', label=u'Аккаунты', required = False)

# -*- encoding: utf-8 -*-
from django import forms
from nas.models import Nas
from ajax_select.fields import AutoCompleteSelectMultipleField

class SessionFilterForm(forms.Form):
    account = AutoCompleteSelectMultipleField( 'account_fts', required = False) 
    nas = forms.ModelMultipleChoiceField(label=u"Сервер доступа субаккаунта", queryset=Nas.objects.all(), required=False)
    id = forms.IntegerField(required=False)
    date_start = forms.DateTimeField(required=False)
    date_end = forms.DateTimeField(required=False)
    only_active = forms.BooleanField(widget = forms.widgets.CheckboxInput, required=False)
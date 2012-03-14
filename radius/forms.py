# -*- encoding: utf-8 -*-
from django import forms


class SessionFilterForm(forms.Form):
    account = forms.IntegerField(required=False) 
    id = forms.IntegerField(required=False)
    date_start = forms.DateTimeField(required=True)
    date_end = forms.DateTimeField(required=False)
    only_active = forms.CheckboxInput()
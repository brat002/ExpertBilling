# -*- encoding: utf-8 -*-

from django import forms

from billservice.models import BankData


class BankDataForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = BankData
        fields = '__all__'

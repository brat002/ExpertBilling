# -*- encoding: utf-8 -*-

from django import forms

from billservice.models import Account, BankData, Organization


class OrganizationForm(forms.ModelForm):
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        required=False,
        widget=forms.widgets.HiddenInput
    )
    bank = forms.ModelChoiceField(
        queryset=BankData.objects.all(),
        required=False,
        widget=forms.widgets.HiddenInput
    )

    class Meta:
        model = Organization
        fields = '__all__'

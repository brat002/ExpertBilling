# -*- encoding: utf-8 -*-

from django import forms

from billservice.models import AccountSuppAgreement, SuppAgreement


class AccountSuppAgreementForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = AccountSuppAgreement
        fields = '__all__'
        widgets = {
            'account': forms.widgets.HiddenInput,
            'created': forms.widgets.DateTimeInput(attrs={
                'class': 'datepicker'
            }),
            'closed': forms.widgets.DateTimeInput(attrs={
                'class': 'datepicker'
            })
        }


class SuppAgreementForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = SuppAgreement
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'cols': 15,
                'class': 'span8'
            }),
            'body': forms.Textarea(attrs={
                'rows': 10,
                'cols': 25,
                'class': 'span8'
            })
        }

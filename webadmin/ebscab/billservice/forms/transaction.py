# -*- encoding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _

from ajax_select.fields import AutoCompleteSelectMultipleField

from billservice.models import (
    Account,
    AccountGroup,
    SystemUser,
    Transaction,
    TransactionType
)


class TransactionModelForm(forms.ModelForm):
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(), widget=forms.HiddenInput)
    type = forms.ModelChoiceField(
        queryset=TransactionType.objects.filter(is_bonus=False),
        widget=forms.widgets.Select(attrs={
            'class': 'input-xlarge'
        })
    )

    def __init__(self, *args, **kwargs):
        super(TransactionModelForm, self).__init__(*args, **kwargs)
        self.fields['type'].widget.attrs['class'] = 'input-xlarge span5'
        self.fields['description'].widget = \
            forms.widgets.TextInput(attrs={'class': 'input-xlarge span5'})
        self.fields['account'].widget.attrs['class'] = 'input-xlarge span5'
        self.fields['bill'].widget.attrs['class'] = 'input-xlarge span5'
        self.fields['created'].widget.attrs['class'] = 'datepicker'
        self.fields['end_promise'].widget = \
            forms.widgets.DateTimeInput(attrs={'class': 'datepicker'})

    def clean_summ(self):
        summ = self.cleaned_data.get('summ', 0)
        if summ == 0:
            raise forms.ValidationError(_(u'Укажите сумму'))
        return summ

    class Meta:
        model = Transaction
        exclude = ('systemuser', 'accounttarif', 'approved', 'tarif',
                   'promise_expired', 'prev_balance', 'is_bonus')


class BonusTransactionModelForm(forms.ModelForm):
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(), widget=forms.HiddenInput)
    type = forms.ModelChoiceField(
        queryset=TransactionType.objects.filter(is_bonus=True),
        widget=forms.widgets.Select(attrs={
            'class': 'input-xlarge'
        })
    )

    def __init__(self, *args, **kwargs):
        super(BonusTransactionModelForm, self).__init__(*args, **kwargs)
        self.fields['type'].widget.attrs['class'] = 'input-xlarge span5'
        self.fields['description'].widget = \
            forms.widgets.TextInput(attrs={'class': 'input-xlarge span5'})
        self.fields['bill'].widget.attrs['class'] = 'input-xlarge span5'

    def clean_summ(self):
        summ = self.cleaned_data.get('summ', 0)
        if summ == 0:
            raise forms.ValidationError(_(u'Укажите сумму'))
        return summ

    class Meta:
        model = Transaction
        exclude = ('systemuser', 'prev_balance', 'accounttarif', 'tarif',
                   'promise_expired', 'approved', 'end_promise', 'is_bonus')


class TransactionReportForm(forms.Form):
    start_date = forms.DateTimeField(
        required=False,
        label=_(u'С'),
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    end_date = forms.DateTimeField(
        required=False,
        label=_(u'По'),
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    account = AutoCompleteSelectMultipleField('account_fts', required=False)
    systemuser = forms.ModelMultipleChoiceField(
        label=_(u"Администратор"),
        queryset=SystemUser.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'size': '10'
        }),
        required=False
    )
    account_group = forms.ModelMultipleChoiceField(
        label=_(u"Группа абонентов"),
        queryset=AccountGroup.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'size': '10'
        }),
        required=False
    )


class TransactionTypeForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        exclude = ('is_deletable',)
        model = TransactionType

# -*- encoding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _

from billservice.models import (
    Account,
    SettlementPeriod,
    SuspendedPeriod,
    TimePeriod,
    TimePeriodNode
)


class SuspendedPeriodModelForm(forms.ModelForm):
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': 'readonly'
        })
    )

    def __init__(self, *args, **kwargs):
        super(SuspendedPeriodModelForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget = \
            forms.widgets.DateTimeInput(attrs={'class': 'datepicker'})
        self.fields['end_date'].widget = \
            forms.widgets.DateTimeInput(attrs={'class': 'datepicker'})

    class Meta:
        model = SuspendedPeriod
        exclude = ('activated_by_account',)


class SuspendedPeriodBatchForm(forms.Form):
    accounts = forms.ModelMultipleChoiceField(
        queryset=Account.objects.all(),
        widget=forms.widgets.MultipleHiddenInput)
    start_date = forms.DateTimeField(
        widget=forms.widgets.DateTimeInput(attrs={'class': 'datepicker'}))
    end_date = forms.DateTimeField(
        widget=forms.widgets.DateTimeInput(attrs={'class': 'datepicker'}))


class SettlementPeriodForm(forms.ModelForm):
    time_start = forms.DateTimeField(
        label=_(u'Начало периода'),
        required=True,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )

    class Meta:
        model = SettlementPeriod
        fields = '__all__'


class TimePeriodForm(forms.ModelForm):

    class Meta:
        model = TimePeriod
        fields = '__all__'


class TimePeriodNodeForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    time_period = forms.ModelChoiceField(
        queryset=TimePeriod.objects.all(),
        required=True,
        widget=forms.HiddenInput
    )
    time_start = forms.DateTimeField(
        label=_(u'Начало периода'),
        required=True,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    time_end = forms.DateTimeField(
        label=_(u'Конец периода'),
        required=True,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    length = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kw):
        super(TimePeriodNodeForm, self).__init__(*args, **kw)
        self.fields.keyOrder = [
            'id',
            'time_period',
            'name',
            'time_start',
            'time_end',
            'length',
            'repeat_after'
        ]

    def clean(self):
        cleaned_data = super(TimePeriodNodeForm, self).clean()
        if cleaned_data.get("time_end") and cleaned_data.get("time_start"):
            cleaned_data["length"] = \
                (cleaned_data.get("time_end") -
                 cleaned_data.get("time_start")).days * 86400 + \
                (cleaned_data.get("time_end") -
                 cleaned_data.get("time_start")).seconds
        return cleaned_data

    class Meta:
        model = TimePeriodNode
        fields = '__all__'

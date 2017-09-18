# -*- encoding: utf-8 -*-

from django import forms

from billservice.models import AccessParameters


class AccessParametersForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = AccessParameters
        fields = '__all__'


class AccessParametersTariffForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = AccessParameters
        exclude = ('max_tx', 'max_rx', 'burst_tx', 'burst_rx',
                   'burst_treshold_tx', 'burst_treshold_rx', 'burst_time_tx',
                   'burst_time_rx', 'min_tx', 'min_rx', 'priority',
                   'sessionscount')

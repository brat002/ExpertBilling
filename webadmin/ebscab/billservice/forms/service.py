# -*- encoding: utf-8 -*-

from django import forms

from billservice.models import (
    AddonService,
    AddonServiceTarif,
    OneTimeService,
    PeriodicalService
)


class AddonServiceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AddonServiceForm, self).__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'input-xlarge'

        self.fields['service_activation_action'].widget.attrs['class'] = \
            'span8'
        self.fields['service_activation_action'].widget.attrs['rows'] = 3
        self.fields['service_deactivation_action'].widget.attrs['class'] = \
            'span8'
        self.fields['service_deactivation_action'].widget.attrs['rows'] = 3
        self.fields['comment'].widget.attrs['class'] = 'input-xlarge span6'
        self.fields['comment'].widget.attrs['rows'] = 3

        for field in ('max_tx', 'max_rx', 'burst_tx', 'burst_rx',
                      'burst_treshold_tx', 'burst_treshold_rx',
                      'burst_time_tx', 'burst_time_rx', 'min_tx',
                      'min_rx', 'priority'):
            self.fields[field].required = True

    class Meta:
        model = AddonService
        fields = '__all__'


class AddonServiceTarifForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(AddonServiceTarifForm, self).__init__(*args, **kwargs)
        self.fields['tarif'].widget = forms.widgets.HiddenInput()

    class Meta:
        model = AddonServiceTarif
        fields = '__all__'


class OneTimeServiceForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(OneTimeServiceForm, self).__init__(*args, **kwargs)
        self.fields['tarif'].widget = forms.widgets.HiddenInput()

    class Meta:
        model = OneTimeService
        fields = '__all__'


class PeriodicalServiceForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(PeriodicalServiceForm, self).__init__(*args, **kwargs)
        self.fields['tarif'].widget = forms.widgets.HiddenInput()

        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'input-xlarge span5'

        self.fields['created'].widget = forms.widgets.DateTimeInput(
            attrs={'class': 'datepicker'})
        self.fields['deactivated'].widget = forms.widgets.DateTimeInput(
            attrs={'class': 'datepicker'})

    class Meta:
        model = PeriodicalService
        exclude = ('deleted',)

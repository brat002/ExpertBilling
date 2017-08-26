# -*- encoding: utf-8 -*-

from django import forms

from billservice.models import (
    Group,
    PrepaidTraffic,
    TrafficLimit,
    TrafficTransmitNodes,
    TrafficTransmitService
)


class TrafficLimitForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(TrafficLimitForm, self).__init__(*args, **kwargs)
        self.fields['tarif'].widget = forms.widgets.HiddenInput()

    class Meta:
        model = TrafficLimit
        fields = '__all__'


class TrafficTransmitServiceForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = TrafficTransmitService
        fields = '__all__'


class TrafficTransmitNodeForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(TrafficTransmitNodeForm, self).__init__(*args, **kwargs)
        self.fields[
            'traffic_transmit_service'].widget = forms.widgets.HiddenInput()

    class Meta:
        model = TrafficTransmitNodes
        fields = '__all__'


class PrepaidTrafficForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    traffic_transmit_service = forms.ModelChoiceField(
        queryset=TrafficTransmitService.objects.all(),
        widget=forms.widgets.HiddenInput
    )

    class Meta:
        model = PrepaidTraffic
        fields = '__all__'


class GroupForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Group
        fields = '__all__'

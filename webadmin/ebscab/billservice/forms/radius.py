# -*- encoding: utf-8 -*-

from django import forms

from nas.models import Nas

from billservice.models import (
    RadiusAttrs,
    RadiusTraffic,
    RadiusTrafficNode,
    Tariff
)


class RadiusAttrsForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    nas = forms.ModelChoiceField(
        queryset=Nas.objects.all(),
        required=False,
        widget=forms.HiddenInput
    )
    tarif = forms.ModelChoiceField(
        queryset=Tariff.objects.all(),
        required=False,
        widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        super(RadiusAttrsForm, self).__init__(*args, **kwargs)

        self.fields['vendor'].widget = forms.HiddenInput()
        self.fields['attrid'].widget = forms.HiddenInput()

    class Meta:
        model = RadiusAttrs
        fields = '__all__'


class RadiusTrafficForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = RadiusTraffic
        fields = '__all__'


class RadiusTrafficNodeForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(RadiusTrafficNodeForm, self).__init__(*args, **kwargs)
        self.fields['radiustraffic'].widget = forms.widgets.HiddenInput()

    class Meta:
        model = RadiusTrafficNode
        exclude = ('created', 'deleted')

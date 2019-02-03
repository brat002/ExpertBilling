# -*- encoding: utf-8 -*-

from django import forms

from billservice.models import TimeAccessNode, TimeAccessService, TimeSpeed


class TimeAccessNodeForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(TimeAccessNodeForm, self).__init__(*args, **kwargs)
        self.fields['time_access_service'].widget = forms.widgets.HiddenInput()

    class Meta:
        model = TimeAccessNode
        fields = '__all__'


class TimeSpeedForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(TimeSpeedForm, self).__init__(*args, **kwargs)
        self.fields['access_parameters'].widget = forms.widgets.HiddenInput()

    class Meta:
        model = TimeSpeed
        fields = '__all__'


class TimeAccessServiceForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = TimeAccessService
        fields = '__all__'

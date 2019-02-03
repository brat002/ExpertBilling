# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from billservice.models import Hardware, HardwareType, Manufacturer, Model


class ManufacturerForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    name = forms.CharField(required=True, label=_(u"Название"))

    class Meta:
        model = Manufacturer
        fields = '__all__'


class ModelHardwareForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    name = forms.CharField(required=True, label=_(u"Название"))

    class Meta:
        model = Model
        fields = '__all__'


class HardwareTypeForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    name = forms.CharField(required=True, label=_(u"Название"))

    class Meta:
        model = HardwareType
        fields = '__all__'


class HardwareForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Hardware
        fields = '__all__'

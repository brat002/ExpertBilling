from django import forms
from datetime import datetime, date
from django.forms import ModelForm
from billservice.models import Tariff, Account, Group, Tariff
from nas.models import Nas, TrafficClass


class ReportForm(forms.Form):
    accounts = forms.ModelMultipleChoiceField(queryset=Account.objects.all(), required=False)
    classes = forms.ModelMultipleChoiceField(queryset=TrafficClass.objects.all(), required=False)
    nasses = forms.ModelMultipleChoiceField(queryset=Nas.objects.all(), required=False)
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)
    tariffs = forms.ModelMultipleChoiceField(queryset=Tariff.objects.all(), required=False)
    start_date = forms.DateTimeField(required=True)
    end_date = forms.DateTimeField(required=True)
    report = forms.CharField(required=True)
    reporttype = forms.CharField(required=True)
    trafficsource = forms.CharField(required=False)
    grouping = forms.CharField(required=False)
    animation = forms.CheckboxInput()
    shadow = forms.CheckboxInput()
    legend = forms.CheckboxInput()
    back = forms.CharField(required=False)
    
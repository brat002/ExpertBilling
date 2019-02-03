# -*- encoding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _

from ajax_select.fields import AutoCompleteSelectMultipleField

from billservice.models import IPPool
from billservice.widgets import InlineRadioSelect


class IpInUseLogForm(forms.Form):
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
    subaccount = AutoCompleteSelectMultipleField(
        'subaccount_fts', required=False)
    ippool = forms.ModelMultipleChoiceField(
        label=_(u"Пул"), queryset=IPPool.objects.all(), required=False)
    ip = forms.GenericIPAddressField(required=False)
    types = forms.ChoiceField(
        required=False,
        choices=(
            ('dynamic', _(u"Динамические")),
            ('static', _(u'Статические')),
            ('', _(u'Любые'))
        ),
        widget=InlineRadioSelect
    )


class IPPoolForm(forms.ModelForm):

    class Meta:
        model = IPPool
        fields = '__all__'

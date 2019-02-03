# -*- encoding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _

from billservice.models import Permission, PermissionGroup
from billservice.widgets import CheckboxSelectMultipleWithSelectAll


class PermissionGroupForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    permissions = forms.ModelMultipleChoiceField(
        label=_(u'Права'),
        queryset=Permission.objects.all(),
        widget=CheckboxSelectMultipleWithSelectAll
    )

    class Meta:
        exclude = ('deletable',)
        model = PermissionGroup

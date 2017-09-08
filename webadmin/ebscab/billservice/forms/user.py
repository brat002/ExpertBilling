# -*- encoding: utf-8 -*-

from django import forms
from django.conf import settings
from django.contrib.auth.models import Group as AuthGroup
from django.utils.translation import ugettext as _

from billservice.models import SystemUser
from billservice.widgets import CustomPasswordWidget


class SystemUserForm(forms.ModelForm):
    last_ip = forms.CharField(
        label=_(u"Последний логин с IP"),
        widget=forms.TextInput(attrs={
            'readonly': 'readonly'
        }),
        required=False
    )
    last_login = forms.CharField(
        label=_(u"Последний логин"),
        widget=forms.TextInput(attrs={
            'readonly': 'readonly'
        }),
        required=False
    )
    created = forms.CharField(
        label=_(u"Создан"),
        widget=forms.TextInput(attrs={
            'readonly': 'readonly'
        }),
        required=False
    )
    authgroup = forms.ModelMultipleChoiceField(
        label=_(u"Группа доступа"),
        queryset=AuthGroup.objects.all(),
        required=False
    )
    is_superuser = forms.BooleanField(
        label=_(u"Суперадминистратор"),
        widget=forms.CheckboxInput,
        required=False
    )
    text_password = forms.CharField(
        label=_(u"Пароль") if settings.HIDE_PASSWORDS == False
        else _(u"Изменить пароль"),
        required=False,
        widget=CustomPasswordWidget() if settings.HIDE_PASSWORDS == True
        else forms.widgets.TextInput()
    )

    class Meta:
        model = SystemUser
        exclude = ('last_ip', 'last_login', 'created', 'password')

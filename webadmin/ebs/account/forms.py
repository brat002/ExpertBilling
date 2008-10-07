# -*- coding:utf-8 -*-

from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label=u'Логин', required=True, error_messages={'required':u'Не введен логин'})
    password = forms.CharField(label=u'Пароль',widget=forms.PasswordInput, required=True, error_messages={'required':u'Не введен пароль'})
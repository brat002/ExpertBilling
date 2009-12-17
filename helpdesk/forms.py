# -*- encoding: utf-8 -*-
from django import forms
from datetime import datetime, date

class LoginForm(forms.Form):
    username = forms.CharField(label=u"Имя пользователя", required = True, error_messages={'required':u'Вы не ввели имя пользователя!'})
    password = forms.CharField(label=u"Пароль", widget=forms.PasswordInput, required = False)
  
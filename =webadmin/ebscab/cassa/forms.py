#-*-coding:utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
class PayForm(forms.Form):
    username = forms.CharField(label=u"Имя администратора или кассира", required = True, error_messages={'required':u'Вы не ввели имя администратора или кассира'})
    password = forms.CharField(label=u"Пароль", widget=forms.PasswordInput, required = True, error_messages={'required':u'Вы не ввели пароль администратора или кассира'})
    account_username = forms.CharField(label=u"Имя аккаунта", required = True, error_messages={'required':u'Вы не ввели имя аккаунта'})
    summ = forms.DecimalField(label=u"Сумма", required = True, error_messages={'required':u'Вы не ввели сумму'})
    description = forms.CharField(label=u"Комментарий", required = False)
    promise = forms.BooleanField(label=u"Обещанный платёж", required=False)
    

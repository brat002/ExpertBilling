# -*- encoding: utf-8 -*-
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label=u"имя пользователя", required = True, error_messages={'required':u'Вы не ввели имя пользователя!'})
    password = forms.CharField(label=u"пароль", required = True, widget=forms.PasswordInput )
    
class PasswordForm(forms.Form):
    old_password = forms.CharField(label=u"Старый пароль", required = True, widget=forms.PasswordInput, error_messages={'required':u'Обязательное поле!'} )
    new_password = forms.CharField(label=u"Новый пароль", required = True, widget=forms.PasswordInput, error_messages={'required':u'Обязательное поле!'} )
    repeat_password = forms.CharField(label=u"Повторите", required = True, widget=forms.PasswordInput, error_messages={'required':u'Обязательное поле!'} )
    
class CardForm(forms.Form):
    series = forms.IntegerField(label=u"Введите серию", required = True, error_messages={'required':u'Обязательное поле!'})
    pin = forms.CharField(label=u"ПИН", required = True, widget=forms.PasswordInput, error_messages={'required':u'Обязательное поле!'})
# -*- encoding: utf-8 -*-
from django import forms

from billservice.models import Tariff

class LoginForm(forms.Form):
    username = forms.CharField(label=u"имя пользователя", required = True, error_messages={'required':u'Вы не ввели имя пользователя!'})
    user = forms.CharField(label=u"user", required = False)
    password = forms.CharField(label=u"пароль", widget=forms.PasswordInput, required = False)
    pin = forms.CharField(label=u"пин", widget=forms.PasswordInput(attrs={'class': 'unset'}), required = False)
    
class PasswordForm(forms.Form):
    old_password = forms.CharField(label=u"Старый пароль", required = True, widget=forms.PasswordInput, error_messages={'required':u'Обязательное поле!'} )
    new_password = forms.CharField(label=u"Новый пароль", required = True, widget=forms.PasswordInput, error_messages={'required':u'Обязательное поле!'} )
    repeat_password = forms.CharField(label=u"Повторите", required = True, widget=forms.PasswordInput, error_messages={'required':u'Обязательное поле!'} )
    
class CardForm(forms.Form):
    series = forms.IntegerField(label=u"Введите серию", required = True, error_messages={'required':u'Обязательное поле!'})
    pin = forms.CharField(label=u"ПИН", required = True, widget=forms.PasswordInput, error_messages={'required':u'Обязательное поле!'})
    
class ChangeTariffForm(forms.Form):
    tariff_id = forms.ChoiceField(choices=[('','----')]+[(x.id, x.name) for x in Tariff.objects.all().order_by('name')], label=u"Выберите тарифный план", widget=forms.Select(attrs={'size': 1, 'onchange':'set_cost()'}))
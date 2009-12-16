# -*- coding=utf-8 -*-
from django import forms

class LoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        
        self.base_fields['username'] = forms.CharField(label=u"Имя пользователя")
        self.base_fields['password'] =  forms.CharField(label=u"Пароль", widget=forms.PasswordInput())
        super(LoginForm, self).__init__(*args, **kwargs)
        
class UserInfo(forms.Form):
    def __init__(self):
        
        self.base_fields['contract_number'] = forms.CharField(label = u"№ договора")
        self.base_fields['username'] = forms.CharField(label = u"Имя пользователя")
        self.base_fileds['fio'] = forms.CharField(label = u"Ф.И.О")
        self.base_fields['city'] = forms.CharField(label = u"Город")
        self.base_fields['state'] = forms.CharField(label = u"Улица")
        self.base_fields['house'] = forms.CharField(label = u"Дом")
        self.base_fields['building'] = forms.CharField(label = u"Корпус")
        self.base_fields['flat'] = forms.CharField(label = u"Квартира")
        self.base_fields['phone'] = forms.CharField(label = u"Телефон")
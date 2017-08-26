# -*- encoding: utf-8 -*-

from captcha.fields import CaptchaField
from django import forms
from django.utils.translation import ugettext as _

from billservice.models import RegistrationRequest


class EmailForm(forms.Form):
    new_email = forms.EmailField(
        label=_(u"Новый e-mail"),
        required=False,
        error_messages={
            'required': _(u'Обязательное поле!')
        }
    )
    repeat_email = forms.EmailField(
        label=_(u"Повторите e-mail"),
        required=False,
        error_messages={
            'required': _(u'Обязательное поле!')
        }
    )


class PasswordForm(forms.Form):
    old_password = forms.CharField(
        label=_(u"Старый пароль"),
        required=True,
        widget=forms.PasswordInput,
        error_messages={
            'required': _(u'Обязательное поле!')
        }
    )
    new_password = forms.CharField(
        label=_(u"Новый пароль"),
        required=True,
        widget=forms.PasswordInput,
        error_messages={
            'required': _(u'Обязательное поле!')
        }
    )
    repeat_password = forms.CharField(
        label=_(u"Повторите пароль"),
        required=True,
        widget=forms.PasswordInput,
        error_messages={
            'required': _(u'Обязательное поле!')
        }
    )


class SimplePasswordForm(forms.Form):
    new_password = forms.CharField(
        label=_(u"Новый пароль"),
        required=True,
        widget=forms.PasswordInput,
        error_messages={
            'required': _(u'Обязательное поле!')
        }
    )
    repeat_password = forms.CharField(
        label=_(u"Повторите"),
        required=True,
        widget=forms.PasswordInput,
        error_messages={
            'required': _(u'Обязательное поле!')
        }
    )


class LoginForm(forms.Form):
    username = forms.CharField(
        label='',
        required=True,
        error_messages={
            'required': _(u'Вы не ввели имя пользователя!')
        }
    )
    password = forms.CharField(
        label='', widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = _(u"Логин")
        self.fields['password'].widget.attrs['placeholder'] = _(u"Пароль")


class RegisterForm(forms.ModelForm):
    captcha = CaptchaField()

    class Meta:
        model = RegistrationRequest
        fields = '__all__'

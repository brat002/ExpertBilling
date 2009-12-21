# -*- encoding: utf-8 -*-
from django import forms
from datetime import datetime, date
from billservice.models import Account, SystemUser, SystemGroup
from helpdesk.models import TICKET_STATUS, TICKET_TYPE, TICKET_ADDITIONAL_TYPE, SOURCE_TYPES, PRIORITY_TYPES

def get_owner():
    owner_list = [('', '---'),] 
    for group in SystemGroup.objects.all():
        group_tuple = ('systemgroup_'+str(group.id), group.name)
        owner_list.append(group_tuple)
        for user in group.get_users():
            user_tuple = ('systemuser_'+str(user.id), '---'+user.username)
            owner_list.append(user_tuple)
    return owner_list 

class LoginForm(forms.Form):
    username = forms.CharField(label=u"Имя пользователя", required = True, error_messages={'required':u'Вы не ввели имя пользователя!'})
    password = forms.CharField(label=u"Пароль", widget=forms.PasswordInput, required = False)

class TicketForm(forms.Form):
    user = forms.ChoiceField(label=u"Создатель", widget=forms.Select(), choices=[(x.id, x.username) for x in Account.objects.all()], required = True, error_messages={'required':u'Вы не выбрали создателя!'})
    assigned_to = forms.ChoiceField(label=u"Исполнитель", widget=forms.Select(), choices=get_owner(), required = False) 
    source = forms.ChoiceField(label=u"Источник", widget=forms.Select(), choices=SOURCE_TYPES, required = False)
    priority = forms.ChoiceField(label=u"Приоритет", widget=forms.Select(), choices=PRIORITY_TYPES, required = False)
    email = forms.CharField(label=u"E-mail", required = False)
    adress = forms.CharField(label=u"Адрес", required = False)
    phone = forms.IntegerField(label=u"Телефон", required = False)
    subject = forms.CharField(label=u"Тема", error_messages={'required':u'Введите тему!'})
    text = forms.CharField(label = u"Описание тикета", error_messages={'required':u'Введите описание!'}, widget=forms.Textarea())
    type = forms.ChoiceField(label=u"Тип", widget=forms.Select(), choices=TICKET_TYPE)
    status = forms.ChoiceField(label=u"Статус", widget=forms.Select(), choices=TICKET_STATUS)
    additional_status = forms.ChoiceField(label=u"Дополнительный статус", widget=forms.Select(), choices=TICKET_ADDITIONAL_TYPE)
    hide_comment = forms.CharField(label = u"Скрытый комментарий", widget=forms.Textarea(), required = False)
    
    
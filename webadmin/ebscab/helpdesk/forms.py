# -*- encoding: utf-8 -*-
from django import forms
from datetime import datetime, date
from billservice.models import Account, SystemUser, SystemGroup
from helpdesk.models import TICKET_STATUS, TICKET_TYPE, TICKET_ADDITIONAL_TYPE, SOURCE_TYPES, PRIORITY_TYPES

ACTIVE = 1
NOT_ACTIVE_NOT_WRITING_OFF  = 2
NOT_ACTIVE_WRITING_OFF = 3 

ACCOUNT_STATUS = (
                  (ACTIVE, u'Активен'),
                  (NOT_ACTIVE_NOT_WRITING_OFF, u'Неактивен, не списывать периодические услуги'),
                  (NOT_ACTIVE_WRITING_OFF, u'Неактивен, списывать периодические услуги'),
                  )

def get_owner():
    owner_list = [('', ''),] 
    for group in SystemGroup.objects.all():
        group_tuple = ('systemgroup_'+str(group.id), group.name)
        owner_list.append(group_tuple)
        for user in group.get_users():
            user_tuple = ('systemuser_'+str(user.id), group.name+'|'+user.username)
            owner_list.append(user_tuple)
    return owner_list 


class CheckboxSelectSimpleMultiple(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        from itertools import chain
        from django.utils.encoding import force_unicode
        from django.utils.html import conditional_escape
        from django.utils.safestring import mark_safe
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<li><label%s><div class="select_widget">%s</div> %s</label></li>' % (label_for, option_label, rendered_cb))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))


def get_systemusers():
    return [(user.id, user.username)  for user in SystemUser.objects.all()]
        

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
    additional_status = forms.ChoiceField(label=u"Дополнительный статус", widget=forms.Select(), choices=TICKET_ADDITIONAL_TYPE)
    hide_comment = forms.CharField(label = u"Скрытый комментарий", widget=forms.Textarea(), required = False)
    
class TicketEditForm(forms.Form): 
    status = forms.ChoiceField(label=u"Статус", widget=forms.Select(), choices=TICKET_STATUS)
    additional_status = forms.ChoiceField(label=u"Дополнительный статус", widget=forms.Select(), choices=TICKET_ADDITIONAL_TYPE, required = False)
    assigned_to = forms.ChoiceField(label=u"Перевести", choices=get_owner(), required = False)
    hide_comment = forms.CharField(label = u"Заметка", widget=forms.Textarea(), required = False)
    send = forms.MultipleChoiceField(label=u"Уведомить", choices=get_systemusers(), widget=CheckboxSelectSimpleMultiple(), required = False)
    
class CommentForm(forms.Form):
    text = forms.CharField(label = u"Введите комментарий", widget=forms.Textarea(), required = True, error_messages={'required':u'Введите комментарий!'})
    time = forms.IntegerField(label = u"Затрачено времени", required = False)
    
class UserFilter(forms.Form):
    id__contains = forms.IntegerField(label = u"Номер договора", required = False, widget = forms.TextInput(attrs={'class':'data',}))
    username__contains = forms.CharField(label = u"Username", required = False, widget = forms.TextInput(attrs={'class':'data',}))
    fullname__contains = forms.CharField(label = u"Ф.И.О.", required = False, widget = forms.TextInput(attrs={'class':'data',}))
    city__contains = forms.CharField(label = u"Город", required = False, widget = forms.TextInput(attrs={'class':'data',}))
    street__contains = forms.CharField(label = u"Улица", required = False, widget = forms.TextInput(attrs={'class':'data',}))
    house__contains = forms.IntegerField(label = u"Дом", required = False, widget = forms.TextInput(attrs={'class':'data',})) 
    house_bulk__contains = forms.IntegerField(label = u"Корпус", required = False, widget = forms.TextInput(attrs={'class':'data',}))
    room__contains = forms.IntegerField(label = u"Квартира", required = False, widget = forms.TextInput(attrs={'class':'data',}))


class ChangeAccountStatusForm(forms.Form):
    status = forms.ChoiceField(label=u"Статус", widget=forms.Select(), choices=ACCOUNT_STATUS, required = False) 
    

class ChangeAccountPasswordForm(forms.Form):
    password = forms.CharField(label=u"Пароль", required = False)
    
class ChangeUserInformation(forms.Form):
    email = forms.CharField(label = 'e-mail', required = False)
    password = forms.CharField(label = 'Пароль', required = False, widget = forms.PasswordInput())
    
    
    
    
    
    
     
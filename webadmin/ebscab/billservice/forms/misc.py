# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _

from dynamicmodel.models import DynamicSchemaField
from sendsms.utils import get_backend_choices

from billservice.models import Account, SpeedLimit, SystemUser, Template


class DynamicSchemaFieldForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = DynamicSchemaField
        fields = '__all__'


class SendSmsForm(forms.Form):
    bc = get_backend_choices()
    accounts = forms.ModelMultipleChoiceField(
        queryset=Account.objects.filter(phone_m__isnull=False),
        widget=forms.widgets.MultipleHiddenInput
    )
    backend = forms.ChoiceField(
        label=_(u'Оператор'),
        choices=bc,
        initial=bc[0][0] if bc else '',
        widget=forms.widgets.Select(attrs={
            'rows': 4,
            'class': 'input-large span5'
        })
    )
    template = forms.ChoiceField(
        label=_(u'Шаблон'),
        choices=[],
        required=False,
        widget=forms.widgets.Select(attrs={
            'rows': 4,
            'class': 'input-large span5'
        })
    )
    body = forms.CharField(
        label=_(u'Сообщение'),
        widget=forms.widgets.Textarea(attrs={
            'id': 'id_sendsms_body',
            'rows': 4,
            'class': 'input-large span5'
        }),
        help_text=_(u"Можно использовать {{account.ballance}}, "
                    u"{{account.fullname}}, {{account.username}}, "
                    u"{{account.contract}}")
    )
    publish_date = forms.DateTimeField(
        label=_(u'Опубликовать'),
        help_text=_(u'Не указывайте, если сообщения должны быть отправлены '
                    u'сразу'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )

    def __init__(self, *args, **kwargs):
        super(SendSmsForm, self).__init__(*args, **kwargs)
        self.fields['template'].choices = [['', '---']] + \
            list(Template.objects.filter(
                type__id=11).values_list('body', 'name', ))


class StatististicForm(forms.Form):
    date_from = forms.DateField(
        label=_(u'с даты'), input_formats=('%d/%m/%Y',), required=False)
    date_to = forms.DateField(
        label=_(u'по дату'), input_formats=('%d/%m/%Y',), required=False)


class ActionLogFilterForm(forms.Form):
    systemuser = forms.ModelChoiceField(
        queryset=SystemUser.objects.all(), required=False)
    start_date = forms.DateTimeField(
        required=False,
        label=_(u'С'),
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    end_date = forms.DateTimeField(
        required=False,
        label=_(u'По'),
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )


class SpeedLimitForm(forms.ModelForm):

    class Meta:
        model = SpeedLimit
        fields = '__all__'

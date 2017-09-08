# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from billservice.models import SystemUser
from object_log.models import LogAction


class LogItemFilterForm(forms.Form):
    id = forms.IntegerField(label=_(u'ID объекта'), required=False)
    ct = forms.ModelChoiceField(
        label=_(u'Тип объекта'),
        queryset=ContentType.objects.all(),
        required=False
    )
    action = forms.ModelMultipleChoiceField(
        queryset=LogAction.objects.all(), label=_(u'Действие'), required=False)
    user = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(
            username__in=[
                x.get('username')
                for x in SystemUser.objects.all().values('username')
            ]
        ),
        label=_(u'Администратор'),
        required=False
    )
    start_date = forms.DateTimeField(
        label=_(u'С даты'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    end_date = forms.DateTimeField(
        label=_(u'По дату'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )

    def __init__(self, *args, **kwargs):
        super(LogItemFilterForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget.attrs['size'] = 15
        self.fields['action'].widget.attrs['size'] = 10

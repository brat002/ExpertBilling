#-*-coding: utf-8 -*-

from django import forms
from object_log.models import LogAction
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from billservice.models import SystemUser
from billservice.widgets import SplitDateTimeWidget

class LogItemFilterForm(forms.Form):
    id = forms.IntegerField(label=u'ID объекта', required=False)
    ct = forms.ModelChoiceField(label=u'Тип объекта', queryset=ContentType.objects.all(),  required=False)
    action = forms.ModelMultipleChoiceField(queryset=LogAction.objects.all(), label=u'Действие', required=False)
    user = forms.ModelMultipleChoiceField(queryset=User.objects.filter(username__in=[x.get('username') for x in SystemUser.objects.all().values('username')]), label=u'Администратор', required=False)
    start_date = forms.DateTimeField(label=u'С даты', required=False, widget=SplitDateTimeWidget(date_attrs={'class':'input-small datepicker'}, time_attrs={'class':'input-small timepicker'}))
    end_date = forms.DateTimeField(label=u'По дату', required=False, widget=SplitDateTimeWidget(date_attrs={'class':'input-small datepicker'}, time_attrs={'class':'input-small timepicker'}))
    
    
    def __init__(self, *args, **kwargs):
        super(LogItemFilterForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget.attrs['size'] =15
        self.fields['action'].widget.attrs['size'] =10
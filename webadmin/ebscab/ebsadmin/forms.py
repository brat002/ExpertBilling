#-*-coding: utf-8 -*-

from django import forms
from datetime import datetime, date
from django.forms import ModelForm
from billservice.models import Tariff, Account, Group, Tariff
from nas.models import Nas, TrafficClass

from billservice.forms import DateRangeField
from ajax_select.fields import AutoCompleteSelectMultipleField
from django.conf import settings
chartdata = {
'sessionsonline':{'name':u'Сессии пользователей', 'yname':u'Аккаунты', 'tabs':['accountsTab', 'nassesTab']},
#'sessionsdynamic':{'name':u'Динамика сессий', 'yname':u'Количество', 'tabs':['accountsTab', 'nassesTab']},
#'trafficclasses': {'name':u'Потребление трафика по классам трафика', 'yname':u'МБ', 'tabs':['classesTab', 'nassesTab']},
#'trafficgroups': {'name':u'Потребление трафика по группам трафика',  'yname':u'МБ','tabs':['accountsTab', 'groupsTab', 'nassesTab']},
'selectedaccountstraffic': {'name':u'Потребление трафика выбранными аккаунтами',  'yname':u'МБ', 'tabs':['accountsTab', 'groupsTab'], 'type': 'line'},
'accountstraffic': {'name':u'Потребление трафика аккаунтами(общее)',  'yname':u'МБ', 'tabs':['accountsTab', 'groupsTab']},
'nassestraffic': {'name':u'Потребление трафика по серверам доступа',  'yname':u'МБ', 'tabs':['nassesTab', 'groupsTab'], 'type': 'line'},
'tariffstraffic': {'name':u'Распределение трафика по тарифам', 'tabs':['groupsTab'], 'type': 'pie'},
#'distrtrafficclasses': {'name':u'Распределение трафика по классам трафика', 'tabs':['classesTab', 'nassesTab'], 'type': 'pie'},
'distrtrafficgroups': {'name':u'Распределение трафика по группам трафика', 'tabs':['accountsTab', 'groupsTab', 'nassesTab'], 'type': 'pie'},
'distraccountstraffic': {'name':u'Распределение трафика по аккаунтам ', 'tabs':['accountsTab', 'groupsTab'], 'type': 'pie'},
'distnassestraffic': {'name':u'Распределение трафика по серверам доступа', 'tabs':['nassesTab', 'groupsTab'], 'type': 'pie'},
'distraccountstoptraffic': {'name':u'ТОП 10 по потреблению трафика ', 'tabs':[ 'groupsTab'], 'type': 'pie'},
'accountsincrease': {'name':u'Прирост абонентской базы ',  'yname':u'Количество', 'tabs':[], 'type': 'spline'},
#'moneydynamic': {'name':u'Динамика прибыли ', 'tabs':[]},
'disttransactiontypessumm': {'name':u'Распределение платежей/списаний по типам (сумма) ', 'units': settings.CURRENCY, 'tabs':[], 'type': 'pie'},
'disttransactiontypescount': {'name':u'Распределение платежей/списаний по типам(кол-во)', 'units': 'шт.', 'tabs':[], 'type': 'pie'},
'balancehistory': {'name':u'Динамика изменения баланса ',  'yname':u'Баланс', 'tabs':['accountsTab', ], 'yaxis': u"Баланс", "type": "line"},
}

groupings = (
               ('minutes', u"Минута", ),
               ('hours', u"Час", ),
               ( 'days', u"День",),
               ('months', u'Месяц', ),
               )
        
reporttypes = [
               ['line', u"Линия", ],
               ['spline', u"Сплайн", ],
               [ 'column', u'Вертикальная',],
               ['bar', u'Горизонтальная', ],
               ['pie', u'Пирог', ],
               ]
        

class ReportForm(forms.Form):
    report = forms.ChoiceField(choices=sorted([(x, chartdata[x].get('name')) for x in chartdata],  key=lambda k: k[1]), required=True, widget = forms.HiddenInput())
    accounts = AutoCompleteSelectMultipleField( 'account_fts', required = False)
    
    classes = forms.ModelMultipleChoiceField(queryset=TrafficClass.objects.all(), required=False)
    nasses = forms.ModelMultipleChoiceField(queryset=Nas.objects.all(), required=False)
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)
    tariffs = forms.ModelMultipleChoiceField(queryset=Tariff.objects.all(), required=False)
    daterange = DateRangeField(label=u'Диапазон', required=False )
    
    reporttype = forms.ChoiceField(choices=reporttypes, required=False)
    trafficsource = forms.CharField(required=False)
    grouping = forms.ChoiceField(choices=groupings, required=False)
    animation = forms.CheckboxInput()
    shadow = forms.CheckboxInput()
    legend = forms.CheckboxInput()
    back = forms.CharField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['nasses'].widget.attrs['size'] =10
        self.fields['tariffs'].widget.attrs['size'] =10
        self.fields['groups'].widget.attrs['size'] =10
        self.fields['classes'].widget.attrs['size'] =10
        
class LogViewer(forms.Form):
    log = forms.ChoiceField(choices=(), label=u'Лог')
    lines = forms.IntegerField(label=u'Количество последних строк', initial=100)
    full = forms.BooleanField(required=False)

class TrafficNodesUploadForm(forms.Form):
    nodes_file = forms.FileField(label=u"Файл с сетями", help_text=u"Сети должны располагаться построчно")
    networks = forms.CharField(label=u"Наши сети(построчно)", required=True, widget=forms.widgets.Textarea)

class TableColumnsForm(forms.Form):
    table_name = forms.CharField(widget = forms.widgets.HiddenInput)
    columns = forms.MultipleChoiceField(choices=(), widget = forms.widgets.SelectMultiple(attrs={'class': 'columns'}))
    
    
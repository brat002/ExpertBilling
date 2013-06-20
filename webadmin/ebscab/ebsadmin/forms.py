#-*-coding: utf-8 -*-

from django import forms
from datetime import datetime, date
from django.forms import ModelForm
from billservice.models import Tariff, Account, Group, Tariff
from nas.models import Nas, TrafficClass
from django.utils.translation import ugettext as _

from ajax_select.fields import AutoCompleteSelectMultipleField
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
chartdata = {
'sessionsonline':{'name': _(u'Сессии пользователей'), 'yname': _(u'Аккаунты'), 'tabs':['accountsTab', 'nassesTab']},
#'sessionsdynamic':{'name':u'Динамика сессий', 'yname':u'Количество', 'tabs':['accountsTab', 'nassesTab']},
#'trafficclasses': {'name':u'Потребление трафика по классам трафика', 'yname':u'МБ', 'tabs':['classesTab', 'nassesTab']},
#'trafficgroups': {'name':u'Потребление трафика по группам трафика',  'yname':u'МБ','tabs':['accountsTab', 'groupsTab', 'nassesTab']},
'selectedaccountstraffic': {'name':_(u'Потребление трафика выбранными аккаунтами'),  'yname':_(u'МБ'), 'tabs':['accountsTab', 'groupsTab'], 'type': 'line'},
'accountstraffic': {'name':_(u'Потребление трафика аккаунтами(общее)'),  'yname':_(u'МБ'), 'tabs':['accountsTab', 'groupsTab']},
'nassestraffic': {'name':_(u'Потребление трафика по серверам доступа'),  'yname':_(u'МБ'), 'tabs':['nassesTab', 'groupsTab'], 'type': 'line'},
'tariffstraffic': {'name':_(u'Распределение трафика по тарифам'), 'tabs':['groupsTab'], 'type': 'pie'},
#'distrtrafficclasses': {'name':u'Распределение трафика по классам трафика', 'tabs':['classesTab', 'nassesTab'], 'type': 'pie'},
'distrtrafficgroups': {'name':_(u'Распределение трафика по группам трафика'), 'tabs':['accountsTab', 'groupsTab', 'nassesTab'], 'type': 'pie'},
'distraccountstraffic': {'name':_(u'Распределение трафика по аккаунтам '), 'tabs':['accountsTab', 'groupsTab'], 'type': 'pie'},
'distnassestraffic': {'name':_(u'Распределение трафика по серверам доступа'), 'tabs':['nassesTab', 'groupsTab'], 'type': 'pie'},
'distraccountstoptraffic': {'name':_(u'ТОП 10 по потреблению трафика '), 'tabs':[ 'groupsTab'], 'type': 'pie'},
'accountsincrease': {'name':_(u'Прирост абонентской базы '),  'yname':_(u'Количество'), 'tabs':[], 'type': 'spline'},
#'moneydynamic': {'name':u'Динамика прибыли ', 'tabs':[]},
'disttransactiontypessumm': {'name':_(u'Распределение платежей/списаний по типам (сумма) '), 'units': settings.CURRENCY, 'tabs':[], 'type': 'pie'},
'disttransactiontypescount': {'name':_(u'Распределение платежей/списаний по типам(кол-во)'), 'units': _('шт.'), 'tabs':[], 'type': 'pie'},
'balancehistory': {'name':_(u'Динамика изменения баланса '),  'yname':u'Баланс', 'tabs':['accountsTab', ], 'yaxis': _(u"Баланс"), "type": "line"},
}

groupings = (
               ('minutes', _(u"Минута"), ),
               ('hours', _(u"Час"), ),
               ( 'days', _(u"День"),),
               ('months', _(u'Месяц'), ),
               )
        
reporttypes = [
               ['line', _(u"Линия"), ],
               ['spline', _(u"Кривая"), ],
               [ 'column', _(u'Вертикальная'),],
               ['bar', _(u'Горизонтальная'), ],
               ['pie', _(u'Пирог'), ],
               ]
        

class ReportForm(forms.Form):
    report = forms.ChoiceField(choices=sorted([(x, chartdata[x].get('name')) for x in chartdata],  key=lambda k: k[1]), required=True, widget = forms.HiddenInput())
    accounts = AutoCompleteSelectMultipleField( 'account_fts', required = False)
    
    classes = forms.ModelMultipleChoiceField(queryset=TrafficClass.objects.all(), required=False)
    nasses = forms.ModelMultipleChoiceField(queryset=Nas.objects.all(), required=False)
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)
    tariffs = forms.ModelMultipleChoiceField(queryset=Tariff.objects.all(), required=False)
    date_start = forms.DateTimeField(label=_(u'С'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    date_end = forms.DateTimeField(label=_(u'По'), required = False, widget=forms.widgets.DateTimeInput(attrs={'class':'datepicker'}))
    
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
    lines = forms.IntegerField(label=_(u'Количество последних строк'), initial=100)
    full = forms.BooleanField(required=False)

class TrafficNodesUploadForm(forms.Form):
    traffic_class = forms.ModelChoiceField(queryset = TrafficClass.objects.all(), label=u'Класс трафика')
    networks = forms.CharField(required=True, label=u'Наши сети (построчно)', widget = forms.widgets.Textarea, help_text = _(u'Перечислите ваши сети построчно. Последняя строка не должна быть пустой.'))
    nodes_file = forms.FileField(label=_(u"Файл с сетями назначения"), help_text=_(u'Пример:<br/> 192.168.11.0/24<br/>172.168.0.0/16<br />127.0.0.0/8'))



class TableColumnsForm(forms.Form):
    table_name = forms.CharField(widget = forms.widgets.HiddenInput)
    columns = forms.MultipleChoiceField(choices=(), widget = forms.widgets.SelectMultiple(attrs={'class': 'columns', 'size': 10}))
    
    
#-*- coding=utf-8 -*-

import django_tables2 as django_tables
from django_tables2.utils import A

from django_tables2_reports.tables import TableReport
from django.utils.safestring import mark_safe
from django.utils.html import escape

from helpdesk.models import Ticket
import itertools

prio={
      1: 'label-important', 
      2: 'label-warning',
      3: 'label-success',
      4: 'label-info',
      4: 'label-inverse',
      }

class FormatUrlColumn(django_tables.Column):
    def render(self, value):
        return value.get_absolute_url()

class TicketTable(TableReport):
    #id = django_tables.LinkColumn('sessage_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    #account = django_tables.LinkColumn('account_edit', verbose_name=u'Аккаунт', get_params={'id':A('pk')})
    ticket = django_tables.TemplateColumn("<a href='{{record.get_absolute_url}}'>{{record.ticket}}</a>", verbose_name='Заявка')
    title = django_tables.TemplateColumn("<a href='{{record.get_absolute_url}}' data='{{record.id}}' class='title-tooltip'>{{record.title}}</a>", verbose_name='Тема')
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    def render_priority(self, value, record):
        return mark_safe('<span class="label %s">%s</span>' % (prio.get(record.priority), value))
    
    class Meta:
        model = Ticket
        #fields = ("id", 'service', 'activation_count_period', 'activation_count', 'type', 'd')
        fields = ('ticket', 'title', 'queue', 'owner', 'created', 'modified', 'priority', 'status', 'resolution')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 


class UnassignedTicketTable(TableReport):
    #id = django_tables.LinkColumn('sessage_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    #account = django_tables.LinkColumn('account_edit', verbose_name=u'Аккаунт', get_params={'id':A('pk')})
    ticket = django_tables.TemplateColumn("<a href='{{record.get_absolute_url}}'>{{record.ticket}}</a>", verbose_name='Заявка')
    title = django_tables.TemplateColumn("<a href='{{record.get_absolute_url}}' data='{{record.id}}' class='title-tooltip'>{{record.title}}</a>", verbose_name='Тема')
    action = django_tables.TemplateColumn("<a href='{{record.get_absolute_url}}?take'  class='btn btn-primary btn-mini'>Принять</a>&nbsp;<a class='btn btn-danger btn-mini' href='{% url helpdesk_delete record.id %}'>Удалить</a>", verbose_name=' ', orderable=False)
    #d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    def render_priority(self, value, record):
        return mark_safe('<span class="label %s">%s</span>' % (prio.get(record.priority), value))
    
    class Meta:
        model = Ticket
        #fields = ("id", 'service', 'activation_count_period', 'activation_count', 'type', 'd')
        fields = ('ticket', 'title', 'queue', 'owner', 'created', 'modified', 'priority', 'status', 'resolution', 'action')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 
        
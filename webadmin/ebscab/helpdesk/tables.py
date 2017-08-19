# -*- coding: utf-8 -*-

from django.utils.safestring import mark_safe

from django_tables2 import columns
from django_tables2_reports.tables import TableReport

from helpdesk.models import prio, Ticket


class FormatUrlColumn(columns.Column):

    def render(self, value):
        return value.get_absolute_url()


class TicketTable(TableReport):
    ticket = columns.TemplateColumn(
        "<a href='{{record.get_absolute_url}}'>{{record.ticket}}</a>",
        verbose_name='Заявка'
    )
    title = columns.TemplateColumn(
        "<a href='{{record.get_absolute_url}}' data='{{record.id}}' "
        "class='title-tooltip'>{{record.title}}</a>",
        verbose_name='Тема'
    )
    d = columns.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm'>"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )

    def __init__(self, *args, **argv):
        super(TicketTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__

    def render_priority(self, value, record):
        return mark_safe('<span class="label %s">%s</span>' %
                         (prio.get(record.priority), value))

    class Meta:
        model = Ticket
        configurable = True
        available_fields = ('ticket', 'title', 'queue', 'owner', 'created',
                            'modified', 'priority', 'status', 'resolution')
        attrs = {
            'class': 'table table-striped table-bordered table-condensed'
        }


class UnpagedTicketTable(TableReport):
    ticket = columns.TemplateColumn(
        "<a href='{{record.get_absolute_url}}'>{{record.ticket}}</a>",
        verbose_name='Заявка'
    )
    title = columns.TemplateColumn(
        "<a href='{{record.get_absolute_url}}' data='{{record.id}}' "
        "class='title-tooltip'>{{record.title}}</a>",
        verbose_name='Тема'
    )
    d = columns.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm'>"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )

    def __init__(self, *args, **argv):
        super(UnpagedTicketTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__

    def render_priority(self, value, record):
        return mark_safe('<span class="label %s">%s</span>' %
                         (prio.get(record.priority), value))

    class Meta:
        model = Ticket

        fields = ('ticket', 'title', 'queue', 'owner', 'created', 'modified',
                  'priority', 'status', 'resolution')
        attrs = {
            'class': 'table table-striped table-bordered table-condensed'
        }


class UnassignedTicketTable(TableReport):
    ticket = columns.TemplateColumn(
        "<a href='{{record.get_absolute_url}}'>{{record.ticket}}</a>",
        verbose_name='Заявка'
    )
    title = columns.TemplateColumn(
        "<a href='{{record.get_absolute_url}}' data='{{record.id}}' "
        "class='title-tooltip'>{{record.title}}</a>",
        verbose_name='Тема'
    )
    action = columns.TemplateColumn(
        '''\
<a href='{{record.get_absolute_url}}?take' class='btn btn-primary btn-mini'>\
Принять</a>&nbsp;<a class='btn btn-danger btn-mini' \
href='{% url 'helpdesk_delete' record.id %}'>Удалить</a>''',
        verbose_name=' ',
        orderable=False
    )

    def __init__(self, *args, **argv):
        super(UnassignedTicketTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__

    def render_priority(self, value, record):
        return mark_safe('<span class="label %s">%s</span>' %
                         (prio.get(record.priority), value))

    class Meta:
        model = Ticket
        configurable = False
        fields = ('ticket', 'title', 'queue', 'owner', 'created', 'modified',
                  'priority', 'status', 'resolution', 'action')
        attrs = {
            'class': 'table table-striped table-bordered table-condensed'
        }

# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from django_tables2.columns import Column, LinkColumn
from django_tables2.utils import A
from helpdesk.models import Ticket

from ebsadmin.columns import FormatDateTimeColumn
from ebsadmin.tables.base import EbsadminTableReport


class TicketTable(EbsadminTableReport):
    id = LinkColumn('helpdesk_view', args=[A('id')])
    title = LinkColumn('helpdesk_view', args=[A('id')])
    created = FormatDateTimeColumn(verbose_name=_(u'Создан'))
    status = Column(
        verbose_name=_(u'Статус'),
        accessor=A('_get_status')
    )

    class Meta(EbsadminTableReport.Meta):
        model = Ticket
        configurable = True
        available_fields = (
            "id",
            'title',
            'queue',
            'created',
            'status',
            'priority'
        )

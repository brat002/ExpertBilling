# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from billservice.models import IPInUse, IPPool
from django_tables2.columns import Column, LinkColumn
from django_tables2.utils import A

from ebsadmin.columns import (
    FormatBlankColumn,
    FormatDateTimeColumn,
    showconfirmcolumn
)
from ebsadmin.tables.base import EbsadminTableReport


class IPInUseTable(EbsadminTableReport):
    datetime = FormatDateTimeColumn()
    disabled = FormatDateTimeColumn()

    class Meta(EbsadminTableReport.Meta):
        model = IPInUse


class IPPoolTable(EbsadminTableReport):
    id = LinkColumn('ippool_edit', get_params={'id': A('pk')})
    name = LinkColumn('ippool_edit', get_params={'id': A('pk')})
    next_ippool = FormatBlankColumn()
    pool_size = Column(
        verbose_name=_(u'IP в пуле'),
        accessor=A('get_pool_size'),
        orderable=False
    )
    used_ip = Column(
        verbose_name=_(u'Используется'),
        accessor=A('get_used_ip_count'),
        orderable=False)
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = IPPool
        configurable = True

# -*- coding: utf-8 -*-

import itertools

from django.utils.translation import ugettext_lazy as _

from billservice.models import Card, SaleCard
from django_tables2.columns import Column, CheckBoxColumn, LinkColumn
from django_tables2.utils import A

from ebsadmin.columns import (
    FormatBlankColumn,
    FormatDateTimeColumn,
    showconfirmcolumn
)
from ebsadmin.tables.base import EbsadminTableReport


class CardTable(EbsadminTableReport):
    row_number = Column(
        verbose_name="#", empty_values=(), orderable=False)
    start_date = FormatDateTimeColumn()
    end_date = FormatDateTimeColumn()
    created = FormatDateTimeColumn()
    salecard = FormatDateTimeColumn(verbose_name=_(
        u'Продана'), accessor=A('salecard.created'))
    activated = FormatDateTimeColumn()
    activated_by = FormatBlankColumn()
    tarif = FormatBlankColumn()
    nas = FormatBlankColumn()
    ippool = FormatBlankColumn()
    ext_id = FormatBlankColumn()
    d = CheckBoxColumn(
        verbose_name=' ', orderable=False, accessor=A('pk'))

    def __init__(self, *args, **kwargs):
        super(CardTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()

    def render_row_number(self):
        return '%d' % next(self.counter)

    class Meta(EbsadminTableReport.Meta):
        model = Card
        configurable = True
        available_fields = (
            'row_number',
            'id',
            'series',
            'nominal',
            'login',
            'pin',
            'type',
            'tarif',
            'nas',
            'salecard',
            'activated',
            'activated_by',
            'ippool',
            'created',
            'start_date',
            'end_date',
            'ext_id',
            'd'
        )
        exclude = ('ipinuse', 'disabled')


class SaleCardsTable(EbsadminTableReport):
    row_number = Column(
        verbose_name="#", empty_values=(), orderable=False)
    start_date = FormatDateTimeColumn()
    end_date = FormatDateTimeColumn()
    created = FormatDateTimeColumn()
    activated = FormatDateTimeColumn()
    tarif = FormatBlankColumn()
    nas = FormatBlankColumn()
    ippool = FormatBlankColumn()

    def render_row_number(self):
        value = getattr(self, '_counter', 0)
        self._counter = value + 1
        return '%d' % value

    def render_row_class(self, value, record):
        return 'disabled-row' if record.disabled else ''

    class Meta(EbsadminTableReport.Meta):
        model = Card
        configurable = True
        available_fields = (
            'row_number',
            'id',
            'series',
            'login',
            'pin',
            'nominal',
            'type',
            'tarif',
            'nas',
            'activated',
            'ippool',
            'created',
            'start_date',
            'end_date',
            'ext_id'
        )
        exclude = ('ipinuse', 'disabled', 'ip', 'activated_by', 'salecard')


class SaleCardTable(EbsadminTableReport):
    id = LinkColumn('salecard_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = SaleCard
        configurable = True
        exclude = ("tarif", 'nas')

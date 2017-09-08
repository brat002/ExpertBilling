# -*- coding: utf-8 -*-

from billservice.models import SettlementPeriod, SuspendedPeriod
from django_tables2.columns import LinkColumn
from django_tables2.utils import A

from ebsadmin.columns import (
    FormatBlankColumn,
    FormatDateTimeColumn,
    showconfirmcolumn
)
from ebsadmin.tables.base import EbsadminTable, EbsadminTableReport


class SuspendedPeriodTable(EbsadminTable):
    d = showconfirmcolumn()

    class Meta(EbsadminTable.Meta):
        model = SuspendedPeriod


class SettlementPeriodTable(EbsadminTableReport):
    id = LinkColumn(
        'settlementperiod_edit', get_params={'id': A('pk')})
    name = LinkColumn(
        'settlementperiod_edit', get_params={'id': A('pk')})
    time_start = FormatDateTimeColumn()
    length = FormatBlankColumn()

    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = SettlementPeriod

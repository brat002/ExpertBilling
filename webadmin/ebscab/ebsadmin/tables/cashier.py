# -*- coding: utf-8 -*-

import itertools

from django.utils.translation import ugettext_lazy as _

from billservice.models import Transaction
from django_tables2.columns import Column, LinkColumn, TemplateColumn
from django_tables2.utils import A

from ebsadmin.columns import (
    FormatBlankColumn,
    FormatFloatColumn,
    FormatDateTimeColumn,
    RadioColumn
)
from ebsadmin.tables.base import EbsadminTableReport


class CashierReportTable(EbsadminTableReport):
    summ = FormatFloatColumn(verbose_name=_(u'Сумма'))
    fullname = Column(
        verbose_name=u'ФИО', accessor=A('account.fullname'))
    address = TemplateColumn(
        (u"{{record.account.street|default:''}} "
         u"{{record.account.house|default:''}}-"
         u"{{record.account.room|default:''}}"),
        orderable=False
    )
    prev_balance = FormatFloatColumn(verbose_name=_(u'Предыдущий баланс'))
    created = FormatDateTimeColumn(verbose_name=_(u'Создан'))

    class Meta(EbsadminTableReport.Meta):
        model = Transaction
        configurable = True
        exclude = ('approved', 'accounttarif', 'tariff')


class AccountsCashierReportTable(EbsadminTableReport):
    d = RadioColumn(verbose_name=' ', orderable=False, accessor=A('pk'))
    row_number = Column(
        verbose_name=u'#', empty_values=(), orderable=False)
    username = LinkColumn(
        'account_edit', verbose_name=_(u'Логин'), get_params={'id': A('pk')})
    contract = FormatBlankColumn(verbose_name=_(u'Договор'))
    fullname = FormatBlankColumn()
    tariff = FormatBlankColumn()
    address = TemplateColumn(
        (u"{{record.city|default:''}} {{record.street|default:''}} "
         u"{{record.house|default:''}}-{{record.room|default:''}}"),
        orderable=False
    )
    entrance = Column(verbose_name=_(u'Подъезд'))
    row = Column(verbose_name=_(u'Этаж'))
    ballance = FormatFloatColumn()
    bonus_ballance = FormatFloatColumn()

    def __init__(self, *args, **kwargs):
        super(AccountsCashierReportTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()

    def render_row_number(self):
        return '%d' % next(self.counter)

    class Meta(EbsadminTableReport.Meta):
        pass

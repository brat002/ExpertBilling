# -*- coding: utf-8 -*-

import itertools

from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from billservice.models import Account, AccountGroup, SubAccount
from django_tables2.columns import (
    CheckBoxColumn,
    Column,
    LinkColumn,
    TemplateColumn
)
from django_tables2.rows import BoundRows
from django_tables2.utils import A

from ebsadmin.columns import (
    FormatBlankColumn,
    FormatDateTimeColumn,
    FormatFloatColumn,
    modallinkcolumn,
    showconfirmcolumn
)
from ebsadmin.tables.base import EbsadminTable, EbsadminTableReport


class AccountsReportTable(EbsadminTableReport):
    row_number = Column(
        verbose_name='#', empty_values=(), orderable=False)
    username = LinkColumn(
        'account_edit', verbose_name=_(u'Логин'), get_params={'id': A('pk')})
    contract = FormatBlankColumn(verbose_name=_(u'Договор'))
    fullname = FormatBlankColumn()
    address = TemplateColumn(
        (u"{{record.street|default:''}} "
         u"{{record.house|default:''}}-{{record.room|default:''}}"),
        orderable=False
    )
    entrance = Column(verbose_name=_(u'Подъезд'))
    row = Column(verbose_name=_(u'Этаж'))
    ballance = FormatFloatColumn()
    tariff = FormatBlankColumn(verbose_name=_(u"Тариф"), orderable=False)
    ips = FormatBlankColumn(verbose_name=_(u"IP"), orderable=False)
    d = CheckBoxColumn(
        verbose_name=' ', orderable=False, accessor=A('pk'))

    def __init__(self, form, *args, **kwargs):
        super(AccountsReportTable, self).__init__(form, *args, **kwargs)
        self.counter = itertools.count()
        self.footer_data = self.TableDataClass(
            data=[self.data.queryset.aggregate(ballance=Sum('ballance'))],
            table=self
        )
        self.footer = BoundRows(self.footer_data, self)

    def paginate(self, *args, **kwargs):
        super(AccountsReportTable, self).paginate(*args, **kwargs)

    def render_row_number(self):
        return '%d' % next(self.counter)

    class Meta(EbsadminTableReport.Meta):
        model = Account
        configurable = True
        exclude = ('password',)
        annotations = ('ballance',)


class AccountGroupTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='accountgroup_edit',
        modal_title=_(u'Изменить тип'),
        modal_id='hardwaretype-modal'
    )
    name = modallinkcolumn(
        url_name='accountgroup_edit',
        modal_title=_(u'Изменить тип'),
        modal_id='hardwaretype-modal'
    )
    cnt = TemplateColumn(
        '{{record.account_set.count}}', verbose_name=_(u'Количество'))
    d = showconfirmcolumn(message=_(u'Удалить?'))

    class Meta(EbsadminTableReport.Meta):
        model = AccountGroup


class SubAccountsTable(EbsadminTable):
    id = LinkColumn('subaccount', get_params={'id': A('pk')})
    username = LinkColumn(
        'subaccount', get_params={'id': A('pk')})
    nas = FormatBlankColumn()

    vpn_ip_address = FormatBlankColumn()
    ipn_ip_address = FormatBlankColumn()
    ipn_mac_address = FormatBlankColumn()

    d = showconfirmcolumn()

    class Meta(EbsadminTable.Meta):
        model = SubAccount
        configurable = True
        available_fields = (
            'id',
            'username',
            'nas',
            'vpn_ip_address',
            'ipn_ip_address',
            'ipn_mac_address',
            'd'
        )
        exclude = ('password',)


class BallanceHistoryTable(EbsadminTableReport):
    account__username = LinkColumn(
        'account_edit', get_params={'id': A('account')})
    balance = FormatBlankColumn(verbose_name=_(u'Новый баланс'))
    summ = FormatBlankColumn(verbose_name=_(u'Сумма'))
    datetime = FormatDateTimeColumn()

    class Meta(EbsadminTableReport.Meta):
        pass

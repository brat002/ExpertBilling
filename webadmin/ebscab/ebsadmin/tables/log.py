# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from billservice.models import PeriodicalServiceLog, SheduleLog
from django_tables2.columns import Column, LinkColumn, TemplateColumn
from django_tables2.utils import A
from object_log.models import LogItem
from radius.models import AuthLog

from ebsadmin.columns import (
    FormatBlankColumn,
    FormatDateTimeColumn,
    showconfirmcolumn
)
from ebsadmin.tables.base import EbsadminTableReport


class LogTable(EbsadminTableReport):
    user = FormatBlankColumn()
    changed_fields = FormatBlankColumn()

    class Meta(EbsadminTableReport.Meta):
        pass


class AuthLogTable(EbsadminTableReport):
    account = LinkColumn(
        'account_edit', get_params={'id': A('account.id')})
    subaccount = LinkColumn(
        'subaccount', get_params={'id': A('subaccount.id')})
    nas = FormatBlankColumn()
    datetime = FormatDateTimeColumn()

    class Meta(EbsadminTableReport.Meta):
        model = AuthLog
        exclude = ('type', 'id')


class ActionLogTable(EbsadminTableReport):
    object1 = Column(
        verbose_name=_(u'Объект'), accessor=A('object1'))

    class Meta(EbsadminTableReport.Meta):
        model = LogItem
        configurable = True
        availablwe_fields = (
            'id',
            'timestamp',
            'user',
            'action',
            'object_type1',
            'object1',
            'changed_data'
        )


class SheduleLogTable(EbsadminTableReport):
    d = TemplateColumn("  ", verbose_name=' ', orderable=False)
    accounttarif = FormatBlankColumn(verbose_name=_(u'Тариф аккаунта'))
    ballance_checkout = FormatDateTimeColumn(
        verbose_name=_(u'Доснятие до стоимости'))
    prepaid_traffic_reset = FormatDateTimeColumn(
        verbose_name=_(u'Обнуление предоплаченного трафика'))
    prepaid_traffic_accrued = FormatDateTimeColumn(
        verbose_name=_(u'Начисление предоплаченного трафика'))
    prepaid_time_reset = FormatDateTimeColumn(
        verbose_name=_(u'Обнуление предоплаченного времени'))
    prepaid_time_accrued = FormatDateTimeColumn(
        verbose_name=_(u'Начисление предоплаченного врeмени'))
    balance_blocked = FormatDateTimeColumn(
        verbose_name=_(u'Блокировка баланса'))

    class Meta(EbsadminTableReport.Meta):
        model = SheduleLog
        configurable = True


class PeriodicalServiceLogTable(EbsadminTableReport):
    d = showconfirmcolumn(message=_(u'Удалить? Удаление записи приведёт к '
                                    u'повторной тарификации указанной услуги '
                                    u'с начала подключения пользователя на '
                                    u'тарифный план.'))
    datetime = FormatDateTimeColumn(verbose_name=_(u'Дата'))

    class Meta(EbsadminTableReport.Meta):
        model = PeriodicalServiceLog
        configurable = True
        available_fields = ("id", 'accounttarif', 'service', 'datetime', 'd')

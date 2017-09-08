# -*- coding: utf-8 -*-

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from billservice.models import (
    AddonServiceTransaction,
    PeriodicalServiceHistory,
    TrafficTransaction,
    Transaction,
    TransactionType
)
from django_tables2.columns import Column, CheckBoxColumn, LinkColumn
from django_tables2.utils import A

from ebsadmin.columns import (
    FormatBlankColumn,
    FormatDateTimeColumn,
    FormatFloatColumn,
    showconfirmcolumn
)
from ebsadmin.constants import SERVICEMODEL_BY_TABLE
from ebsadmin.tables.base import EbsadminTableReport


class TransactionReportTable(EbsadminTableReport):
    id = FormatBlankColumn()
    account = LinkColumn(
        'account_edit',
        verbose_name=_(u'Аккаунт'),
        get_params={'id': A('account')},
        accessor=A('account__username')
    )
    fullname = FormatBlankColumn(
        verbose_name=_(u'ФИО'),
        accessor=A('account__fullname')
    )
    address = FormatBlankColumn(
        verbose_name=_(u'Адреc'),
        orderable=False,
        accessor=A('account__house')
    )
    type = FormatBlankColumn(verbose_name=_(u'Тип'), accessor=A('type__name'))
    prev_balance = FormatFloatColumn(verbose_name=_(u'Предыдущий баланс'))
    systemuser = FormatBlankColumn(
        verbose_name=_(u'Выполнил'),
        accessor=A('systemuser__username')
    )
    d = CheckBoxColumn(
        verbose_name=' ', orderable=False, accessor=A('id'))

    def render_d(self, value, record):
        return mark_safe(('<input type="checkbox" name="d" '
                          'value="billservice_transaction__%s">') % (value,))

    def render_summ(self, value, record):
        return '%.2f' % value

    def render_address(self, value, record):
        return '%s %s %s/%s' % (record.get('account__city__name'),
                                record.get('account__street'),
                                record.get('account__house'),
                                record.get('account__room'))

    class Meta(EbsadminTableReport.Meta):
        model = Transaction
        configurable = True
        exclude = ('tarif', 'approved', 'accounttarif')


class TransactionTypeTable(EbsadminTableReport):
    id = LinkColumn(
        'transactiontype_edit', get_params={'id': A('pk')})
    name = LinkColumn(
        'transactiontype_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn(message=_(u'Удалить проводку #{{ record.id }}?'))

    class Meta(EbsadminTableReport.Meta):
        model = TransactionType
        configurable = False


class TotalTransactionReportTable(EbsadminTableReport):
    tariff__name = FormatBlankColumn(verbose_name=_(u'Тариф'))
    id = FormatBlankColumn()
    account = LinkColumn(
        'account_edit',
        verbose_name=_(u'Аккаунт'),
        get_params={'id': A('account')},
        accessor=A('account__username')
    )
    fullname = FormatBlankColumn(
        verbose_name=_(u'ФИО'),
        accessor=A('account__fullname')
    )
    address = FormatBlankColumn(
        verbose_name=_(u'Адреc'),
        orderable=False,
        accessor=A('account__house')
    )
    bill = FormatBlankColumn(verbose_name=_(u'Платёжный документ'))
    description = FormatBlankColumn(verbose_name=_(u'Комментарий'))
    service_id = Column(verbose_name=_(u'ID Услуги'))
    type = FormatBlankColumn(verbose_name=_(u'Тип'), accessor=A('type__name'))
    is_bonus = FormatBlankColumn(verbose_name=_(u'Бонус'))
    summ = FormatFloatColumn(verbose_name=_(u'Сумма'))
    prev_balance = FormatFloatColumn(verbose_name=_(u'Предыдущий баланс'))
    created = FormatDateTimeColumn(verbose_name=_(u'Создана'))
    end_promise = FormatDateTimeColumn(verbose_name=_(u'Окончание о.п.'))
    promise_expired = FormatDateTimeColumn()
    d = CheckBoxColumn(
        verbose_name=' ', orderable=False, accessor=A('id'))

    def render_d(self, value, record):
        return mark_safe('<input type="checkbox" name="d" value="%s__%s">' %
                         (record.get('table'), value))

    def render_address(self, value, record):
        return '%s %s %s/%s' % (record.get('account__city__name'),
                                record.get('account__street'),
                                record.get('account__house'),
                                record.get('account__room'))

    def render_service_id(self, value, record):
        item = ''
        if value:
            model = SERVICEMODEL_BY_TABLE.get(record.get('table'))
            try:
                item = model.objects.get(id=value)
            except Exception, e:
                print e
                item = ''
        return unicode(item)

    class Meta(EbsadminTableReport.Meta):
        configurable = True
        available_fields = (
            "id",
            "account",
            "fullname",
            'address',
            "type",
            "summ",
            'prev_balance',
            "bill",
            "description",
            "end_promise",
            "service_id",
            "created",
            'd'
        )


class AddonServiceTransactionReportTable(EbsadminTableReport):
    id = FormatBlankColumn()
    account = LinkColumn(
        'account_edit',
        verbose_name=_(u'Аккаунт'),
        get_params={'id': A('account')},
        accessor=A('account__username')
    )
    fullname = FormatBlankColumn(
        verbose_name=_(u'ФИО'),
        accessor=A('account__fullname')
    )
    address = FormatBlankColumn(
        verbose_name=_(u'Адреc'),
        orderable=False,
        accessor=A('account__house')
    )
    type = FormatBlankColumn(verbose_name=_(u'Тип'), accessor=A('type__name'))
    prev_balance = FormatFloatColumn(
        verbose_name=_(u'Предыдущий баланс'))
    d = CheckBoxColumn(
        verbose_name=' ', orderable=False, accessor=A('id'))

    def render_d(self, value, record):
        return mark_safe(
            ('<input type="checkbox" name="d" '
             'value="billservice_addonservicetransaction__%s">') % (value,))

    def render_summ(self, value, record):
        return '%.2f' % value

    def render_address(self, value, record):
        return '%s %s %s/%s' % (record.get('account__city__name'),
                                record.get('account__street'),
                                record.get('account__house'),
                                record.get('account__room'))

    class Meta(EbsadminTableReport.Meta):
        model = AddonServiceTransaction
        configurable = True
        exclude = ('tarif', 'approved', 'accounttarif')


class TrafficTransactionReportTable(EbsadminTableReport):
    id = FormatBlankColumn()
    account__username = LinkColumn(
        'account_edit',
        verbose_name=_(u'Аккаунт'),
        get_params={'id': A('account')}
    )
    fullname = FormatBlankColumn(
        verbose_name=_(u'ФИО'), accessor=A('account__fullname'))
    address = FormatBlankColumn(
        verbose_name=_(u'Адреc'),
        orderable=False, accessor=A('account__house')
    )
    prev_balance = FormatFloatColumn(verbose_name=_(u'Предыдущий баланс'))
    d = CheckBoxColumn(
        verbose_name=' ', orderable=False, accessor=A('id'))

    def render_d(self, value, record):
        return mark_safe(
            ('<input type="checkbox" name="d" '
             'value="billservice_traffictransaction__%s">') % (value,))

    def render_address(self, value, record):
        return '%s %s %s/%s' % (record.get('account__city__name'),
                                record.get('account__street'),
                                record.get('account__house'),
                                record.get('account__room'))

    def render_summ(self, value, record):
        return '%.2f' % value

    class Meta(EbsadminTableReport.Meta):
        model = TrafficTransaction
        sequence = ('id', 'account__username', )
        configurable = True
        exclude = (
            'tarif',
            'traffictransmitservice',
            'accounttarif',
            'account'
        )


class PeriodicalServiceTransactionReportTable(EbsadminTableReport):
    id = FormatBlankColumn()
    account__username = LinkColumn(
        'account_edit',
        verbose_name=_(u'Аккаунт'),
        get_params={'id': A('account')}
    )
    fullname = FormatBlankColumn(
        verbose_name=_(u'ФИО'),
        accessor=A('account__fullname')
    )
    address = FormatBlankColumn(
        verbose_name=_(u'Адреc'),
        orderable=False,
        accessor=A('account__house')
    )
    service = Column(accessor=A('service__name'))
    prev_balance = FormatFloatColumn(verbose_name=_(u'Предыдущий баланс'))
    type = Column(accessor=A('type__name'))
    real_created = FormatDateTimeColumn()
    d = CheckBoxColumn(
        verbose_name=' ', orderable=False, accessor=A('id'))

    def render_d(self, value, record):
        return mark_safe(
            ('<input type="checkbox" name="d" '
             'value="billservice_periodicalservicehistory__%s">') % (value,))

    def render_address(self, value, record):
        return '%s %s %s/%s' % (record.get('account__city__name'),
                                record.get('account__street'),
                                record.get('account__house'),
                                record.get('account__room'))

    def render_summ(self, value, record):
        return '%.2f' % value

    class Meta(EbsadminTableReport.Meta):
        model = PeriodicalServiceHistory
        sequence = ('id', 'account__username', 'service')
        configurable = True
        exclude = ('tarif', 'approved', 'accounttarif')

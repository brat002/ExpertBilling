# -*- coding: utf-8 -*-

import itertools

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum

from billservice.models import (
    Account,
    AccountAddonService,
    AccountGroup,
    AccountHardware,
    AccountPrepaysRadiusTrafic,
    AccountPrepaysTime,
    AccountPrepaysTrafic,
    AccountSuppAgreement,
    AddonService,
    AddonServiceTarif,
    AddonServiceTransaction,
    Card,
    ContractTemplate,
    Dealer,
    Group,
    Hardware,
    HardwareType,
    IPInUse,
    IPPool,
    Manufacturer,
    Model,
    News,
    NotificationsSettings,
    OneTimeService,
    PeriodicalService,
    PeriodicalServiceHistory,
    PeriodicalServiceLog,
    PermissionGroup,
    PrepaidTraffic,
    RadiusAttrs,
    RadiusTrafficNode,
    RegistrationRequest,
    SaleCard,
    SettlementPeriod,
    SheduleLog,
    SubAccount,
    SuppAgreement,
    SuspendedPeriod,
    Switch,
    SystemUser,
    Tariff,
    Template,
    TimeAccessNode,
    TimeSpeed,
    TPChangeRule,
    TrafficLimit,
    TrafficTransaction,
    TrafficTransmitNodes,
    Transaction,
    TransactionType
)

from django_tables2 import columns, rows, tables
from django_tables2.utils import A, AttributeDict
from django_tables2_reports.tables import TableReport
from dynamicmodel.models import DynamicSchemaField
from getpaid.models import Payment
from helpdesk.models import Ticket
from nas.models import Nas, TrafficClass, TrafficNode
from object_log.models import LogItem
from radius.models import ActiveSession, AuthLog
from sendsms.models import Message

from ebsadmin.models import Comment
from ebsadmin.transactionreport import servicemodel_by_table


def showconfirmcolumn(href='{{record.get_remove_url}}', message=_(u'Удалить?'),
                      verbose_name=' ', icon_type='icon-remove'):
    return columns.TemplateColumn(
        '<a href="%s" class="show-confirm" title="%s" data-clickmessage="%s">'
        '<i class="%s"></i></a>' % (href, message, message, icon_type),
        verbose_name=verbose_name,
        orderable=False
    )


def modallinkcolumn(url_name='', modal_title='', modal_id=''):
    return columns.LinkColumn(
        url_name,
        get_params={
            'id': A('pk')
        },
        attrs={
            'a': {
                'rel': 'alert3',
                'class': 'general-modal-dialog',
                'data-dlgtitle': modal_title,
                'data-dlgid': modal_id
            }
        }
    )


class EbsadminTable(tables.Table):

    def __init__(self, *args, **argv):
        super(EbsadminTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__

    class Meta:
        attrs = {
            'class': 'table table-disable-hover table-bordered table-condensed'
        }


class EbsadminTableReport(TableReport):

    def __init__(self, *args, **argv):
        super(EbsadminTableReport, self).__init__(*args, **argv)
        self.name = self.__class__.__name__

    class Meta:
        attrs = {
            'class': 'table table-bordered table-condensed'
        }


class FormatBlankColumn(columns.Column):

    def render(self, value):
        return "" if value is None else value


class FormatBooleanHTMLColumn(columns.TemplateColumn):

    def render(self, value):
        return "" if value else value


class FormatFloatColumn(columns.Column):

    def render(self, value):
        return "%.2f" % float(value) if value else ''


class FormatDateTimeColumn(columns.Column):

    def render(self, value):
        try:
            return value.strftime("%d.%m.%Y %H:%M:%S") if value else ''
        except:
            return value


class FormatBlankSpeedColumn(columns.LinkColumn):

    def render(self, value):
        return value if value else ''


class YesNoColumn(columns.Column):

    def render(self, value):
        return mark_safe(
            '<img src="/media/icons/16/%s.png" />' %
            ('accept' and True or 'cross'))


class RadioColumn(columns.Column):

    def render(self, value, bound_column):
        default = {
            'type': 'radio',
            'name': bound_column.name,
            'value': value
        }
        general = self.attrs.get('input')
        specific = self.attrs.get('td__input')
        attrs = AttributeDict(
            default, **(specific or general or {}))
        return mark_safe(u'<input %s/>' % attrs.as_html())


class SubAccountsTable(EbsadminTable):
    id = columns.LinkColumn('subaccount', get_params={'id': A('pk')})
    username = columns.LinkColumn(
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


class AccountHardwareTable(EbsadminTable):
    id = columns.LinkColumn(
        'accounthardware',
        get_params={'id': A('pk')},
        attrs={
            'a': {
                'rel': "alert3",
                'class': "open-custom-dialog"
            }
        }
    )
    d = showconfirmcolumn()

    class Meta(EbsadminTable.Meta):
        model = AccountHardware
        fields = ('id', 'hardware', 'datetime', 'returned', 'comment')


class AccountAddonServiceTable(EbsadminTable):
    id = columns.LinkColumn(
        'accountaddonservice',
        get_params={
            'id': A('pk')
        },
        attrs={
            'a': {
                'rel': "alert3",
                'class': "open-custom-dialog"
            }
        }
    )
    service = columns.Column()
    subaccount = columns.LinkColumn(
        'subaccount',
        get_params={
            'id': A('subaccount.id')
        },
        attrs={
            'a': {
                'rel': "alert3",
                'class': "open-custom-dialog"
            }
        }
    )
    cost = columns.TemplateColumn(
        '{{record.cost|default:record.service.cost|floatformat}}')
    activated = FormatDateTimeColumn()
    deactivated = FormatDateTimeColumn()
    deactivate = showconfirmcolumn(
        href='{{record.get_deactivate_url}}',
        message='Отключить подклюачемую услугу?',
        verbose_name='Отключить',
        icon_type='icon-ban-circle')
    d = showconfirmcolumn()

    class Meta(EbsadminTable.Meta):
        model = AccountAddonService
        fields = (
            'id',
            'service',
            'subaccount',
            'cost',
            'activated',
            'deactivated',
            'deactivate',
            'd'
        )


class SuspendedPeriodTable(EbsadminTable):
    d = showconfirmcolumn()

    class Meta(EbsadminTable.Meta):
        model = SuspendedPeriod


class AccountTarifTable(EbsadminTable):
    id = FormatBlankColumn()
    tarif = FormatBlankColumn()
    datetime = FormatDateTimeColumn()
    d = showconfirmcolumn()

    class Meta(EbsadminTable.Meta):
        pass


class TotalTransactionReportTable(EbsadminTableReport):
    tariff__name = FormatBlankColumn(verbose_name=_(u'Тариф'))
    id = FormatBlankColumn()
    account = columns.LinkColumn(
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
    service_id = columns.Column(verbose_name=_(u'ID Услуги'))
    type = FormatBlankColumn(verbose_name=_(u'Тип'), accessor=A('type__name'))
    is_bonus = FormatBlankColumn(verbose_name=_(u'Бонус'))
    summ = FormatFloatColumn(verbose_name=_(u'Сумма'))
    prev_balance = FormatFloatColumn(verbose_name=_(u'Предыдущий баланс'))
    created = FormatDateTimeColumn(verbose_name=_(u'Создана'))
    end_promise = FormatDateTimeColumn(verbose_name=_(u'Окончание о.п.'))
    promise_expired = FormatDateTimeColumn()
    d = columns.CheckBoxColumn(
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
            model = servicemodel_by_table.get(record.get('table'))
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


class TransactionReportTable(EbsadminTableReport):
    id = FormatBlankColumn()
    account = columns.LinkColumn(
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
    d = columns.CheckBoxColumn(
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


class AddonServiceTransactionReportTable(EbsadminTableReport):
    id = FormatBlankColumn()
    account = columns.LinkColumn(
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
    d = columns.CheckBoxColumn(
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


class PeriodicalServiceTransactionReportTable(EbsadminTableReport):
    id = FormatBlankColumn()
    account__username = columns.LinkColumn(
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
    service = columns.Column(accessor=A('service__name'))
    prev_balance = FormatFloatColumn(verbose_name=_(u'Предыдущий баланс'))
    type = columns.Column(accessor=A('type__name'))
    real_created = FormatDateTimeColumn()
    d = columns.CheckBoxColumn(
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


class TrafficTransactionReportTable(EbsadminTableReport):
    id = FormatBlankColumn()
    account__username = columns.LinkColumn(
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
    d = columns.CheckBoxColumn(
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


class CashierReportTable(EbsadminTableReport):
    summ = FormatFloatColumn(verbose_name=_(u'Сумма'))
    fullname = columns.Column(
        verbose_name=u'ФИО', accessor=A('account.fullname'))
    address = columns.TemplateColumn(
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


class AccountsReportTable(EbsadminTableReport):
    row_number = columns.Column(
        verbose_name='#', empty_values=(), orderable=False)
    username = columns.LinkColumn(
        'account_edit', verbose_name=_(u'Логин'), get_params={'id': A('pk')})
    contract = FormatBlankColumn(verbose_name=_(u'Договор'))
    fullname = FormatBlankColumn()
    address = columns.TemplateColumn(
        (u"{{record.street|default:''}} "
         u"{{record.house|default:''}}-{{record.room|default:''}}"),
        orderable=False
    )
    entrance = columns.Column(verbose_name=_(u'Подъезд'))
    row = columns.Column(verbose_name=_(u'Этаж'))
    ballance = FormatFloatColumn()
    tariff = FormatBlankColumn(verbose_name=_(u"Тариф"), orderable=False)
    ips = FormatBlankColumn(verbose_name=_(u"IP"), orderable=False)
    d = columns.CheckBoxColumn(
        verbose_name=' ', orderable=False, accessor=A('pk'))

    def __init__(self, form, *args, **kwargs):
        super(AccountsReportTable, self).__init__(form, *args, **kwargs)
        self.counter = itertools.count()
        self.footer_data = self.TableDataClass(
            data=[self.data.queryset.aggregate(ballance=Sum('ballance'))], table=self)
        self.footer = rows.BoundRows(self.footer_data, self)

    def paginate(self, *args, **kwargs):
        super(AccountsReportTable, self).paginate(*args, **kwargs)

    def render_row_number(self):
        return '%d' % next(self.counter)

    class Meta(EbsadminTableReport.Meta):
        model = Account
        configurable = True
        exclude = ('password',)
        annotations = ('ballance',)


class AccountsCashierReportTable(EbsadminTableReport):
    d = RadioColumn(verbose_name=' ', orderable=False, accessor=A('pk'))
    row_number = columns.Column(
        verbose_name=u'#', empty_values=(), orderable=False)
    username = columns.LinkColumn(
        'account_edit', verbose_name=_(u'Логин'), get_params={'id': A('pk')})
    contract = FormatBlankColumn(verbose_name=_(u'Договор'))
    fullname = FormatBlankColumn()
    tariff = FormatBlankColumn()
    address = columns.TemplateColumn(
        (u"{{record.city|default:''}} {{record.street|default:''}} "
         u"{{record.house|default:''}}-{{record.room|default:''}}"),
        orderable=False
    )
    entrance = columns.Column(verbose_name=_(u'Подъезд'))
    row = columns.Column(verbose_name=_(u'Этаж'))
    ballance = FormatFloatColumn()
    bonus_ballance = FormatFloatColumn()

    def __init__(self, *args, **kwargs):
        super(AccountsCashierReportTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()

    def render_row_number(self):
        return '%d' % next(self.counter)

    class Meta(EbsadminTableReport.Meta):
        pass


class ActiveSessionTable(EbsadminTableReport):
    row_number = columns.Column(
        verbose_name=u'#', empty_values=(), orderable=False)
    session_status = columns.TemplateColumn(
        "<span class='label {% if record.session_status == 'ACK' %}info"
        "{% endif %}'>{{ record.session_status }}</span>")
    date_start = FormatDateTimeColumn()
    interrim_update = FormatDateTimeColumn(
        verbose_name=_(u'Последнее обновление'))
    caller_id = columns.Column(
        verbose_name=_(u'Caller ID'), empty_values=())
    address = columns.TemplateColumn(
        (u"{{record.account__street|default:''}} "
         u"{{record.account__house|default:''}}-"
         u"{{record.account__room|default:''}}"),
        orderable=False,
        verbose_name=u'Адрес'
    )
    framed_ip_address = columns.Column(
        verbose_name=_(u'IP'), empty_values=())
    framed_protocol = columns.Column(
        verbose_name=_(u'Протокол'), empty_values=())
    session_time = columns.Column(
        verbose_name=_(u'Онлайн'), empty_values=())
    date_end = FormatDateTimeColumn()
    nas_int = columns.Column(
        verbose_name=_(u'NAS'), accessor=A('nas_int__name'))
    bytes = columns.TemplateColumn(
        "{{record.bytes_in|filesizeformat}}/"
        "{{record.bytes_out|filesizeformat}}",
        verbose_name=_(u'Байт'),
        orderable=False
    )
    subaccount__username = columns.LinkColumn(
        'subaccount',
        get_params={
            'id': A('subaccount')
        },
        verbose_name=_(u'Субаккаунт')
    )
    action = columns.TemplateColumn(
        '''\
<button data='{{record.id}}' class='btn btn-success btn-mini sreset' \
title='Soft reset'>R</button>&nbsp;
<button data='{{record.id}}' class='btn btn-danger btn-mini hreset' \
title='Hard reset'>H</button>&nbsp;
<button class='btn btn-info btn-mini ping' title='Ping' \
data='{{record.framed_ip_address}}'>P</button>''',
        verbose_name=_(u'Action')
    )

    def __init__(self, *args, **kwargs):
        super(ActiveSessionTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()

    def render_row_number(self):
        return '%d' % next(self.counter)

    class Meta(EbsadminTableReport.Meta):
        model = ActiveSession
        configurable = True
        available_fields = (
            'row_number',
            'subaccount__username',
            'date_start',
            'interrim_update',
            'date_end',
            'nas_int',
            'caller_id',
            'framed_ip_address',
            'framed_protocol',
            'session_time',
            'bytes',
            'session_status',
            'action'
        )
        attrs = {
            'class': 'table table-bordered table-condensed'
        }


class AuthLogTable(EbsadminTableReport):
    account = columns.LinkColumn(
        'account_edit', get_params={'id': A('account.id')})
    subaccount = columns.LinkColumn(
        'subaccount', get_params={'id': A('subaccount.id')})
    nas = FormatBlankColumn()
    datetime = FormatDateTimeColumn()

    class Meta(EbsadminTableReport.Meta):
        model = AuthLog
        exclude = ('type', 'id')


class BallanceHistoryTable(EbsadminTableReport):
    account__username = columns.LinkColumn(
        'account_edit', get_params={'id': A('account')})
    balance = FormatBlankColumn(verbose_name=_(u'Новый баланс'))
    summ = FormatBlankColumn(verbose_name=_(u'Сумма'))
    datetime = FormatDateTimeColumn()

    class Meta(EbsadminTableReport.Meta):
        pass


class IPInUseTable(EbsadminTableReport):
    datetime = FormatDateTimeColumn()
    disabled = FormatDateTimeColumn()

    class Meta(EbsadminTableReport.Meta):
        model = IPInUse


class LogTable(EbsadminTableReport):
    user = FormatBlankColumn()
    changed_fields = FormatBlankColumn()

    class Meta(EbsadminTableReport.Meta):
        pass


class NasTable(EbsadminTableReport):
    name = columns.LinkColumn(
        'nas_edit', verbose_name=_(u"Имя"), get_params={'id': A('pk')})
    radiusattrs = columns.TemplateColumn(
        (u"<a href='{% url 'radiusattr' %}?nas={{record.id}}' "
         u"class='btn btn-mini btn-primary'>Изменить</a>"),
        verbose_name=_(u'RADIUS атрибуты'),
        orderable=False
    )
    id = columns.LinkColumn(
        'nas_edit',
        get_params={
            'id': A('pk')
        },
        attrs={
            'a': {
                'rel': "alert3",
                'class': "open-custom-dialog"
            }
        }
    )
    d = showconfirmcolumn(message=_(u'Удалить? Все связанные с сервером '
                                    u'доступа записи будут сброшены на '
                                    u'значение по умолчанию для '
                                    u'выбранной записи'))

    class Meta(EbsadminTableReport.Meta):
        model = Nas
        configurable = True
        available_fields = (
            'id',
            'name',
            'radiusattrs',
            'identify',
            'type',
            'ipaddress'
        )


class TemplateTable(EbsadminTableReport):
    id = columns.LinkColumn(
        'template_edit',
        get_params={
            'id': A('pk')
        },
        attrs={
            'a': {
                'rel': "alert3",
                'class': "open-custom-dialog"
            }
        }
    )
    name = columns.LinkColumn(
        'template_edit',
        get_params={
            'id': A('pk')
        },
        attrs={
            'a': {
                'rel': "alert3",
                'class': "open-custom-dialog"
            }
        }
    )
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = Template
        configurable = False
        exclude = ("", 'body')


class SettlementPeriodTable(EbsadminTableReport):
    id = columns.LinkColumn(
        'settlementperiod_edit', get_params={'id': A('pk')})
    name = columns.LinkColumn(
        'settlementperiod_edit', get_params={'id': A('pk')})
    time_start = FormatDateTimeColumn()
    length = FormatBlankColumn()

    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = SettlementPeriod


class SystemUserTable(EbsadminTableReport):
    id = columns.LinkColumn(
        'systemuser_edit', get_params={'id': A('pk')})
    username = columns.LinkColumn(
        'systemuser_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = SystemUser
        configurable = True
        available_fields = ('id', 'username', 'last_login', 'd')
        exclude = ("password", 'text_password')


class AddonServiceTable(EbsadminTableReport):
    id = columns.LinkColumn(
        'addonservice_edit', get_params={'id': A('pk')})
    name = columns.LinkColumn(
        'addonservice_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = AddonService
        configurable = True


class IPPoolTable(EbsadminTableReport):
    id = columns.LinkColumn('ippool_edit', get_params={'id': A('pk')})
    name = columns.LinkColumn('ippool_edit', get_params={'id': A('pk')})
    next_ippool = FormatBlankColumn()
    pool_size = columns.Column(
        verbose_name=_(u'IP в пуле'),
        accessor=A('get_pool_size'),
        orderable=False
    )
    used_ip = columns.Column(
        verbose_name=_(u'Используется'),
        accessor=A('get_used_ip_count'),
        orderable=False)
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = IPPool
        configurable = True


class CommentTable(EbsadminTableReport):
    id = columns.LinkColumn(
        'comment_edit',
        get_params={
            'id': A('pk')
        },
        attrs={
            'a': {
                'rel': "alert3",
                'class': "open-log-custom-dialog"
            }
        }
    )
    done = columns.TemplateColumn(
        '''\
<a href='{% url 'comment_edit' %}?id={{record.id}}&done=True' \
class='btn btn-mini btn-success comment-done'>
<i class='icon-ok icon-white'></i></a>&nbsp;
<a href='{{record.get_remove_url}}' \
class='btn btn-mini btn-danger show-confirm'>
<i class='icon-remove icon-white'></i></a>''',
        verbose_name='Действия',
        orderable=False
    )
    object = columns.Column(verbose_name=u'Объект')

    class Meta(EbsadminTableReport.Meta):
        model = Comment
        configurable = True
        available_fields = ('id', 'comment', 'object',
                            'created', 'due_date', 'done',)


class TransactionTypeTable(EbsadminTableReport):
    id = columns.LinkColumn(
        'transactiontype_edit', get_params={'id': A('pk')})
    name = columns.LinkColumn(
        'transactiontype_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn(message=_(u'Удалить проводку #{{ record.id }}?'))

    class Meta(EbsadminTableReport.Meta):
        model = TransactionType
        configurable = False


class TrafficClassTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='trafficclass_edit',
        modal_title=_(u'Изменить класс'),
        modal_id='trafficclass-modal'
    )
    name = modallinkcolumn(
        url_name='trafficclass_edit',
        modal_title=_(u'Изменить класс'),
        modal_id='trafficclass-modal'
    )
    directions = columns.TemplateColumn(
        u'''\
<a href='{% url 'trafficnode_list' %}?id={{record.id}}' \
class='btn btn-primary btn-mini'>Список направлений</a>''',
        verbose_name=_(u'Направления'),
        orderable=False
    )
    d = columns.TemplateColumn(
        '''\
<a href='{{record.get_remove_url}}' class='show-confirm' \
data-clickmessage='Удалить?'>
<i class='icon-remove'></i></a><input type='hidden' name='id' \
value='{{record.id}}'>''',
        verbose_name=' ',
        orderable=False
    )

    class Meta(EbsadminTableReport.Meta):
        model = TrafficClass
        configurable = True
        available_fields = ('id', 'name', 'passthrough', 'directions', 'd')


class TrafficNodeTable(EbsadminTableReport):
    row_number = columns.Column(
        verbose_name="#", empty_values=(), orderable=False)
    id = modallinkcolumn(
        url_name='trafficnode',
    )
    d = columns.CheckBoxColumn(
        verbose_name=' ', orderable=False, accessor=A('pk'))

    def __init__(self, *args, **kwargs):
        super(TrafficNodeTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()

    def render_row_number(self):
        return '%d' % next(self.counter)

    class Meta(EbsadminTableReport.Meta):
        model = TrafficNode
        configurable = True
        exclude = ("traffic_class", )
        available_fields = (
            'row_number',
            'id',
            'name',
            'protocol',
            'src_port',
            'in_index',
            'src_ip',
            'dst_ip',
            'dst_port',
            'out_index',
            'src_as',
            'dst_as',
            'next_hop',
            'd'
        )


class UploadTrafficNodeTable(EbsadminTableReport):
    row_number = columns.Column(
        verbose_name="#", empty_values=(), orderable=False)
    src_net = columns.Column(verbose_name="Src Net")
    dst_net = columns.Column(verbose_name="Dst Net")
    direction = columns.Column(verbose_name="Direction")

    def __init__(self, *args, **kwargs):
        super(UploadTrafficNodeTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()

    def render_row_number(self):
        return '%d' % next(self.counter)

    class Meta(EbsadminTableReport.Meta):
        fields = ('row_number', 'src_net', 'dst_net')


class RadiusAttrTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='radiusattr_edit',
        modal_title=_(u'Изменить атрибут'),
        modal_id='radiusattr-modal'
    )
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = RadiusAttrs
        exclude = ("tarif", 'nas', 'vendor', 'attrid')


class ManufacturerTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='manufacturer_edit',
        modal_title=_(u'Изменить название'),
        modal_id='manufacturer-modal'
    )
    name = modallinkcolumn(
        url_name='manufacturer_edit',
        modal_title=_(u'Изменить название'),
        modal_id='manufacturer-modal'
    )
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = Manufacturer


class ModelTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='model_edit',
        modal_title=_(u'Изменить модель'),
        modal_id='model-modal'
    )
    name = modallinkcolumn(
        url_name='model_edit',
        modal_title=_(u'Изменить модель'),
        modal_id='model-modal'
    )
    d = showconfirmcolumn(message=_(u'Удалить? Удаление модели оборудования '
                                    u'вызовет удаление всех связаных объектов'
                                    u' в системе.'))

    class Meta(EbsadminTableReport.Meta):
        model = Model


class HardwareTypeTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='hardwaretype_edit',
        modal_title=_(u'Изменить тип'),
        modal_id='hardwaretype-modal'
    )
    name = modallinkcolumn(
        url_name='hardwaretype_edit',
        modal_title=_(u'Изменить тип'),
        modal_id='hardwaretype-modal'
    )
    d = showconfirmcolumn(message=_(u'Удалить? Удаление типа оборудования '
                                    u'вызовёт удаление всех связанных '
                                    u'объектов в системе.'))

    class Meta(EbsadminTableReport.Meta):
        model = HardwareType


class HardwareTable(EbsadminTableReport):
    id = columns.LinkColumn('hardware_edit', get_params={'id': A('pk')})
    model = columns.LinkColumn(
        'hardware_edit', get_params={'id': A('pk')})
    name = columns.LinkColumn(
        'hardware_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn(message=_(u'Удалить? Удаление устройства вызовет '
                                    u'удаление всех связаных с ним объектов '
                                    u'в системе.'))

    class Meta(EbsadminTableReport.Meta):
        model = Hardware
        configurable = True


class SwitchTable(EbsadminTableReport):
    id = columns.LinkColumn('switch_edit', get_params={'id': A('pk')})
    name = columns.LinkColumn('switch_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn(message=_(u'Удалить? Перед удалением коммутатора '
                                    u'убедитесь, что он не используется в '
                                    u'биллинг-системе'))

    class Meta(EbsadminTableReport.Meta):
        model = Switch
        configurable = True
        available_fields = (
            "id",
            'name',
            'manufacturer',
            'model',
            'sn',
            'city',
            'street',
            'place'
        )


class CardTable(EbsadminTableReport):
    row_number = columns.Column(
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
    d = columns.CheckBoxColumn(
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
    row_number = columns.Column(
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
    id = columns.LinkColumn('salecard_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = SaleCard
        configurable = True
        exclude = ("tarif", 'nas')


class DealerTable(EbsadminTableReport):
    id = columns.LinkColumn('dealer_edit', get_params={'id': A('pk')})
    organization = columns.LinkColumn(
        'dealer_edit', get_params={'id': A('pk')})

    class Meta(EbsadminTableReport.Meta):
        model = Dealer
        configurable = True
        available_fields = (
            'id',
            'organization',
            'contactperson',
            'unp',
            'phone'
        )


class TariffTable(EbsadminTableReport):
    name = columns.LinkColumn('tariff_edit', get_params={'id': A('pk')})
    radiusattrs = columns.TemplateColumn(
        u'''\
<a href='{% url 'radiusattr' %}?tarif={{record.id}}' \
class='btn btn-mini btn-primary'>Изменить</a>''',
        verbose_name=_(u'RADIUS атрибуты'),
        orderable=False
    )
    access_type = FormatBlankColumn(
        verbose_name=_(u'Тип доступа'),
        accessor=A('access_parameters.access_type')
    )
    accounts_count = columns.TemplateColumn(
        u'''\
<a href='{% url 'account_list' %}?tariff={{record.id}}' \
class='btn btn-mini'>{{record.accounts_count}} \
<i class='icon-arrow-right'></i></a>''',
        verbose_name=_(u'Аккаунтов')
    )
    delete = showconfirmcolumn(
        href='{{record.get_hide_url}}',
        message='Скрыть?',
        verbose_name='Скрыть',
        icon_type='icon-ban-circle'
    )

    class Meta(EbsadminTableReport.Meta):
        model = Tariff
        configurable = True
        available_fields = (
            'name',
            'settlement_period',
            'cost',
            'access_type',
            'reset_tarif_cost',
            'accounts_count',
            'radiusattrs',
            'delete'
        )


class PeriodicalServiceTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_periodicalservice_edit',
        modal_title=_(u'Периодическая услуга'),
        modal_id='periodicalservice-modal'
    )
    name = modallinkcolumn(
        url_name='tariff_periodicalservice_edit',
        modal_title=_(u'Периодическая услуга'),
        modal_id='periodicalservice-modal'
    )
    d = showconfirmcolumn(message=_(u'Удалить? Удаление периодической услуги '
                                    u'вызовет обнуление информации о '
                                    u'списаниях по ней. '
                                    u'Вместо этого рекомемендуется '
                                    u'воспользоваться отключением услуги.'))
    created = FormatDateTimeColumn()
    deactivated = FormatDateTimeColumn()

    class Meta(EbsadminTableReport.Meta):
        model = PeriodicalService
        fields = (
            "id",
            'name',
            'settlement_period',
            'cost',
            'cash_method',
            'ps_condition',
            'condition_summ',
            'created',
            'deactivated'
        )


class GroupTable(EbsadminTableReport):
    id = columns.LinkColumn('group_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn(message=_(u'Удалить? Удаление группы трафика '
                                    u'вызовет её удаление во всех тарифных '
                                    u'планах.'))

    class Meta(EbsadminTableReport.Meta):
        model = Group


class RegistrationRequestTable(EbsadminTableReport):
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = RegistrationRequest


class ContractTemplateTable(EbsadminTableReport):
    id = columns.LinkColumn(
        'contracttemplate_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn(message=_(u'Удалить шаблон номера договора?'))

    class Meta(EbsadminTableReport.Meta):
        model = ContractTemplate


class TrafficTransmitNodesTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_traffictransmitnode_edit',
        modal_title=_(u'Правило начисления предоплаченного трафика'),
        modal_id='periodicalservice-modal'
    )
    group = columns.LinkColumn(
        'group_edit', get_params={'id': A('group.id')})
    d = showconfirmcolumn(
        message=_(u'Удалить? Вы уверены, что хотите удалить запись?'))

    class Meta(EbsadminTableReport.Meta):
        model = TrafficTransmitNodes
        fields = ('id', 'timeperiod', 'group', 'cost', 'd')


class PrepaidTrafficTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_prepaidtraffic_edit'
    )
    group = columns.LinkColumn(
        'group_edit', get_params={'id': A('group.id')})
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = PrepaidTraffic
        fields = ("id", 'group', 'size', 'd')


class TimeSpeedTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_timespeed_edit',
        modal_title=_(u'Правило изменения скорости'),
        modal_id='timespeed-modal'
    )
    d = showconfirmcolumn(
        message=_(u'Удалить? Вы уверены, что хотите удалить строку?'))

    class Meta(EbsadminTableReport.Meta):
        model = TimeSpeed
        fields = (
            'id',
            'time',
            'max_tx',
            'max_rx',
            'burst_tx',
            'burst_rx',
            'burst_treshold_tx',
            'burst_treshold_rx',
            'burst_time_tx',
            'burst_time_rx',
            'min_tx',
            'min_rx',
            'priority'
        )


class OneTimeServiceTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='onetimeservice_edit',
        modal_title=_(u'Периодическая услуга'),
        modal_id='periodicalservice-modal'
    )
    name = modallinkcolumn(
        url_name='onetimeservice_edit',
        modal_title=_(u'Периодическая услуга'),
        modal_id='periodicalservice-modal'
    )
    d = showconfirmcolumn(message=_(u'Удалить? Удаление разовой услуги '
                                    u'вызовет обнуление информации о '
                                    u'списаниях по ней. Вместо этого '
                                    u'рекомемендуется воспользоваться '
                                    u'отключением услуги.'))

    class Meta(EbsadminTableReport.Meta):
        model = OneTimeService
        fields = ("id", 'name', 'cost', 'd')


class RadiusTrafficNodeTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_radiustrafficnode_edit',
        modal_title=_(u'Правило тарификации трафика')
    )
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = RadiusTrafficNode
        fields = ("id", 'value', 'timeperiod', 'cost', 'd')


class TrafficLimitTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_trafficlimit_edit',
        modal_title=_(u'Лимит трафика'),
        modal_id='periodicalservice-modal'
    )
    d = showconfirmcolumn(message='Удалить лимит трафика?')
    speedlimit = columns.TemplateColumn(
        '''\
<a href='{% url 'tariff_speedlimit_edit' %}?trafficlimit_id={{record.id}}' \
class='open-speedlimit-dialog' data-dlgtitle='Правило изменения скорости' \
data-dlgid='speedlimit-modal'>
{% if record.speedlimit %}{{record.speedlimit}}
<a href='{{record.speedlimit.get_remove_url}}' \
class='show-speedlimit-confirm' data-clickmessage='Удалить? Если в лимите \
трафика указано действие Изменить скорость - вы обязаны указать параметры \
изменения скорости.'>
<i class='icon-remove'></i></a>{% else %}Указать{% endif %}</a>''',
        verbose_name='Изменить скорость',
        orderable=False
    )

    class Meta(EbsadminTableReport.Meta):
        model = TrafficLimit
        fields = (
            "id",
            'name',
            'settlement_period',
            'mode',
            'group',
            'size',
            'action',
            'speedlimit',
            'd'
        )


class TimeAccessNodeTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_timeaccessnode_edit',
        modal_title=_(u'Правило тарификации времени'),
        modal_id='timeaccessnode-modal'
    )
    d = showconfirmcolumn(message=_(u'Удалить правило тарификации времени?'))

    class Meta(EbsadminTableReport.Meta):
        model = TimeAccessNode
        fields = ("id", 'time_period', 'cost', 'd')


class AddonServiceTarifTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_addonservicetariff_edit',
        modal_title=_(u'Подключаемая услуга'),
        modal_id='periodicalservice-modal'
    )
    d = showconfirmcolumn(message=_(u'Вы действительно хотите удалить '
                                    u'правило активации подключаемых услуг?'))

    class Meta(EbsadminTableReport.Meta):
        model = AddonServiceTarif
        fields = (
            "id",
            'service',
            'activation_count_period',
            'activation_count',
            'type',
            'd'
        )


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


class SheduleLogTable(EbsadminTableReport):
    d = columns.TemplateColumn("  ", verbose_name=' ', orderable=False)
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


class NewsTable(EbsadminTableReport):
    id = columns.LinkColumn('news_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn(message='Удалить новость?')
    created = FormatDateTimeColumn(verbose_name=_(u'Активна с'))
    age = FormatDateTimeColumn(verbose_name=_(u'Активна по'))

    class Meta(EbsadminTableReport.Meta):
        model = News
        configurable = True
        available_fields = (
            "id",
            'body',
            'created',
            'age',
            'public',
            'private',
            'agent',
            'd'
        )


class TPChangeRuleTable(EbsadminTableReport):
    id = columns.LinkColumn(
        'tpchangerule_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn(message='Удалить правило?')
    settlement_period = FormatBlankColumn(verbose_name=_(u'Расчётный период'))
    on_next_sp = columns.TemplateColumn(
        "<img src='/media/img/icons/{% if record.on_next_sp %}accept.png"
        "{% else %}icon_error.gif{% endif %}'>")
    row_class = columns.Column(visible=False)

    def render_row_class(self, value, record):
        return 'error' if record.disabled else ''

    class Meta(EbsadminTableReport.Meta):
        model = TPChangeRule
        configurable = True
        available_fields = (
            "id",
            'row_class',
            'from_tariff',
            'to_tariff',
            'cost',
            'ballance_min',
            'on_next_sp',
            'settlement_period',
            'disabled',
            'd'
        )


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
    cnt = columns.TemplateColumn(
        '{{record.account_set.count}}', verbose_name=_(u'Количество'))
    d = showconfirmcolumn(message=_(u'Удалить?'))

    class Meta(EbsadminTableReport.Meta):
        model = AccountGroup


class ActionLogTable(EbsadminTableReport):
    object1 = columns.Column(
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


class GroupStatTable(EbsadminTableReport):
    account = columns.Column(
        _(u'Аккаунт'), accessor=A('account__username'))
    group = columns.Column(_(u'Группа'), accessor=A('group__name'))
    bytes = columns.TemplateColumn(
        "{{record.summ_bytes|filesizeformat}}({{record.summ_bytes}})",
        verbose_name=_(u'Сумма'),
        accessor=A('summ_bytes')
    )

    class Meta(EbsadminTableReport.Meta):
        available_fields = ('account', 'group', 'bytes')
        configurable = True


class GlobalStatTable(EbsadminTableReport):
    account = columns.Column(
        _(u'Аккаунт'), accessor=A('account__username'))
    bytes_in = columns.TemplateColumn(
        "{{record.bytes_in|filesizeformat}}({{record.bytes_in}})",
        verbose_name=_(u'ВХ'))
    bytes_out = columns.TemplateColumn(
        "{{record.bytes_out|filesizeformat}}({{record.bytes_out}})",
        verbose_name=_(u'ИСХ'))
    max = columns.Column(_(u'Последние данные'))

    class Meta(EbsadminTableReport.Meta):
        available_fields = ('account', 'group', 'bytes')
        configurable = False


class AccountPrepaysTraficTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='accountprepaystraffic_edit',
        modal_title=_(u'Изменить значения')
    )
    account_tarif = columns.Column(_(u'Аккаунт/Тариф'))
    prepaid_traffic = columns.TemplateColumn(
        "{{record.prepaid_traffic.size|filesizeformat}}"
        "({{record.prepaid_traffic.size}})",
        verbose_name=_(u'Начислено')
    )
    size = columns.TemplateColumn(
        "{{record.size|filesizeformat}}({{record.size}})",
        verbose_name=_(u'Остаток')
    )
    progress = columns.TemplateColumn(
        """\
<div class="progress progress-success">
    <div class="bar" style="width: {{record.in_percents}}%"></div>
</div>""",
        verbose_name=_(u'Осталось')
    )
    datetime = FormatDateTimeColumn(verbose_name=_(u'Начислен'))

    def render_bytes(self, value, record):
        return value

    class Meta(EbsadminTableReport.Meta):
        model = AccountPrepaysTrafic
        configurable = True


class AccountPrepaysRadiusTraficTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='accountprepaystraffic_edit',
        modal_title=_(u'Изменить значения')
    )
    account_tarif = columns.Column(_(u'Аккаунт/Тариф'))
    size = columns.TemplateColumn(
        "{{record.size|filesizeformat}}({{record.size}})",
        verbose_name=_(u'Остаток')
    )
    datetime = FormatDateTimeColumn(verbose_name=_(u'Начислен'))
    progress = columns.TemplateColumn(
        """\
<div class="progress progress-success">
    <div class="bar" style="width: {{record.in_percents}}%"></div>
</div>""",
        verbose_name=_(u'Расходовано')
    )

    def render_bytes(self, value, record):
        return value

    class Meta(EbsadminTableReport.Meta):
        model = AccountPrepaysRadiusTrafic
        configurable = True


class AccountPrepaysTimeTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='accountprepaystraffic_edit',
        modal_title=_(u'Изменить тип')
    )
    account_tarif = columns.Column(_(u'Аккаунт/Тариф'))
    datetime = FormatDateTimeColumn(verbose_name=_(u'Начислен'))
    progress = columns.TemplateColumn(
        """\
<div class="progress progress-success">
    <div class="bar" style="width: {{record.in_percents}}%"></div>
</div>""",
        verbose_name=_(u'Расходовано')
    )

    def render_bytes(self, value, record):
        return value

    class Meta(EbsadminTableReport.Meta):
        model = AccountPrepaysTime
        configurable = True


class SwitchPortsTable(EbsadminTableReport):
    port = columns.TemplateColumn(
        "<input type='hidden' name='port' value='{{record.port}}'>{{record.port}}",
        verbose_name=_(u'Порт')
    )
    broken_port = columns.TemplateColumn(
        "<input type='checkbox' name='broken_port' "
        "{% if record.broken_port %} checked{% endif %}>",
        verbose_name=_(u'Битый')
    )
    uplink_port = columns.TemplateColumn(
        "<input type='checkbox'  name='uplink_port' "
        "{% if record.uplink_port %} checked{% endif %}>",
        verbose_name=_(u'Аплинк')
    )
    protected_port = columns.TemplateColumn(
        "<input type='checkbox'  name='protected_port' "
        "{% if record.protected_port %} checked{% endif %}>",
        verbose_name=_(u'Защита')
    )
    monitored_port = columns.TemplateColumn(
        "<input type='checkbox'  name='monitored_port' "
        "{% if record.monitored_port %} checked{% endif %}>",
        verbose_name=_(u'Мониторинг')
    )
    disabled_port = columns.TemplateColumn(
        "<input type='checkbox'  name='disabled_port' "
        "{% if record.disabled_port %} checked{% endif %}>",
        verbose_name=_(u'Отключён')
    )

    class Meta(EbsadminTableReport.Meta):
        pass


class TicketTable(EbsadminTableReport):
    id = columns.LinkColumn('helpdesk_view', args=[A('id')])
    title = columns.LinkColumn('helpdesk_view', args=[A('id')])
    created = FormatDateTimeColumn(verbose_name=_(u'Создан'))
    status = columns.Column(
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


class PermissionGroupTable(EbsadminTableReport):
    id = columns.LinkColumn(
        'permissiongroup_edit', get_params={'id': A('pk')})
    name = columns.LinkColumn(
        'permissiongroup_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = PermissionGroup
        available_fields = ("id", 'name', 'd')


class NotificationsSettingsTable(TableReport):

    id = columns.LinkColumn(
        'notificationssettings_edit', get_params={'id': A('pk')})
    name = columns.LinkColumn(
        'notificationssettings_edit', get_params={'id': A('pk')})
    d = columns.TemplateColumn(
        "<a href='{{record.get_remove_url}}' "
        "class='show-confirm'><i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )

    def __init__(self, *args, **argv):
        super(NotificationsSettingsTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__

    class Meta:
        model = NotificationsSettings
        available_fields = ("id", 'name', 'd', )
        attrs = {
            'class': 'table table-bordered table-condensed'
        }


class PaymentTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='payment_edit',
        modal_title=_(u'Изменить платёж'),
        modal_id='payment-modal'

    )
    account = columns.LinkColumn(
        'account_edit',
        verbose_name=_(u'Аккаунт'),
        get_params={'id': A('account.id')}
    )
    d = showconfirmcolumn(message=_(u'Внимание. Удаление платежа может '
                                    u'вызвать нежелательные последствия при '
                                    u'перетарификации. Если вы не уверены в '
                                    u'своих действиях - лучше откажитесь от '
                                    u'удаления.'))

    class Meta(EbsadminTableReport.Meta):
        model = Payment


class DynamicSchemaFieldTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='dynamicschemafield_edit',
        modal_title=_(u'Изменить название'),
        modal_id='manufacturer-modal'
    )
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = DynamicSchemaField


class MessageTable(EbsadminTableReport):
    account = columns.LinkColumn(
        'account_edit',
        verbose_name=u'Аккаунт',
        get_params={
            'id': A('account.id')
        }
    )
    d = showconfirmcolumn(message=_(u'Удалить SMS сообщение?'))

    class Meta(EbsadminTableReport.Meta):
        model = Message


class SuppAgreementTable(EbsadminTableReport):
    id = columns.LinkColumn(
        'suppagreement_edit',
        get_params={
            'id': A('pk')
        },
        attrs={
            'a': {
                'rel': "alert3",
                'class': "open-custom-dialog"
            }
        }
    )
    accounts_count = columns.TemplateColumn(
        '''\
<a href='{% url 'account_list' %}?suppagreement={{record.id}}' \
class='btn btn-mini'>{{record.accounts_count}} <i class='icon-arrow-right'>\
</i></a>''',
        verbose_name=_(u'У аккаунтов'),
        accessor=A('accounts_count')
    )
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = SuppAgreement
        configurable = True


class AccountSuppAgreementTable(EbsadminTableReport):
    id = columns.LinkColumn(
        'accountsuppagreement_edit',
        get_params={
            'id': A('pk')
        },
        attrs={
            'a': {
                'rel': "alert3",
                'class': "open-custom-dialog"
            }
        }
    )
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = AccountSuppAgreement
        configurable = True

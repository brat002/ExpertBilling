#-*- coding=utf-8 -*-

from billservice.forms import AccountForm
from billservice.models import Account, SuspendedPeriod, AccountHardware, Transaction
from billservice.models import AccountAddonService, BalanceHistory, IPInUse, Template 
from billservice.models import SettlementPeriod, SystemUser, PrepaidTraffic
from billservice.models import TimeSpeed, AddonServiceTarif, PeriodicalServiceLog, News
from billservice.models import AddonService, SheduleLog, TrafficLimit, TimeAccessNode, RegistrationRequest
from billservice.models import TrafficTransmitNodes, IPPool, Group, Dealer, TransactionType, TrafficTransaction
from billservice.models import RadiusAttrs, Manufacturer, HardwareType, Hardware, Model, PermissionGroup, PeriodicalServiceHistory
from billservice.models import Card, SaleCard, Tariff, PeriodicalService, OneTimeService, RadiusTrafficNode, SubAccount, AddonServiceTransaction
from billservice.models import AccountSuppAgreement, SuppAgreement, News, TPChangeRule, Switch, AccountGroup, GroupStat, AccountPrepaysTrafic, AccountPrepaysRadiusTrafic, AccountPrepaysTime, ContractTemplate
from dynamicmodel.models import DynamicSchemaField

import django_tables2 as django_tables
from django_tables2.utils import A
from radius.models import ActiveSession, AuthLog
from object_log.models import LogItem
from nas.models import Nas, TrafficClass, TrafficNode
from django_tables2_reports.tables import TableReport
from django.utils.safestring import mark_safe
from django.utils.html import escape
from ebsadmin.models import TableSettings, Comment
from getpaid.models import Payment
from sendsms.models import Message

from helpdesk.models import Ticket
import itertools
from django.utils.translation import ugettext_lazy as _

from ebsadmin.transactionreport import servicemodel_by_table
from django.db.models import Sum

class FormatBlankColumn(django_tables.Column):
    def render(self, value):
        return "" if value is None else value

class FormatBooleanHTMLColumn(django_tables.TemplateColumn):
    def render(self, value):
        return "" if value else value
    


class FormatFloatColumn(django_tables.Column):
    def render(self, value):
        return "%.2f" % float(value) if value else ''
    
class FormatDateTimeColumn(django_tables.Column):
    def render(self, value):
        try:
            return value.strftime("%d.%m.%Y %H:%M:%S") if value else ''
        except:
            return value

class FormatBlankSpeedColumn(django_tables.LinkColumn):
    def render(self, value):
        return value if value else ''
    
class YesNoColumn(django_tables.Column):
    def render(self, value):
        return mark_safe('<img src="/media/icons/16/%s.png" />'
                         % ('accept' and True or 'cross'))

class RadioColumn(django_tables.Column):
    def render(self, value, bound_column):
        default = {
            'type': 'radio',
            'name': bound_column.name,
            'value': value
        }
        general = self.attrs.get('input')
        specific = self.attrs.get('td__input')
        attrs = django_tables.utils.AttributeDict(default, **(specific or general or {}))
        return mark_safe(u'<input %s/>' % attrs.as_html())

class SubAccountsTable(django_tables.Table):
    id = django_tables.LinkColumn('subaccount', get_params={'id':A('pk')})
    username = django_tables.LinkColumn('subaccount', get_params={'id':A('pk')})
    #password = FormatBlankColumn()
    nas = FormatBlankColumn()
    
    vpn_ip_address = FormatBlankColumn()
    ipn_ip_address = FormatBlankColumn()
    ipn_mac_address = FormatBlankColumn()
    
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    
    def __init__(self, *args, **argv):
        super(SubAccountsTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
    

    
    class Meta:
        model = SubAccount
        configurable=True
        available_fields = ('id', 'username',  'nas', 'vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'd')
        exclude = ('password', )
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-disable-hover table-bordered table-condensed'}


class AccountHardwareTable(django_tables.Table):
    id = django_tables.LinkColumn('accounthardware', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)

    def __init__(self, *args, **argv):
        super(AccountHardwareTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = AccountHardware
        fields = ('id', 'hardware','datetime', 'returned', 'comment')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class AccountAddonServiceTable(django_tables.Table):
    id = django_tables.LinkColumn('accountaddonservice', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    account =  FormatBlankColumn()
    service =  django_tables.Column()
    subaccount =  django_tables.LinkColumn('subaccount', get_params={'id':A('subaccount.id')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    #service = django_tables.LinkColumn('subaccount_detail', args=[A('pk')])
    cost =  django_tables.TemplateColumn('{{record.cost|default:record.service.cost|floatformat}}')
    activated = FormatDateTimeColumn()
    deactivated = FormatDateTimeColumn()
    temporary_blocked = FormatDateTimeColumn(verbose_name=_(u'Отключена'))
    #d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
        
    def __init__(self, *args, **argv):
        super(AccountAddonServiceTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = AccountAddonService
        #sequence = ('id', 'service', 'cost', 'activated', 'deactivated', 'temporary_blocked', '')
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
            
        
class SuspendedPeriodTable(django_tables.Table):

    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)

    def __init__(self, *args, **argv):
        super(SuspendedPeriodTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
            
    class Meta:
        model = SuspendedPeriod
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class AccountTarifTable(django_tables.Table):
    id = FormatBlankColumn()
    tarif = FormatBlankColumn()
    datetime = FormatDateTimeColumn()
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    def __init__(self, *args, **argv):
        super(AccountTarifTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
    
    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
            
            #-*-coding=utf-8-*-
class TotalTransactionReportTable(TableReport):
    tariff__name = FormatBlankColumn(verbose_name=_(u'Тариф'))
    id = FormatBlankColumn()
    account = django_tables.LinkColumn('account_edit', verbose_name=_(u'Аккаунт'), get_params={'id':A('account')}, accessor=A('account__username'))
    fullname = FormatBlankColumn(verbose_name=_(u'ФИО'), accessor=A('account__fullname'))
    address =  FormatBlankColumn(verbose_name=_(u'Адреc'), orderable=False, accessor=A('account__house'))
    bill = FormatBlankColumn(verbose_name=_(u'Платёжный документ'))
    description = FormatBlankColumn(verbose_name=_(u'Комментарий'))
    service_id = django_tables.Column(verbose_name=_(u'ID Услуги'))
    type = FormatBlankColumn(verbose_name=_(u'Тип'), accessor=A('type__name'))
    is_bonus = FormatBlankColumn(verbose_name=_(u'Бонус'))

    summ = FormatFloatColumn(verbose_name=_(u'Сумма'))
    prev_balance = FormatFloatColumn(verbose_name=_(u'Предыдущий баланс'))
    created = FormatDateTimeColumn(verbose_name=_(u'Создана'))
    end_promise = FormatDateTimeColumn(verbose_name=_(u'Окончание о.п.'))
    promise_expired = FormatDateTimeColumn()
    d = django_tables.CheckBoxColumn(verbose_name=' ', orderable=False, accessor=A('id'))
    
    
    def __init__(self, *args, **argv):
        super(TotalTransactionReportTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    def render_d(self, value, record):

        return mark_safe('<input type="checkbox" name="d" value="%s__%s">' % (record.get('table'), value))
    
    def render_address(self, value, record):
        return '%s %s %s/%s' % (record.get('account__city__name'), record.get('account__street'), record.get('account__house'), record.get('account__room'))
    
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

    
    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed"'}
        configurable = True
        available_fields = ("id", "account", "fullname",  'address', "type", "summ", 'prev_balance', "bill", "description", "end_promise",  "service_id", "created", 'd')
        #model = TotalTransactionReport
        #exclude = ( 'table','tariff__name', "tariff", "systemuser")
        
        
class TransactionReportTable(TableReport):

    id = FormatBlankColumn()
    account = django_tables.LinkColumn('account_edit', verbose_name=_(u'Аккаунт'), get_params={'id':A('account')}, accessor=A('account__username'))
    fullname = FormatBlankColumn(verbose_name=_(u'ФИО'), accessor=A('account__fullname'))
    address =  FormatBlankColumn(verbose_name=_(u'Адреc'), orderable=False, accessor=A('account__house'))
    type = FormatBlankColumn(verbose_name=_(u'Тип'), accessor=A('type__name'))
    prev_balance = FormatFloatColumn(verbose_name=_(u'Предыдущий баланс'))
    systemuser = FormatBlankColumn(verbose_name=_(u'Выполнил'), accessor=A('systemuser__username'))
    d = django_tables.CheckBoxColumn(verbose_name=' ', orderable=False, accessor=A('id'))
    
    def __init__(self, *args, **argv):
        super(TransactionReportTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    def render_d(self, value, record):
        return mark_safe('<input type="checkbox" name="d" value="billservice_transaction__%s">' % ( value, ))
    
    def render_summ(self, value, record):
        return '%.2f' % value
    
    def render_address(self, value, record):
        return '%s %s %s/%s' % (record.get('account__city__name'), record.get('account__street'), record.get('account__house'), record.get('account__room'))

    
    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed"'}
        model = Transaction
        configurable = True
        exclude = ('tarif', 'approved', 'accounttarif')
        
class AddonServiceTransactionReportTable(TableReport):

    id = FormatBlankColumn()
    account = django_tables.LinkColumn('account_edit', verbose_name=_(u'Аккаунт'), get_params={'id':A('account')}, accessor=A('account__username'))
    fullname = FormatBlankColumn(verbose_name=_(u'ФИО'), accessor=A('account__fullname'))
    address =  FormatBlankColumn(verbose_name=_(u'Адреc'), orderable=False, accessor=A('account__house'))
    type = FormatBlankColumn(verbose_name=_(u'Тип'), accessor=A('type__name'))
    prev_balance = FormatFloatColumn(verbose_name=_(u'Предыдущий баланс'))
    d = django_tables.CheckBoxColumn(verbose_name=' ', orderable=False, accessor=A('id'))
    
    def __init__(self, *args, **argv):
        super(AddonServiceTransactionReportTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    def render_d(self, value, record):

        return mark_safe('<input type="checkbox" name="d" value="billservice_addonservicetransaction__%s">' % ( value, ))
    
    def render_summ(self, value, record):
        return '%.2f' % value

    def render_address(self, value, record):
        return '%s %s %s/%s' % (record.get('account__city__name'), record.get('account__street'), record.get('account__house'), record.get('account__room'))
    
    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed"'}
        model = AddonServiceTransaction
        configurable = True
        exclude = ('tarif', 'approved', 'accounttarif')
        
        #available_fields = ("id", "account",  "type", "summ", "bill", "description", "end_promise",  "service__name", "created", 'd')
        
class PeriodicalServiceTransactionReportTable(TableReport):

    id = FormatBlankColumn()
    account__username = django_tables.LinkColumn('account_edit', verbose_name=_(u'Аккаунт'), get_params={'id':A('account')})
    fullname = FormatBlankColumn(verbose_name=_(u'ФИО'), accessor=A('account__fullname'))
    address =  FormatBlankColumn(verbose_name=_(u'Адреc'), orderable=False, accessor=A('account__house'))
    service = django_tables.Column(accessor=A('service__name'))
    prev_balance = FormatFloatColumn(verbose_name=_(u'Предыдущий баланс'))
    type = django_tables.Column(accessor=A('type__name'))
    real_created = FormatDateTimeColumn()
    d = django_tables.CheckBoxColumn(verbose_name=' ', orderable=False, accessor=A('id'))
    
    def __init__(self, *args, **argv):
        super(PeriodicalServiceTransactionReportTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    def render_d(self, value, record):

        return mark_safe('<input type="checkbox" name="d" value="billservice_periodicalservicehistory__%s">' % ( value, ))
    
    def render_address(self, value, record):
        return '%s %s %s/%s' % (record.get('account__city__name'), record.get('account__street'), record.get('account__house'), record.get('account__room'))
    
    def render_summ(self, value, record):
        return '%.2f' % value
    
    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed"'}
        model = PeriodicalServiceHistory
        sequence = ('id', 'account__username', 'service')
        configurable = True
        exclude = ('tarif', 'approved', 'accounttarif')


class TrafficTransactionReportTable(TableReport):

    id = FormatBlankColumn()
    account__username = django_tables.LinkColumn('account_edit', verbose_name=_(u'Аккаунт'), get_params={'id':A('account')})
    fullname = FormatBlankColumn(verbose_name=_(u'ФИО'), accessor=A('account__fullname'))
    address =  FormatBlankColumn(verbose_name=_(u'Адреc'), orderable=False, accessor=A('account__house'))
    #type = django_tables.Column(accessor=A('type__name'))
    prev_balance = FormatFloatColumn(verbose_name=_(u'Предыдущий баланс'))
    d = django_tables.CheckBoxColumn(verbose_name=' ', orderable=False, accessor=A('id'))
    
    def __init__(self, *args, **argv):
        super(TrafficTransactionReportTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    def render_d(self, value, record):

        return mark_safe('<input type="checkbox" name="d" value="billservice_traffictransaction__%s">' % ( value, ))
    
    def render_address(self, value, record):
        return '%s %s %s/%s' % (record.get('account__city__name'), record.get('account__street'), record.get('account__house'), record.get('account__room'))
    
    def render_summ(self, value, record):
        return '%.2f' % value
    
    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed"'}
        model = TrafficTransaction
        sequence = ('id', 'account__username', )
        configurable = True
        exclude = ('tarif', 'traffictransmitservice', 'accounttarif', 'account')


class CashierReportTable(TableReport):
    
    summ = FormatFloatColumn(verbose_name=_(u'Сумма'))
    fullname =django_tables.Column(verbose_name=u'ФИО', accessor=A('account.fullname'))
    address = django_tables.TemplateColumn(u"{{record.account.street|default:''}} {{record.account.house|default:''}}-{{record.account.room|default:''}}", orderable=False)
    prev_balance = FormatFloatColumn(verbose_name=_(u'Предыдущий баланс'))
    created = FormatDateTimeColumn(verbose_name=_(u'Создан'))
    
    def __init__(self, *args, **argv):
        super(CashierReportTable, self).__init__(*args, **argv)
        self.name = 'CashierReportTable'
        
    class Meta:
        model = Transaction
        configurable = True
        #available_fields = ('id', 'account', 'fullname', 'type', 'bill', 'description',  'summ', 'prev_balance', 'promise', 'promise_expired', 'created')
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed"'}
        exclude = ('approved', 'accounttarif', 'tariff')
        

class AccountsReportTable(TableReport):
    row_number = django_tables.Column(verbose_name='#', empty_values=(), orderable=False)
    #id = FormatBlankColumn()
    username = django_tables.LinkColumn('account_edit', verbose_name=_(u'Логин'), get_params={'id':A('pk')})
    contract = FormatBlankColumn(verbose_name=_(u'Договор'))
    fullname = FormatBlankColumn()
    address = django_tables.TemplateColumn(u"{{record.street|default:''}} {{record.house|default:''}}-{{record.room|default:''}}", orderable=False)
    entrance = django_tables.Column(verbose_name=_(u'Подъезд'))
    row = django_tables.Column(verbose_name=_(u'Этаж'))
    ballance = FormatFloatColumn()
    tariff  = FormatBlankColumn(verbose_name=_(u"Тариф"), orderable=False)
    ips  = FormatBlankColumn(verbose_name=_(u"IP"), orderable=False)
    d = django_tables.CheckBoxColumn(verbose_name=' ', orderable=False, accessor=A('pk'))
    #credit = FormatFloatColumn()
    #created = FormatDateTimeColumn()

    def __init__(self, form, *args, **kwargs):
        super(AccountsReportTable, self).__init__(form, *args, **kwargs)
        self.counter = itertools.count()
        self.footer_data = self.TableDataClass(data=[self.data.queryset.aggregate(ballance=Sum('ballance'))], table=self)
        self.footer = django_tables.rows.BoundRows(self.footer_data, self)
        self.name = self.__class__.__name__    

    def paginate(self, *args, **kwargs):
        super(AccountsReportTable, self).paginate(*args, **kwargs)        
        #print 'pagg', len(self.page.object_list), self.per_page, self.data.queryset.count()

        
    #def render_ballance(self, value):
    #    return mark_safe(value)
    
    def render_row_number(self):
        return '%d' % next(self.counter)
    
    class Meta:
        model = Account
        configurable = True
        exclude = ('password', )
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-bordered table-condensed'}
        annotations = ('ballance', )
        
class AccountsCashierReportTable(TableReport):
    d = RadioColumn(verbose_name=' ', orderable=False, accessor=A('pk'))
    row_number = django_tables.Column(verbose_name=u'#', empty_values=(), orderable=False)
    #id = FormatBlankColumn()
    username = django_tables.LinkColumn('account_edit', verbose_name=_(u'Логин'), get_params={'id':A('pk')})
    contract = FormatBlankColumn(verbose_name=_(u'Договор'))
    fullname = FormatBlankColumn()
    tariff  = FormatBlankColumn()
    address = django_tables.TemplateColumn(u"{{record.city|default:''}} {{record.street|default:''}} {{record.house|default:''}}-{{record.room|default:''}}", orderable=False)
    entrance = django_tables.Column(verbose_name=_(u'Подъезд'))
    row = django_tables.Column(verbose_name=_(u'Этаж'))
    ballance = FormatFloatColumn()
    bonus_ballance = FormatFloatColumn()
    
    


    def __init__(self, *args, **kwargs):
        super(AccountsCashierReportTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()
        self.name = 'AccountsCashierReportTable'
        
    def render_row_number(self):
        return '%d' % next(self.counter)
    
    class Meta:
        #model = Account

        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-bordered table-condensed'}
        
class ActiveSessionTable(TableReport):
    row_number = django_tables.Column(verbose_name=u'#', empty_values=(), orderable=False)
    session_status = django_tables.TemplateColumn("<span class='label {% if record.session_status == 'ACK' %}info{% endif %}'>{{ record.session_status }}</span>")
    date_start = FormatDateTimeColumn()
    interrim_update = FormatDateTimeColumn(verbose_name=_(u'Последнее обновление'))
    caller_id = django_tables.Column(verbose_name=_(u'Caller ID'), empty_values=())
    address = django_tables.TemplateColumn(u"{{record.account__street|default:''}} {{record.account__house|default:''}}-{{record.account__room|default:''}}", orderable=False, verbose_name=u'Адрес')
    framed_ip_address = django_tables.Column(verbose_name=_(u'IP'), empty_values=())
    framed_protocol = django_tables.Column(verbose_name=_(u'Протокол'), empty_values=())
    session_time = django_tables.Column(verbose_name=_(u'Онлайн'), empty_values=())
    date_end = FormatDateTimeColumn()
    nas_int = django_tables.Column(verbose_name=_(u'NAS'), accessor=A('nas_int__name'))
    bytes = django_tables.TemplateColumn("{{record.bytes_in|filesizeformat}}/{{record.bytes_out|filesizeformat}}", verbose_name=_(u'Байт'))
    #account = django_tables.LinkColumn('account_edit', get_params={'id':A('account.id')})
    subaccount__username = django_tables.LinkColumn('subaccount', get_params={'id':A('subaccount')}, verbose_name=_(u'Субаккаунт'))
    action = django_tables.TemplateColumn("<button data='{{record.id}}' class='btn btn-success btn-mini sreset' title='Soft reset'>R</button>&nbsp;<button data='{{record.id}}' class='btn btn-danger btn-mini hreset' title='Hard reset'>H</button>&nbsp;<button class='btn btn-info btn-mini ping' title='Ping' data='{{record.framed_ip_address}}'>P</button>", verbose_name=_(u'Action'))
    
    def __init__(self, *args, **kwargs):
        super(ActiveSessionTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()
        self.name = self.__class__.__name__
        
    def render_row_number(self):
        return '%d' % next(self.counter)

    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        model = ActiveSession
        configurable=True
        available_fields = ('row_number', 'subaccount__username', 'date_start', 'interrim_update', 'date_end',  'nas_int', 'caller_id', 'framed_ip_address', 'framed_protocol', 'session_time','bytes', 'session_status', 'action')
        #exclude = ("id", "speed_string", 'called_id', 'nas_id', 'bytes_in', 'bytes_out', 'ipinuse', 'interrim_update', 'account', 'sessionid', 'acct_terminate_cause')
        attrs = {'class': 'table table-bordered table-condensed'}

class AuthLogTable(TableReport):
    account = django_tables.LinkColumn('account_edit', get_params={'id':A('account.id')})
    subaccount = django_tables.LinkColumn('subaccount', get_params={'id':A('subaccount.id')})
    nas = FormatBlankColumn()
    datetime = FormatDateTimeColumn()
    
    def __init__(self, *args, **argv):
        super(AuthLogTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = AuthLog
        exclude = ('type', 'id')
        attrs = {'class': 'table table-bordered table-condensed'}
        
class BallanceHistoryTable(TableReport):
    account__username = django_tables.LinkColumn('account_edit', get_params={'id':A('account')})
    balance = FormatBlankColumn(verbose_name=_(u'Новый баланс'))
    summ = FormatBlankColumn(verbose_name=_(u'Сумма'))
    datetime = FormatDateTimeColumn()
    
    def __init__(self, *args, **argv):
        super(BallanceHistoryTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class IPInUseTable(TableReport):
    datetime = FormatDateTimeColumn()
    disabled = FormatDateTimeColumn()
    
    def __init__(self, *args, **argv):
        super(IPInUseTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = IPInUse
        attrs = {'class': 'table table-striped table-bordered table-condensed'}


class LogTable(TableReport):
    user = FormatBlankColumn()
    changed_fields = FormatBlankColumn()
    
    def __init__(self, *args, **argv):
        super(LogTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class NasTable(TableReport):
    #row_number = django_tables.Column(verbose_name="#")
    name = django_tables.LinkColumn('nas_edit', verbose_name=_(u"Имя"), get_params={'id':A('pk')})
    radiusattrs = django_tables.TemplateColumn(u"<a href='{% url 'radiusattr' %}?nas={{record.id}}' class='btn btn-mini btn-primary'>Изменить</a>", verbose_name=_(u'RADIUS атрибуты'), orderable=False)
    id = django_tables.LinkColumn('nas_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    def __init__(self, *args, **argv):
        super(NasTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = Nas
        configurable = True
        #exclude = ("secret", 'login', 'password', 'snmp_version', 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        available_fields=( 'id', 'name', 'radiusattrs', 'identify', 'type', 'ipaddress')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TemplateTable(TableReport):
    id = django_tables.LinkColumn('template_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('template_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        "data-clickmessage='Удалить?'>"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )
    
    def __init__(self, *args, **argv):
        super(TemplateTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = Template
        configurable = False
        exclude = ("", 'body')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class SettlementPeriodTable(TableReport):
    id = django_tables.LinkColumn('settlementperiod_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('settlementperiod_edit', get_params={'id':A('pk')})
    time_start = FormatDateTimeColumn()
    length = FormatBlankColumn()
    
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    def __init__(self, *args, **argv):
        super(SettlementPeriodTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = SettlementPeriod
        #exclude = ("secret", 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class SystemUserTable(TableReport):
    id = django_tables.LinkColumn('systemuser_edit', get_params={'id':A('pk')})
    username = django_tables.LinkColumn('systemuser_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        "data-clickmessage='Удалить?'>"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )
    
    def __init__(self, *args, **argv):
        super(SystemUserTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = SystemUser
        configurable = True
        available_fields = ('id', 'username', 'last_login', 'd')
        exclude = ("password", 'text_password')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class AddonServiceTable(TableReport):
    id = django_tables.LinkColumn('addonservice_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('addonservice_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    def __init__(self, *args, **argv):
        super(AddonServiceTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = AddonService
        configurable = True
        #exclude = ('allow_activation', "wyte_period", 'wyte_cost', 'cancel_subscription', 'action', 'nas', 'service_activation_action', 'service_deactivation_action', 'change_speed', 'deactivate_service_for_blocked_account', 'change_speed_type', 'speed_units', 'max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx', 'burst_time_tx', 'burst_time_rx', 'min_tx', 'min_rx', 'priority')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class IPPoolTable(TableReport):
    id = django_tables.LinkColumn('ippool_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('ippool_edit', get_params={'id':A('pk')})
    next_ippool = FormatBlankColumn()
    pool_size = django_tables.Column(verbose_name=_(u'IP в пуле'), accessor=A('get_pool_size'), orderable=False)
    used_ip =  django_tables.Column(verbose_name=_(u'Используется'), accessor=A('get_used_ip_count'), orderable=False)
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    def __init__(self, *args, **argv):
        super(IPPoolTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = IPPool
        configurable = True
        #exclude = ("secret", 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        

class CommentTable(TableReport):
    def __init__(self, *args, **argv):
        super(CommentTable, self).__init__(*args, **argv)
        self.name = 'CommentTable'

    id = django_tables.LinkColumn('comment_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-log-custom-dialog"})
    done = django_tables.TemplateColumn("<a href='{% url 'comment_edit' %}?id={{record.id}}&done=True' class='btn btn-mini btn-success comment-done'><i class='icon-ok icon-white'></i></a>&nbsp;<a href='{{record.get_remove_url}}' class='btn btn-mini btn-danger show-confirm'><i class='icon-remove icon-white'></i></a>", verbose_name='Действия', orderable=False)
    object = django_tables.Column(verbose_name=u'Объект')
    #d = django_tables.TemplateColumn("", verbose_name=' ', orderable=False)
    
        
    class Meta:
        model = Comment
        configurable = True
        available_fields = ('id', 'comment', 'object', 'created', 'due_date', 'done', )
        #exclude = ("secret", 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
        
class TransactionTypeTable(TableReport):
    id = django_tables.LinkColumn('transactiontype_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('transactiontype_edit', get_params={'id':A('pk')})
    
    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        "data-clickmessage='Удалить проводку #{{ record.id }}?'>"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )
    
    def __init__(self, *args, **argv):
        super(TransactionTypeTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = TransactionType
        configurable = False
        #exclude = ("secret", 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TrafficClassTable(TableReport):
    id = django_tables.LinkColumn(
        'trafficclass_edit',
        get_params={'id':A('pk')},
        attrs={
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Изменить класс'),
            'data-dlgid': "trafficclass-modal"
        }
    )
    name = django_tables.LinkColumn(
        'trafficclass_edit',
        get_params={'id':A('pk')},
        attrs={
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Изменить класс'),
            'data-dlgid': "trafficclass-modal"
        }
    )
    directions = django_tables.TemplateColumn(u"<a href='{% url 'trafficnode_list' %}?id={{record.id}}' class='btn btn-primary btn-mini'>Список направлений</a>", verbose_name=_(u'Направления'), orderable=False)
    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        "data-clickmessage='Удалить?'>"
        "<i class='icon-remove'></i></a><input type='hidden' name='id' value='{{record.id}}'>",
        verbose_name=' ',
        orderable=False
    )
    
    def __init__(self, *args, **argv):
        super(TrafficClassTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = TrafficClass
        configurable = True
        #exclude = ("weight", )
        available_fields = ('id', 'name', 'passthrough', 'directions',   'd')
        #exclude = ("secret", 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TrafficNodeTable(TableReport):
    row_number = django_tables.Column(verbose_name="#", empty_values=(), orderable=False)
    #control = django_tables.TemplateColumn("<a class='edit'><i class='icon-edit'></i></a>", verbose_name=' ', orderable=False)
    id = django_tables.LinkColumn('trafficnode', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    
    d = django_tables.CheckBoxColumn(verbose_name=' ', orderable=False, accessor=A('pk'))

    def __init__(self, *args, **kwargs):
        super(TrafficNodeTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()
        self.name = self.__class__.__name__
        
    def render_row_number(self):
        return '%d' % next(self.counter)
    
    class Meta:
        model = TrafficNode
        configurable = True
        exclude = ("traffic_class", )
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        available_fields = ('row_number', 'id', 'name',  'protocol', 'src_port', 'in_index',  'src_ip', 'dst_ip', 'dst_port', 'out_index', 'src_as', 'dst_as', 'next_hop', 'd')


class UploadTrafficNodeTable(TableReport):
    row_number = django_tables.Column(verbose_name="#", empty_values=(), orderable=False)
    src_net = django_tables.Column(verbose_name="Src Net")
    dst_net = django_tables.Column(verbose_name="Dst Net")
    direction = django_tables.Column(verbose_name="Direction")
    #control = django_tables.TemplateColumn("<a class='edit'><i class='icon-edit'></i></a>", verbose_name=' ', orderable=False)
    
    
    

    def __init__(self, *args, **kwargs):
        super(UploadTrafficNodeTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()
        self.name = self.__class__.__name__
        
    def render_row_number(self):
        return '%d' % next(self.counter)
    
    class Meta:
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ('row_number', 'src_net', 'dst_net')


class RadiusAttrTable(TableReport):
    id = django_tables.LinkColumn(
        'radiusattr_edit',
        get_params={'id': A('pk')},
        attrs={
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Изменить атрибут'),
            'data-dlgid': "radiusattr-modal"
        }
    )
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    def __init__(self, *args, **argv):
        super(RadiusAttrTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = RadiusAttrs
        exclude = ("tarif", 'nas')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class ManufacturerTable(TableReport):
    id = django_tables.LinkColumn('manufacturer_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('manufacturer_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    def __init__(self, *args, **argv):
        super(ManufacturerTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = Manufacturer
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class ModelTable(TableReport):
    id = django_tables.LinkColumn(
        'model_edit',
        get_params={'id': A('pk')},
        attrs= {
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Изменить модель'),
            'data-dlgid': "model-modal"
        }
    )
    name = django_tables.LinkColumn(
        'model_edit',
        get_params={'id':A('pk')},
        attrs= {
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Изменить модель'),
            'data-dlgid': "model-modal"
        }
    )
    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        "data-clickmessage='Удалить? Удаление модели оборудования вызовет удаление всех связаных объектов в системе.'>"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )
    
    def __init__(self, *args, **argv):
        super(ModelTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = Model
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class HardwareTypeTable(TableReport):
    id = django_tables.LinkColumn(
        'hardwaretype_edit',
        get_params={'id':A('pk')},
        attrs= {
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Изменить тип'),
            'data-dlgid': "hardwaretype-modal"
        }
    )
    name = django_tables.LinkColumn(
        'hardwaretype_edit',
        get_params={'id':A('pk')},
        attrs= {
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Изменить тип'),
            'data-dlgid': "hardwaretype-modal"
        }
    )
    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        "data-clickmessage='Удалить? Удаление типа оборудования вызовёт удаление всех связанных объектов в системе.'>"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )
    
    def __init__(self, *args, **argv):
        super(HardwareTypeTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = HardwareType
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class HardwareTable(TableReport):
    id = django_tables.LinkColumn('hardware_edit', get_params={'id':A('pk')})
    model = django_tables.LinkColumn('hardware_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('hardware_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    def __init__(self, *args, **argv):
        super(HardwareTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = Hardware
        configurable = True
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class SwitchTable(TableReport):
    id = django_tables.LinkColumn('switch_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('switch_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    def __init__(self, *args, **argv):
        super(SwitchTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = Switch
        configurable=True
        available_fields = ("id", 'name', 'manufacturer', 'model', 'sn', 'city', 'street', 'place')
        #exclude = ('comment', 'snmp_version', 'ports_count', 'house', 'option82_template',  'identify',  'disable_port', 'remote_id', 'secret', 'option82_auth_type',  'monitored_ports', 'protected_ports', 'enable_port', 'snmp_community', 'broken_ports', 'uplink_ports', 'disabled_ports', 'password', 'ipaddress', 'macaddress', 'd', 'option82', 'username', 'snmp_support', 'management_method')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
        
class CardTable(TableReport):
    row_number = django_tables.Column(verbose_name="#", empty_values=(), orderable=False)
    start_date = FormatDateTimeColumn()
    end_date = FormatDateTimeColumn()
    created = FormatDateTimeColumn()
    salecard = FormatDateTimeColumn(verbose_name=_(u'Продана'), accessor=A('salecard.created'))
    activated = FormatDateTimeColumn()
    activated_by = FormatBlankColumn()
    tarif = FormatBlankColumn()
    nas = FormatBlankColumn()
    ippool = FormatBlankColumn()
    ext_id = FormatBlankColumn()
    d = django_tables.CheckBoxColumn(verbose_name=' ', orderable=False, accessor=A('pk'))


    def __init__(self, *args, **kwargs):
        super(CardTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()
        self.name = self.__class__.__name__

    def render_row_number(self):
        return '%d' % next(self.counter)


    class Meta:
        model = Card
        configurable = True
        available_fields = ('row_number',   'id', 'series', 'nominal', 'login', 'pin', 'type', 'tarif', 'nas', 'salecard', 'activated', 'activated_by', 'ippool', 'created', 'start_date', 'end_date', 'ext_id',  'd')
        attrs = {'class': 'table table-bordered table-condensed'}
        exclude = ('ipinuse', 'disabled', )

class SaleCardsTable(TableReport):
    row_number = django_tables.Column(verbose_name="#", empty_values=(), orderable=False)
    start_date = FormatDateTimeColumn()
    end_date = FormatDateTimeColumn()
    created = FormatDateTimeColumn()
    activated = FormatDateTimeColumn()
    tarif = FormatBlankColumn()
    nas = FormatBlankColumn()
    ippool = FormatBlankColumn()
    
    def __init__(self, *args, **argv):
        super(SaleCardsTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    def render_row_number(self):
        value = getattr(self, '_counter', 0)
        self._counter = value + 1
        return '%d' % value
    
    def render_row_class(self, value, record):
        return 'disabled-row' if record.disabled else ''
    
    class Meta:
        model = Card
        configurable = True
        available_fields = ('row_number',  'id', 'series', 'login', 'pin', 'nominal', 'type', 'tarif', 'nas',  'activated', 'ippool', 'created', 'start_date', 'end_date','ext_id',)
        attrs = {'class': 'table table-bordered table-condensed'}
        exclude = ('ipinuse', 'disabled', 'ip', 'activated_by',  'salecard')
        
class SaleCardTable(TableReport):
    id = django_tables.LinkColumn('salecard_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    def __init__(self, *args, **argv):
        super(SaleCardTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = SaleCard
        configurable = True
        exclude = ("tarif", 'nas')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class DealerTable(TableReport):
    def __init__(self,*args, **kwargs):
        super(DealerTable, self).__init__(*args, **kwargs)
        self.name = self.__class__.__name__
        
    id = django_tables.LinkColumn('dealer_edit', get_params={'id':A('pk')})
    organization = django_tables.LinkColumn('dealer_edit', get_params={'id':A('pk')})
    
    class Meta:
        model = Dealer
        configurable = True
        available_fields = ('id', 'organization', 'contactperson', 'unp', 'phone')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TariffTable(TableReport):
    name = django_tables.LinkColumn('tariff_edit', get_params={'id':A('pk')})
    radiusattrs = django_tables.TemplateColumn(u"<a href='{% url 'radiusattr' %}?tarif={{record.id}}' class='btn btn-mini btn-primary'>Изменить</a>", verbose_name=_(u'RADIUS атрибуты'), orderable=False)
    access_type = FormatBlankColumn(verbose_name=_(u'Тип доступа'), accessor=A('access_parameters.access_type'))
    
    accounts_count = django_tables.TemplateColumn(u"<a href='{% url 'account_list' %}?tariff={{record.id}}' class='btn btn-mini'>{{record.accounts_count}} <i class='icon-arrow-right'></i></a>", verbose_name=_(u'Аккаунтов'))
    
    def __init__(self, *args, **argv):
        super(TariffTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = Tariff
        configurable = True
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        available_fields = ( 'name', 'settlement_period', 'cost', 'access_type', 'reset_tarif_cost', 'accounts_count', 'radiusattrs')
        
class PeriodicalServiceTable(TableReport):
    id = django_tables.LinkColumn(
        'tariff_periodicalservice_edit',
        get_params={'id': A('pk')},
        attrs={
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Периодическая услуга'),
            'data-dlgid': "periodicalservice-modal"
        }
    )
    name = django_tables.LinkColumn(
        'tariff_periodicalservice_edit',
        get_params={'id': A('pk')},
        attrs={
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Периодическая услуга'),
            'data-dlgid': "periodicalservice-modal"
        }
    )
    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        "data-clickmessage='Удалить? Удаление периодической услуги вызовет обнуление информации о списаниях по ней. Вместо этого рекомемендуется воспользоваться отключением услуги.'>"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )
    created = FormatDateTimeColumn()
    deactivated = FormatDateTimeColumn()
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    def __init__(self, *args, **argv):
        super(PeriodicalServiceTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = PeriodicalService
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'name', 'settlement_period', 'cost', 'cash_method', 'ps_condition', 'condition_summ', 'created', 'deactivated' )
        
class GroupTable(TableReport):
    id = django_tables.LinkColumn('group_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        "data-clickmessage='Удалить? Удаление группы трафика вызовет её удаление во всех тарифных планах.'>"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )

    def __init__(self, *args, **argv):
        super(GroupTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = Group
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class RegistrationRequestTable(TableReport):
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)

    def __init__(self, *args, **argv):
        super(RegistrationRequestTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = RegistrationRequest
        attrs = {'class': 'table table-striped table-bordered table-condensed'}  


class ContractTemplateTable(TableReport):
    id = django_tables.LinkColumn('contracttemplate_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        "data-clickmessage='Удалить шаблон номера договора?'>"
        "<i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)

    def __init__(self, *args, **argv):
        super(ContractTemplateTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = ContractTemplate
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class TrafficTransmitNodesTable(TableReport):
    id = django_tables.LinkColumn(
        'tariff_traffictransmitnode_edit',
        get_params={'id': A('pk')},
        attrs={
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Правило начисления предоплаченного трафика'),
            'data-dlgid': "periodicalservice-modal"
        }
    )
    group = django_tables.LinkColumn('group_edit', get_params={'id':A('group.id')})
    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        "data-clickmessage='Удалить? Вы уверены, что хотите удалить запись?'>"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )
    
    def __init__(self, *args, **argv):
        super(TrafficTransmitNodesTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = TrafficTransmitNodes
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'timeperiod', 'group', 'cost','d' )

class PrepaidTrafficTable(TableReport):
    id = django_tables.LinkColumn('tariff_prepaidtraffic_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    group = django_tables.LinkColumn('group_edit', get_params={'id':A('group.id')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    def __init__(self, *args, **argv):
        super(PrepaidTrafficTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = PrepaidTraffic
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'group', 'size', 'd')

class TimeSpeedTable(TableReport):
    id = django_tables.LinkColumn('tariff_timespeed_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #group = django_tables.LinkColumn('group_edit', get_params={'id':A('group.id')})
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    def __init__(self, *args, **argv):
        super(TimeSpeedTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = TimeSpeed
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'time', 'max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx', 'burst_time_tx', 'burst_time_rx', 'min_tx', 'min_rx', 'priority')

class OneTimeServiceTable(TableReport):
    id = django_tables.LinkColumn('onetimeservice_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('onetimeservice_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    def __init__(self, *args, **argv):
        super(OneTimeServiceTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = OneTimeService
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'name', 'cost', 'd')

class RadiusTrafficNodeTable(TableReport):
    id = django_tables.LinkColumn(
        'tariff_radiustrafficnode_edit',
        get_params={'id': A('pk')},
        attrs={
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Правило тарификации трафика'),
            'data-dlgid': "periodicalservice-modal"
        }
    )
    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        ">"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    def __init__(self, *args, **argv):
        super(RadiusTrafficNodeTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = RadiusTrafficNode
        fields = ("id", 'value', 'timeperiod', 'cost', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class TrafficLimitTable(TableReport):
    id = django_tables.LinkColumn(
        'tariff_trafficlimit_edit',
        get_params={'id': A('pk')},
        attrs={
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Лимит трафика'),
            'data-dlgid': "periodicalservice-modal"
        }
    )
    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        "data-clickmessage='Удалить лимит трафика?'>"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )
    speedlimit = django_tables.TemplateColumn(
        "<a href='{% url 'tariff_speedlimit_edit' %}?trafficlimit_id={{record.id}}' "
        "class='open-speedlimit-dialog' "
        "data-dlgtitle='Правило изменения скорости' "
        "data-dlgid='speedlimit-modal'"
        ">"
        "{% if record.speedlimit %}{{record.speedlimit}}"
        "<a href='{{record.speedlimit.get_remove_url}}' class='show-speedlimit-confirm' "
        "data-clickmessage='Удалить? Если в лимите трафика указано действие Изменить скорость - вы обязаны указать параметры изменения скорости.'>"
        "<i class='icon-remove'></i></a>{% else %}Указать{% endif %}</a>",
        verbose_name='Изменить скорость',
        orderable=False
    )
    #speed = TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    def __init__(self, *args, **argv):
        super(TrafficLimitTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = TrafficLimit
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'name', 'settlement_period', 'mode', 'group', 'size', 'action', 'speedlimit', 'd' )
        
class TimeAccessNodeTable(TableReport):
    id = django_tables.LinkColumn(
        'tariff_timeaccessnode_edit',
        get_params={'id': A('pk')},
        attrs={
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Правило тарификации времени'),
            'data-dlgid': "timeaccessnode-modal"
        }
    )

    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        "data-clickmessage='Удалить правило тарификации времени?'>"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    def __init__(self, *args, **argv):
        super(TimeAccessNodeTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = TimeAccessNode
        fields = ("id", 'time_period', 'cost', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
       
class AddonServiceTarifTable(TableReport):
    id = django_tables.LinkColumn('tariff_addonservicetariff_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    def __init__(self, *args, **argv):
        super(AddonServiceTarifTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = AddonServiceTarif
        fields = ("id", 'service', 'activation_count_period', 'activation_count', 'type', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 

class PeriodicalServiceLogTable(TableReport):

    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    datetime = FormatDateTimeColumn(verbose_name=_(u'Дата'))
    
    def __init__(self, *args, **argv):
        super(PeriodicalServiceLogTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = PeriodicalServiceLog
        configurable = True
        available_fields = ("id", 'accounttarif', 'service', 'datetime', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 
        
class SheduleLogTable(TableReport):

    d = django_tables.TemplateColumn("  ", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    accounttarif = FormatBlankColumn(verbose_name=_(u'Тариф аккаунта'))
    ballance_checkout = FormatDateTimeColumn(verbose_name=_(u'Доснятие до стоимости'))
    prepaid_traffic_reset = FormatDateTimeColumn(verbose_name=_(u'Обнуление предоплаченного трафика'))
    prepaid_traffic_accrued = FormatDateTimeColumn(verbose_name=_(u'Начисление предоплаченного трафика'))
    prepaid_time_reset = FormatDateTimeColumn(verbose_name=_(u'Обнуление предоплаченного времени'))
    prepaid_time_accrued = FormatDateTimeColumn(verbose_name=_(u'Начисление предоплаченного врeмени'))
    balance_blocked = FormatDateTimeColumn(verbose_name=_(u'Блокировка баланса'))
    
    def __init__(self, *args, **argv):
        super(SheduleLogTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = SheduleLog
        configurable = True
        #fields = ("id", 'accounttarif', 'service', 'datetime', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 

class NewsTable(TableReport):

    id = django_tables.LinkColumn('news_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        "data-clickmessage='Удалить новость?'>"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )
    created = FormatDateTimeColumn(verbose_name=_(u'Активна с'))
    age = FormatDateTimeColumn(verbose_name=_(u'Активна по'))

    def __init__(self, *args, **argv):
        super(NewsTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = News
        configurable = True
        available_fields = ("id", 'body', 'created', 'age', 'public', 'private', 'agent', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 
        

class TPChangeRuleTable(TableReport):

    id = django_tables.LinkColumn('tpchangerule_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        "data-clickmessage='Удалить правило?'>"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )
    settlement_period = FormatBlankColumn(verbose_name=_(u'Расчётный период'))
    on_next_sp = django_tables.TemplateColumn("<img src='/media/img/icons/{% if record.on_next_sp %}accept.png{% else %}icon_error.gif{% endif %}'>")
    row_class = django_tables.Column(visible=False)

    def __init__(self, *args, **argv):
        super(TPChangeRuleTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    def render_row_class(self, value, record):
        return 'error' if record.disabled else ''
    
    class Meta:
        model = TPChangeRule
        configurable = True
        available_fields = ("id", 'row_class',  'from_tariff', 'to_tariff', 'cost', 'ballance_min', 'on_next_sp', 'settlement_period', 'disabled', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 


class AccountGroupTable(TableReport):
    id = django_tables.LinkColumn(
        'accountgroup_edit',
        get_params={'id': A('pk')},
        attrs={'rel': "alert3", 'class': "general-modal-dialog", 'data-dlgid': "hardwaretype-modal", 'data-dlgtitle': _(u'Изменить тип')}
    )
    name = django_tables.LinkColumn(
        'accountgroup_edit',
        get_params={'id': A('pk')},
        attrs={'rel': "alert3", 'class': "general-modal-dialog", 'data-dlgid': "hardwaretype-modal", 'data-dlgtitle': _(u'Изменить тип')}
    )
    cnt = django_tables.TemplateColumn('{{record.account_set.count}}', verbose_name=_(u'Количество'))
    d = django_tables.TemplateColumn(
        "<a href='{{record.get_remove_url}}' class='show-confirm' "
        "data-clickmessage='Удалить?'>"
        "<i class='icon-remove'></i></a>",
        verbose_name=' ',
        orderable=False
    )
    
    def __init__(self, *args, **argv):
        super(AccountGroupTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = AccountGroup
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class ActionLogTable(TableReport):
    object1 = django_tables.Column(verbose_name=_(u'Объект'), accessor=A('object1'))
    
    def __init__(self, *args, **argv):
        super(ActionLogTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = LogItem
        configurable = True
        availablwe_fields = ('id', 'timestamp', 'user', 'action', 'object_type1', 'object1', 'changed_data')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class GroupStatTable(TableReport):

    account = django_tables.Column(_(u'Аккаунт'), accessor=A('account__username'))
    group = django_tables.Column(_(u'Группа'), accessor=A('group__name'))
    bytes = django_tables.TemplateColumn("{{record.summ_bytes|filesizeformat}}({{record.summ_bytes}})", verbose_name=_(u'Сумма'), accessor=A('summ_bytes'))
    #django_tables.TemplateColumn("{{record.bytes_in|filesizeformat}}({{record.bytes_in}})", verbose_name=_(u'ВХ')
    
    #def render_bytes(self, value, record):
    #    return value
    def __init__(self, *args, **argv):
        super(GroupStatTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        available_fields = ('account', 'group', 'bytes')
        configurable = True
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
      
class GlobalStatTable(TableReport):

    account = django_tables.Column(_(u'Аккаунт'), accessor=A('account__username'))
    #group = django_tables.Column(u'Группа', accessor=A('group__name'))
    bytes_in = django_tables.TemplateColumn("{{record.bytes_in|filesizeformat}}({{record.bytes_in}})", verbose_name=_(u'ВХ'))
    bytes_out = django_tables.TemplateColumn("{{record.bytes_out|filesizeformat}}({{record.bytes_out}})", verbose_name=_(u'ИСХ'))
    #min = django_tables.Column(u'С даты')
    max = django_tables.Column(_(u'Последние данные'))
    
    def __init__(self, *args, **argv):
        super(GlobalStatTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        available_fields = ('account', 'group', 'bytes')
        configurable = False
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class AccountPrepaysTraficTable(TableReport):

    #account = django_tables.Column(u'Аккаунт', accessor=A('account__username'))
    #group = django_tables.Column(u'Группа', accessor=A('group__name'))
    id = django_tables.LinkColumn(
        'accountprepaystraffic_edit',
        get_params={'id': A('pk')},
        attrs={
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Изменить значения'),
        }
    )
    account_tarif = django_tables.Column(_(u'Аккаунт/Тариф'))
    prepaid_traffic = django_tables.TemplateColumn("{{record.prepaid_traffic.size|filesizeformat}}({{record.prepaid_traffic.size}})", verbose_name=_(u'Начислено'))
    size = django_tables.TemplateColumn("{{record.size|filesizeformat}}({{record.size}})", verbose_name=_(u'Остаток'))
    progress = django_tables.TemplateColumn("""    <div class="progress progress-success">
          <div class="bar" style="width: {{record.in_percents}}%"></div>
        </div>""", verbose_name=_(u'Осталось'))

    datetime = FormatDateTimeColumn(verbose_name=_(u'Начислен'))
    
    def __init__(self, *args, **argv):
        super(AccountPrepaysTraficTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    def render_bytes(self, value, record):
        return value
    
    class Meta:
        model = AccountPrepaysTrafic
        configurable = True
        #fields = (u'account', 'group', u'bytes')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}  

class AccountPrepaysRadiusTraficTable(TableReport):

    #account = django_tables.Column(u'Аккаунт', accessor=A('account__username'))
    #group = django_tables.Column(u'Группа', accessor=A('group__name'))
    id = django_tables.LinkColumn('accountprepaystraffic_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    account_tarif = django_tables.Column(_(u'Аккаунт/Тариф'))
    size = django_tables.TemplateColumn("{{record.size|filesizeformat}}({{record.size}})", verbose_name=_(u'Остаток'))
    datetime = FormatDateTimeColumn(verbose_name=_(u'Начислен'))
    progress = django_tables.TemplateColumn("""    <div class="progress progress-success">
          <div class="bar" style="width: {{record.in_percents}}%"></div>
        </div>""", verbose_name=_(u'Расходовано'))
    
    
    def __init__(self, *args, **argv):
        super(AccountPrepaysRadiusTraficTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    def render_bytes(self, value, record):
        return value
    
    class Meta:
        model = AccountPrepaysRadiusTrafic
        configurable = True
        #fields = (u'account', 'group', u'bytes')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}  
        
class AccountPrepaysTimeTable(TableReport):

    #account = django_tables.Column(u'Аккаунт', accessor=A('account__username'))
    #group = django_tables.Column(u'Группа', accessor=A('group__name'))
    id = django_tables.LinkColumn(
        'accountprepaystraffic_edit',
        get_params={'id': A('pk')},
        attrs={
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Изменить тип')
        }
    )
    account_tarif = django_tables.Column(_(u'Аккаунт/Тариф'))
    
    datetime = FormatDateTimeColumn(verbose_name=_(u'Начислен'))
    progress = django_tables.TemplateColumn("""    <div class="progress progress-success">
          <div class="bar" style="width: {{record.in_percents}}%"></div>
        </div>""", verbose_name=_(u'Расходовано'))
    

    def __init__(self, *args, **argv):
        super(AccountPrepaysTimeTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    def render_bytes(self, value, record):
        return value
    
    class Meta:
        model = AccountPrepaysTime
        configurable = True
        #fields = (u'account', 'group', u'bytes')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}  
        
class SwitchPortsTable(TableReport):
    port = django_tables.TemplateColumn("<input type='hidden' name='port' value='{{record.port}}'>{{record.port}}", verbose_name=_(u'Порт'))
    broken_port = django_tables.TemplateColumn("<input type='checkbox' name='broken_port' {% if record.broken_port %} checked{% endif %}>", verbose_name=_(u'Битый'))
    uplink_port = django_tables.TemplateColumn("<input type='checkbox'  name='uplink_port' {% if record.uplink_port %} checked{% endif %}>", verbose_name=_(u'Аплинк'))
    protected_port = django_tables.TemplateColumn("<input type='checkbox'  name='protected_port' {% if record.protected_port %} checked{% endif %}>", verbose_name=_(u'Защита'))
    monitored_port = django_tables.TemplateColumn("<input type='checkbox'  name='monitored_port' {% if record.monitored_port %} checked{% endif %}>", verbose_name=_(u'Мониторинг'))
    disabled_port = django_tables.TemplateColumn("<input type='checkbox'  name='disabled_port' {% if record.disabled_port %} checked{% endif %}>", verbose_name=_(u'Отключён'))
    
    def __init__(self, *args, **argv):
        super(SwitchPortsTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        attrs = {'class': 'table table-bordered table-condensed'}  
        
class TicketTable(TableReport):
    
    id = django_tables.LinkColumn('helpdesk_view', args=[A('id')])
    title = django_tables.LinkColumn('helpdesk_view', args=[A('id')])
    created = FormatDateTimeColumn(verbose_name=_(u'Создан'))
    status = django_tables.Column(verbose_name=_(u'Статус'), accessor=A('_get_status'))

    def __init__(self, *args, **argv):
        super(TicketTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
    
    class Meta:
        model = Ticket
        configurable = True
        available_fields = ("id", 'title', 'queue', 'created', 'status', 'priority', )
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 
        
class PermissionGroupTable(TableReport):
    
    id = django_tables.LinkColumn('permissiongroup_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('permissiongroup_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)

    
    def __init__(self, *args, **argv):
        super(PermissionGroupTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = PermissionGroup
        available_fields = ("id", 'name', 'd', )
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 
        
        
class PaymentTable(TableReport):
    id = django_tables.LinkColumn('payment_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    account = django_tables.LinkColumn('account_edit', verbose_name=_(u'Аккаунт'), get_params={'id':A('account.id')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    def __init__(self, *args, **argv):
        super(PaymentTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = Payment
        #fields = ("id", 'service', 'activation_count_period', 'activation_count', 'type', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 


class DynamicSchemaFieldTable(TableReport):
    id = django_tables.LinkColumn(
        'dynamicschemafield_edit',
        get_params={'id': A('pk')},
        attrs={
            'rel': "alert3",
            'class': "general-modal-dialog",
            'data-dlgtitle': _(u'Изменить название'),
            'data-dlgid': "manufacturer-modal"
        }
    )
    #account = django_tables.LinkColumn('account_edit', verbose_name=u'Аккаунт', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    def __init__(self, *args, **argv):
        super(DynamicSchemaFieldTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = DynamicSchemaField
        #fields = ("id", 'service', 'activation_count_period', 'activation_count', 'type', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}   

class MessageTable(TableReport):
    #id = django_tables.LinkColumn('sessage_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    #account = django_tables.LinkColumn('account_edit', verbose_name=u'Аккаунт', get_params={'id':A('pk')})
    account = django_tables.LinkColumn('account_edit', verbose_name=u'Аккаунт', get_params={'id':A('account.id')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    def __init__(self, *args, **argv):
        super(MessageTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = Message
        #fields = ("id", 'service', 'activation_count_period', 'activation_count', 'type', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 

class SuppAgreementTable(TableReport):
    id = django_tables.LinkColumn('suppagreement_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    #account = django_tables.LinkColumn('account_edit', verbose_name=u'Аккаунт', get_params={'id':A('pk')})
    #account = django_tables.LinkColumn('account_edit', verbose_name=u'Аккаунт', get_params={'id':A('account.id')})
    accounts_count = django_tables.TemplateColumn("<a href='{% url 'account_list' %}?suppagreement={{record.id}}' class='btn btn-mini'>{{record.accounts_count}} <i class='icon-arrow-right'></i></a>", verbose_name=_(u'У аккаунтов'), accessor=A('accounts_count'))
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    #d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    def __init__(self, *args, **argv):
        super(SuppAgreementTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = SuppAgreement
        configurable = True
        
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 
        #fields = ("id", 'service', 'activation_count_period', 'activation_count', 't

class AccountSuppAgreementTable(TableReport):
    id = django_tables.LinkColumn('accountsuppagreement_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    #account = django_tables.LinkColumn('account_edit', verbose_name=u'Аккаунт', get_params={'id':A('pk')})
    #account = django_tables.LinkColumn('account_edit', verbose_name=u'Аккаунт', get_params={'id':A('account.id')})
    #accounts_count = django_tables.TemplateColumn("<a href='{% url 'account_list' %}?suppagreement={{record.id}}' class='btn btn-mini'>{{record.accounts_count}} <i class='icon-arrow-right'></i></a>", verbose_name=_(u'Аккаунтов'), accessor=A('accounts_count'))
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    #d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    def __init__(self, *args, **argv):
        super(AccountSuppAgreementTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__
        
    class Meta:
        model = AccountSuppAgreement
        configurable = True
        
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 


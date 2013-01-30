#-*-coding=utf-8-*-

from billservice.forms import AccountForm
from billservice.models import Account, SuspendedPeriod, AccountHardware
from billservice.models import AccountAddonService, BalanceHistory, IPInUse, Template 
from billservice.models import SettlementPeriod, SystemUser, PrepaidTraffic
from billservice.models import TimeSpeed, AddonServiceTarif, PeriodicalServiceLog, News
from billservice.models import AddonService, SheduleLog, TrafficLimit, TimeAccessNode 
from billservice.models import TrafficTransmitNodes, IPPool, Group, Dealer, TransactionType
from billservice.models import RadiusAttrs, Manufacturer, HardwareType, Hardware, Model, PermissionGroup
from billservice.models import Card, SaleCard, Tariff, PeriodicalService, OneTimeService, RadiusTrafficNode, SubAccount
from billservice.models import News, TPChangeRule, Switch, AccountGroup, GroupStat, AccountPrepaysTrafic, AccountPrepaysRadiusTrafic, AccountPrepaysTime
import django_tables2 as django_tables
from django_tables2.utils import A
from radius.models import ActiveSession, AuthLog
from object_log.models import LogItem
from nas.models import Nas, TrafficClass, TrafficNode
from django_tables2_reports.tables import TableReport
from django.utils.safestring import mark_safe
from django.utils.html import escape
from ebsadmin.models import TableSettings

from helpdesk.models import Ticket
import itertools

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
        return value.strftime("%d.%m.%Y %H:%M:%S") if value else ''

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
    password = FormatBlankColumn()
    nas = FormatBlankColumn()
    
    vpn_ip_address = FormatBlankColumn()
    ipn_ip_address = FormatBlankColumn()
    ipn_mac_address = FormatBlankColumn()
    
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    
    
    

    
    class Meta:
        model = SubAccount
        configurable=True
        available_fields = ('id', 'username', 'password', 'nas', 'vpn_ip_address', 'ipn_ip_address', 'ipn_mac_address', 'd')
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed'}


class AccountHardwareTable(django_tables.Table):

    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    class Meta:
        model = AccountHardware
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class AccountAddonServiceTable(django_tables.Table):
    id = django_tables.LinkColumn('accountaddonservice', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    account =  FormatBlankColumn()
    service =  django_tables.Column()
    subaccount =  django_tables.LinkColumn('subaccount', get_params={'id':A('subaccount.id')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    #service = django_tables.LinkColumn('subaccount_detail', args=[A('pk')])
    activated = FormatDateTimeColumn()
    deactivated = FormatDateTimeColumn()
    temporary_blocked = FormatDateTimeColumn(verbose_name=u'Отключена')
    #d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    
    
    
    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
            
        
class SuspendedPeriodTable(django_tables.Table):

    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    class Meta:
        model = SuspendedPeriod
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class AccountTarifTable(django_tables.Table):
    id = FormatBlankColumn()
    tarif = FormatBlankColumn()
    datetime = FormatDateTimeColumn()
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    

    
    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
            
            #-*-coding=utf-8-*-
class TotalTransactionReportTable(TableReport):
    tariff__name = FormatBlankColumn(verbose_name=u'Тариф')
    id = FormatBlankColumn()
    account__username = django_tables.LinkColumn('account_edit', verbose_name=u'Аккаунт', get_params={'id':A('account')})
    bill = FormatBlankColumn(verbose_name=u'Платёжный документ')
    description = FormatBlankColumn(verbose_name=u'Комментарий')
    service__name = FormatBlankColumn(verbose_name=u'Услуга')
    type__name = FormatBlankColumn(verbose_name=u'Тип')

    summ = FormatFloatColumn(verbose_name=u'Сумма')
    created = FormatDateTimeColumn(verbose_name=u'Создана')
    end_promise = FormatDateTimeColumn(verbose_name=u'Окончание о.п.')
    #promise_expired = FormatDateTimeColumn()
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed"'}
        
        available_fields = ("id", "account__username",  "type__name", "summ", "bill", "description", "end_promise",  "service__name", "created", 'd')
        #model = TotalTransactionReport
        #exclude = ( 'table','tariff__name', "tariff", "systemuser")
        
        
class AccountsReportTable(TableReport):
    row_number = django_tables.Column(verbose_name=u'#', empty_values=())
    #id = FormatBlankColumn()
    username = django_tables.LinkColumn('account_edit', verbose_name=u'Имя', get_params={'id':A('pk')})
    contract = FormatBlankColumn(verbose_name=u'Договор')
    fullname = FormatBlankColumn()
    address = django_tables.TemplateColumn(u"{{record.street|default:''}} {{record.house|default:''}}-{{record.room|default:''}}")
    entrance = django_tables.Column(verbose_name=u'Подъезд')
    row = django_tables.Column(verbose_name=u'Этаж')
    ballance = FormatFloatColumn()
    d = django_tables.CheckBoxColumn(verbose_name=' ', orderable=False, accessor=A('pk'))
    #credit = FormatFloatColumn()
    #created = FormatDateTimeColumn()

    def __init__(self, *args, **kwargs):
        super(AccountsReportTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()

    def render_row_number(self):
        return '%d' % next(self.counter)
    
    class Meta:
        model = Account
        configurable = True
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-bordered table-condensed'}
        
class AccountsCashierReportTable(TableReport):
    d = RadioColumn(verbose_name=' ', orderable=False, accessor=A('pk'))
    row_number = django_tables.Column(verbose_name=u'#', empty_values=())
    #id = FormatBlankColumn()
    username = django_tables.Column(verbose_name=u'Имя')
    contract = FormatBlankColumn(verbose_name=u'Договор')
    fullname = FormatBlankColumn()
    address = django_tables.TemplateColumn(u"{{record.street|default:''}} {{record.house|default:''}}-{{record.room|default:''}}")
    entrance = django_tables.Column(verbose_name=u'Подъезд')
    row = django_tables.Column(verbose_name=u'Этаж')
    ballance = FormatFloatColumn()
    
    


    def __init__(self, *args, **kwargs):
        super(AccountsCashierReportTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()

    def render_row_number(self):
        return '%d' % next(self.counter)
    
    class Meta:
        #model = Account

        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-bordered table-condensed'}
        
class ActiveSessionTable(TableReport):
    row_number = django_tables.Column(verbose_name=u'#', empty_values=())
    session_status = django_tables.TemplateColumn("<span class='label {% if record.session_status == 'ACK' %}info{% endif %}'>{{ record.session_status }}</span>")
    date_start = FormatDateTimeColumn()
    #interrim_update = FormatDateTimeColumn()
    caller_id = django_tables.Column(verbose_name=u'Caller ID', empty_values=())
    framed_ip_address = django_tables.Column(verbose_name=u'IP', empty_values=())
    framed_protocol = django_tables.Column(verbose_name=u'Протокол', empty_values=())
    session_time = django_tables.Column(verbose_name=u'Онлайн', empty_values=())
    date_end = FormatDateTimeColumn()
    nas_int = django_tables.Column(verbose_name=u'NAS', accessor=A('nas_int__name'))
    bytes = django_tables.TemplateColumn("{{record.bytes_in|filesizeformat}}/{{record.bytes_out|filesizeformat}}", verbose_name=u'Байт')
    #account = django_tables.LinkColumn('account_edit', get_params={'id':A('account.id')})
    subaccount__username = django_tables.LinkColumn('subaccount', get_params={'id':A('subaccount')}, verbose_name=u'Субаккаунт')

    def __init__(self, *args, **kwargs):
        super(ActiveSessionTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()

    def render_row_number(self):
        return '%d' % next(self.counter)

    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        model = ActiveSession
        configurable=True
        available_fields = ('row_number', 'subaccount__username', 'date_start', 'date_end',  'nas_int', 'caller_id', 'framed_ip_address', 'framed_protocol', 'session_time','bytes', 'session_status')
        #exclude = ("id", "speed_string", 'called_id', 'nas_id', 'bytes_in', 'bytes_out', 'ipinuse', 'interrim_update', 'account', 'sessionid', 'acct_terminate_cause')
        attrs = {'class': 'table table-bordered table-condensed'}

class AuthLogTable(TableReport):
    account = django_tables.LinkColumn('account_edit', get_params={'id':A('account.id')})
    subaccount = django_tables.LinkColumn('subaccount', get_params={'id':A('subaccount.id')})
    nas = FormatBlankColumn()
    datetime = FormatDateTimeColumn()
    
    class Meta:
        model = AuthLog
        exclude = ('type', 'id')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class BallanceHistoryTable(TableReport):
    account__username = django_tables.LinkColumn('account_edit', get_params={'id':A('account')})
    balance = FormatBlankColumn()
    datetime = FormatDateTimeColumn()
    
    class Meta:
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class IPInUseTable(TableReport):
    datetime = FormatDateTimeColumn()
    disabled = FormatDateTimeColumn()
    
    class Meta:
        model = IPInUse
        attrs = {'class': 'table table-striped table-bordered table-condensed'}


class LogTable(TableReport):
    user = FormatBlankColumn()
    changed_fields = FormatBlankColumn()
    
    class Meta:
        
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class NasTable(TableReport):
    #row_number = django_tables.Column(verbose_name="#")
    name = django_tables.LinkColumn('nas_edit', verbose_name=u"Имя", get_params={'id':A('pk')})
    radiusattrs = django_tables.TemplateColumn(u"<a href='{% url radiusattr %}?nas={{record.id}}' >Дополнительные RADIUS атрибуты</a>", verbose_name=u'Дополнительные RADIUS атрибуты', orderable=False)
    id = django_tables.LinkColumn('nas_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = Nas
        configurable = True
        #exclude = ("secret", 'login', 'password', 'snmp_version', 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        available_fields=( 'id', 'name', 'radiusattrs', 'identify', 'type', 'ipaddress')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TemplateTable(TableReport):
    id = django_tables.LinkColumn('template_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('template_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
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
    
    class Meta:
        model = SettlementPeriod
        #exclude = ("secret", 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class SystemUserTable(TableReport):
    id = django_tables.LinkColumn('systemuser_edit', get_params={'id':A('pk')})
    username = django_tables.LinkColumn('systemuser_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = SystemUser
        configurable = True
        available_fields = ('id', 'username', 'last_login', 'd')
        #exclude = ("password", 'text_password', 'address', 'passport', 'passport_details', 'passport_number', 'unp', 'im', 'home_phone','mobile_phone', 'created', 'host')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class AddonServiceTable(TableReport):
    id = django_tables.LinkColumn('addonservice_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('addonservice_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = AddonService
        configurable = True
        #exclude = ('allow_activation', "wyte_period", 'wyte_cost', 'cancel_subscription', 'action', 'nas', 'service_activation_action', 'service_deactivation_action', 'change_speed', 'deactivate_service_for_blocked_account', 'change_speed_type', 'speed_units', 'max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx', 'burst_time_tx', 'burst_time_rx', 'min_tx', 'min_rx', 'priority')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class IPPoolTable(TableReport):
    id = django_tables.LinkColumn('ippool_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('ippool_edit', get_params={'id':A('pk')})
    next_ippool = FormatBlankColumn()
    pool_size = django_tables.Column(verbose_name=u'IP в пуле', accessor=A('get_pool_size'))
    used_ip =  django_tables.Column(verbose_name=u'Используется', accessor=A('get_used_ip_count'))
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = IPPool
        configurable = True
        #exclude = ("secret", 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TransactionTypeTable(TableReport):
    id = django_tables.LinkColumn('transactiontype_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('transactiontype_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = TransactionType
        configurable = True
        #exclude = ("secret", 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TrafficClassTable(TableReport):
    id = django_tables.LinkColumn('trafficclass_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('trafficclass_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    directions = django_tables.TemplateColumn(u"<a href='{% url trafficnode_list %}?id={{record.id}}' >Список направлений</a>", verbose_name=u'Направления', orderable=False)
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a><input type='hidden' name='id' value='{{record.id}}'>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = TrafficClass
        configurable = True
        #exclude = ("weight", )
        available_fields = ('id', 'name', 'directions', 'passthrough',  'd')
        #exclude = ("secret", 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TrafficNodeTable(TableReport):
    row_number = django_tables.Column(verbose_name="#", empty_values=())
    #control = django_tables.TemplateColumn("<a class='edit'><i class='icon-edit'></i></a>", verbose_name=' ', orderable=False)
    id = django_tables.LinkColumn('trafficnode', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    
    d = django_tables.CheckBoxColumn(verbose_name=' ', orderable=False, accessor=A('pk'))

    def __init__(self, *args, **kwargs):
        super(TrafficNodeTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()

    def render_row_number(self):
        return '%d' % next(self.counter)
    
    class Meta:
        model = TrafficNode
        configurable = True
        exclude = ("traffic_class", )
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        available_fields = ('row_number', 'id', 'name', 'direction', 'protocol', 'src_ip', 'src_port', 'in_index', 'dst_ip', 'dst_port', 'out_index', 'src_as', 'dst_as', 'next_hop', 'd')

    
class RadiusAttrTable(TableReport):
    id = django_tables.LinkColumn('radiusattr_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = RadiusAttrs
        exclude = ("tarif", 'nas')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class ManufacturerTable(TableReport):
    id = django_tables.LinkColumn('manufacturer_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('manufacturer_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = Manufacturer
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class ModelTable(TableReport):
    id = django_tables.LinkColumn('model_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('model_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = Model
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class HardwareTypeTable(TableReport):
    id = django_tables.LinkColumn('hardwaretype_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('hardwaretype_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = HardwareType
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class HardwareTable(TableReport):
    id = django_tables.LinkColumn('hardware_edit', get_params={'id':A('pk')})
    model = django_tables.LinkColumn('hardware_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('hardware_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = Hardware
        configurable = True
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class SwitchTable(TableReport):
    id = django_tables.LinkColumn('switch_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('switch_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = Switch
        configurable=True
        available_fields = ("id", 'name', 'manufacturer', 'model', 'sn', 'city', 'street', 'place')
        #exclude = ('comment', 'snmp_version', 'ports_count', 'house', 'option82_template',  'identify',  'disable_port', 'remote_id', 'secret', 'option82_auth_type',  'monitored_ports', 'protected_ports', 'enable_port', 'snmp_community', 'broken_ports', 'uplink_ports', 'disabled_ports', 'password', 'ipaddress', 'macaddress', 'd', 'option82', 'username', 'snmp_support', 'management_method')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
        
class CardTable(TableReport):
    row_number = django_tables.Column(verbose_name="#", empty_values=())
    start_date = FormatDateTimeColumn()
    end_date = FormatDateTimeColumn()
    created = FormatDateTimeColumn()
    salecard = FormatDateTimeColumn(verbose_name=u'Продана', accessor=A('salecard.created'))
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

    def render_row_number(self):
        return '%d' % next(self.counter)


    class Meta:
        model = Card
        configurable = True
        available_fields = ('row_number',   'id', 'series', 'nominal', 'login', 'pin', 'type', 'tarif', 'nas', 'salecard', 'activated', 'activated_by', 'ippool', 'created', 'start_date', 'end_date', 'ext_id',  'd')
        attrs = {'class': 'table table-bordered table-condensed'}
        exclude = ('ipinuse', 'disabled', )

class SaleCardsTable(TableReport):
    row_number = django_tables.Column(verbose_name="#", empty_values=())
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
    
    class Meta:
        model = Card
        configurable = True
        available_fields = ('row_number',  'id', 'series', 'login', 'pin', 'nominal', 'type', 'tarif', 'nas',  'activated', 'ippool', 'created', 'start_date', 'end_date','ext_id',)
        attrs = {'class': 'table table-bordered table-condensed'}
        exclude = ('ipinuse', 'disabled', 'ip', 'activated_by',  'salecard')
        
class SaleCardTable(TableReport):
    id = django_tables.LinkColumn('salecard_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = SaleCard
        configurable = True
        exclude = ("tarif", 'nas')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class DealerTable(TableReport):
    def __init__(self,*args, **kwargs):
        super(DealerTable, self).__init__(*args, **kwargs)

        
    id = django_tables.LinkColumn('dealer_edit', get_params={'id':A('pk')})
    organization = django_tables.LinkColumn('dealer_edit', get_params={'id':A('pk')})
    
    class Meta:
        model = Dealer
        configurable = True
        available_fields = ('id', 'organization', 'contactperson', 'unp', 'phone')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TariffTable(TableReport):
    name = django_tables.LinkColumn('tariff_edit', get_params={'id':A('pk')})
    radiusattrs = django_tables.TemplateColumn(u"<a href='{% url radiusattr %}?tarif_id={{record.id}}' >Дополнительные RADIUS атрибуты</a>", verbose_name=u'Дополнительные RADIUS атрибуты', orderable=False)
    access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = Tariff
        configurable = True
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        available_fields = ( 'name', 'settlement_period', 'cost', 'access_type', 'reset_tarif_cost', 'radiusattrs')
        
class PeriodicalServiceTable(TableReport):
    id = django_tables.LinkColumn('tariff_periodicalservice_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('tariff_periodicalservice_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    created = FormatDateTimeColumn()
    deactivated = FormatDateTimeColumn()
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = PeriodicalService
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'name', 'settlement_period', 'cost', 'cash_method', 'condition', 'created', 'deactivated' )
        
class GroupTable(TableReport):
    id = django_tables.LinkColumn('group_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    class Meta:
        model = Group
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TrafficTransmitNodesTable(TableReport):
    id = django_tables.LinkColumn('tariff_traffictransmitnode_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    group = django_tables.LinkColumn('group_edit', get_params={'id':A('group.id')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = TrafficTransmitNodes
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'timeperiod', 'group', 'cost','d' )

class PrepaidTrafficTable(TableReport):
    id = django_tables.LinkColumn('tariff_prepaidtraffic_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    group = django_tables.LinkColumn('group_edit', get_params={'id':A('group.id')})
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = PrepaidTraffic
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'group', 'size')

class TimeSpeedTable(TableReport):
    id = django_tables.LinkColumn('tariff_prepaidtraffic_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #group = django_tables.LinkColumn('group_edit', get_params={'id':A('group.id')})
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = TimeSpeed
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'time', 'max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx', 'burst_time_tx', 'burst_time_rx', 'min_tx', 'min_rx', 'priority')

class OneTimeServiceTable(TableReport):
    id = django_tables.LinkColumn('onetimeservice_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('onetimeservice_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = OneTimeService
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'name', 'cost', 'd')

class RadiusTrafficNodeTable(TableReport):
    id = django_tables.LinkColumn('tariff_radiustrafficnode_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = RadiusTrafficNode
        fields = ("id", 'value', 'timeperiod', 'cost', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class TrafficLimitTable(TableReport):
    id = django_tables.LinkColumn('tariff_trafficlimit_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    speedlimit = django_tables.TemplateColumn("<a href='{% url tariff_speedlimit_edit %}?trafficlimit_id={{record.id}}' class='open-speedlimit-dialog'>{% if record.speedlimit %}{{record.speedlimit}}<a href='{{record.speedlimit.get_remove_url}}' class='show-speedlimit-confirm'><i class='icon-remove'></i></a>{% else %}Указать{% endif %}</a>", verbose_name='Изменить скорость', orderable=False)
    #speed = TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = TrafficLimit
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'name', 'settlement_period', 'mode', 'group', 'size', 'action', 'speedlimit', 'd' )
        
class TimeAccessNodeTable(TableReport):
    id = django_tables.LinkColumn('tariff_timeaccessnode_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = TimeAccessNode
        fields = ("id", 'time_period', 'cost', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
       
class AddonServiceTarifTable(TableReport):
    id = django_tables.LinkColumn('tariff_addonservicetariff_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = AddonServiceTarif
        fields = ("id", 'service', 'activation_count_period', 'activation_count', 'type', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 

class PeriodicalServiceLogTable(TableReport):

    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    datetime = FormatDateTimeColumn(verbose_name=u'Дата')
    
    class Meta:
        model = PeriodicalServiceLog
        configurable = True
        available_fields = ("id", 'accounttarif', 'service', 'datetime', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 
        
class SheduleLogTable(TableReport):

    d = django_tables.TemplateColumn("  ", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    accounttarif = FormatBlankColumn(verbose_name=u'Тариф аккаунта')
    ballance_checkout = FormatDateTimeColumn(verbose_name=u'Доснятие до стоимости')
    prepaid_traffic_reset = FormatDateTimeColumn(verbose_name=u'Обнуление предоплаченного трафика')
    prepaid_traffic_accrued = FormatDateTimeColumn(verbose_name=u'Начисление предоплаченного трафика')
    prepaid_time_reset = FormatDateTimeColumn(verbose_name=u'Обнуление предоплаченного времени')
    prepaid_time_accrued = FormatDateTimeColumn(verbose_name=u'Начисление предоплаченного врeмени')
    balance_blocked = FormatDateTimeColumn(verbose_name=u'Блокировка баланса')
    
    class Meta:
        model = SheduleLog
        configurable = True
        #fields = ("id", 'accounttarif', 'service', 'datetime', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 

class NewsTable(TableReport):

    id = django_tables.LinkColumn('news_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    created = FormatDateTimeColumn(verbose_name=u'Активна с')
    age = FormatDateTimeColumn(verbose_name=u'Активна по')

    
    class Meta:
        model = News
        configurable = True
        available_fields = ("id", 'body', 'created', 'age', 'public', 'private', 'agent', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 
        

class TPChangeRuleTable(TableReport):

    id = django_tables.LinkColumn('tpchangerule_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    settlement_period = FormatBlankColumn(verbose_name=u'Расчётный период')
    on_next_sp = django_tables.TemplateColumn("<img src='/media/img/icons/{% if record.on_next_sp %}accept.png{% else %}icon_error.gif{% endif %}'>")
    row_class = django_tables.Column(visible=False)

    def render_row_class(self, value, record):
        return 'error' if record.disabled else ''
    
    class Meta:
        model = TPChangeRule
        configurable = True
        available_fields = ("id", 'row_class',  'from_tariff', 'to_tariff', 'cost', 'ballance_min', 'on_next_sp', 'settlement_period', 'disabled', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 

class AccountGroupTable(TableReport):

    id = django_tables.LinkColumn('accountgroup_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('accountgroup_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    cnt = django_tables.TemplateColumn('{{record.account_set.count}}', verbose_name = u'Количество')
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = AccountGroup
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class ActionLogTable(TableReport):
    object1 = django_tables.Column(verbose_name=u'Объект', accessor=A('object1'))
    
    
    class Meta:
        model = LogItem
        configurable = True
        availablwe_fields = ('id', 'timestamp', 'user', 'action', 'object_type1', 'object1', 'changed_data')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class GroupStatTable(TableReport):

    account = django_tables.Column(u'Аккаунт', accessor=A('account__username'))
    group = django_tables.Column(u'Группа', accessor=A('group__name'))
    bytes = django_tables.Column(u'Сумма', accessor=A('summ_bytes'))
    
    def render_bytes(self, value, record):
        return value
    
    class Meta:
        available_fields = (u'account', 'group', u'bytes')
        configurable = True
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
      
class AccountPrepaysTraficTable(TableReport):

    #account = django_tables.Column(u'Аккаунт', accessor=A('account__username'))
    #group = django_tables.Column(u'Группа', accessor=A('group__name'))
    id = django_tables.LinkColumn('accountprepaystraffic_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    account_tarif = django_tables.Column(u'Аккаунт/Тариф')
    prepaid_traffic = django_tables.TemplateColumn("{{record.prepaid_traffic.size|filesizeformat}}", verbose_name=u'Начислено')
    size = django_tables.TemplateColumn("{{record.size|filesizeformat}}", verbose_name=u'Остаток')
    progress = django_tables.TemplateColumn("""    <div class="progress progress-success">
          <div class="bar" style="width: {{record.in_percents}}%"></div>
        </div>""", verbose_name=u'Осталось')

    datetime = FormatDateTimeColumn(verbose_name=u'Начислен')
    
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
    account_tarif = django_tables.Column(u'Аккаунт/Тариф')
    size = django_tables.TemplateColumn("{{record.size|filesizeformat}}", verbose_name=u'Остаток')
    datetime = FormatDateTimeColumn(verbose_name=u'Начислен')
    progress = django_tables.TemplateColumn("""    <div class="progress progress-success">
          <div class="bar" style="width: {{record.in_percents}}%"></div>
        </div>""", verbose_name=u'Расходовано')
    
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
    id = django_tables.LinkColumn('accountprepaystraffic_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    account_tarif = django_tables.Column(u'Аккаунт/Тариф')
    
    datetime = FormatDateTimeColumn(verbose_name=u'Начислен')
    progress = django_tables.TemplateColumn("""    <div class="progress progress-success">
          <div class="bar" style="width: {{record.in_percents}}%"></div>
        </div>""", verbose_name=u'Расходовано')
    
    def render_bytes(self, value, record):
        return value
    
    class Meta:
        model = AccountPrepaysTime
        configurable = True
        #fields = (u'account', 'group', u'bytes')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}  
        
class SwitchPortsTable(TableReport):
    port = django_tables.TemplateColumn("<input type='hidden' name='port' value='{{record.port}}'>{{record.port}}", verbose_name=u'Порт')
    broken_port = django_tables.TemplateColumn("<input type='checkbox' name='broken_port' {% if record.broken_port %} checked{% endif %}>", verbose_name=u'Битый')
    uplink_port = django_tables.TemplateColumn("<input type='checkbox'  name='uplink_port' {% if record.uplink_port %} checked{% endif %}>", verbose_name=u'Аплинк')
    protected_port = django_tables.TemplateColumn("<input type='checkbox'  name='protected_port' {% if record.protected_port %} checked{% endif %}>", verbose_name=u'Защита')
    monitored_port = django_tables.TemplateColumn("<input type='checkbox'  name='monitored_port' {% if record.monitored_port %} checked{% endif %}>", verbose_name=u'Мониторинг')
    disabled_port = django_tables.TemplateColumn("<input type='checkbox'  name='disabled_port' {% if record.disabled_port %} checked{% endif %}>", verbose_name=u'Отключён')
    
    class Meta:
        attrs = {'class': 'table table-bordered table-condensed'}  
        
class TicketTable(TableReport):
    
    id = django_tables.LinkColumn('helpdesk_view', args=[A('id')])
    title = django_tables.LinkColumn('helpdesk_view', args=[A('id')])
    created = FormatDateTimeColumn(verbose_name=u'Создан')
    status = django_tables.Column(verbose_name=u'Статус', accessor=A('_get_status'))

    
    
    class Meta:
        model = Ticket
        configurable = True
        available_fields = ("id", 'title', 'queue', 'created', 'status', 'priority', )
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 
        
class PermissionGroupTable(TableReport):
    
    id = django_tables.LinkColumn('permissiongroup_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('permissiongroup_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)

    
    
    class Meta:
        model = PermissionGroup
        available_fields = ("id", 'name', 'd', )
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 
        
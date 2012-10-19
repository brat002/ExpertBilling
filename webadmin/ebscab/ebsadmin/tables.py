#-*-coding=utf-8-*-

from billservice.forms import AccountForm
from billservice.models import Account, SuspendedPeriod, AccountHardware, AccountAddonService, BalanceHistory, IPInUse, Template, SettlementPeriod, SystemUser, PrepaidTraffic, TimeSpeed, AddonServiceTarif, PeriodicalServiceLog
from billservice.models import AddonService, SheduleLog, TrafficLimit, TimeAccessNode, TrafficTransmitNodes, IPPool, Group, Dealer, TransactionType, RadiusAttrs, Manufacturer, HardwareType, Hardware, Model, Card, SaleCard, Tariff, PeriodicalService, OneTimeService, RadiusTrafficNode
import django_tables2 as django_tables
from django_tables2.utils import A
from radius.models import ActiveSession, AuthLog
from object_log.models import LogItem
from nas.models import Nas, TrafficClass, TrafficNode, Switch

class FormatBlankColumn(django_tables.Column):
    def render(self, value):
        return "" if value is None else value

class FormatFloatColumn(django_tables.Column):
    def render(self, value):
        return "%.2f" % float(value) if value else ''
    
class FormatDateTimeColumn(django_tables.Column):
    def render(self, value):
        return value.strftime("%d.%m.%Y %H:%M:%S") if value else ''

class FormatBlankSpeedColumn(django_tables.LinkColumn):
    def render(self, value):
        return value if value else ''
    
class SubAccountsTable(django_tables.Table):
    row_number = django_tables.Column(verbose_name="#")
    id = django_tables.LinkColumn('subaccount', get_params={'id':A('pk')})
    username = django_tables.LinkColumn('subaccount', get_params={'id':A('pk')})
    password = FormatBlankColumn()
    nas = FormatBlankColumn()
    
    vpn_ip_address = FormatBlankColumn()
    ipn_ip_address = FormatBlankColumn()
    ipn_mac_address = FormatBlankColumn()
    
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    
    
    
    def render_row_number(self):
        value = getattr(self, '_counter', 0)
        self._counter = value + 1
        return '%d' % value
    
    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed'}


class AccountHardwareTable(django_tables.Table):

    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    class Meta:
        model = AccountHardware
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class AccountAddonServiceTable(django_tables.Table):
    row_number = django_tables.Column(verbose_name="#")
    id = django_tables.LinkColumn('accountaddonservice', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    account =  FormatBlankColumn()
    service =  django_tables.LinkColumn('addonservice_edit', get_params={'id':A('service.id')})
    subaccount =  django_tables.LinkColumn('subaccount', get_params={'id':A('subaccount.id')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    #service = django_tables.LinkColumn('subaccount_detail', args=[A('pk')])
    activated = FormatDateTimeColumn()
    deactivated = FormatDateTimeColumn()
    temporary_blocked = FormatDateTimeColumn()
    #d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    
    

    def render_row_number(self):
        value = getattr(self, '_counter', 0)
        self._counter = value + 1
        return '%d' % value
    
    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
            
        
class SuspendedPeriodTable(django_tables.Table):

    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    class Meta:
        model = SuspendedPeriod
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class AccountTarifTable(django_tables.Table):
    row_number = django_tables.Column(verbose_name="#")
    id = FormatBlankColumn()
    tarif = FormatBlankColumn()
    datetime = FormatDateTimeColumn()
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    

    def render_row_number(self):
        value = getattr(self, '_counter', 0)
        self._counter = value + 1
        return '%d' % value
    
    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
            
            #-*-coding=utf-8-*-
class TotalTransactionReportTable(django_tables.Table):
    tariff__name = FormatBlankColumn()
    id = FormatBlankColumn()
    account__username = django_tables.LinkColumn('account_edit', get_params={'id':A('account')})
    bill = FormatBlankColumn()
    description = FormatBlankColumn()
    service__name = FormatBlankColumn()
    type__name = FormatBlankColumn()

    summ = FormatFloatColumn()
    created = FormatDateTimeColumn()
    end_promise = FormatDateTimeColumn()
    #promise_expired = FormatDateTimeColumn()
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed"'}
        
        sequence = ("id", "account__username",  "type__name", "summ", "bill", "description", "end_promise",  "service__name", "created", 'd')
        #model = TotalTransactionReport
        exclude = ( 'table','tariff__name', "tariff", "systemuser")
        
        
class AccountsReportTable(django_tables.Table):
    row_number = django_tables.Column(verbose_name="#")
    id = FormatBlankColumn()
    username = django_tables.LinkColumn('account_edit', get_params={'id':A('pk')})
    contract = FormatBlankColumn()
    fullname = FormatBlankColumn()
    
    ballance = FormatFloatColumn()
    credit = FormatFloatColumn()
    created = FormatDateTimeColumn()

    def render_row_number(self):
        value = getattr(self, '_counter', 0)
        self._counter = value + 1
        return '%d' % value
    
    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class ActiveSessionTable(django_tables.Table):
    session_status = django_tables.TemplateColumn("<span class='label {% if record.session_status == 'ACK' %}info{% endif %}'>{{ record.session_status }}</span>")
    date_start = FormatDateTimeColumn()
    interrim_update = FormatDateTimeColumn()
    date_end = FormatDateTimeColumn()
    bytes = django_tables.TemplateColumn("{{record.bytes_in|filesizeformat}}/{{record.bytes_out|filesizeformat}}")
    account = django_tables.LinkColumn('account_edit', get_params={'id':A('account.id')})
    subaccount = django_tables.LinkColumn('subaccount', get_params={'id':A('subaccount.id')})
    
    class Meta:
        #attrs = {'class': 'table table-striped table-bordered table-condensed'}
        model = ActiveSession
        exclude = ("speed_string", 'called_id', 'nas_id', 'bytes_in', 'bytes_out', 'ipinuse')
        attrs = {'class': 'paleblue'}

class AuthLogTable(django_tables.Table):
    account = django_tables.LinkColumn('account_edit', get_params={'id':A('account.id')})
    subaccount = django_tables.LinkColumn('subaccount', get_params={'id':A('subaccount.id')})
    nas = FormatBlankColumn()
    datetime = FormatDateTimeColumn()
    
    class Meta:
        model = AuthLog
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class BallanceHistoryTable(django_tables.Table):
    account__username = django_tables.LinkColumn('account_edit', get_params={'id':A('account')})
    balance = FormatBlankColumn()
    datetime = FormatDateTimeColumn()
    
    class Meta:
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class IPInUseTable(django_tables.Table):
    datetime = FormatDateTimeColumn()
    disabled = FormatDateTimeColumn()
    
    class Meta:
        model = IPInUse
        attrs = {'class': 'table table-striped table-bordered table-condensed'}


class LogTable(django_tables.Table):
    user = FormatBlankColumn()
    changed_fields = FormatBlankColumn()
    
    class Meta:
        
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class NasTable(django_tables.Table):
    row_number = django_tables.Column(verbose_name="#")
    name = django_tables.LinkColumn('nas_edit', get_params={'id':A('pk')})
    radiusattrs = django_tables.TemplateColumn(u"<a href='{% url radiusattr %}?nas_id={{record.id}}' >Дополнительные RADIUS атрибуты</a>", verbose_name=u'Дополнительные RADIUS атрибуты', orderable=False)
    id = django_tables.LinkColumn('nas_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    def render_row_number(self):
        value = getattr(self, '_counter', 1)
        self._counter = value + 1
        return '%d' % value
    
    class Meta:
        model = Nas
        exclude = ("secret", 'login', 'password', 'snmp_version', 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        sequence=('row_number', 'id', 'name', 'radiusattrs', 'identify', 'type', 'ipaddress')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TemplateTable(django_tables.Table):
    id = django_tables.LinkColumn('template_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('template_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = Template
        exclude = ("", 'body', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class SettlementPeriodTable(django_tables.Table):
    id = django_tables.LinkColumn('settlementperiod_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('settlementperiod_edit', get_params={'id':A('pk')})
    time_start = FormatDateTimeColumn()
    length = FormatBlankColumn()
    
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = SettlementPeriod
        #exclude = ("secret", 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class SystemUserTable(django_tables.Table):
    id = django_tables.LinkColumn('systemuser_edit', get_params={'id':A('pk')})
    username = django_tables.LinkColumn('systemuser_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = SystemUser
        exclude = ("password", 'text_password', 'address', 'passport', 'passport_details', 'passport_number', 'unp', 'im', 'home_phone','mobile_phone', 'created', 'host')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class AddonServiceTable(django_tables.Table):
    id = django_tables.LinkColumn('addonservice_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('addonservice_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = AddonService
        exclude = ('allow_activation', "wyte_period", 'wyte_cost', 'cancel_subscription', 'action', 'nas', 'service_activation_action', 'service_deactivation_action', 'change_speed', 'deactivate_service_for_blocked_account', 'change_speed_type', 'speed_units', 'max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx', 'burst_time_tx', 'burst_time_rx', 'min_tx', 'min_rx', 'priority')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class IPPoolTable(django_tables.Table):
    id = django_tables.LinkColumn('ippool_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('ippool_edit', get_params={'id':A('pk')})
    next_ippool = FormatBlankColumn()
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = IPPool
        #exclude = ("secret", 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TransactionTypeTable(django_tables.Table):
    id = django_tables.LinkColumn('transactiontype_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('transactiontype_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = TransactionType
        #exclude = ("secret", 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TrafficClassTable(django_tables.Table):
    id = django_tables.LinkColumn('trafficclass_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('trafficclass_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    directions = django_tables.TemplateColumn(u"<a href='{% url trafficnode_list %}?id={{record.id}}' >Список направлений</a>", verbose_name=u'Направления', orderable=False)
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a><input type='hidden' name='id' value='{{record.id}}'>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = TrafficClass
        exclude = ("weight", )
        #exclude = ("secret", 'username', 'vpn_speed_action', 'ipn_speed_action', 'reset_action', 'subacc_disable_action', 'subacc_enable_action', 'subacc_add_action', 'subacc_delete_action', 'subacc_ipn_speed_action', 'speed_vendor_1', 'speed_vendor_2', 'speed_attr_id1', 'speed_attr_id2', 'speed_value1', 'speed_value2', 'acct_interim_interval', 'user_add_action', 'user_enable_action', 'user_disable_action', 'user_delete_action')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TrafficNodeTable(django_tables.Table):
    row_number = django_tables.Column(verbose_name="#")
    #control = django_tables.TemplateColumn("<a class='edit'><i class='icon-edit'></i></a>", verbose_name=' ', orderable=False)
    id = django_tables.LinkColumn('trafficnode', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    
    d = django_tables.CheckBoxColumn(verbose_name=' ', orderable=False, accessor=A('pk'))
    
    class Meta:
        model = TrafficNode
        exclude = ("traffic_class", )
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        sequence = ('row_number', 'id', 'name', 'direction', 'protocol', 'src_ip', 'src_port', 'in_index', 'dst_ip', 'dst_port', 'out_index', 'src_as', 'dst_as', 'next_hop', 'd')
    
    def render_row_number(self):
        value = getattr(self, '_counter', 0)
        self._counter = value + 1
        return '%d' % value
    
class RadiusAttrTable(django_tables.Table):
    id = django_tables.LinkColumn('radiusattr_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = RadiusAttrs
        exclude = ("tarif", 'nas')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class ManufacturerTable(django_tables.Table):
    id = django_tables.LinkColumn('manufacturer_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('manufacturer_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = Manufacturer
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class ModelTable(django_tables.Table):
    id = django_tables.LinkColumn('model_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('model_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = Model
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class HardwareTypeTable(django_tables.Table):
    id = django_tables.LinkColumn('radiusattr_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('hardwaretype_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = HardwareType
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class HardwareTable(django_tables.Table):
    id = django_tables.LinkColumn('hardware_edit', get_params={'id':A('pk')})
    model = django_tables.LinkColumn('hardware_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('hardware_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = Hardware
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class SwitchTable(django_tables.Table):
    id = django_tables.LinkColumn('switch_edit', get_params={'id':A('pk')})
    name = django_tables.LinkColumn('switch_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = Switch
        sequence = ("id", 'name', 'manufacturer', 'model', 'sn', 'city', 'street', 'place')
        exclude = ('comment', 'snmp_version', 'ports_count', 'house', 'option82_template',  'identify',  'disable_port', 'remote_id', 'secret', 'option82_auth_type',  'monitored_ports', 'protected_ports', 'enable_port', 'snmp_community', 'broken_ports', 'uplink_ports', 'disabled_ports', 'password', 'ipaddress', 'macaddress', 'd', 'option82', 'username', 'snmp_support', 'management_method')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
        
class CardTable(django_tables.Table):
    row_number = django_tables.Column(verbose_name="#")
    row_class = django_tables.Column(visible=False)
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
    
    def render_row_number(self):
        value = getattr(self, '_counter', 0)
        self._counter = value + 1
        return '%d' % value
    
    def render_row_class(self, value, record):
        return 'disabled-row' if record.disabled else ''
    
    class Meta:
        model = Card
        sequence = ('row_number', 'row_class',  'id', 'series', 'nominal', 'login', 'pin', 'type', 'tarif', 'nas', 'salecard', 'activated', 'activated_by', 'ippool', 'created', 'start_date', 'end_date', 'template',  'ext_id',  'd')
        attrs = {'class': 'table table-bordered table-condensed'}
        exclude = ('ipinuse', 'disabled', 'ip')

class SaleCardsTable(django_tables.Table):
    row_number = django_tables.Column(verbose_name="#")
    row_class = django_tables.Column(visible=False)
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
        sequence = ('row_number', 'row_class',  'id', 'series', 'login', 'pin', 'nominal', 'type', 'tarif', 'nas',  'activated', 'ippool', 'created', 'start_date', 'end_date', 'template')
        attrs = {'class': 'table table-bordered table-condensed'}
        exclude = ('ipinuse', 'disabled', 'ip', 'activated_by', 'ext_id', 'salecard')
        
class SaleCardTable(django_tables.Table):
    id = django_tables.LinkColumn('salecard_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    class Meta:
        model = SaleCard
        exclude = ("tarif", 'nas')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class DealerTable(django_tables.Table):
    id = django_tables.LinkColumn('dealer_edit', get_params={'id':A('pk')})
    organization = django_tables.LinkColumn('dealer_edit', get_params={'id':A('pk')})
    
    class Meta:
        model = Dealer
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TariffTable(django_tables.Table):
    id = django_tables.LinkColumn('tariff_edit', get_params={'id':A('pk')})
    access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = Tariff
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'name', 'settlement_period', 'cost', 'access_type', 'reset_tarif_cost', )
        
class PeriodicalServiceTable(django_tables.Table):
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
        
class GroupTable(django_tables.Table):
    id = django_tables.LinkColumn('group_edit', get_params={'id':A('pk')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    class Meta:
        model = Group
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        
class TrafficTransmitNodesTable(django_tables.Table):
    id = django_tables.LinkColumn('tariff_traffictransmitnode_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    group = django_tables.LinkColumn('group_edit', get_params={'id':A('group.id')})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    
    
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = TrafficTransmitNodes
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'timeperiod', 'group', 'cost','d' )

class PrepaidTrafficTable(django_tables.Table):
    id = django_tables.LinkColumn('tariff_prepaidtraffic_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    group = django_tables.LinkColumn('group_edit', get_params={'id':A('group.id')})
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = PrepaidTraffic
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'group', 'size')

class TimeSpeedTable(django_tables.Table):
    id = django_tables.LinkColumn('tariff_prepaidtraffic_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #group = django_tables.LinkColumn('group_edit', get_params={'id':A('group.id')})
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = TimeSpeed
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'time', 'max_tx', 'max_rx', 'burst_tx', 'burst_rx', 'burst_treshold_tx', 'burst_treshold_rx', 'burst_time_tx', 'burst_time_rx', 'min_tx', 'min_rx', 'priority')

class OneTimeServiceTable(django_tables.Table):
    id = django_tables.LinkColumn('onetimeservice_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    name = django_tables.LinkColumn('onetimeservice_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = OneTimeService
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'name', 'cost', 'd')

class RadiusTrafficNodeTable(django_tables.Table):
    id = django_tables.LinkColumn('tariff_radiustrafficnode_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = RadiusTrafficNode
        fields = ("id", 'value', 'timeperiod', 'cost', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}

class TrafficLimitTable(django_tables.Table):
    id = django_tables.LinkColumn('tariff_trafficlimit_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    speedlimit = django_tables.TemplateColumn("<a href='{% url tariff_speedlimit_edit %}?trafficlimit_id={{record.id}}' class='open-speedlimit-dialog'>{% if record.speedlimit %}{{record.speedlimit}}<a href='{{record.speedlimit.get_remove_url}}' class='show-speedlimit-confirm'><i class='icon-remove'></i></a>{% else %}Указать{% endif %}</a>", verbose_name='Изменить скорость', orderable=False)
    #speed = TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = TrafficLimit
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
        fields = ("id", 'name', 'settlement_period', 'mode', 'group', 'size', 'action', 'speedlimit', 'd' )
        
class TimeAccessNodeTable(django_tables.Table):
    id = django_tables.LinkColumn('tariff_timeaccessnode_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = TimeAccessNode
        fields = ("id", 'time_period', 'cost', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'}
       
class AddonServiceTarifTable(django_tables.Table):
    id = django_tables.LinkColumn('tariff_addonservicetariff_edit', get_params={'id':A('pk')}, attrs= {'rel': "alert3", 'class': "open-custom-dialog"})
    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = AddonServiceTarif
        fields = ("id", 'service', 'activation_count_period', 'activation_count', 'type', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 

class PeriodicalServiceLogTable(django_tables.Table):

    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    
    class Meta:
        model = PeriodicalServiceLog
        fields = ("id", 'accounttarif', 'service', 'datetime', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 
        
class SheduleLogTable(django_tables.Table):

    d = django_tables.TemplateColumn("<a href='{{record.get_remove_url}}' class='show-confirm'><i class='icon-remove'></i></a>", verbose_name=' ', orderable=False)
    #access_type = FormatBlankColumn(verbose_name=u'Тип доступа', accessor=A('access_parameters.access_type'))
    accounttarif = FormatBlankColumn(verbose_name=u'Тариф аккаунта')
    ballance_checkout = FormatDateTimeColumn(verbose_name=u'Доснятие до стоимости')
    prepaid_traffic_reset = FormatDateTimeColumn(verbose_name=u'Обнуление предоплаченного трафика')
    prepaid_traffic_accrued = FormatDateTimeColumn(verbose_name=u'Начисление предоплаченного трафика')
    prepaid_time_reset = FormatDateTimeColumn(verbose_name=u'Обнуление предоплаченного времени')
    prepaid_time_accrued = FormatDateTimeColumn(verbose_name=u'Начисление предоплаченного врумени')
    balance_blocked = FormatDateTimeColumn(verbose_name=u'Блокировка баланса')
    
    class Meta:
        model = SheduleLog
        #fields = ("id", 'accounttarif', 'service', 'datetime', 'd')
        attrs = {'class': 'table table-striped table-bordered table-condensed'} 


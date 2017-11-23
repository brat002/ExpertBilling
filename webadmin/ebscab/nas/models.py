# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _

from ebscab.fields import EncryptedTextField, IPNetworkField


NAS_LIST = (
    (u'mikrotik2.8', 'MikroTik 2.8'),
    (u'mikrotik2.9', 'MikroTik 2.9'),
    (u'mikrotik3', 'Mikrotik 3'),
    (u'mikrotik4', 'Mikrotik 4'),
    (u'mikrotik5', 'Mikrotik 5'),
    (u'mikrotik6', 'Mikrotik 6'),
    (u'cisco', u'cisco'),
    (u'common_radius', 'Common RADIUS interface'),
    (u'common_ssh', u'common_ssh'),
    (u'localhost', 'Local execution'),
    (u'switch', 'Switch'),
    (u'accel-ipoe', u'Accel IPOE'),
    (u'accel-ipoe-l3', u'Accel IPOE L3'),
    (u'lISG', u'lISG')
)

DIRECTIONS_LIST = (
    (u'INPUT', u'INPUT'),
    (u'OUTPUT', u'OUTPUT')
)

SNMP_VERSIONS = (
    (u'v1', u'v1'),
    (u'v2c', u'v2c')
)

SERVICE_LIST = (
    ('Virtual', 'VPN'),
    ('IPN', 'IPN')
)


PROTOCOLS = (
    (0, _(u'Любой')),
    (37, 'ddp'),
    (98, 'encap'),
    (3, 'ggp'),
    (47, 'gre'),
    (20, 'hmp'),
    (1, 'icmp'),
    (38, 'idpr-cmtp'),
    (2, 'igmp'),
    (4, 'ipencap'),
    (94, 'ipip',),
    (89, 'ospf'),
    (27, 'rdp'),
    (6, 'tcp'),
    (17, 'udp')
)

actions = {
    'mikrotik2.8': {
        'user_add_action': '',
        'subacc_add_action': '/ip firewall address-list add list=internet_users address=$subacc_ipn_ip_address disabled=yes comment=$acc_account_id-$subacc_id',
        'user_delete_action': '',
        'subacc_delete_action': '/ip firewall address-list remove [find comment==$acc_account_id-$subacc_id];/queue simple remove [find comment=$acc_account_id-$subacc_id]',
        'user_enable_action': '',
        'subacc_enable_action': '/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] address=$subacc_ipn_ip_address disabled=no',
        'user_disable_action': '',
        'subacc_disable_action': '/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] disabled=yes',
        'vpn_speed_action': '/queue simple set [find interface=<$access_type-$subacc_username>] max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx',
        'ipn_speed_action': '',
        'subacc_ipn_speed_action': '/queue simple remove [find name=$acc_account_id-$subacc_id]; /queue simple add name=$acc_account_id-$subacc_id max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx target-addresses=$subacc_ipn_ip_address/32',
        'reset_action': '/interface $access_type-server remove [find user=$subacc_username]',
        'speed_vendor_1': 14988,
        'speed_attr_id1': 8,
        'speed_value1': '$max_limit_rx/$max_limit_tx $burst_limit_rx/$burst_limit_tx $burst_treshold_rx/$burst_treshold_tx $burst_time_rx/$burst_time_tx $priority $min_limit_rx/$min_limit_tx',
        'speed_vendor_2': '',
        'speed_attr_id2': '',
        'speed_value2': '',
        'type': 'mikrotik2.8'
    },
    'mikrotik2.9': {
        'user_add_action': '',
        'subacc_add_action': '/ip firewall address-list add list=internet_users address=$subacc_ipn_ip_address disabled=yes comment=$acc_account_id-$subacc_id',
        'user_delete_action': '',
        'subacc_delete_action': '/ip firewall address-list remove [find comment==$acc_account_id-$subacc_id];/queue simple remove [find comment=$acc_account_id-$subacc_id]',
        'user_enable_action': '',
        'subacc_enable_action': '/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] address=$subacc_ipn_ip_address disabled=no',
        'user_disable_action': '',
        'subacc_disable_action': '/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] disabled=yes',
        'vpn_speed_action': '/queue simple set [find interface=<$access_type-$subacc_username>] max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx',
        'ipn_speed_action': '',
        'subacc_ipn_speed_action': '/queue simple remove [find name=$acc_account_id-$subacc_id]; /queue simple add name=$acc_account_id-$subacc_id max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx target-addresses=$subacc_ipn_ip_address/32',
        'reset_action': '/interface $access_type-server remove [find user=$subacc_username]',
        'speed_vendor_1': 14988,
        'speed_attr_id1': 8,
        'speed_value1': '$max_limit_rx/$max_limit_tx $burst_limit_rx/$burst_limit_tx $burst_treshold_rx/$burst_treshold_tx $burst_time_rx/$burst_time_tx $priority $min_limit_rx/$min_limit_tx',
        'speed_vendor_2': '',
        'speed_attr_id2': '',
        'speed_value2': '',
        'type': 'mikrotik2.9'
    },
    'mikrotik3': {
        'user_add_action': '',
        'subacc_add_action': '/ip firewall address-list add list=internet_users address=$subacc_ipn_ip_address disabled=yes comment=$acc_account_id-$subacc_id',
        'user_delete_action': '',
        'subacc_delete_action': '/ip firewall address-list remove [find comment==$acc_account_id-$subacc_id];/queue simple remove [find comment=$acc_account_id-$subacc_id]',
        'user_enable_action': '',
        'subacc_enable_action': '/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] address=$subacc_ipn_ip_address disabled=no',
        'user_disable_action': '',
        'subacc_disable_action': '/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] disabled=yes',
        'vpn_speed_action': '/queue simple set [find interface=<$access_type-$subacc_username>] max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx',
        'ipn_speed_action': '',
        'subacc_ipn_speed_action': '/queue simple remove [find name=$acc_account_id-$subacc_id]; /queue simple add name=$acc_account_id-$subacc_id max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx target-addresses=$subacc_ipn_ip_address/32',
        'reset_action': '/interface $access_type-server remove [find user=$subacc_username]',
        'speed_vendor_1': 14988,
        'speed_attr_id1': 8,
        'speed_value1': '$max_limit_rx/$max_limit_tx $burst_limit_rx/$burst_limit_tx $burst_treshold_rx/$burst_treshold_tx $burst_time_rx/$burst_time_tx $priority $min_limit_rx/$min_limit_tx',
        'speed_vendor_2': '',
        'speed_attr_id2': '',
        'speed_value2': '',
        'type': 'mikrotik3',
    },
    'mikrotik4': {
        'user_add_action': '',
        'subacc_add_action': '/ip firewall address-list add list=internet_users address=$subacc_ipn_ip_address disabled=yes comment=$acc_account_id-$subacc_id',
        'user_delete_action': '',
        'subacc_delete_action': '/ip firewall address-list remove [find comment==$acc_account_id-$subacc_id];/queue simple remove [find comment=$acc_account_id-$subacc_id]',
        'user_enable_action': '',
        'subacc_enable_action': '/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] address=$subacc_ipn_ip_address disabled=no',
        'user_disable_action': '',
        'subacc_disable_action': '/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] disabled=yes',
        'vpn_speed_action': '/queue simple set [find interface=<$access_type-$subacc_username>] max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx',
        'ipn_speed_action': '',
        'subacc_ipn_speed_action': '/queue simple remove [find name=$acc_account_id-$subacc_id]; /queue simple add name=$acc_account_id-$subacc_id max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx target-addresses=$subacc_ipn_ip_address/32',
        'reset_action': '/interface $access_type-server remove [find user=$subacc_username]',
        'speed_vendor_1': 14988,
        'speed_attr_id1': 8,
        'speed_value1': '$max_limit_rx/$max_limit_tx $burst_limit_rx/$burst_limit_tx $burst_treshold_rx/$burst_treshold_tx $burst_time_rx/$burst_time_tx $priority $min_limit_rx/$min_limit_tx',
        'speed_vendor_2': '',
        'speed_attr_id2': '',
        'speed_value2': '',
        'type': 'mikrotik4'
    },
    'mikrotik5': {
        'user_add_action': '',
        'subacc_add_action': '/ip firewall address-list add list=internet_users address=$subacc_ipn_ip_address disabled=yes comment=$acc_account_id-$subacc_id',
        'user_delete_action': '',
        'subacc_delete_action': '/ip firewall address-list remove [find comment==$acc_account_id-$subacc_id];/queue simple remove [find comment=$acc_account_id-$subacc_id]',
        'user_enable_action': '',
        'subacc_enable_action': '/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] address=$subacc_ipn_ip_address disabled=no',
        'user_disable_action': '',
        'subacc_disable_action': '/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] disabled=yes',
        'vpn_speed_action': '/queue simple set [find interface=<$access_type-$subacc_username>] max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx',
        'ipn_speed_action': '',
        'subacc_ipn_speed_action': '/queue simple remove [find name=$acc_account_id-$subacc_id]; /queue simple add name=$acc_account_id-$subacc_id max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority limit-at=$min_limit_tx/$min_limit_rx target-addresses=$subacc_ipn_ip_address/32',
        'reset_action': '/interface $access_type-server remove [find user=$subacc_username]',
        'speed_vendor_1': 14988,
        'speed_attr_id1': 8,
        'speed_value1': '$max_limit_rx/$max_limit_tx $burst_limit_rx/$burst_limit_tx $burst_treshold_rx/$burst_treshold_tx $burst_time_rx/$burst_time_tx $priority $min_limit_rx/$min_limit_tx',
        'speed_vendor_2': '',
        'speed_attr_id2': '',
        'speed_value2': '',
        'type': 'mikrotik5'
    },
    'mikrotik6': {
        'user_add_action': '',
        'subacc_add_action': '/ip firewall address-list add list=internet_users address=$subacc_ipn_ip_address disabled=yes comment=$acc_account_id-$subacc_id',
        'user_delete_action': '',
        'subacc_delete_action': '/ip firewall address-list remove [find comment=$acc_account_id-$subacc_id];/queue simple remove [find comment=$acc_account_id-$subacc_id]',
        'user_enable_action': '',
        'subacc_enable_action': '/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] address=$subacc_ipn_ip_address disabled=no',
        'user_disable_action': '',
        'subacc_disable_action': '/ip firewall address-list set [find comment=$acc_account_id-$subacc_id] disabled=yes',
        'vpn_speed_action': '/queue simple set target=<$access_type-$subacc_username> max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority/$priority limit-at=$min_limit_tx/$min_limit_rx [find target=<$access_type-$subacc_username>]',
        'ipn_speed_action': '',
        'subacc_ipn_speed_action': '/queue simple remove [find name=$subacc_username]; /queue simple add name=$subacc_username max-limit=$max_limit_tx/$max_limit_rx burst-limit=$burst_limit_tx/$burst_limit_rx burst-threshold=$burst_treshold_tx/$burst_treshold_rx burst-time=$burst_time_tx/$burst_time_rx priority=$priority/$priority limit-at=$min_limit_tx/$min_limit_rx target=$subacc_ipn_ip_address/32',
        'reset_action': '/interface $access_type-server remove [find user=$subacc_username]',
        'speed_vendor_1': 14988,
        'speed_attr_id1': 8,
        'speed_value1': '$max_limit_rx/$max_limit_tx $burst_limit_rx/$burst_limit_tx $burst_treshold_rx/$burst_treshold_tx $burst_time_rx/$burst_time_tx $priority $min_limit_rx/$min_limit_tx',
        'speed_vendor_2': '',
        'speed_attr_id2': '',
        'speed_value2': '',
        'type': 'mikrotik5'
    },
    'common_ssh': {
        'user_add_action': '',
        'subacc_add_action': '',
        'user_delete_action': '',
        'subacc_delete_action': '',
        'user_enable_action': '',
        'subacc_enable_action': '',
        'subacc_disable_action': '',
        'user_disable_action': '',
        'vpn_speed_action': '',
        'ipn_speed_action': '',
        'reset_action': '',
        'speed_vendor_1': '',
        'speed_attr_id1': '',
        'speed_value1': '',
        'speed_vendor_2': '',
        'speed_attr_id2': '',
        'speed_value2': '',
        'type': 'mikrotik5',
        'type': 'common_ssh'
    },
    'common_radius': {
        'user_add_action': '',
        'subacc_add_action': '',
        'user_delete_action': '',
        'subacc_delete_action': '',
        'user_enable_action': '',
        'subacc_enable_action': '',
        'subacc_disable_action': '',
        'user_disable_action': '',
        'vpn_speed_action': '',
        'ipn_speed_action': '',
        'reset_action': '',
        'speed_vendor_1': '',
        'speed_attr_id1': '',
        'speed_value1': '',
        'speed_vendor_2': '',
        'speed_attr_id2': '',
        'speed_value2': '',
        'type': 'common_radius',
    },
    'localhost': {
        'user_add_action': '',
        'subacc_add_action': '',
        'user_delete_action': '',
        'subacc_delete_action': '',
        'user_enable_action': '',
        'subacc_enable_action': '',
        'subacc_disable_action': '',
        'user_disable_action': '',
        'vpn_speed_action': '',
        'ipn_speed_action': '',
        'reset_action': '',
        'speed_vendor_1': '',
        'speed_attr_id1': '',
        'speed_value1': '',
        'speed_vendor_2': '',
        'speed_attr_id2': '',
        'speed_value2': '',
        'type': 'localhost'
    },
    'cisco': {
        'user_add_action': '',
        'subacc_add_action': '',
        'user_delete_action': '',
        'subacc_delete_action': '',
        'user_enable_action': '',
        'subacc_enable_action': '',
        'subacc_disable_action': '',
        'user_disable_action': '',
        'vpn_speed_action': '',
        'ipn_speed_action': '',
        'reset_action': '',
        'speed_vendor_1': 9,
        'speed_attr_id1': 1,
        'speed_value1': 'lcp:interface-config#1=rate-limit input $max_limit_tx 8000 8000 conform-action transmit exceed-action drop',
        'speed_vendor_2': 9,
        'speed_attr_id2': 1,
        'speed_value2': 'lcp:interface-config#1=rate-limit output $max_limit_tx 8000 8000 conform-action transmit exceed-action drop',
        'type': 'cisco'
    },

    'switch': {
        'user_add_action': '',
        'subacc_add_action': '',
        'user_delete_action': '',
        'subacc_delete_action': '',
        'user_enable_action': '',
        'subacc_enable_action': '',
        'subacc_disable_action': '',
        'user_disable_action': '',
        'vpn_speed_action': '',
        'ipn_speed_action': '',
        'reset_action': '',
        'speed_vendor_1': '',
        'speed_attr_id1': '',
        'speed_value1': '',
        'speed_vendor_2': '',
        'speed_attr_id2': '',
        'speed_value2': '',
        'type': 'switch'
    },
    '---': {
        'user_add_action': '',
        'subacc_add_action': '',
        'user_delete_action': '',
        'subacc_delete_action': '',
        'user_enable_action': '',
        'subacc_enable_action': '',
        'subacc_disable_action': '',
        'user_disable_action': '',
        'vpn_speed_action': '',
        'ipn_speed_action': '',
        'reset_action': '',
        'speed_vendor_1': '',
        'speed_attr_id1': '',
        'speed_value1': '',
        'speed_vendor_2': '',
        'speed_attr_id2': '',
        'speed_value2': ''
    }
}


class Nas(models.Model):
    """
    /ip firewall address-list add address=$ipaddress list=allow_ip comment=$user_id
    /ip firewall address-list remove $user_id
    """
    type = models.CharField(
        choices=NAS_LIST, max_length=32, default='mikrotik3')
    identify = models.CharField(verbose_name=_(u'RADIUS имя'), max_length=255)
    name = models.CharField(
        verbose_name=_(u'Имя'), max_length=255, unique=True)
    ipaddress = models.GenericIPAddressField(
        verbose_name=_(u'IP адрес'), max_length=255)
    secret = EncryptedTextField(
        verbose_name=_(u'Секретная фраза'),
        help_text=_(u"Смотрите вывод команды /radius print"),
        max_length=255)
    login = models.CharField(
        verbose_name=_(u'Имя пользователя'),
        max_length=255,
        blank=True,
        default='admin'
    )
    password = EncryptedTextField(
        verbose_name=_(u'Пароль'),
        max_length=255,
        blank=True,
        default=''
    )
    snmp_version = models.CharField(
        verbose_name=_(u'Версия SNMP'),
        choices=SNMP_VERSIONS,
        max_length=10,
        blank=True,
        null=True
    )
    user_add_action = models.TextField(
        verbose_name=_(u'Действие при создании пользователя'),
        blank=True,
        null=True,
        default=""
    )
    user_enable_action = models.TextField(
        verbose_name=_(u'Действие при разрешении работы пользователя'),
        blank=True,
        null=True,
        default=""
    )
    user_disable_action = models.TextField(
        verbose_name=_(u'Действие при запрещении работы пользователя'),
        blank=True,
        null=True,
        default=""
    )
    user_delete_action = models.TextField(
        verbose_name=_(u'Действие при удалении пользователя'),
        blank=True,
        null=True,
        default=""
    )
    vpn_speed_action = models.TextField(
        max_length=255, blank=True, null=True, default="")
    ipn_speed_action = models.TextField(
        max_length=255, blank=True, null=True, default="")
    reset_action = models.TextField(
        max_length=255, blank=True, null=True, default="")
    subacc_disable_action = models.TextField(blank=True, null=True, default="")
    subacc_enable_action = models.TextField(blank=True, null=True, default="")
    subacc_add_action = models.TextField(blank=True, null=True, default="")
    subacc_delete_action = models.TextField(blank=True, null=True, default="")
    subacc_ipn_speed_add_action = models.TextField(verbose_name = _(u"Add IPN speed command"),
        blank=True, null=True, default="")
    subacc_ipn_speed_action = models.TextField(verbose_name = _(u"Change IPN speed command"),
        blank=True, null=True, default="")
    subacc_ipn_speed_remove_action = models.TextField(verbose_name = _(u"Remove IPN speed command"),
        blank=True, null=True, default="")
    subacc_vpn_speed_change_action = models.TextField(verbose_name = _(u"Change VPN speed command"),
        blank=True, null=True, default="")
        
    speed_attr_id1 = models.CharField(max_length=128, blank=True, null=True, default="")
    speed_attr_id2 = models.CharField(max_length=128, blank=True, null=True, default="")
    speed_value1 = models.TextField(blank=True, default="")
    speed_value2 = models.TextField(blank=True, default="")
    acct_interim_interval = models.IntegerField(
        default=60, blank=True, null=False)

    class Admin:
        ordering = ['-name']
        list_display = ('name', 'ipaddress')

    class Meta:
        verbose_name = _(u"Сервер доступа")
        verbose_name_plural = _(u"Сервера доступа")
        permissions = (
           ("nas_view", _(u"Просмотр")),
        )

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('nas_delete'), self.id)

    def __unicode__(self):
        return u"%s" % self.name


class TrafficClass(models.Model):
    """
    Классы трафика не должны пересекаться, ноды внутри одного класса не должны указывать сразу входящие
    и исходящие направления. Правило: Один класс на одно направление (вх/исх/межабонентский)
    """
    name = models.CharField(
        verbose_name=_(u'Навзание класса'), max_length=255, unique=True)
    weight = models.IntegerField(
        verbose_name=_(u'Вес класа в цепочке классов'), blank=True, null=True)
    store = models.BooleanField(
        verbose_name=_(u"Хранить сырую статистику по классу"),
        help_text=_(u"Хранить NetFlow статистику в текстовом виде"),
        blank=True,
        default=True
    )
    passthrough = models.BooleanField(
        verbose_name=_(u"Пометить и продолжить"), blank=True, default=False)

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        pass

    def save(self):
        if not self.id and not self.weight:
            self.weight = (TrafficClass.objects
                           .all()
                           .aggregate(Max('weight'))
                           .get("weight__max", 1) or 1) + 1
        super(TrafficClass, self).save()

    class Meta:
        verbose_name = _(u"Класс трафика")
        verbose_name_plural = _(u"Классы трафика")
        ordering = ['weight']
        permissions = (
            ("trafficclass_view", _(u"Просмотр")),
        )

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('trafficclass_delete'), self.id)


class TrafficNode(models.Model):
    """
    Направления трафика. Внутри одного класса не должно быть пересекающихся направлений
    """
    traffic_class = models.ForeignKey(TrafficClass, on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_(u'Название'), max_length=255)
    protocol = models.IntegerField(choices=PROTOCOLS, default=0)

    src_ip = IPNetworkField(
        verbose_name=_(u'Наша сеть'), blank=True, default='0.0.0.0/0')
    src_port = models.IntegerField(
        verbose_name=u'Src port', blank=True, default=0)

    dst_ip = IPNetworkField(
        verbose_name=_(u'Удалённая сеть'), blank=True, default='0.0.0.0/0')
    dst_port = models.IntegerField(
        verbose_name=_(u'Dst port'), blank=True, default=0)

    next_hop = models.GenericIPAddressField(
        verbose_name=_(u'next Hop'),
        blank=True,
        null=True,
        default='0.0.0.0'
    )
    in_index = models.IntegerField(
        verbose_name=u'SNMP IN', blank=True, default=0)
    out_index = models.IntegerField(
        verbose_name=u'SNMP OUT', blank=True, default=0)

    src_as = models.IntegerField(verbose_name=u'src_as', blank=True, default=0)
    dst_as = models.IntegerField(verbose_name=u'dst_as', blank=True, default=0)

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        pass

    class Meta:
        verbose_name = _(u"Направление трафика")
        verbose_name_plural = _(u"Направления трафика")
        permissions = (
           ("trafficnode_view", _(u"Просмотр")),
        )

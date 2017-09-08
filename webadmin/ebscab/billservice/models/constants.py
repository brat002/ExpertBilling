# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _


ACTIVE = 1
NOT_ACTIVE_NOT_WRITING_OFF = 2
NOT_ACTIVE_WRITING_OFF = 3

ACCOUNT_STATUS = (
    (ACTIVE, _(u'Активен')),
    (NOT_ACTIVE_NOT_WRITING_OFF, _(u'Неактивен, не списывать периодические '
                                   u'услуги')),
    (NOT_ACTIVE_WRITING_OFF, _(u'Неактивен, списывать периодические услуги'))
)


PROTOCOLS = {
    '0': '-all-',
    '37': 'ddp',
    '98': 'encap',
    '3': 'ggp',
    '47': 'gre',
    '20': 'hmp',
    '1': 'icmp',
    '38': 'idpr-cmtp',
    '2': 'igmp',
    '4': 'ipencap',
    '94': 'ipip',
    '89': 'ospf',
    '27': 'rdp',
    '6': 'tcp',
    '17': 'udp'
}

PERIOD_CHOISES = (
    ('DONT_REPEAT', _(u'Не повторять')),
    ('DAY', _(u'День')),
    ('WEEK', _(u'Неделя')),
    ('MONTH', _(u'Месяц')),
    ('YEAR', _(u'Год')),
)

CASH_METHODS = (
    ('AT_START', _(u'В начале периода')),
    ('AT_END', _(u'В конце периода')),
    ('GRADUAL', _(u'В течении периода')),
)

ACCESS_TYPE_METHODS = (
    ("PPTP", "PPTP"),
    ("PPPOE", "PPPOE"),
    ("IPN", "IPN"),
    ("HotSpot", "HotSpot"),
    ('HotSpotIp+Mac', 'HotSpotIp+Mac'),
    ('HotSpotIp+Password', 'HotSpotIp+Password'),
    ('HotSpotMac', 'HotSpotMac'),
    ('HotSpotMac+Password', 'HotSpotMac+Password'),
    ('lISG', 'lISG'),
    ("DHCP", "DHCP")
)
# choiCe
ACTIVITY_CHOISES = (
    ("Enabled", _(u"Активен")),
    ("Disabled", _(u"Неактивен")),
)
# choiCe
CHOISE_METHODS = (
    ("MAX", _(u"Наибольший")),
    ("SUMM", _(u"Сумма всех")),
)

CHECK_PERIODS = (
    ("period_checkSP_START", _(u"С начала расчётного периода")),
    ("AG_START", _(u"С начала интервала агрегации")),
)

STATISTIC_MODE = (
    ('NETFLOW', _(u'NetFlow')),
    ('ACCOUNTING', _(u'RADIUS Accounting')),
)

PRIORITIES = (
    ('1', _(u'1')),
    ('2', _(u'2')),
    ('3', _(u'3')),
    ('4', _(u'4')),
    ('5', _(u'5')),
    ('6', _(u'6')),
    ('7', _(u'7')),
    ('8', _(u'8')),
)

DIRECTIONS_LIST = (
    ('INPUT', _(u'Входящий на абонента')),
    ('OUTPUT', _(u'Исходящий от абонента')),
    ('TRANSIT', _(u'Межабонентский')),
)

AUTH_TYPES = (
    ('BY_LOGIN', 'BY_LOGIN'),
    ('BY_MAC', 'BY_MAC'),
)

STATUS_CLASS = {
    1: '',
    2: 'inactive-light',
    3: 'inactive',
    4: 'info',
    False: 'inactive',
}

PORT_OPER_STATUS = (
    (1, 'up'),
    (2, 'down'),
    (3, 'testing'),
    (4, 'unknown'),
    (5, 'dormant'),
    (6, 'notPresent'),
    (7, 'lowerLayerDown')
)

ADMIN_OPER_STATUS = (
    (1, 'up'),
    (2, 'down'),
    (3, 'testing'),
)

PERMISSION_ROLES = (
    ('ADMIN', _(u'Администратор')),
    ('CASHIER', _(u'Кассир')),
)

# -*- coding: utf-8 -*-

from django.db import connection

from billservice.models.access import AccessParameters
from billservice.models.limit import SpeedLimit
from billservice.models.organization import Organization
from billservice.models.permission import Permission, PermissionGroup
from billservice.models.log import SheduleLog
from billservice.models.hardware import (
    Hardware,
    HardwareType,
    Manufacturer,
    Model
)
from billservice.models.bank import BankData
from billservice.models.operator import Operator
from billservice.models.pereodical_service import (
    PeriodicalService,
    PeriodicalServiceHistory,
    PeriodicalServiceLog
)
from billservice.models.switch import Switch, SwitchPort, SwitchPortStat
from billservice.models.transaction import Transaction, TransactionType
from billservice.models.radius import (
    RadiusAttrs,
    RadiusTraffic,
    RadiusTrafficNode
)
from billservice.models.one_time_service import (
    OneTimeService,
    OneTimeServiceHistory
)
from billservice.models.registration import RegistrationRequest
from billservice.models.card import Card, SaleCard
from billservice.models.account import (
    Account,
    AccountAddonService,
    AccountGroup,
    AccountHardware,
    AccountIPNSpeed,
    AccountNotification,
    AccountPrepaysRadiusTrafic,
    AccountPrepaysTime,
    AccountPrepaysTrafic,
    AccountSpeedLimit,
    AccountTarif,
    BalanceHistory,
    City,
    House,
    Street,
    SubAccount
)
from billservice.models.template import (
    ContractTemplate,
    Template,
    TemplateType
)
from billservice.models.time import (
    TimeAccessNode, TimeAccessService, TimeSpeed, TimeTransaction)
from billservice.models.addon_service import (
    AddonService,
    AddonServiceTarif,
    AddonServiceTransaction
)
from billservice.models.tariff import NotificationsSettings, TPChangeRule, Tariff
from billservice.models.ip import IPInUse, IPPool
from billservice.models.report import TotalTransactionReport
from billservice.models.traffic import (
    Group,
    PrepaidTraffic,
    TrafficLimit,
    TrafficTransaction,
    TrafficTransmitNodes,
    TrafficTransmitService
)
from billservice.models.document import Document, DocumentType
from billservice.models.user import SystemUser
from billservice.models.stat import GlobalStat, GroupStat
from billservice.models.period import (
    SettlementPeriod,
    SuspendedPeriod,
    TimePeriod,
    TimePeriodNode
)
from billservice.models.agreement import (
    AccountSuppAgreement,
    SuppAgreement
)
from billservice.models.dealer import Dealer, DealerPay
from billservice.models.news import AccountViewedNews, News


connection.features.can_return_id_from_insert = False

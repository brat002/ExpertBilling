# -*- coding: utf-8 -*-

from ebsadmin.tables.account import (
    AccountGroupTable,
    AccountsReportTable,
    BallanceHistoryTable,
    SubAccountsTable
)
from ebsadmin.tables.agreements import (
    AccountSuppAgreementTable,
    SuppAgreementTable
)
from ebsadmin.tables.base import EbsadminTable, EbsadminTableReport
from ebsadmin.tables.cards import CardTable, SaleCardTable, SaleCardsTable
from ebsadmin.tables.cashier import (
    AccountsCashierReportTable,
    CashierReportTable
)
from ebsadmin.tables.comments import CommentTable
from ebsadmin.tables.dealer import DealerTable
from ebsadmin.tables.hardware import (
    AccountHardwareTable,
    HardwareTable,
    HardwareTypeTable,
    ManufacturerTable,
    ModelTable
)
from ebsadmin.tables.ip import IPInUseTable, IPPoolTable
from ebsadmin.tables.log import (
    ActionLogTable,
    AuthLogTable,
    LogTable,
    PeriodicalServiceLogTable,
    SheduleLogTable
)
from ebsadmin.tables.misc import (
    DynamicSchemaFieldTable,
    RegistrationRequestTable
)
from ebsadmin.tables.news import NewsTable
from ebsadmin.tables.payment import PaymentTable
from ebsadmin.tables.periods import SettlementPeriodTable, SuspendedPeriodTable
from ebsadmin.tables.permission import PermissionGroupTable
from ebsadmin.tables.radius_ import (
    ActiveSessionTable,
    NasTable,
    RadiusAttrTable
)
from ebsadmin.tables.services import (
    AccountAddonServiceTable,
    AddonServiceTable,
    OneTimeServiceTable,
    PeriodicalServiceTable
)
from ebsadmin.tables.sms import MessageTable
from ebsadmin.tables.stat import GlobalStatTable, GroupStatTable
from ebsadmin.tables.switch import SwitchPortsTable, SwitchTable
from ebsadmin.tables.tariff import (
    AccountTarifTable,
    AddonServiceTarifTable,
    NotificationsSettingsTable,
    TPChangeRuleTable,
    TariffTable,
    TimeAccessNodeTable,
    TimeSpeedTable
)
from ebsadmin.tables.templates import ContractTemplateTable, TemplateTable
from ebsadmin.tables.tickets import TicketTable
from ebsadmin.tables.traffic import (
    AccountPrepaysRadiusTraficTable,
    AccountPrepaysTimeTable,
    AccountPrepaysTraficTable,
    GroupTable,
    PrepaidTrafficTable,
    RadiusTrafficNodeTable,
    TrafficClassTable,
    TrafficLimitTable,
    TrafficNodeTable,
    TrafficTransmitNodesTable,
    UploadTrafficNodeTable
)
from ebsadmin.tables.transaction import (
    AddonServiceTransactionReportTable,
    PeriodicalServiceTransactionReportTable,
    TotalTransactionReportTable,
    TrafficTransactionReportTable,
    TransactionReportTable,
    TransactionTypeTable
)
from ebsadmin.tables.user import SystemUserTable

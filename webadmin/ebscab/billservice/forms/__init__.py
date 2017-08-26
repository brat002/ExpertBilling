# -*- encoding: utf-8 -*-

from billservice.forms.access import (
    AccessParametersForm,
    AccessParametersTariffForm
)
from billservice.forms.account import (
    AccountAddonForm,
    AccountAddonServiceModelForm,
    AccountExtraForm,
    AccountForm,
    AccountGroupForm,
    AccountHardwareForm,
    AccountManagementForm,
    AccountPrepaysRadiusTraficForm,
    AccountPrepaysRadiusTraficSearchForm,
    AccountPrepaysTimeForm,
    AccountPrepaysTimeSearchForm,
    AccountPrepaysTraficForm,
    AccountPrepaysTraficSearchForm,
    AccountTariffBathForm,
    AccountTariffForm,
    BallanceHistoryForm,
    BatchAccountTariffForm,
    CashierAccountForm,
    CityForm,
    HouseForm,
    StreetForm,
    SubAccountForm,
    SubAccountPartialForm
)
from billservice.forms.agreement import (
    AccountSuppAgreementForm,
    SuppAgreementForm
)
from billservice.forms.auth import (
    EmailForm,
    LoginForm,
    PasswordForm,
    RegisterForm,
    SimplePasswordForm
)
from billservice.forms.bank import BankDataForm
from billservice.forms.card import (
    ActivationCardForm,
    CardBatchChangeForm,
    CardForm,
    CardGenerationForm,
    SaleCardForm
)
from billservice.forms.dealer import (
    DealerForm,
    DealerPayForm,
    DealerSelectForm
)
from billservice.forms.document import DocumentModelForm, DocumentRenderForm
from billservice.forms.hardware import (
    HardwareForm,
    HardwareTypeForm,
    ManufacturerForm,
    ModelHardwareForm
)
from billservice.forms.ip import IPPoolForm, IpInUseLogForm
from billservice.forms.misc import (
    ActionLogFilterForm,
    DynamicSchemaFieldForm,
    SendSmsForm,
    SpeedLimitForm,
    StatististicForm
)
from billservice.forms.news import NewsForm
from billservice.forms.operator import OperatorForm
from billservice.forms.organization import OrganizationForm
from billservice.forms.payment import PaymentForm, PromiseForm
from billservice.forms.period import (
    SettlementPeriodForm,
    SuspendedPeriodBatchForm,
    SuspendedPeriodModelForm,
    TimePeriodForm,
    TimePeriodNodeForm
)
from billservice.forms.permission import PermissionGroupForm
from billservice.forms.radius import (
    RadiusAttrsForm,
    RadiusTrafficForm,
    RadiusTrafficNodeForm
)
from billservice.forms.search import (
    CardSearchForm,
    GlobalStatSearchForm,
    GroupStatSearchForm,
    PaymentSearchForm,
    PeriodicalServiceLogSearchForm,
    SearchAccountForm,
    SearchAuthLogForm,
    SearchSmsForm,
    SheduleLogSearchForm
)
from billservice.forms.service import (
    AddonServiceForm,
    AddonServiceTarifForm,
    OneTimeServiceForm,
    PeriodicalServiceForm
)
from billservice.forms.switch import SwitchForm
from billservice.forms.tariff import (
    ChangeTariffForm,
    NotificationsSettingsForm,
    TPChangeMultipleRuleForm,
    TPChangeRuleForm,
    TariffForm
)
from billservice.forms.template import (
    ContractTemplateForm,
    TemplateForm,
    TemplateSelectForm
)
from billservice.forms.time import (
    TimeAccessNodeForm,
    TimeAccessServiceForm,
    TimeSpeedForm
)
from billservice.forms.traffic import (
    GroupForm,
    PrepaidTrafficForm,
    TrafficLimitForm,
    TrafficTransmitNodeForm,
    TrafficTransmitServiceForm
)
from billservice.forms.transaction import (
    BonusTransactionModelForm,
    TransactionModelForm,
    TransactionReportForm,
    TransactionTypeForm
)
from billservice.forms.user import SystemUserForm

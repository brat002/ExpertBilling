# -*- coding: utf-8 -*-

from billservice.models import (
    AddonService,
    AddonServiceTransaction,
    OneTimeService,
    OneTimeServiceHistory,
    PeriodicalService,
    PeriodicalServiceHistory,
    TimeTransaction,
    TrafficTransaction,
    Transaction
)


TRANSACTION_MODELS = {
    "PS_GRADUAL": 'PeriodicalServiceHistory',
    "PS_AT_END": 'PeriodicalServiceHistory',
    "PS_AT_START": 'PeriodicalServiceHistory',
    "TIME_ACCESS": "TimeTransaction",
    "NETFLOW_BILL": 'TrafficTransaction',
    "END_PS_MONEY_RESET": 'Transaction',
    "MANUAL_TRANSACTION": 'Transaction',
    "ACTIVATION_CARD": 'Transaction',
    "ONETIME_SERVICE": 'OneTimeServiceHistory',
    "OSMP_BILL": 'Transaction',
    "ADDONSERVICE_WYTE_PAY": 'AddonServiceTransaction',
    "ADDONSERVICE_PERIODICAL_GRADUAL": 'AddonServiceTransaction',
    "ADDONSERVICE_PERIODICAL_AT_START": 'AddonServiceTransaction',
    "ADDONSERVICE_PERIODICAL_AT_END": 'AddonServiceTransaction',
    "ADDONSERVICE_ONETIME": 'AddonServiceTransaction',
    "PAY_CARD": 'Transaction',
    "CASSA_TRANSACTION": 'Transaction',
    "PAYMENTGATEWAY_BILL": 'Transaction',
    "BELARUSBANK_PAYMENT_IMPORT": 'Transaction',
    "WEBMONEY_PAYMENT_IMPORT": 'Transaction',
    "EASYPAY_PAYMENT_IMPORT": 'Transaction',
    "PRIORBANK_PAYMENT_IMPORT": 'Transaction',
    "BELPOST_PAYMENT_IMPORT": 'Transaction',
    "ERIP_PAYMENT_IMPORT": 'Transaction',
    "SHTRAF_PAYMENT": 'Transaction',
    "QUICKPAY_BILL": 'Transaction',
    "OSMP_CUSTOM_BILL": 'Transaction',
    "USERBLOCK_PAYMENT": 'Transaction',
    "MONEY_TRANSFER_TO": 'Transaction',
    "MONEY_TRANSFER_FROM": 'Transaction'
}

MODEL_BY_TABLE = {
    'billservice_transaction': Transaction,
    'billservice_periodicalservicehistory': PeriodicalServiceHistory,
    'billservice_traffictransaction': TrafficTransaction,
    'billservice_onetimeservicehistory': OneTimeServiceHistory,
    'billservice_addonservicetransaction': AddonServiceTransaction,
    'billservice_timetransaction': TimeTransaction
}

SERVICEMODEL_BY_TABLE = {
    'billservice_periodicalservicehistory': PeriodicalService,
    'billservice_onetimeservicehistory': OneTimeService,
    'billservice_addonservicetransaction': AddonService
}

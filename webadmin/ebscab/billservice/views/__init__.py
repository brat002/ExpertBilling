# -*- coding: utf-8 -*-

from billservice.views.account import (
    account_prepays_traffic,
    get_ballance,
    user_block,
    userblock_action
)
from billservice.views.auth import login, login_out, register, simple_login
from billservice.views.card import card_acvation, card_form
from billservice.views.credentials import (
    change_email,
    change_password,
    password_form,
    subaccount_change_password,
    subaccount_password_form
)
from billservice.views.index import index
from billservice.views.misc import one_time_history, statistics, vpn_session
from billservice.views.news import news_delete
from billservice.views.payment import (
    SelectPaymentView,
    get_promise,
    make_payment
)
from billservice.views.service import (
    addon_service,
    addon_service_transaction,
    periodical_service_history,
    service_action,
    services_info
)
from billservice.views.tariff import change_tariff, change_tariff_form
from billservice.views.traffic import (
    traffic_limit,
    traffic_transaction,
    traffic_volume
)
from billservice.views.transaction import transaction

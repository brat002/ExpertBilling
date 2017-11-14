from ebsweb.views.account import (
    AccountEmailView,
    AccountInfoView,
    AccountPasswordView,
    AccountServiceAddView,
    AccountServiceDelView,
    AccountServicesView,
    AccountSubAccountPasswordView,
    AccountSubAccountsView,
    AccountTariffView,
    AccountView
)
from ebsweb.views.errors import (
    bad_request,
    page_not_found,
    permission_denied,
    server_error
)
from ebsweb.views.index import IndexView
from ebsweb.views.money import (
    MoneyCardView,
    MoneyPaymentView,
    MoneyPromiseView,
    MoneyTransferView,
    MoneyView
)
from ebsweb.views.notifications import NotificationView, NotificationsView
from ebsweb.views.signout import SignoutView
from ebsweb.views.support import (
    SupportFollowupCreateView,
    SupportTicketCreateView,
    SupportTicketsView,
    SupportTicketView,
    SupportView
)

# -*- coding: utf-8 -*-

import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import (
    AccountExtraForm,
    AccountForm,
    AccountManagementForm,
    AccountTariffForm,
    BankDataForm,
    BatchAccountTariffForm,
    OrganizationForm,
    SubAccountPartialForm,
    SuspendedPeriodBatchForm
)
from billservice.utils import systemuser_required
from billservice.models import (
    Account,
    AccountAddonService,
    AccountHardware,
    AccountSuppAgreement,
    AccountTarif,
    Organization,
    SubAccount,
    SuspendedPeriod,
)
from django_tables2.config import RequestConfig as DTRequestConfig
from ebscab.utils.decorators import ajax_request, render_to
from helpdesk.models import Ticket
from object_log.models import LogItem

from ebsadmin.tables import (
    AccountAddonServiceTable,
    AccountHardwareTable,
    AccountSuppAgreementTable,
    AccountTarifTable,
    SubAccountsTable,
    SuspendedPeriodTable,
    TicketTable
)


log = LogItem.objects.log_action


@ajax_request
@systemuser_required
def account_management_status(request):
    if not (request.user.account.has_perm('billservice.change_account')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на изменение аккаунтов')
        }
    status = request.GET.get('status')
    if request.method == 'POST' and status:
        form = AccountManagementForm(request.POST)
        if form.is_valid():
            accounts = form.cleaned_data.get('accounts')
            if accounts:
                accounts.update(status=status)

            messages.success(request,
                             _(u'Статус успешно изменён.'),
                             extra_tags='alert-success')
            return {
                'status': True
            }

        messages.error(request,
                       _(u'Ошибка при изменении статуса.'),
                       extra_tags='alert-danger')
        return {
            'status': False
        }
    return {}


@systemuser_required
@render_to('ebsadmin/accounttarif/edit.html')
def accounttarif_edit(request):
    account = None
    account_id = request.GET.get("account_id")
    id = request.POST.get("id")

    if request.method == 'POST':
        form = AccountTariffForm(request.POST)
        if id:
            if not (request.user.account.has_perm(
                    'billservice.change_accounttarif')):
                messages.error(request,
                               _(u'У вас нет прав на изменение тарифных '
                                 u'планов у аккаунта'),
                               extra_tags='alert-danger')
                return {}

        else:
            if not (request.user.account.has_perm(
                    'billservice.add_accounttarif')):
                messages.error(request,
                               _(u'У вас нет прав на создание тарифных '
                                 u'планов у аккаунта'),
                               extra_tags='alert-danger')
                return {}

        if form.is_valid():
            model = form.save(commit=False)
            if (AccountTarif.objects
                    .filter(account=model.account,
                            datetime__gte=model.datetime)
                    .exists()):
                messages.error(request,
                               _(u'Нельзя создавать правило смены тарифного '
                                 u'плана, если уже существует правило с '
                                 u'большей датой.'),
                               extra_tags='alert-danger')
                return {
                    'form': form,
                    'status': False
                }
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)

            return {
                'form': form,
                'status': True
            }
        else:
            return {
                'form': form,
                'status': False
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm(
                'billservice.add_accounttarif')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return {}

        if id:
            accounttariff = AccountTarif.objects.get(id=id)
            form = AccountTariffForm(instance=accounttariff)
        elif account_id:
            account = Account.objects.get(id=account_id)

        form = AccountTariffForm(
            initial={
                'account': account.id,
                'datetime': datetime.datetime.now()
            }
        )  # An unbound form

    return {
        'form': form,
        'status': False,
        'account': account
    }


@systemuser_required
@render_to('ebsadmin/accounttarif/batch_edit.html')
def account_management_accounttariff(request):
    account = None
    account_id = request.GET.get("account_id")
    id = request.POST.get("id")

    if request.method == 'POST':
        form = BatchAccountTariffForm(request.POST)
        if not (request.user.account.has_perm('billservice.add_accounttarif')):
            messages.error(request,
                           _(u'У вас нет прав на создание тарифных планов у '
                             u'аккаунта'),
                           extra_tags='alert-danger')
            return {}

        if form.is_valid():
            tariff = form.cleaned_data.get('tariff')
            dt = form.cleaned_data.get('datetime')
            for acc in form.cleaned_data.get('accounts'):
                acct = AccountTarif()
                acct.account = acc
                acct.tarif = tariff
                acct.datetime = dt
                acct.save()

                log('CREATE', request.user, acct)
            return {
                'form': form,
                'status': True
            }
        else:
            print form._errors
            return {
                'form': form,
                'status': False
            }
    else:
        if not (request.user.account.has_perm('billservice.add_accounttarif')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return {}

        m_form = AccountManagementForm(request.GET)
        form = None
        if m_form.is_valid():
            form = BatchAccountTariffForm(
                initial={
                    'accounts': m_form.cleaned_data.get('accounts', []),
                    'datetime': datetime.datetime.now()
                }
            )  # An unbound form

    return {
        'form': form,
        'status': False,
        'account': account
    }


@systemuser_required
@render_to('ebsadmin/suspendedperiod/batch_edit.html')
def account_management_suspendedperiod(request):
    if request.method == 'POST':
        form = SuspendedPeriodBatchForm(request.POST)
        if not (request.user.account.has_perm(
                'billservice.add_suspendedperiod')):
            messages.error(request,
                           _(u'У вас нет прав на создание периодов без '
                             u'списаний'),
                           extra_tags='alert-danger')
            return {}

        if form.is_valid():
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            for acc in form.cleaned_data.get('accounts'):
                item = SuspendedPeriod()
                item.start_date = start_date
                item.end_date = end_date
                item.account = acc
                item.save()

                log('CREATE', request.user, item)
            return {
                'form': form,
                'status': True
            }
        else:
            return {
                'form': form,
                'status': False
            }
    else:
        if not (request.user.account.has_perm(
                'billservice.add_suspendedperiod')):
            messages.error(request,
                           _(u'У вас нет прав на создание периодов без '
                             u'списаний'),
                           extra_tags='alert-danger')
            return {}

        m_form = AccountManagementForm(request.GET)
        form = None
        if m_form.is_valid():
            form = SuspendedPeriodBatchForm(
                initial={
                    'accounts': m_form.cleaned_data.get('accounts', [])
                }
            )  # An unbound form

    return {
        'form': form,
        'status': False
    }


@systemuser_required
@ajax_request
def account_management_delete(request):
    if not (request.user.account.has_perm('billservice.delete_account')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление аккаунтов')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    m_form = AccountManagementForm(request.GET)
    if m_form.is_valid():
        for acc in m_form.cleaned_data.get('accounts'):
            log('DELETE', request.user, acc)
            acc.delete()
        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "message": "Account not found"
        }


@systemuser_required
@ajax_request
def account_management_restore(request):
    if not (request.user.account.has_perm('billservice.edit_account')):
        return {
            'status': False,
            'message': _(u'У вас нет прав редактирование аккаунтов')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    m_form = AccountManagementForm(request.GET)
    if m_form.is_valid():
        for acc in m_form.cleaned_data.get('accounts'):
            acc.deleted = None
            acc.save()
            log('EDIT', request.user, acc)

        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "message": "Account not found"
        }


@systemuser_required
@render_to('ebsadmin/account_edit.html')
def accountedit(request):
    subaccounts_table = None
    accounttarif_table = None
    accounthardware_table = None
    suspendedperiod_table = None
    accountaddonservice_table = None
    accountsuppagreement_table = None
    accountsupp = None
    account_id = request.GET.get("id")
    account = None
    org_form = None
    bank_form = None
    action_log_table = None
    org = None
    prepaidradiustraffic = 0
    prepaidradiustime = 0
    ticket_table = None
    prepaidtraffic = []
    extra_form = None
    if account_id:
        if not (request.user.account.has_perm('billservice.change_account')):
            messages.error(request,
                           _(u'У вас нет прав на редактирование аккаунтов'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect(request.path)

        account = Account.objects.all_with_deleted().get(id=account_id)

        res = SubAccount.objects.filter(account=account)
        subaccounts_table = SubAccountsTable(res)
        DTRequestConfig(request, paginate=False).configure(subaccounts_table)

        res = AccountTarif.objects.filter(account=account)
        accounttarif_table = AccountTarifTable(res)
        DTRequestConfig(request, paginate=False).configure(accounttarif_table)

        res = AccountHardware.objects.filter(account=account)
        accounthardware_table = AccountHardwareTable(res)
        DTRequestConfig(request, paginate=False).configure(
            accounthardware_table)

        res = SuspendedPeriod.objects.filter(account=account)
        suspendedperiod_table = SuspendedPeriodTable(res)
        DTRequestConfig(request, paginate=False).configure(
            suspendedperiod_table)

        res = AccountAddonService.objects.filter(account=account)
        accountaddonservice_table = AccountAddonServiceTable(res)
        DTRequestConfig(request, paginate=False).configure(
            accountaddonservice_table)

        res = AccountSuppAgreement.objects.filter(account=account)
        accountsupp = AccountSuppAgreement.objects.filter(
            account=account, closed__isnull=True)

        accountsuppagreement_table = AccountSuppAgreementTable(res)
        DTRequestConfig(request, paginate=False).configure(
            AccountSuppAgreementTable(res))

        try:
            res = Ticket.objects.filter(
                Q(owner=User.objects.get(username=account.username)) |
                Q(account=account))
            ticket_table = TicketTable(res)
            DTRequestConfig(request, paginate=False).configure(ticket_table)
        except:
            pass

    else:
        if not (request.user.account.has_perm('billservice.add_account')):
            messages.error(request,
                           _(u'У вас нет прав на создание аккаунтов'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect(request.path)

    subaccount_form = None
    subaccounts_count = 0
    if account and request.method == 'POST':
        subaccounts_count = SubAccount.objects.filter(account=account).count()
        if subaccounts_count == 1:
            subaccount = SubAccount.objects.filter(account=account)[0]
            subaccount_form = SubAccountPartialForm(
                request.POST, instance=subaccount, prefix='subacc')
    elif account and request.method == 'GET':
        subaccounts_count = SubAccount.objects.filter(account=account).count()
        if subaccounts_count == 1:
            subaccount = SubAccount.objects.filter(account=account)[0]
            subaccount_form = SubAccountPartialForm(
                instance=subaccount, prefix='subacc')
    else:

        subaccount_form = SubAccountPartialForm(request.POST, prefix='subacc')

    if request.method == 'POST':

        if account and request.POST:
            form = AccountForm(request.POST, instance=account)
            org = Organization.objects.filter(account=account)

            if org:
                org_form = OrganizationForm(
                    request.POST, instance=org[0], prefix='org')
                bank = org[0].bank
                if bank:
                    bank_form = BankDataForm(
                        request.POST, instance=bank, prefix='bankdata')
                else:
                    bank_form = BankDataForm(request.POST, prefix='bankdata')

            else:
                org_form = OrganizationForm(request.POST, prefix='org')

                bank_form = BankDataForm(request.POST, prefix='bankdata')
        else:
            form = AccountForm(request.POST)
            org_form = OrganizationForm(request.POST, prefix='org')
            bank_form = BankDataForm(request.POST, prefix='bankdata')

        extra_form = AccountExtraForm(request.POST, instance=account)

        if form.is_valid():
            if not org_form.is_valid():
                return {
                    'subaccount_form': subaccount_form,
                    'extra_form': extra_form,
                    'org_form': org_form,
                    'prepaidtraffic': prepaidtraffic,
                    'prepaidradiustraffic': prepaidradiustraffic,
                    'prepaidradiustime': prepaidradiustime,
                    'bank_form': bank_form,
                    "accounttarif_table": accounttarif_table,
                    'accountaddonservice_table': accountaddonservice_table,
                    "account": account,
                    'subaccounts_table': subaccounts_table,
                    'accounthardware_table': accounthardware_table,
                    'suspendedperiod_table': suspendedperiod_table,
                    'accountsuppagreement_table': accountsuppagreement_table,
                    'accountsupp': accountsupp,
                    'form': form
                }

            model = form.save(commit=False)
            model.save()
            contract_num = form.cleaned_data.get("contract_num")

            if subaccounts_count <= 1:
                new = False
                if subaccounts_count == 0:
                    subaccount = SubAccount(account=model)
                    subaccount.save()
                    new = True
                    subaccount_form = SubAccountPartialForm(
                        request.POST, instance=subaccount, prefix='subacc')
                else:
                    subaccount = SubAccount.objects.filter(account=model)[0]

                subaccount_form = SubAccountPartialForm(
                    request.POST, instance=subaccount, prefix='subacc')

                if subaccount_form.is_valid():
                    subacc_model = subaccount_form.save(commit=False)
                    if subacc_model.username or subacc_model.nas or \
                            subacc_model.ipn_ip_address or \
                            subacc_model.vpn_ip_address or \
                            subacc_model.vpn_ipv6_ip_address or \
                            subacc_model.ipv4_vpn_pool or \
                            subacc_model.ipv4_ipn_pool or \
                            subacc_model.switch:
                        subacc_model.save()

                        if id:
                            log('EDIT', request.user, subacc_model)
                        else:
                            log('CREATE', request.user, subacc_model)
                    else:
                        subacc_model.delete()
                else:
                    if new == True:
                        subaccount.delete()

                    if subaccount_form.errors:
                        for k, v in subaccount_form._errors.items():
                            messages.error(request,
                                           '%s=>%s' % (k, ','.join(v)),
                                           extra_tags='alert-danger')
                    return {
                        'subaccount_form': subaccount_form,
                        'extra_form': extra_form,
                        'org_form': org_form,
                        'prepaidtraffic': prepaidtraffic,
                        'prepaidradiustraffic': prepaidradiustraffic,
                        'prepaidradiustime': prepaidradiustime,
                        'bank_form': bank_form,
                        "accounttarif_table": accounttarif_table,
                        'accountaddonservice_table': accountaddonservice_table,
                        "account": account,
                        'subaccounts_table': subaccounts_table,
                        'accounthardware_table': accounthardware_table,
                        'suspendedperiod_table': suspendedperiod_table,
                        'accountsuppagreement_table': accountsuppagreement_table,
                        'accountsupp': accountsupp,
                        'form': form
                    }

            if not model.contract and contract_num:
                contract_template = contract_num.template
                contract_counter = contract_num.counter or 1

                year = model.created.year
                month = model.created.month
                day = model.created.day
                hour = model.created.hour
                minute = model.created.minute
                second = model.created.second

                accid = model.id
                username = model.username

                d = {
                    'account_id': accid,
                    'username': username,
                    'year': year,
                    'month': month,
                    'day': day,
                    'hour': hour,
                    'minute': minute,
                    'second': second,
                    'contract_num': contract_counter
                }

                contract = (contract_template % d) if contract_template else ''
                model.contract = contract
                model.save()

                contract_num.count = contract_counter
                contract_num.save()

            if form.cleaned_data.get('organization'):
                org_model = org_form.save(commit=False)
                if request.POST.get("bankdata-bank"):

                    bank_model = bank_form.save(commit=False)
                    bank_model.save()
                    org_model.bank = bank_model

                org_model.acount = model
                org_model.save()
            elif org:  # if not organization and organization for account exists
                org.delete()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(
                request, u'Аккаунт сохранён.', extra_tags='alert-success')
            return HttpResponseRedirect(
                "%s?id=%s" % (reverse("account_edit"), model.id))
        else:
            if form._errors:
                for k, v in form._errors.items():
                    messages.error(request,
                                   '%s=>%s' % (k, ','.join(v)),
                                   extra_tags='alert-danger')

            if extra_form._errors:
                for k, v in extra_form._errors.items():
                    messages.error(request, '%s=>%s' % (k, ','.join(v)),
                                   extra_tags='alert-danger')
            if org_form._errors:
                for k, v in org_form._errors.items():
                    messages.error(request, '%s=>%s' % (k, ','.join(v)),
                                   extra_tags='alert-danger')
            if bank_form._errors:
                for k, v in bank_form._errors.items():
                    messages.error(request, '%s=>%s' % (k, ','.join(v)),
                                   extra_tags='alert-danger')

            return {
                'subaccount_form': subaccount_form,
                'extra_form': extra_form,
                'ticket_table': ticket_table,
                'org_form': org_form,
                'bank_form': bank_form,
                'prepaidtraffic': prepaidtraffic,
                'prepaidradiustraffic': prepaidradiustraffic,
                'prepaidradiustime': prepaidradiustime,
                "accounttarif_table": accounttarif_table,
                'accountaddonservice_table': accountaddonservice_table,
                "account": account,
                'subaccounts_table': subaccounts_table,
                'accounthardware_table': accounthardware_table,
                'suspendedperiod_table': suspendedperiod_table,
                'accountsuppagreement_table': accountsuppagreement_table,
                'accountsupp': accountsupp,
                'form': form
            }
    if account:
        org = Organization.objects.filter(account=account)
        if org:
            org_form = OrganizationForm(instance=org[0], prefix='org')
            bank = None
            if org[0].bank:
                bank = org[0].bank
                bank_form = BankDataForm(instance=bank, prefix='bankdata')
            form = AccountForm(
                initial={'organization': True}, instance=account)

        else:
            org_form = OrganizationForm(
                initial={'account': account}, prefix='org')
            bank_form = BankDataForm(prefix='org')
            form = AccountForm(instance=account)
            extra_form = AccountExtraForm(instance=account)
    else:
        form = AccountForm(
            initial={'credit': 0, 'ballance': 0, 'created': datetime.datetime.now()})
        extra_form = AccountExtraForm()
        org_form = OrganizationForm(prefix='org')
        bank_form = BankDataForm(prefix='org')
    if not subaccount_form and subaccounts_count == 0:
        subaccount_form = SubAccountPartialForm(request.POST, prefix='subacc')
    return {
        'form': form,
        'subaccount_form': subaccount_form,
        'extra_form': extra_form,
        'org_form': org_form,
        'bank_form': bank_form,
        "accounttarif_table": accounttarif_table,
        'accountaddonservice_table': accountaddonservice_table,
        "account": account,
        'subaccounts_table': subaccounts_table,
        'accounthardware_table': accounthardware_table,
        'suspendedperiod_table': suspendedperiod_table,
        'accountsuppagreement_table': accountsuppagreement_table,
        'ticket_table': ticket_table,
        'accountsupp': accountsupp
    }

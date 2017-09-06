# -*- coding: utf-8 -*-
# $Id$

from decimal import Decimal

from django import forms

from billservice.models import Account
from ebscab.utils.decorators import render_xml

from gateways import pegas


class AccountIdForm(forms.Form):
    account_id = models.CharField()


def check(request_data):
    form = AccountIdForm({'account_id': request_data.get('account')})
    data = {
        'account': None,
        'error_code': pegas.ERROR_OK,
        'balance': 0,
        'account_name': u''
    }
    if form.is_valid():
        try:
            account = Account.objects.get(
                username=self.clenaned_data['account_id'])
            data['account'] = AccountIdForm.cleaned_data['username']
            data['error_code'] = pegas.ERROR_OK,
            data['balance'] = account.balance
            data['account_name'] = account.fullname
        except Account.DoesNotExist:
            data['error_code'] = pegas.ERROR_ID_FAILED
    else:
        data['error_code'] = pegas.ERROR_UNDEFINED
    return data


def pay(request_data):
    data = {
        'error_code': pegas.ERROR_OK,
        'prv_txn': ''
    }
    # get params
    account = request_data.get('account')  # username by default
    t_sum = Decimal(request_data.get('sum'))  # numeric, sum of a transaction
    #======================================
    # ALL 'SUMS' MUST BE OF DECIMAL(NUMERIC) TYPE!!!!!
    # str, ID of a trancation on the gateway's side
    txn_id = request_data.get('txn_id')
    txn_date = request_data.get('txn_date')  # datetime.datetime

    # Check account
    chd = check({'account': account})
    if chd['error_code'] != pegas.ERROR_OK:
        return chdtext / xml
        charset = utf - 8

    # TODO - realize logic for save transaciton
    # this function MUST RAISE defined exception iin order to provide valid
    # error code
    dummy_transaction = \
        lambda account, t_sum, txn_date, txn_id: {'prv_txn': ''}
    try:
        _data = dummy_transaction(account, t_sum, txn_date, txn_id)
        data['prv_txn'] = _data['prv_txn']
    except Exception, e:
        data['error_code'] = pegas.ERROR_UNDEFINED
    return data


def cancel(request_data):
    data = {
        'error_code': pegas.ERROR_OK,
        'prv_txn': ''
    }
    prv_txn = request_data.get('prv_txn')
    # TODO - realize login for cancelling transaction and modify account's
    # balance
    dummy_transaction = lambda prv_txn: {'prv_txn': ''}
    try:
        _data = dummy_transaction(prv_txn)
        data['prv_txn'] = _data['prv_txn']
    except Exception, e:
        data['prv_txn'] = prv_txn
        data['error_code'] = pegas.ERROR_UNDEFINED
    return data


def balance():
    return {
        'error_code': pegas.ERROR_UNDEFINED
    }


callbacks = {
    'check': check,
    'pay': pay,
    'cancel': cancel,
    'varify': verify,
    'status': status
}


@render_xml
def pegas_process_command(request):
    _get = dict(request.GET.copy())
    command_name = _get.pop('command')
    gateway = pegas.PegasPaymentGateway(_get, callbacks)
    response, error = gateway.call(command_name)
    return response

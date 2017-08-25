# -*- coding: utf-8 -*-

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import mail_admins
from django.db import connection
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed
)
from django.template import loader
try:
    from django.views.decorators.csrf import csrf_exempt
except ImportError:
    from django.contrib.csrf.middleware import csrf_exempt

from ebscab.lib.decorators import render_to

import settings
from forms import *
from models import Payment


@render_to('wm_sample/redirect.html')
def simple_payment(request):
    resp = {}
    if request.method == 'POST':
        amount = request.POST.get('amount', 0)
        initial = {
            'LMI_PAYEE_PURSE': settings.PURSE,
            'LMI_PAYMENT_AMOUNT': amount,
            'LMI_PAYMENT_NO': Payment.objects.create(
                account=request.user.account,
                amount=amount).id,
            'LMI_PAYMENT_DESC': loader.render_to_string(
                'wm_sample/simple_payment_desc.txt',
                {},
                request).strip()[:255],
        }
        resp['form'] = PaymentRequestForm(initial=initial)

    return resp


@render_to('wm_sample/success.html')
def success(request):
    response = {}
    if request.method == 'POST':
        form = SettledPaymentForm(request.POST)
        if form.is_valid():
            response['id'] = form.cleaned_data['LMI_PAYMENT_NO']
            response['sys_invs_no'] = form.cleaned_data['LMI_SYS_INVS_NO']
            response['sys_trans_no'] = form.cleaned_data['LMI_SYS_TRANS_NO']
            response['date'] = form.cleaned_data['LMI_SYS_TRANS_DATE']

    return response


@render_to('wm_sample/fail.html')
def fail(request):
    response = {}
    if request.method == 'POST':
        form = UnSettledPaymentForm(request.POST)
        if form.is_valid():
            response['id'] = form.cleaned_data['LMI_PAYMENT_NO']
            response['sys_invs_no'] = form.cleaned_data['LMI_SYS_INVS_NO']
            response['sys_trans_no'] = form.cleaned_data['LMI_SYS_TRANS_NO']
            response['date'] = form.cleaned_data['LMI_SYS_TRANS_DATE']

    return response


@csrf_exempt
def result(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(permitted_methods=('POST',))

    form = PrerequestForm(request.POST)
    if form.is_valid() and form.cleaned_data['LMI_PREREQUEST']:
        payment_no = int(form.cleaned_data['LMI_PAYMENT_NO'])
        try:
            payment = Payment.objects.get(id=payment_no)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(
                "Invoice with number %s not found." % payment_no)
        return HttpResponse("YES")

    form = PaymentNotificationForm(request.POST)
    if form.is_valid():
        purse = form.cleaned_data['LMI_PAYEE_PURSE']
        if purse.lower() != settings.PURSE.lower():
            return HttpResponseBadRequest("Incorrect purse")

        key = "%s%s%s%s%s%s%s%s%s%s" % (
            purse,
            form.cleaned_data['LMI_PAYMENT_AMOUNT'],
            form.cleaned_data['LMI_PAYMENT_NO'],
            form.cleaned_data['LMI_MODE'],
            form.cleaned_data['LMI_SYS_INVS_NO'],
            form.cleaned_data['LMI_SYS_TRANS_NO'],
            form.cleaned_data['LMI_SYS_TRANS_DATE'].strftime(
                '%Y%m%d %H:%M:%S'),
            settings.SECRET_KEY,
            form.cleaned_data['LMI_PAYER_PURSE'],
            form.cleaned_data['LMI_PAYER_WM'])

        generated_hash = md5(key).hexdigest().upper()

        if generated_hash == form.cleaned_data['LMI_HASH']:
            payment = Payment.objects.get(id=payment_no)
            payment.purse = purse
            payment.amount = form.cleaned_data['LMI_PAYMENT_AMOUNT']
            payment.mode = form.cleaned_data['LMI_MODE']
            payment.sys_invs_no = form.cleaned_data['LMI_SYS_INVS_NO']
            payment.sys_trans_no = form.cleaned_data['LMI_SYS_TRANS_NO']
            payment.sys_trans_date = form.cleaned_data['LMI_SYS_TRANS_DATE']
            payment.payer_purse = form.cleaned_data['LMI_PAYER_PURSE']
            payment.payer_wm = form.cleaned_data['LMI_PAYER_WM']
            payment.paymer_number = form.cleaned_data['LMI_PAYMER_NUMBER']
            payment.paymer_email = form.cleaned_data['LMI_PAYMER_EMAIL']
            payment.telepat_phonenumber = \
                form.cleaned_data['LMI_TELEPAT_PHONENUMBER']
            payment.telepat_orderid = form.cleaned_data['LMI_TELEPAT_ORDERID']
            payment.payment_creditdays = \
                form.cleaned_data['LMI_PAYMENT_CREDITDAYS']

            try:
                cursor = connection.cursor()
                cursor.execute(u"""\
INSERT INTO billservice_transaction(account_id, bill, type_id, approved, \
tarif_id, summ, created)
VALUES(%s, '%s', 'WEBMONEY_PAYMENT', True, get_tarif(%s), %s, now())\
""" % (payment.account.id, payment.id, payment.amount * (-1), payment.created))
                cursor.connection.commit()
                payment.save()
            except:
                mail_admins(
                    'Unprocessed payment without invoice!',
                    'Payment NO is %s.\npayment:\n%s\ndata:\n%s' % payment_no,
                    repr(payment),
                    repr(form.cleaned_data),
                    fail_silently=True)
            return HttpResponse("OK")
        else:
            mail_admins('Unprocessed payment with incorrect hash!',
                        'Payment NO is %s.' % payment_no,
                        fail_silently=True)
            return HttpResponseBadRequest("Incorrect hash")

    return HttpResponseBadRequest("Unknown error!")

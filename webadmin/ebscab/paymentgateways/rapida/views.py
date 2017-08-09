# -*- coding: utf-8 -*-

import datetime
import decimal
import time

from django.http import HttpResponse

from billservice.models import Account, Transaction


response_check = u"""\
<?xml version="1.0" encoding="utf-8"?>
<response>
    <rapida_txn_id>%s</rapida_txn_id>
    <result>%s</result>
    <comment>%s</comment>
</response>
"""

response_pay = u"""\
<?xml version="1.0" encoding="utf-8"?>
<response>
    <rapida_txn_id>%s</rapida_txn_id>
    <prv_txn>%s</prv_txn>
    <result>%s</result>
    <comment>%s</comment>
</response>
"""


def payment(request):
    txn_id = request.GET.get("txn_id")
    contract = request.GET.get('account')
    amount = float(request.GET.get('sum', 0))
    action = request.GET.get('command')
    date = request.GET.get("txn_date")

    if not (contract or amount or action not in ['check', 'pay']):
        response = response_check % (
            txn_id, 300, u"Ошибка передачи параметров")
        return HttpResponse(response)

    try:
        amount = decimal.Decimal(amount)
    except:
        response = response_check % (
            txn_id, 300, u"Введённая сумма не является числом")
        return HttpResponse(response)

    if amount <= 0:
        response = response_check % (
            txn_id, 241, u"Введённая сумма слишком мала")

        return HttpResponse(response)

    try:
        account = Account.objects.get(contract=contract)
    except Exception, e:
        response = response_check % (txn_id, 5, u"Договор не найден")
        return HttpResponse(response)

    if action == 'check':
        response = response_check % (txn_id, 0, u"Договор найден")
        return HttpResponse(response)

    if action == 'pay':
        if not date:
            response = response_check % (txn_id, 300, u"Дата не указана")
            return HttpResponse(response)
        try:
            payment_date = datetime.datetime(
                *time.strptime(date, "%Y%m%d%H%M%S")[0:5])
        except Exception, e:
            response = response_check % (txn_id, 300, u"Неверный формат даты")
            return HttpResponse(response)

        try:
            model, created = Transaction.objects.get_or_create(
                summ=amount,
                account=account,
                approved=True,
                created=payment_date,
                promise=False,
                bill=txn_id,
                type_id='RAPIDA_PAYMENT'
            )

            response = response_pay % (
                txn_id, model.id, 0, u"Оплата произведена успешно.")
            return HttpResponse(response)
        except Exception, e:
            response = response_check % (
                txn_id, 300, u"Ошибка выполнения платежа")
            return HttpResponse(response)

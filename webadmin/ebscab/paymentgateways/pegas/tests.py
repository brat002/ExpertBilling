# -*- coding: utf-8 -*-
# $Id$

import datetime
import unittest

from django.test import Client

from paymentgateways.gateways.pegas import PegasPaymentGateway


class CheckAccountTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.response_mime = 'text/xml'

    def test_auth_by_ip(self):
        response_body = u"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <response>
            <result>0</result>
            <name>Абонент И.О</name>
            <balance>10.55</balance>
        </response>"""


class PegasPaymentGatewayTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.response_mime = 'text/xml'

    def test_check_ok(self):
        transaction_id = 2345
        account_name = 'Bob'
        balance = 100.00
        date = datetime.datetime.now()
        error = (0, u'ОК', False)

        def callback(kwargs):
            return {
                'transaction_id': transaction_id,
                'account_name': account_name,
                'balance': balance,
                'error_code': error[0]
            }
        pegas = PegasPaymentGateway(
            {
                'account': 3245,
                'date': date
            },
            {
                'check': callback
            })
        response = u"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <response>
            <result>%(result)d</result>
            <name>%(account_name)s</name>
            <balance>%(balance).02f</balance>
        </response>""" % {'result': error[0],
                          'account_name': account_name,
                          'balance': balance, }
        self.assertEquals(pegas.check(), (response, error))

    def test_check_timeout(self):
        transaction_id = 2345
        account_name = 'Bob'
        balance = 100.00
        account = 3245
        date = datetime.datetime.now()
        error = (1, u'Временная ошибка. Повторите запрос позже', False)

        def callback(kwargs):
            return {
                'transaction_id': transaction_id,
                'account_name': account_name,
                'balance': balance,
                'error_code': error[0]
            }
        pegas = PegasPaymentGateway(
            {
                'account': account,
                'date': date
            },
            {
                'check': callback
            })
        response = u"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <response>
            <result>%(result)d</result>
            <comment>%(comment)s</comment>
        </response>""" % {'result': error[0],
                          'comment': error[1]}
        self.assertEquals(pegas.check(), (response, error))

    def test_pay_ok(self):
        transaction_id = 2345
        txn_id = 123
        error = (0, u'ОК', False)

        def callback():
            return {
                'transaction_id': transaction_id,
                'error_code': error[0]
            }
        pegas = PegasPaymentGateway({'txn_id': txn_id}, {'pay': callback})
        response = u"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <response>
            <txn_id>%(txn_id)s</txn_id>
            <prv_txn>%(transaction_id)s</prv_txn>
            <result>%(result)d</result>
        </response>""" % {'txn_id': txn_id,
                          'transaction_id': transaction_id,
                          'result': error[0]}
        self.assertEquals(pegas.pay(), (response, error))

    def test_pay_timeout(self):
        transaction_id = 2345
        txn_id = 123
        error = (1, u'Временная ошибка. Повторите запрос позже', False)

        def callback():
            return {
                'transaction_id': transaction_id,
                'error_code': error[0]
            }
        pegas = PegasPaymentGateway({'txn_id': txn_id}, {'pay': callback})
        response = u"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <response>
            <txn_id>%(txn_id)s</txn_id>
            <prv_txn>%(transaction_id)s</prv_txn>
            <result>%(result)d</result>
            <comment>%(comment)s</comment>
        </response>""" % {'txn_id': txn_id,
                          'transaction_id': transaction_id,
                          'result': error[0],
                          'comment': error[1]}
        self.assertEquals(pegas.pay(), (response, error))

    def test_cancel_status_ok(self):
        """
        cancel transaction for payment: error_code = 0
        """
        transaction_id = 2345
        error = (0, u'ОК', False)

        def callback():
            return {
                'transaction_id': transaction_id,
                'error_code': error[0]
            }
        pegas = PegasPaymentGateway({}, {'cancel': callback})
        response_body =  u"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <response>
            <prv_txn>%(prv_txn)s</prv_txn>
            <result>%(result)d</result>
        </response>"""
        self.assertEquals(pegas.cancel(),
                          (response_body % {
                              'prv_txn': transaction_id,
                              'result': error[0]
                           },
                           error))

    def test_cancel_status_timeout(self):
        """
        cancel transaction for payment: error_code = 1
        """
        transaction_id = 2345
        error = (1, u'Временная ошибка. Повторите запрос позже', False)

        def callback():
            return {
                'transaction_id': transaction_id,
                'error_code': error[0]
            }
        pegas = PegasPaymentGateway({}, {'cancel': callback})

        response_body = u"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <response>
            <prv_txn>%(prv_txn)s</prv_txn>
            <result>%(result)d</result>
            <comment>%(comment)s</comment>
        </response>"""
        self.assertEquals(
            pegas.cancel(),
            (response_body % {
                'prv_txn': transaction_id,
                'result': error[0],
                'comment': error[1]
            },
             error))

    def test_status_ok(self):
        balance = 100.00
        error = (0, u'ОК', False)

        def callback():
            return {
                'balance': balance,
                'error_code': error[0]
            }
        pegas = PegasPaymentGateway({}, {'status': callback})
        response = u"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <response>
            <result>%(error)d</result>
            <balance>%(ballance).02f</balance>
        </response>""" % {
            'error': error[0],
            'ballance': balance
        }
        self.assertEquals(pegas.status(), (response, error))

    def test_status_timeout(self):
        balance = 100.00
        error = (1, u'Временная ошибка. Повторите запрос позже', False)

        def callback():
            return {
                'balance': balance,
                'error_code': error[0]
            }
        pegas = PegasPaymentGateway({}, {'status': callback})
        response = u"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <response>
            <result>%(error)d</result>
            <comment>%(comment)s</comment>
        </response>""" % {
            'error': error[0],
            'comment': error[1]
        }
        self.assertEquals(pegas.status(), (response, error))

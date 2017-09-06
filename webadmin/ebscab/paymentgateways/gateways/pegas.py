# -*- coding: utf-8 -*-

"""
This module provides interface to Pegas (http://pegaspay.com.ua) payment system
"""

from django.utils.translation import ugettext_lazy as _


AUTH_FIELDS = ('id', 'username', '')

# Pegas specific error codes and settings

ERROR_OK = 0
ERROR_TIME = 1
ERROR_ID_FAILED = 4
ERROR_ID_NONEXIST = 5
ERROR_PAY_DEPRECATED = 7
ERROR_PAY_UNAVAILABLE = 8
ERROR_ACCOUNT_NOTACTIVE = 79
ERROR_SUM_SMALL = 241
ERROR_SUM_BIG = 242
ERROR_ACCOUNT_STATE = 243
ERROR_CANCEL_UNAVAILABLE = 251
ERROR_UNDEFINED = 300

ERROR_CODES = (  # int code, unicode message, boolean is_fatal
    (ERROR_OK, _(u'ОК'), False),
    (ERROR_TIME, _(u'Временная ошибка. Повторите запрос позже'), False),
    (ERROR_ID_FAILED, _(u'Неверный формат идентификатора абонента'), True),
    (ERROR_ID_NONEXIST,
     _(u'Идентификатор абонента не найден (Ошиблись номером)'),
     True),
    (ERROR_PAY_DEPRECATED, _(u'Прием платежа запрещен провайдером'), True),
    (ERROR_PAY_UNAVAILABLE,
     _(u'Прием платежа запрещен по техническим причинам'),
     True),
    (ERROR_ACCOUNT_NOTACTIVE, _(u'Счет абонента не активен'), True),
    (ERROR_SUM_SMALL, _(u'Сумма слишком мала'), True),
    (ERROR_SUM_BIG, _(u'Сумма слишком велика'), True),
    (ERROR_ACCOUNT_STATE, _(u'Невозможно проверить состояние счета'), True),
    (ERROR_CANCEL_UNAVAILABLE, _(u'Отмена платежа невозможна'), True),
    (ERROR_UNDEFINED, _(u'Другая ошибка провайдера'), True)
)

PAYMENT_ID_NAME = 'txn_id'
PAYMENT_DATE_NAME = 'txn_date'

DATE_FORMAT = '%Y%m%d%H%L%s'  # ГГГММДДЧЧММСС


class BasePaymentGateway(object):

    def auth(self):
        """
        realize different strategies of getting user account data
        """
        pass

    def pay(self):
        raise NotImplementedError

    def error(self):
        raise NotImplementedError

    def save_transaction(self):
        raise NotImplementedError


class PegasPaymentGateway(BasePaymentGateway):

    COMMANDS = ('check', 'pay', 'cancel', 'verify', 'status')

    def __init__(self, params_dict, callbacks=None):
        """
        You should define a number of callback functions for fallowing commands:
        1. 'check',
           receives dict:
                account: string for identifying user account


           returns dict:
                acccount: int account - account ID in pegas system,
                error_code: int error_code - error code from ERROR_CODES,
                balance: float balance - current balance value,
                acccount_name: unicode account_name - user verbose name

        2. 'pay',
            receives dict:
                txn_id=1234567&
                txn_date=20050815120133&
                account=1234567&
                sum=10.45
        """
        if not callbacks:
            raise Exception('No callback functions defined!')

        self.params = params_dict
        self.callbacks = callbacks

    def get_param(self, name):
        return self.params.get(name, None)

    def get_callback(self, callback_name):
        try:
            return self.callbacks[callback_name]
        except KeyError:
            raise Exception("'Callback for command %s is not implemented!'" %
                            (callback_name))

    def is_error(self, error_code):
        return error_code != ERROR_OK

    def error(self, code):
        try:
            return [x for x in ERROR_CODES if x[0] == code][0]
        except IndexError:
            raise Exception('Error code %d is not supported!' % code)

    def error_is_fatal(self, error):
        return error[2]

    def call(command_name):
        func = getattr(self, u'command_%s' % command_name)
        if is_callable(func):
            return func()
        else:
            raise AttributError

    def check_params(self, *params):
        """
        Check if given params exist in request params
        This method SHOUD BE CALLED in the top of each command method
        """
        for param_name in params:
            if not self.get_param(param_name):
                response = u"""\
                <xml version="1.0" encoding="UTF-8">
                <response>
                  <result>%s</result>
                  <comment>Incomplete GET parameters for current command</comment>
                </response>""" % ERROR_TIME
                return (response, self.error(ERROR_TIME), self.is_error(ERROR_TIME))
        return (u'', self.error(ERROR_OK), is_error(ERROR_OK))

    def command_check(self):
        # Check error
        respose, error, is_error = self.check_params('account')
        if is_error:
            return (response, error)
        """
        Performs check of existence of selected user
        """
        account = self.params.get('account')
        resp = self.get_callback('check')({'account': account})
        error = self.error(resp['error_code'])
        balance = resp['balance']
        account_name = resp['account_name']

        if not self.is_error(error[0]):
            response = u"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <response>
              <result>%(result)d</result>
              <name>%(account_name)s</name>
              <balance>%(balance).02f</balance>
            </response>""" % {
                'result': error[0],
                'account_name': account_name,
                'balance': balance}
        else:  # error
            response = u"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <response>
              <result>%(result)d</result>
              <comment>%(comment)s</comment>
            </response>""" % {
                'result': error[0],
                'comment': error[1]}
        return (response, error)

    def command_pay(self):
        response, error, is_error = self.check_params(
            'txn_date', 'txn_id', 'account', 'sum')
        if is_error:
            return (response, error)
        try:
            txn_date = self.get_param('txn_date')
        except ValueEror, KeyError:  # unrecognized datetime format from gateway
            error = self.error(ERROR_UNDEFINED)
            response = u"""\
            <xml version="1.0" encoding="UTF-8">
            <response>
              <result>1</result>
              <comment>Incorrect input date format, shoud be YYYYMMDDHHIISS</comment>
            </response>
            """
            return (response, error)
        input_data = {
            'txn_date': txn_date,
            'txn_id': self.get_param('txn_id')
        }

        resp = self.get_callback('pay')(input_data)
        prv_tnx = resp['prv_tnx']
        txn_id = self.params.get(PAYMENT_ID_NAME)
        error = self.error(resp['error_code'])
        if not self.is_error(error[0]):
            response = u"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <response>
              <txn_id>%(txn_id)s</txn_id>
              <prv_txn>%(prv_tnx)s</prv_txn>
              <result>%(result)d</result>
            </response>""" % {'txn_id': txn_id,
                              'prv_tnx': prv_tnx,
                              'result': error[0]}
        else:  # error
            response = u"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <response>
              <txn_id>%(txn_id)s</txn_id>
              <prv_txn>%(prv_tnx)s</prv_txn>
              <result>%(result)d</result>
              <comment>%(comment)s</comment>
            </response>""" % {'txn_id': txn_id,
                              'prv_tnx': prv_tnx,
                              'result': error[0],
                              'comment': error[1]}
        return (response, error)

    def command_cancel(self):
        response, error, is_error = self.check_params(
            'txn_date', 'txn_id', 'account', 'sum')
        if is_error:
            return (response, error)

        resp = self.get_callback('cancel')()
        prv_txn = resp['transaction_id']
        error = self.error(resp['error_code'])
        if not self.is_error(error[0]):
            response = u"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <response>
                <prv_txn>%(prv_txn)s</prv_txn>
                <result>%(result)d</result>
            </response>""" % {
                'prv_txn': prv_txn,
                'result': error[0]}
        else:
            response = u"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <response>
               <prv_txn>%(prv_txn)s</prv_txn>
               <result>%(result)d</result>
               <comment>%(comment)s</comment>
            </response>""" % {
                'prv_txn': prv_txn,
                'result': error[0],
                'comment': error[1]}
        return (response, error)

    def command_verify(self):
        error = self.error(1)
        response = u"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <response>
            <result>%(error)d</result>
            <comment>%(comment)s</comment>
        </response>""" % {
            'error': error[0],
            'comment': error[1]}
        return (response, error)

    def command_balance(self):
        resp = self.get_callback('balance')()
        error = self.error(resp['error_code'])
        ballance = resp['balance']
        if not self.is_error(error[0]):
            response = u"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <response>
              <result>%(error)d</result>
              <balance>%(balance).02f</balance>
            </response>""" % {
                'error': error[0],
                'balance': ballance}
        else:
            response = u"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <response>
              <result>%(error)d</result>
              <comment>%(comment)s</comment>
            </response>""" % {
                'error': error[0],
                'comment': error[1]}
        return (response, error)

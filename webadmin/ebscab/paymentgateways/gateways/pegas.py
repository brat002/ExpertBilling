# -*- coding=utf-8 -*-
# $Id$

"""
This module provides interface to Pegas (http://pegaspay.com.ua) payment system
"""
AUTH_FIELDS = ('id','username','') 

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
    
    ERROR_CODES = ( # int code, unicode message, boolean is_fatal
        (ERROR_OK,u'ОК',False),
        (ERROR_TIME,u'Временная ошибка. Повторите запрос позже',False),
        (ERROR_ID_FAILED,u'Неверный формат идентификатора абонента',True),
        (ERROR_ID_NONEXIST,u'Идентификатор абонента не найден (Ошиблись номером)',True),
        (ERROR_PAY_DEPRECATED,u'Прием платежа запрещен провайдером',True),
        (ERROR_PAY_UNAVAILABLE,u'Прием платежа запрещен по техническим причинам',True),
        (ERROR_ACCOUNT_NOTACTIVE,u'Счет абонента не активен',True),
        (ERROR_SUM_SMALL,u'Сумма слишком мала',True),
        (ERROR_SUM_BIG,u'Сумма слишком велика',True),
        (ERROR_ACCOUNT_STATE,u'Невозможно проверить состояние счета',True),
        (ERROR_CANCEL_UNAVAILABLE,u'Отмена платежа невозможна',True),
        (ERROR_UNDEFINED,u'Другая ошибка провайдера',True)
    )
    
    PAYMENT_ID_NAME = 'txn_id'
    PAYMENT_DATE_NAME = 'txn_date'

    DATE_FORMAT = '%Y%m%d%H%L%s' # ГГГММДДЧЧММСС
    
    COMMANDS = ('check','pay','cancel','verify', 'status')
    
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
        return self.params.get(name,None)
    
    def get_callback(self, callback_name):
       try:
           return self.callbacks[callback_name]
       except KeyError:
           raise Exception("'Callback for command %s is not implemented!'"%(callback_name))
    
    def is_error(self, error_code):
        return error_code != self.ERROR_OK
    
    def error(self, code):
        try:
            return [x for x in self.ERROR_CODES if x[0] == code][0]
        except IndexError:
            raise Exception('Error code %d is not supported!' % code)  
    
    def error_is_fatal(self, error):
        return error[2]
    
    def check(self):
        """
        Performs check of existence of selected user
        """
        account =self.params.get('account')
        resp = self.get_callback('check')({'account':account, \
                                        'date':self.params.get('date')})
        error =  self.error(resp['error_code'])
        balance = resp['balance']
        account_name = resp['account_name']
        
        
        if not self.is_error(error[0]):
            response = \
            u"""<?xml version="1.0" encoding="UTF-8"?>
                <response>
                  <result>%(result)d</result>
                  <name>%(account_name)s</name>
                  <balance>%(balance).02f</balance>
                </response>""" % {'result':error[0],
                                  'account_name':account_name,
                                  'balance':balance}
        else: # error
            response = \
            u"""<?xml version="1.0" encoding="UTF-8"?>
                <response>
                  <result>%(result)d</result>
                  <comment>%(comment)s</comment>
                </response>""" % {'result':error[0],
                                   'comment':error[1]}
        return (response, error)
            
    def pay(self):
        resp = self.get_callback('pay')()
        prv_tnx = resp['transaction_id']
        txn_id = self.params.get(self.PAYMENT_ID_NAME)
        error = self.error(resp['error_code'])
        if not self.is_error(error[0]):
            response = \
            u"""<?xml version="1.0" encoding="UTF-8"?>
                <response>
                  <txn_id>%(txn_id)s</txn_id>
                  <prv_txn>%(transaction_id)s</prv_txn>
                  <result>%(result)d</result>
                </response>""" % {'txn_id':txn_id,
                                  'transaction_id':prv_tnx,
                                  'result':error[0]}
        else: # error
            response = \
            u"""<?xml version="1.0" encoding="UTF-8"?>
                <response>
                  <txn_id>%(txn_id)s</txn_id>
                  <prv_txn>%(transaction_id)s</prv_txn>
                  <result>%(result)d</result>
                  <comment>%(comment)s</comment>
                </response>""" % {'txn_id':txn_id,
                                  'transaction_id':prv_tnx,
                                  'result':error[0],
                                  'comment':error[1]}
        return (response, error)
    
    
    def cancel(self):
        resp = self.get_callback('cancel')()
        prv_txn = resp['transaction_id']
        error = self.error(resp['error_code'])
        if not self.is_error(error[0]):
            response = \
            u"""<?xml version="1.0" encoding="UTF-8"?>
                     <response>
                        <prv_txn>%(prv_txn)s</prv_txn>
                        <result>%(result)d</result>
                     </response>"""%{'prv_txn':prv_txn, 'result':error[0],}
        else:
            response = \
            u"""<?xml version="1.0" encoding="UTF-8"?>
                     <response>
                       <prv_txn>%(prv_txn)s</prv_txn>
                       <result>%(result)d</result>
                       <comment>%(comment)s</comment>
                      </response>""" %{'prv_txn':prv_txn, 'result':error[0], 'comment':error[1],}
        return (response, error)
    
    def verify(self):
        error = self.error(1)
        response = \
        u"""
            <?xml version="1.0" encoding="UTF-8"?>
                <response>
                    <result>%(error)d</result>
                      <comment>%(comment)s</comment>
                </response>
          """ %{'error':error[0], 'comment':error[1]}
        return (response, error)
    
    def status(self):
        resp = self.get_callback('status')()
        error = self.error(resp['error_code'])
        ballance = resp['balance']
        if not self.is_error(error[0]):
            response = \
            u"""
            <?xml version="1.0" encoding="UTF-8"?>
                <response>
                  <result>%(error)d</result>
                  <balance>%(balance).02f</balance>
                </response>"""% {'error':error[0], 'balance':ballance}
        else:
            response = \
            u"""
            <?xml version="1.0" encoding="UTF-8"?>
                <response>
                  <result>%(error)d</result>
                  <comment>%(comment)s</comment>
                </response>""" % {'error':error[0], 'comment':error[1]}
        return (response, error)
# -*- coding: utf-8 -*-

import logging

from sendsms.base import BaseSmsBackend
from sendsms.utils import get_backend_settings
from tasks import iqsmsru_get


logger = logging.getLogger(__name__)


class SmsBackend(BaseSmsBackend):
    """
    http_username
    http_password
    from_phone
    format: txt
    """
    name = 'sendsms.backends.iqsmsru'
    SEND_ADDR = 'http://gate.iqsms.ru/send/'

    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self.login = get_backend_settings(self.name).get('LOGIN')
        self.password = get_backend_settings(self.name).get('PASSWORD')

        self.sender = get_backend_settings(self.name).get('SENDER')
        self.flash = get_backend_settings(self.name).get('FLASH')

    def send_message(self, message):
        parameters = {
            'login': self.login,
            'password': self.password,
            'flash': self.flash,
            'phone': message.to,
            'text': message.body,  # .encode('utf-8'),
        }

        resp = iqsmsru_get.delay(self.SEND_ADDR, parameters, id=message.id)

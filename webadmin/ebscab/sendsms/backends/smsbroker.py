# -*- coding: utf-8 -*-

import datetime
import logging

from sendsms.utils import get_backend_settings
from tasks import smsbroker_post

from .base import BaseSmsBackend


logger = logging.getLogger(__name__)


class SmsBackend(BaseSmsBackend):
    name = 'sendsms.backends.smsbroker'
    SEND_ADDR = 'http://transport.wsoft.ru'

    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self.login = get_backend_settings(self.name).get('LOGIN')
        self.password = get_backend_settings(self.name).get('PASSWORD')
        self.service_number = \
            get_backend_settings(self.name).get('SERVICE_NUMBER')
        self.operator = get_backend_settings(self.name).get('OPERATOR')
        self.validity_period = \
            get_backend_settings(self.name).get('VALIDITY_PERIOD')
        self.priority = get_backend_settings(self.name).get('PRIORITY')

    def send_message(self, message):
        now = datetime.datetime.now()

        parameters = {
            'login': self.login,
            'password': self.password,
            'service_number': self.service_number,
            'msisdn': message.to,
            'content': message.body,  # .encode('utf-8'),
            'ref-id': now.strftime('%Y-%m-%d %H:%M:%S'),
            'validity_period': self.validity_period,
            'priority': self.priority,
        }

        template = """\
<?xml version="1.0" encoding="UTF-8"?>
<bulk-request login="%(login)s" password="%(password)s" ref-id="%(ref-id)s" delivery-notification-requested="true" version="1.0">
<message id="1"
         msisdn="%(msisdn)s"
         service-number="%(service_number)s"
         defer-date="%(ref-id)s"
         validity-period="%(validity_period)s"
         priority="%(priority)s">
    <content type="text/plain">%(content)s</content>
</message>
</bulk-request>"""
        content = template % parameters

        resp = smsbroker_post.delay(self.SEND_ADDR, content, id=message.id)

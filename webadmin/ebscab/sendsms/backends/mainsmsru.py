# -*- coding: utf-8 -*-

import logging

from sendsms.utils import get_backend_settings
from tasks import sendmainsmsru_post

from .base import BaseSmsBackend


logger = logging.getLogger(__name__)


class SmsBackend(BaseSmsBackend):
    name = 'sendsms.backends.mainsmsru'
    SEND_ADDR = 'http://mainsms.ru/api/mainsms/message/send'

    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self.project = get_backend_settings(self.name).get('PROJECT')
        self.sender = get_backend_settings(self.name).get('SENDER')
        self.apikey = get_backend_settings(self.name).get('APIKEY')
        self.test = get_backend_settings(self.name).get('TEST')

    def send_message(self, message):

        parameters = {
            'apikey': self.api_id,
            'project': self.project,
            'test': self.test,
            'sender': self.from_name,
            'recipients': message.to.replace('+', ''),
            'message': message.body.encode('utf-8'),

        }

        resp = sendmainsmsru_post.delay(
            self.SEND_ADDR, parameters, id=message.id)

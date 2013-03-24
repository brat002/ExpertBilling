#-*- coding: UTF-8 -*-

from .base import BaseSmsBackend

from _functools import partial
import io
import urllib
import urllib2
from sendsms.utils import get_backend_settings
import ConfigParser

from tasks import sendsmsru_post
import BeautifulSoup
import logging
import io
# Get an instance of a logger
logger = logging.getLogger(__name__)

# http_username
# http_password
# from_phone
# format: txt

class SmsBackend(BaseSmsBackend):
    name='sendsms.backends.smsru'
    SEND_ADDR = 'http://sms.ru/sms/send'
    
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self.api_id = get_backend_settings(self.name).get('API_ID')
        self.from_name = get_backend_settings(self.name).get('FROM_NAME')
        self.translit = get_backend_settings(self.name).get('TRANSLIT')
        self.test = get_backend_settings(self.name).get('TEST')
        self.partner_id = get_backend_settings(self.name).get('PARTNER_ID')


    def send_message(self, message):

        parameters={
                         'api_id': self.api_id,
                         'from': self.from_name,
                         'translit': self.translit,
                         'test': self.test,
                         'to': message.to,
                         'body': message.body.encode('utf-8'),
                         }
        
        resp = sendsmsru_post.delay(self.SEND_ADDR, parameters, id=message.id)

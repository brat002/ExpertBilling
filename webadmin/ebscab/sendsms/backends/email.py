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

from django.core.mail import send_mail



class SmsBackend(BaseSmsBackend):
    name='sendsms.backends.email'
    #SEND_ADDR = 'http://sms.ru/sms/send'
    
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
                         'text': message.body.encode('utf-8'),
                         }
        
        send_mail('Subject here', 'Here is the message.', self.from_name,
                  [message.to, ], fail_silently=False)

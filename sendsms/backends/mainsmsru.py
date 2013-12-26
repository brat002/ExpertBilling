#-*- coding: UTF-8 -*-

from .base import BaseSmsBackend

from _functools import partial
import io
import urllib
import urllib2
from sendsms.utils import get_backend_settings
import ConfigParser

from tasks import sendmainsmsru_post
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
    name='sendsms.backends.mainsmsru'
    SEND_ADDR = 'http://mainsms.ru/api/mainsms/message/send'
    
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self.project = get_backend_settings(self.name).get('PROJECT')
        self.sender = get_backend_settings(self.name).get('SENDER')
        self.apikey = get_backend_settings(self.name).get('APIKEY')
        self.test = get_backend_settings(self.name).get('TEST')



    def send_message(self, message):

        parameters={
                         'apikey': self.api_id,
                         'project': self.project,
                         'test': self.test,
                         'sender': self.from_name,
                         'recipients': message.to.replace('+', ''),
                         'message': message.body.encode('utf-8'),

                         }
        
        resp = sendmainsmsru_post.delay(self.SEND_ADDR, parameters, id=message.id)

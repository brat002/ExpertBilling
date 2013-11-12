#-*- coding: UTF-8 -*-

from .base import BaseSmsBackend

from _functools import partial
import io
import urllib
import urllib2
from sendsms.utils import get_backend_settings
import ConfigParser

from tasks import sendsmspilotru_post
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
    name='sendsms.backends.smspilotru'
    SEND_ADDR = 'http://smspilot.ru/api2.php'
    
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self.api_id = get_backend_settings(self.name).get('API_ID')
        self.from_name = get_backend_settings(self.name).get('FROM_NAME')



    def send_message(self, message):

        parameters={
                         'apikey': self.api_id,
                         'send':
                             [{
                             'from': self.from_name,
                             'to': message.to.replace('+', ''),
                             'text': message.body.encode('utf-8'),
                             }]
                         }
        
        resp = sendsmspilotru_post.delay(self.SEND_ADDR, parameters, id=message.id)

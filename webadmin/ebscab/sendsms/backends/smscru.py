#-*- coding: UTF-8 -*-

from .base import BaseSmsBackend

from _functools import partial
import io
import urllib
import urllib2
from sendsms.utils import get_backend_settings
import ConfigParser

from tasks import sendsmscru_post
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
    name='sendsms.backends.smscru'
    SEND_ADDR = 'http://smsc.ru/sys/send.php'
    
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self.login = get_backend_settings(self.name).get('LOGIN')
        self.password = get_backend_settings(self.name).get('PASSWORD')
        
        self.sender = get_backend_settings(self.name).get('SENDER')
        self.flash = get_backend_settings(self.name).get('FLASH')
        
        self.translit = get_backend_settings(self.name).get('TRANSLIT')



    def send_message(self, message):

        parameters={
                         'login': self.login,
                         'psw': self.password,
                         'translit': self.translit,
                         'flash': self.flash,
                         'phones': message.to,
                         'mes': message.body, #.encode('utf-8'),
                         }
        
        resp = sendsmscru_post.delay(self.SEND_ADDR, parameters, id=message.id)

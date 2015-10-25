#-*- coding: UTF-8 -*-

from .base import BaseSmsBackend

from _functools import partial
import io
import urllib
import urllib2
from sendsms.utils import get_backend_settings
import ConfigParser

from tasks import sendsms_post
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
    name='sendsms.backends.websms'
    SEND_ADDR = 'http://websms.ru/xml_in5.asp'
    
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self.username = get_backend_settings(self.name).get('USERNAME')
        self.password = get_backend_settings(self.name).get('PASSWORD')
        self.from_name = get_backend_settings(self.name).get('FROM_NAME')


    def send_message(self, message):

        send_template = (u"""<message>
        <service id="single" login="%(LOGIN)s" password="%(PASSWORD)s" source="%(DEFAULT_FROM)s" uniq_key="%(ID)s" />
        <to>%(TO)s</to><body>%(BODY)s</body>
        </message>""" % {
                         'LOGIN': self.username,
                         'PASSWORD': self.password,
                         'DEFAULT_FROM': self.from_name,
                         'ID': message.id,
                         'TO': message.to,
                         'BODY': message.body,
                         }).encode('utf-8')
        
        resp = sendsms_post.delay(self.SEND_ADDR, send_template, id=message.id)

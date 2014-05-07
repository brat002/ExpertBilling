#-*- coding: UTF-8 -*-

from .base import BaseSmsBackend

from _functools import partial
import io
import urllib
import urllib2
import base64
from sendsms.utils import get_backend_settings
import ConfigParser

from tasks import sendsmsfly_post
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
    name='sendsms.backends.smsfly'
    SEND_ADDR = 'http://sms-fly.com/api/api.php'
    
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self.username = get_backend_settings(self.name).get('USERNAME')
        self.password = get_backend_settings(self.name).get('PASSWORD')
        self.from_name = get_backend_settings(self.name).get('FROM_NAME')

    def send_message(self, message):
        request = urllib2.Request(self.SEND_ADDR)
        print self.username
        print self.password
        print self.from_name
        request.add_header('Authorization', b'Basic ' + base64.b64encode(self.username + b':' + self.password))
        send_template = (u"""<?xml version="1.0" encoding="utf-8"?>
        <request>
        <operation>SENDSMS</operation>
        <message start_time="AUTO" end_time="AUTO" livetime="24" rate="120" desc="ebs" source="%(DEFAULT_FROM)s">
        <body>%(BODY)s</body>
        <recipient>%(TO)s</recipient>
        </message>
        </request>""" % {
                         'DEFAULT_FROM': self.from_name,
                         'BODY': message.body,
                         'TO': message.to,
                         }).encode('utf-8')
        
        resp = sendsmsfly_post.delay(request, send_template, id=message.id)

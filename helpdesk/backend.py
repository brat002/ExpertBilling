 #-*- coding=UTF-8 -*-
from django.contrib.auth.backends import ModelBackend

from billservice.models import SystemUser


class LoginSystemUserBackend(object):
    def authenticate(self, username=None, password=None):
        try:
            user = SystemUser.objects.get(username=username, password=password)
            return user
        except:
            pass
        return None
    
    def get_user(self, user_id):
        try:
            return SystemUser.objects.get(id=user_id)
        except:
            return None
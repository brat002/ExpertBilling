 #-*- coding=UTF-8 -*-
from django.contrib.auth.backends import ModelBackend

from billservice.models import Account


class LoginUserBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = Account.objects.get(username=username, password=password)
            return user
        except:
            pass
        return None
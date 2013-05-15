#-*- coding=utf-8 -*-
from django.db import models
from jsonfield import JSONField
from django.contrib.auth.models import User

class TableSettings(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=128)
    value = JSONField()
    
    
from django.db.models.signals import class_prepared

def longer_username(sender, *args, **kwargs):
    # You can't just do `if sender == django.contrib.auth.models.User`
    # because you would have to import the model
    # You have to test using __name__ and __module__
    if sender.__name__ == "User" and sender.__module__ == "django.contrib.auth.models":
        sender._meta.get_field("username").max_length = 256
        sender._meta.get_field("first_name").max_length = 256
        sender._meta.get_field("last_name").max_length = 256
        sender._meta.get_field("email").max_length = 256

class_prepared.connect(longer_username)

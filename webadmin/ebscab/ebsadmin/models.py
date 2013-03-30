#-*- coding=utf-8 -*-
from django.db import models
from jsonfield import JSONField
from django.contrib.auth.models import User

class TableSettings(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=128)
    value = JSONField()
    
    

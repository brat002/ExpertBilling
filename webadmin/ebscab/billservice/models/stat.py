# -*- coding: utf-8 -*-

from django.db import models


class GroupStat(models.Model):
    group = models.ForeignKey('billservice.Group', on_delete=models.CASCADE)
    account = models.ForeignKey(
        'billservice.Account', on_delete=models.CASCADE)
    bytes = models.IntegerField()
    datetime = models.DateTimeField()


class GlobalStat(models.Model):
    account = models.ForeignKey(
        'billservice.Account', on_delete=models.CASCADE)
    bytes_in = models.BigIntegerField()
    bytes_out = models.BigIntegerField()
    datetime = models.DateTimeField()

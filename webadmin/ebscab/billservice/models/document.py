# -*- coding: utf-8 -*-

from django.db import models


class Document(models.Model):
    account = models.ForeignKey(
        'billservice.Account', blank=True, null=True, on_delete=models.CASCADE)
    type = models.ForeignKey(
        'billservice.Template',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    body = models.TextField()
    contractnumber = models.CharField(max_length=1024)
    date_start = models.DateTimeField(blank=True)
    date_end = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return u"%s %s" % (self.type, self.date_start)


class DocumentType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']

from django.db import models
from billservice.models import Account

class Invoice(models.Model):
    txn_id = models.CharField(max_length=64, blank=True, null=True)# qiwi transaction id
    account = models.ForeignKey(Account)
    phone = models.CharField(max_length=15)
    summ = models.DecimalField(decimal_places=10, max_digits=60)
    password = models.CharField(max_length=512)
    autoaccept= models.BooleanField(default=False)
    created = models.DateTimeField(blank=True, null=True)
    lifetime = models.IntegerField(blank=True, null=True)
    check_after = models.IntegerField(blank=True, null=True)
    accepted = models.BooleanField(default=False)
    date_accepted = models.DateTimeField(blank=True, null=True)
    
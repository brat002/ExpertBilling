# -*- coding: utf-8 -*-

from django.dispatch import receiver

from billservice.models import new_transaction


@receiver(new_transaction)
def notification_sender(sender, **kwargs):
    pass

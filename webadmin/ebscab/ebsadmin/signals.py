from billservice.models import new_transaction
from django.dispatch import receiver


@receiver(new_transaction)
def notification_sender(sender, **kwargs):
    print 123
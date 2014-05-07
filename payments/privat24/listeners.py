from getpaid import signals

def payment_status_changed_listener(sender, instance, old_status, new_status, **kwargs):
    """
    Here we will actually do something, when payment is accepted.
    E.g. lets change an order status.
    """
    if instance.backend!='payments.privat24': return
    if old_status != 'paid' and new_status == 'paid':
        # Ensures that we process order only one
        if not instance.order:
            cls = instance.ORDER_MODEL
            cls.create_payment(account=instance.account, summ=instance.amount_paid, created=instance.paid_on, bill=instance.external_id, trtype=instance.backend)
            
    if old_status == 'paid' and new_status == 'canceled':
        # Ensures that we process order only one
        if instance.order:
            order = instance.order
            order.delete()
            instance.order=None
            instance.save()
            
            
            
        #instance.order.save()

signals.payment_status_changed.connect(payment_status_changed_listener)

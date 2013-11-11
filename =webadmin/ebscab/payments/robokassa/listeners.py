from getpaid import signals

def payment_status_changed_listener(sender, instance, old_status, new_status, **kwargs):
    """
    Here we will actually do something, when payment is accepted.
    E.g. lets change an order status.
    """
    if instance.backend!='payments.w1ru': return
    if old_status != 'paid' and new_status == 'paid':
        # Ensures that we process order only one
        if not instance.order:
            instance.amount_paid = instance.amount
            instance.paid_on = instance.created_on
            instance.save()
            cls = instance.ORDER_MODEL
            cls.create_payment(account=instance.account, summ=instance.amount_paid, created=instance.paid_on, bill=instance.external_id, trtype=instance.backend)
            

            
            
            
        #instance.order.save()

signals.payment_status_changed.connect(payment_status_changed_listener)

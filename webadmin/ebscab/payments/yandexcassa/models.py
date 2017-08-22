# -*- coding: utf-8 -*-


def build_models(payment_class):
    """
    Here you can dynamically build a Model class that needs to have ForeignKey to Payment model
    """
    return []


class PAYMENT_TYPE:
    PC = 'pc'
    AC = 'ac'
    GP = 'gp'
    MC = 'mc'

    CHOICES = (
        (PC, u'Яндекс.Деньги'),
        (AC, u'Банковская карта'),
        (GP, u'По коду через терминал'),
        (MC, u'со счета мобильного телефона')
    )

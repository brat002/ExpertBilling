# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _


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
        (PC, _(u'Яндекс.Деньги')),
        (AC, _(u'Банковская карта')),
        (GP, _(u'По коду через терминал')),
        (MC, _(u'со счета мобильного телефона'))
    )

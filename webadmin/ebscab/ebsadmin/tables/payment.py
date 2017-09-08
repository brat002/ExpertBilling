# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from django_tables2.columns import LinkColumn
from django_tables2.utils import A
from getpaid.models import Payment

from ebsadmin.columns import modallinkcolumn, showconfirmcolumn
from ebsadmin.tables.base import EbsadminTableReport


class PaymentTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='payment_edit',
        modal_title=_(u'Изменить платёж'),
        modal_id='payment-modal'

    )
    account = LinkColumn(
        'account_edit',
        verbose_name=_(u'Аккаунт'),
        get_params={'id': A('account.id')}
    )
    d = showconfirmcolumn(message=_(u'Внимание. Удаление платежа может '
                                    u'вызвать нежелательные последствия при '
                                    u'перетарификации. Если вы не уверены в '
                                    u'своих действиях - лучше откажитесь от '
                                    u'удаления.'))

    class Meta(EbsadminTableReport.Meta):
        model = Payment

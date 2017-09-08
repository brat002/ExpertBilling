# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from django_tables2.columns import LinkColumn
from django_tables2.utils import A
from sendsms.models import Message

from ebsadmin.columns import showconfirmcolumn
from ebsadmin.tables.base import EbsadminTableReport


class MessageTable(EbsadminTableReport):
    account = LinkColumn(
        'account_edit',
        verbose_name=_(u'Аккаунт'),
        get_params={
            'id': A('account.id')
        }
    )
    d = showconfirmcolumn(message=_(u'Удалить SMS сообщение?'))

    class Meta(EbsadminTableReport.Meta):
        model = Message

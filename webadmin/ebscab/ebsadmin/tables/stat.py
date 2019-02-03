# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from django_tables2.columns import Column, TemplateColumn
from django_tables2.utils import A

from ebsadmin.tables.base import EbsadminTableReport


class GroupStatTable(EbsadminTableReport):
    account = Column(
        _(u'Аккаунт'), accessor=A('account__username'))
    group = Column(_(u'Группа'), accessor=A('group__name'))
    bytes = TemplateColumn(
        "{{record.summ_bytes|filesizeformat}}({{record.summ_bytes}})",
        verbose_name=_(u'Сумма'),
        accessor=A('summ_bytes')
    )

    class Meta(EbsadminTableReport.Meta):
        available_fields = ('account', 'group', 'bytes')
        configurable = True


class GlobalStatTable(EbsadminTableReport):
    account = Column(
        _(u'Аккаунт'), accessor=A('account__username'))
    bytes_in = TemplateColumn(
        "{{record.bytes_in|filesizeformat}}({{record.bytes_in}})",
        verbose_name=_(u'ВХ'))
    bytes_out = TemplateColumn(
        "{{record.bytes_out|filesizeformat}}({{record.bytes_out}})",
        verbose_name=_(u'ИСХ'))
    max = Column(_(u'Последние данные'))

    class Meta(EbsadminTableReport.Meta):
        available_fields = ('account', 'group', 'bytes')
        configurable = False

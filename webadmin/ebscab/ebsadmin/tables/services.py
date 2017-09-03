# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from billservice.models import (
    AccountAddonService,
    AddonService,
    OneTimeService,
    PeriodicalService
)
from django_tables2.columns import Column, LinkColumn, TemplateColumn
from django_tables2.utils import A

from ebsadmin.columns import (
    FormatDateTimeColumn,
    modallinkcolumn,
    showconfirmcolumn
)
from ebsadmin.tables.base import EbsadminTable, EbsadminTableReport


class AddonServiceTable(EbsadminTableReport):
    id = LinkColumn(
        'addonservice_edit', get_params={'id': A('pk')})
    name = LinkColumn(
        'addonservice_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = AddonService
        configurable = True


class OneTimeServiceTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='onetimeservice_edit',
        modal_title=_(u'Периодическая услуга'),
        modal_id='periodicalservice-modal'
    )
    name = modallinkcolumn(
        url_name='onetimeservice_edit',
        modal_title=_(u'Периодическая услуга'),
        modal_id='periodicalservice-modal'
    )
    d = showconfirmcolumn(message=_(u'Удалить? Удаление разовой услуги '
                                    u'вызовет обнуление информации о '
                                    u'списаниях по ней. Вместо этого '
                                    u'рекомемендуется воспользоваться '
                                    u'отключением услуги.'))

    class Meta(EbsadminTableReport.Meta):
        model = OneTimeService
        fields = ("id", 'name', 'cost', 'd')


class PeriodicalServiceTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_periodicalservice_edit',
        modal_title=_(u'Периодическая услуга'),
        modal_id='periodicalservice-modal'
    )
    name = modallinkcolumn(
        url_name='tariff_periodicalservice_edit',
        modal_title=_(u'Периодическая услуга'),
        modal_id='periodicalservice-modal'
    )
    d = showconfirmcolumn(message=_(u'Удалить? Удаление периодической услуги '
                                    u'вызовет обнуление информации о '
                                    u'списаниях по ней. '
                                    u'Вместо этого рекомемендуется '
                                    u'воспользоваться отключением услуги.'))
    created = FormatDateTimeColumn()
    deactivated = FormatDateTimeColumn()

    class Meta(EbsadminTableReport.Meta):
        model = PeriodicalService
        fields = (
            "id",
            'name',
            'settlement_period',
            'cost',
            'cash_method',
            'ps_condition',
            'condition_summ',
            'created',
            'deactivated'
        )


class AccountAddonServiceTable(EbsadminTable):
    id = LinkColumn(
        'accountaddonservice',
        get_params={
            'id': A('pk')
        },
        attrs={
            'a': {
                'rel': "alert3",
                'class': "open-custom-dialog"
            }
        }
    )
    service = Column()
    subaccount = LinkColumn(
        'subaccount',
        get_params={
            'id': A('subaccount.id')
        },
        attrs={
            'a': {
                'rel': "alert3",
                'class': "open-custom-dialog"
            }
        }
    )
    cost = TemplateColumn(
        '{{record.cost|default:record.service.cost|floatformat}}')
    activated = FormatDateTimeColumn()
    deactivated = FormatDateTimeColumn()
    deactivate = showconfirmcolumn(
        href='{{record.get_deactivate_url}}',
        message='Отключить подклюачемую услугу?',
        verbose_name='Отключить',
        icon_type='icon-ban-circle')
    d = showconfirmcolumn()

    class Meta(EbsadminTable.Meta):
        model = AccountAddonService
        fields = (
            'id',
            'service',
            'subaccount',
            'cost',
            'activated',
            'deactivated',
            'deactivate',
            'd'
        )

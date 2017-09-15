# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from billservice.models import (
    AddonServiceTarif,
    NotificationsSettings,
    Tariff,
    TimeAccessNode,
    TimeSpeed,
    TPChangeRule
)
from django_tables2.columns import Column, LinkColumn, TemplateColumn
from django_tables2.utils import A
from django_tables2_reports.tables import TableReport

from ebsadmin.columns import (
    FormatBlankColumn,
    FormatDateTimeColumn,
    modallinkcolumn,
    showconfirmcolumn
)
from ebsadmin.tables.base import EbsadminTable, EbsadminTableReport


class TariffTable(EbsadminTableReport):
    name = LinkColumn('tariff_edit', get_params={'id': A('pk')})
    radiusattrs = TemplateColumn(
        u'''\
<a href='{% url 'radiusattr' %}?tarif={{record.id}}' \
class='btn btn-mini btn-primary'>Изменить</a>''',
        verbose_name=_(u'RADIUS атрибуты'),
        orderable=False
    )
    access_type = FormatBlankColumn(
        verbose_name=_(u'Тип доступа'),
        accessor=A('access_parameters.access_type')
    )
    accounts_count = TemplateColumn(
        u'''\
<a href='{% url 'account_list' %}?tariff={{record.id}}' \
class='btn btn-mini'>{{record.accounts_count}} \
<i class='icon-arrow-right'></i></a>''',
        verbose_name=_(u'Аккаунтов')
    )
    delete = showconfirmcolumn(
        href='{{record.get_hide_url}}',
        message=_(u'Скрыть?'),
        verbose_name=_(u'Скрыть'),
        icon_type='icon-ban-circle'
    )

    class Meta(EbsadminTableReport.Meta):
        model = Tariff
        configurable = True
        available_fields = (
            'name',
            'settlement_period',
            'cost',
            'access_type',
            'reset_tarif_cost',
            'accounts_count',
            'radiusattrs',
            'delete'
        )


class AccountTarifTable(EbsadminTable):
    id = FormatBlankColumn()
    tarif = FormatBlankColumn()
    datetime = FormatDateTimeColumn()
    d = showconfirmcolumn()

    class Meta(EbsadminTable.Meta):
        pass


class AddonServiceTarifTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_addonservicetariff_edit',
        modal_title=_(u'Подключаемая услуга'),
        modal_id='periodicalservice-modal'
    )
    d = showconfirmcolumn(message=_(u'Вы действительно хотите удалить '
                                    u'правило активации подключаемых услуг?'))

    class Meta(EbsadminTableReport.Meta):
        model = AddonServiceTarif
        fields = (
            "id",
            'service',
            'activation_count_period',
            'activation_count',
            'type',
            'd'
        )


class TPChangeRuleTable(EbsadminTableReport):
    id = LinkColumn(
        'tpchangerule_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn(message='Удалить правило?')
    settlement_period = FormatBlankColumn(verbose_name=_(u'Расчётный период'))
    on_next_sp = TemplateColumn(
        "<img src='/media/img/icons/{% if record.on_next_sp %}accept.png"
        "{% else %}icon_error.gif{% endif %}'>")
    row_class = Column(visible=False)

    def render_row_class(self, value, record):
        return 'error' if record.disabled else ''

    class Meta(EbsadminTableReport.Meta):
        model = TPChangeRule
        configurable = True
        available_fields = (
            "id",
            'row_class',
            'from_tariff',
            'to_tariff',
            'cost',
            'ballance_min',
            'on_next_sp',
            'settlement_period',
            'disabled',
            'd'
        )


class NotificationsSettingsTable(TableReport):
    id = LinkColumn(
        'notificationssettings_edit', get_params={'id': A('pk')})
    name = LinkColumn(
        'notificationssettings_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn()

    def __init__(self, *args, **argv):
        super(NotificationsSettingsTable, self).__init__(*args, **argv)
        self.name = self.__class__.__name__

    class Meta:
        model = NotificationsSettings
        available_fields = ("id", 'name', 'd', )
        attrs = {
            'class': 'table table-bordered table-condensed'
        }


class TimeSpeedTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_timespeed_edit',
        modal_title=_(u'Правило изменения скорости'),
        modal_id='timespeed-modal'
    )
    d = showconfirmcolumn(
        message=_(u'Удалить? Вы уверены, что хотите удалить строку?'))

    class Meta(EbsadminTableReport.Meta):
        model = TimeSpeed
        fields = (
            'id',
            'time',
            'max_tx',
            'max_rx',
            'burst_tx',
            'burst_rx',
            'burst_treshold_tx',
            'burst_treshold_rx',
            'burst_time_tx',
            'burst_time_rx',
            'min_tx',
            'min_rx',
            'priority'
        )


class TimeAccessNodeTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_timeaccessnode_edit',
        modal_title=_(u'Правило тарификации времени'),
        modal_id='timeaccessnode-modal'
    )
    d = showconfirmcolumn(message=_(u'Удалить правило тарификации времени?'))

    class Meta(EbsadminTableReport.Meta):
        model = TimeAccessNode
        fields = ("id", 'time_period', 'cost', 'd')

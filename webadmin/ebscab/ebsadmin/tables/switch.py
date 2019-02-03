# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from billservice.models import Switch
from django_tables2.columns import LinkColumn, TemplateColumn
from django_tables2.utils import A

from ebsadmin.columns import showconfirmcolumn
from ebsadmin.tables.base import EbsadminTableReport


class SwitchTable(EbsadminTableReport):
    id = LinkColumn('switch_edit', get_params={'id': A('pk')})
    name = LinkColumn('switch_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn(message=_(u'Удалить? Перед удалением коммутатора '
                                    u'убедитесь, что он не используется в '
                                    u'биллинг-системе'))

    class Meta(EbsadminTableReport.Meta):
        model = Switch
        configurable = True
        available_fields = (
            "id",
            'name',
            'manufacturer',
            'model',
            'sn',
            'city',
            'street',
            'place'
        )


class SwitchPortsTable(EbsadminTableReport):
    port = TemplateColumn(
        "<input type='hidden' name='port' value='{{record.port}}'>{{record.port}}",
        verbose_name=_(u'Порт')
    )
    broken_port = TemplateColumn(
        "<input type='checkbox' name='broken_port' "
        "{% if record.broken_port %} checked{% endif %}>",
        verbose_name=_(u'Битый')
    )
    uplink_port = TemplateColumn(
        "<input type='checkbox'  name='uplink_port' "
        "{% if record.uplink_port %} checked{% endif %}>",
        verbose_name=_(u'Аплинк')
    )
    protected_port = TemplateColumn(
        "<input type='checkbox'  name='protected_port' "
        "{% if record.protected_port %} checked{% endif %}>",
        verbose_name=_(u'Защита')
    )
    monitored_port = TemplateColumn(
        "<input type='checkbox'  name='monitored_port' "
        "{% if record.monitored_port %} checked{% endif %}>",
        verbose_name=_(u'Мониторинг')
    )
    disabled_port = TemplateColumn(
        "<input type='checkbox'  name='disabled_port' "
        "{% if record.disabled_port %} checked{% endif %}>",
        verbose_name=_(u'Отключён')
    )

    class Meta(EbsadminTableReport.Meta):
        pass

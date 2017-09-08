# -*- coding: utf-8 -*-

import itertools

from django.utils.translation import ugettext_lazy as _

from billservice.models import (
    AccountPrepaysRadiusTrafic,
    AccountPrepaysTime,
    AccountPrepaysTrafic,
    Group,
    PrepaidTraffic,
    RadiusTrafficNode,
    TrafficLimit,
    TrafficTransmitNodes
)
from django_tables2.columns import (
    CheckBoxColumn,
    Column,
    LinkColumn,
    TemplateColumn
)
from django_tables2.utils import A
from nas.models import TrafficClass, TrafficNode

from ebsadmin.columns import (
    FormatDateTimeColumn,
    modallinkcolumn,
    showconfirmcolumn
)
from ebsadmin.tables.base import EbsadminTableReport


class TrafficClassTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='trafficclass_edit',
        modal_title=_(u'Изменить класс'),
        modal_id='trafficclass-modal'
    )
    name = modallinkcolumn(
        url_name='trafficclass_edit',
        modal_title=_(u'Изменить класс'),
        modal_id='trafficclass-modal'
    )
    directions = TemplateColumn(
        u'''\
<a href='{% url 'trafficnode_list' %}?id={{record.id}}' \
class='btn btn-primary btn-mini'>Список направлений</a>''',
        verbose_name=_(u'Направления'),
        orderable=False
    )
    d = TemplateColumn(
        '''\
<a href='{{record.get_remove_url}}' class='show-confirm' \
data-clickmessage='Удалить?'>
<i class='icon-remove'></i></a><input type='hidden' name='id' \
value='{{record.id}}'>''',
        verbose_name=' ',
        orderable=False
    )

    class Meta(EbsadminTableReport.Meta):
        model = TrafficClass
        configurable = True
        available_fields = ('id', 'name', 'passthrough', 'directions', 'd')


class TrafficNodeTable(EbsadminTableReport):
    row_number = Column(
        verbose_name="#", empty_values=(), orderable=False)
    id = modallinkcolumn(
        url_name='trafficnode',
    )
    d = CheckBoxColumn(
        verbose_name=' ', orderable=False, accessor=A('pk'))

    def __init__(self, *args, **kwargs):
        super(TrafficNodeTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()

    def render_row_number(self):
        return '%d' % next(self.counter)

    class Meta(EbsadminTableReport.Meta):
        model = TrafficNode
        configurable = True
        exclude = ("traffic_class", )
        available_fields = (
            'row_number',
            'id',
            'name',
            'protocol',
            'src_port',
            'in_index',
            'src_ip',
            'dst_ip',
            'dst_port',
            'out_index',
            'src_as',
            'dst_as',
            'next_hop',
            'd'
        )


class UploadTrafficNodeTable(EbsadminTableReport):
    row_number = Column(
        verbose_name="#", empty_values=(), orderable=False)
    src_net = Column(verbose_name="Src Net")
    dst_net = Column(verbose_name="Dst Net")
    direction = Column(verbose_name="Direction")

    def __init__(self, *args, **kwargs):
        super(UploadTrafficNodeTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()

    def render_row_number(self):
        return '%d' % next(self.counter)

    class Meta(EbsadminTableReport.Meta):
        fields = ('row_number', 'src_net', 'dst_net')


class TrafficLimitTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_trafficlimit_edit',
        modal_title=_(u'Лимит трафика'),
        modal_id='periodicalservice-modal'
    )
    d = showconfirmcolumn(message='Удалить лимит трафика?')
    speedlimit = TemplateColumn(
        '''\
<a href='{% url 'tariff_speedlimit_edit' %}?trafficlimit_id={{record.id}}' \
class='open-speedlimit-dialog' data-dlgtitle='Правило изменения скорости' \
data-dlgid='speedlimit-modal'>
{% if record.speedlimit %}{{record.speedlimit}}
<a href='{{record.speedlimit.get_remove_url}}' \
class='show-speedlimit-confirm' data-clickmessage='Удалить? Если в лимите \
трафика указано действие Изменить скорость - вы обязаны указать параметры \
изменения скорости.'>
<i class='icon-remove'></i></a>{% else %}Указать{% endif %}</a>''',
        verbose_name='Изменить скорость',
        orderable=False
    )

    class Meta(EbsadminTableReport.Meta):
        model = TrafficLimit
        fields = (
            "id",
            'name',
            'settlement_period',
            'mode',
            'group',
            'size',
            'action',
            'speedlimit',
            'd'
        )


class TrafficTransmitNodesTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_traffictransmitnode_edit',
        modal_title=_(u'Правило начисления предоплаченного трафика'),
        modal_id='periodicalservice-modal'
    )
    group = LinkColumn(
        'group_edit', get_params={'id': A('group.id')})
    d = showconfirmcolumn(
        message=_(u'Удалить? Вы уверены, что хотите удалить запись?'))

    class Meta(EbsadminTableReport.Meta):
        model = TrafficTransmitNodes
        fields = ('id', 'timeperiod', 'group', 'cost', 'd')


class GroupTable(EbsadminTableReport):
    id = LinkColumn('group_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn(message=_(u'Удалить? Удаление группы трафика '
                                    u'вызовет её удаление во всех тарифных '
                                    u'планах.'))

    class Meta(EbsadminTableReport.Meta):
        model = Group


class AccountPrepaysTraficTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='accountprepaystraffic_edit',
        modal_title=_(u'Изменить значения')
    )
    account_tarif = Column(_(u'Аккаунт/Тариф'))
    prepaid_traffic = TemplateColumn(
        "{{record.prepaid_traffic.size|filesizeformat}}"
        "({{record.prepaid_traffic.size}})",
        verbose_name=_(u'Начислено')
    )
    size = TemplateColumn(
        "{{record.size|filesizeformat}}({{record.size}})",
        verbose_name=_(u'Остаток')
    )
    progress = TemplateColumn(
        """\
<div class="progress progress-success">
    <div class="bar" style="width: {{record.in_percents}}%"></div>
</div>""",
        verbose_name=_(u'Осталось')
    )
    datetime = FormatDateTimeColumn(verbose_name=_(u'Начислен'))

    def render_bytes(self, value, record):
        return value

    class Meta(EbsadminTableReport.Meta):
        model = AccountPrepaysTrafic
        configurable = True


class AccountPrepaysRadiusTraficTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='accountprepaystraffic_edit',
        modal_title=_(u'Изменить значения')
    )
    account_tarif = Column(_(u'Аккаунт/Тариф'))
    size = TemplateColumn(
        "{{record.size|filesizeformat}}({{record.size}})",
        verbose_name=_(u'Остаток')
    )
    datetime = FormatDateTimeColumn(verbose_name=_(u'Начислен'))
    progress = TemplateColumn(
        """\
<div class="progress progress-success">
    <div class="bar" style="width: {{record.in_percents}}%"></div>
</div>""",
        verbose_name=_(u'Расходовано')
    )

    def render_bytes(self, value, record):
        return value

    class Meta(EbsadminTableReport.Meta):
        model = AccountPrepaysRadiusTrafic
        configurable = True


class PrepaidTrafficTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_prepaidtraffic_edit'
    )
    group = LinkColumn(
        'group_edit', get_params={'id': A('group.id')})
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = PrepaidTraffic
        fields = ("id", 'group', 'size', 'd')


class RadiusTrafficNodeTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='tariff_radiustrafficnode_edit',
        modal_title=_(u'Правило тарификации трафика')
    )
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = RadiusTrafficNode
        fields = ("id", 'value', 'timeperiod', 'cost', 'd')


class AccountPrepaysTimeTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='accountprepaystraffic_edit',
        modal_title=_(u'Изменить тип')
    )
    account_tarif = Column(_(u'Аккаунт/Тариф'))
    datetime = FormatDateTimeColumn(verbose_name=_(u'Начислен'))
    progress = TemplateColumn(
        """\
<div class="progress progress-success">
    <div class="bar" style="width: {{record.in_percents}}%"></div>
</div>""",
        verbose_name=_(u'Расходовано')
    )

    def render_bytes(self, value, record):
        return value

    class Meta(EbsadminTableReport.Meta):
        model = AccountPrepaysTime
        configurable = True

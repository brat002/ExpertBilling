# -*- coding: utf-8 -*-

import itertools

from django.utils.translation import ugettext_lazy as _

from billservice.models import RadiusAttrs
from django_tables2.columns import Column, LinkColumn, TemplateColumn
from django_tables2.utils import A
from nas.models import Nas
from radius.models import ActiveSession

from ebsadmin.columns import (
    FormatDateTimeColumn,
    modallinkcolumn,
    showconfirmcolumn
)
from ebsadmin.tables.base import EbsadminTableReport


class NasTable(EbsadminTableReport):
    name = LinkColumn(
        'nas_edit', verbose_name=_(u"Имя"), get_params={'id': A('pk')})
    radiusattrs = TemplateColumn(
        (u"<a href='{% url 'radiusattr' %}?nas={{record.id}}' "
         u"class='btn btn-mini btn-primary'>Изменить</a>"),
        verbose_name=_(u'RADIUS атрибуты'),
        orderable=False
    )
    id = LinkColumn(
        'nas_edit',
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
    d = showconfirmcolumn(message=_(u'Удалить? Все связанные с сервером '
                                    u'доступа записи будут сброшены на '
                                    u'значение по умолчанию для '
                                    u'выбранной записи'))

    class Meta(EbsadminTableReport.Meta):
        model = Nas
        configurable = True
        available_fields = (
            'id',
            'name',
            'radiusattrs',
            'identify',
            'type',
            'ipaddress'
        )


class RadiusAttrTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='radiusattr_edit',
        modal_title=_(u'Изменить атрибут'),
        modal_id='radiusattr-modal'
    )
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = RadiusAttrs
        exclude = ("tarif", 'nas', 'vendor', 'attrid')


class ActiveSessionTable(EbsadminTableReport):
    row_number = Column(
        verbose_name=u'#', empty_values=(), orderable=False)
    session_status = TemplateColumn(
        "<span class='label {% if record.session_status == 'ACK' %}info"
        "{% endif %}'>{{ record.session_status }}</span>")
    date_start = FormatDateTimeColumn()
    interrim_update = FormatDateTimeColumn(
        verbose_name=_(u'Последнее обновление'))
    caller_id = Column(
        verbose_name=_(u'Caller ID'), empty_values=())
    address = TemplateColumn(
        (u"{{record.account__street|default:''}} "
         u"{{record.account__house|default:''}}-"
         u"{{record.account__room|default:''}}"),
        orderable=False,
        verbose_name=u'Адрес'
    )
    framed_ip_address = Column(
        verbose_name=_(u'IP'), empty_values=())
    framed_protocol = Column(
        verbose_name=_(u'Протокол'), empty_values=())
    session_time = Column(
        verbose_name=_(u'Онлайн'), empty_values=())
    date_end = FormatDateTimeColumn()
    nas_int = Column(
        verbose_name=_(u'NAS'), accessor=A('nas_int__name'))
    bytes = TemplateColumn(
        "{{record.bytes_in|filesizeformat}}/"
        "{{record.bytes_out|filesizeformat}}",
        verbose_name=_(u'Байт'),
        orderable=False
    )
    subaccount__username = LinkColumn(
        'subaccount',
        get_params={
            'id': A('subaccount')
        },
        verbose_name=_(u'Субаккаунт')
    )
    action = TemplateColumn(
        '''\
<button data='{{record.id}}' class='btn btn-success btn-mini sreset' \
title='Soft reset'>R</button>&nbsp;
<button data='{{record.id}}' class='btn btn-danger btn-mini hreset' \
title='Hard reset'>H</button>&nbsp;
<button class='btn btn-info btn-mini ping' title='Ping' \
data='{{record.framed_ip_address}}'>P</button>''',
        verbose_name=_(u'Action')
    )

    def __init__(self, *args, **kwargs):
        super(ActiveSessionTable, self).__init__(*args, **kwargs)
        self.counter = itertools.count()

    def render_row_number(self):
        return '%d' % next(self.counter)

    class Meta(EbsadminTableReport.Meta):
        model = ActiveSession
        configurable = True
        available_fields = (
            'row_number',
            'subaccount__username',
            'date_start',
            'interrim_update',
            'date_end',
            'nas_int',
            'caller_id',
            'framed_ip_address',
            'framed_protocol',
            'session_time',
            'bytes',
            'session_status',
            'action'
        )
        attrs = {
            'class': 'table table-bordered table-condensed'
        }

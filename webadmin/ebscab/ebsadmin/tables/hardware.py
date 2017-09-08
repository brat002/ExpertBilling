# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from billservice.models import (
    AccountHardware,
    Hardware,
    HardwareType,
    Manufacturer,
    Model
)
from django_tables2.columns import LinkColumn
from django_tables2.utils import A

from ebsadmin.columns import showconfirmcolumn, modallinkcolumn
from ebsadmin.tables.base import EbsadminTable, EbsadminTableReport


class HardwareTable(EbsadminTableReport):
    id = LinkColumn('hardware_edit', get_params={'id': A('pk')})
    model = LinkColumn(
        'hardware_edit', get_params={'id': A('pk')})
    name = LinkColumn(
        'hardware_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn(message=_(u'Удалить? Удаление устройства вызовет '
                                    u'удаление всех связаных с ним объектов '
                                    u'в системе.'))

    class Meta(EbsadminTableReport.Meta):
        model = Hardware
        configurable = True


class HardwareTypeTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='hardwaretype_edit',
        modal_title=_(u'Изменить тип'),
        modal_id='hardwaretype-modal'
    )
    name = modallinkcolumn(
        url_name='hardwaretype_edit',
        modal_title=_(u'Изменить тип'),
        modal_id='hardwaretype-modal'
    )
    d = showconfirmcolumn(message=_(u'Удалить? Удаление типа оборудования '
                                    u'вызовёт удаление всех связанных '
                                    u'объектов в системе.'))

    class Meta(EbsadminTableReport.Meta):
        model = HardwareType


class AccountHardwareTable(EbsadminTable):
    id = LinkColumn(
        'accounthardware',
        get_params={'id': A('pk')},
        attrs={
            'a': {
                'rel': "alert3",
                'class': "open-custom-dialog"
            }
        }
    )
    d = showconfirmcolumn()

    class Meta(EbsadminTable.Meta):
        model = AccountHardware
        fields = ('id', 'hardware', 'datetime', 'returned', 'comment')


class ManufacturerTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='manufacturer_edit',
        modal_title=_(u'Изменить название'),
        modal_id='manufacturer-modal'
    )
    name = modallinkcolumn(
        url_name='manufacturer_edit',
        modal_title=_(u'Изменить название'),
        modal_id='manufacturer-modal'
    )
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = Manufacturer


class ModelTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='model_edit',
        modal_title=_(u'Изменить модель'),
        modal_id='model-modal'
    )
    name = modallinkcolumn(
        url_name='model_edit',
        modal_title=_(u'Изменить модель'),
        modal_id='model-modal'
    )
    d = showconfirmcolumn(message=_(u'Удалить? Удаление модели оборудования '
                                    u'вызовет удаление всех связаных объектов'
                                    u' в системе.'))

    class Meta(EbsadminTableReport.Meta):
        model = Model

# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from billservice.models import RegistrationRequest
from dynamicmodel.models import DynamicSchemaField

from ebsadmin.columns import modallinkcolumn, showconfirmcolumn
from ebsadmin.tables.base import EbsadminTableReport


class RegistrationRequestTable(EbsadminTableReport):
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = RegistrationRequest


class DynamicSchemaFieldTable(EbsadminTableReport):
    id = modallinkcolumn(
        url_name='dynamicschemafield_edit',
        modal_title=_(u'Изменить название'),
        modal_id='manufacturer-modal'
    )
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = DynamicSchemaField

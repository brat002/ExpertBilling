# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from billservice.models import ContractTemplate, Template
from django_tables2.columns import LinkColumn
from django_tables2.utils import A

from ebsadmin.columns import showconfirmcolumn
from ebsadmin.tables.base import EbsadminTableReport


class TemplateTable(EbsadminTableReport):
    id = LinkColumn(
        'template_edit',
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
    name = LinkColumn(
        'template_edit',
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
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = Template
        configurable = False
        exclude = ("", 'body')


class ContractTemplateTable(EbsadminTableReport):
    id = LinkColumn(
        'contracttemplate_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn(message=_(u'Удалить шаблон номера договора?'))

    class Meta(EbsadminTableReport.Meta):
        model = ContractTemplate

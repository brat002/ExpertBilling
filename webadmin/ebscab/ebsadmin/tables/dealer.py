# -*- coding: utf-8 -*-

from billservice.models import Dealer
from django_tables2.columns import LinkColumn
from django_tables2.utils import A

from ebsadmin.tables.base import EbsadminTableReport


class DealerTable(EbsadminTableReport):
    id = LinkColumn('dealer_edit', get_params={'id': A('pk')})
    organization = LinkColumn(
        'dealer_edit', get_params={'id': A('pk')})

    class Meta(EbsadminTableReport.Meta):
        model = Dealer
        configurable = True
        available_fields = (
            'id',
            'organization',
            'contactperson',
            'unp',
            'phone'
        )

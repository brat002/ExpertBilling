# -*- coding: utf-8 -*-

from billservice.models import SystemUser
from django_tables2.columns import LinkColumn
from django_tables2.utils import A

from ebsadmin.columns import showconfirmcolumn
from ebsadmin.tables.base import EbsadminTableReport


class SystemUserTable(EbsadminTableReport):
    id = LinkColumn(
        'systemuser_edit', get_params={'id': A('pk')})
    username = LinkColumn(
        'systemuser_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = SystemUser
        configurable = True
        available_fields = ('id', 'username', 'last_login', 'd')
        exclude = ("password", 'text_password')

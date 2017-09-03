# -*- coding: utf-8 -*-

from billservice.models import PermissionGroup
from django_tables2.columns import LinkColumn
from django_tables2.utils import A

from ebsadmin.columns import showconfirmcolumn
from ebsadmin.tables.base import EbsadminTableReport


class PermissionGroupTable(EbsadminTableReport):
    id = LinkColumn(
        'permissiongroup_edit', get_params={'id': A('pk')})
    name = LinkColumn(
        'permissiongroup_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = PermissionGroup
        available_fields = ("id", 'name', 'd')

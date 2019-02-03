# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from billservice.models import AccountSuppAgreement, SuppAgreement
from django_tables2.columns import LinkColumn, TemplateColumn
from django_tables2.utils import A

from ebsadmin.columns import showconfirmcolumn
from ebsadmin.tables.base import EbsadminTableReport


class SuppAgreementTable(EbsadminTableReport):
    id = LinkColumn(
        'suppagreement_edit',
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
    accounts_count = TemplateColumn(
        '''\
<a href='{% url 'account_list' %}?suppagreement={{record.id}}' \
class='btn btn-mini'>{{record.accounts_count}} <i class='icon-arrow-right'>\
</i></a>''',
        verbose_name=_(u'У аккаунтов'),
        accessor=A('accounts_count')
    )
    d = showconfirmcolumn()

    class Meta(EbsadminTableReport.Meta):
        model = SuppAgreement
        configurable = True


class AccountSuppAgreementTable(EbsadminTableReport):
    id = LinkColumn(
        'accountsuppagreement_edit',
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
        model = AccountSuppAgreement
        configurable = True

# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from billservice.models import News
from django_tables2.columns import LinkColumn
from django_tables2.utils import A

from ebsadmin.columns import showconfirmcolumn, FormatDateTimeColumn
from ebsadmin.tables.base import EbsadminTableReport


class NewsTable(EbsadminTableReport):
    id = LinkColumn('news_edit', get_params={'id': A('pk')})
    d = showconfirmcolumn(message=_(u'Удалить новость?'))
    created = FormatDateTimeColumn(verbose_name=_(u'Активна с'))
    age = FormatDateTimeColumn(verbose_name=_(u'Активна по'))

    class Meta(EbsadminTableReport.Meta):
        model = News
        configurable = True
        available_fields = (
            'id',
            'title',
            'body',
            'created',
            'age',
            'public',
            'private',
            'agent',
            'd'
        )

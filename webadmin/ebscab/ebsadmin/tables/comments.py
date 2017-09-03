# -*- coding: utf-8 -*-

from django_tables2.columns import Column, LinkColumn, TemplateColumn
from django_tables2.utils import A

from ebsadmin.models import Comment
from ebsadmin.tables.base import EbsadminTableReport


class CommentTable(EbsadminTableReport):
    id = LinkColumn(
        'comment_edit',
        get_params={
            'id': A('pk')
        },
        attrs={
            'a': {
                'rel': "alert3",
                'class': "open-log-custom-dialog"
            }
        }
    )
    done = TemplateColumn(
        '''\
<a href='{% url 'comment_edit' %}?id={{record.id}}&done=True' \
class='btn btn-mini btn-success comment-done'>
<i class='icon-ok icon-white'></i></a>&nbsp;
<a href='{{record.get_remove_url}}' \
class='btn btn-mini btn-danger show-confirm'>
<i class='icon-remove icon-white'></i></a>''',
        verbose_name='Действия',
        orderable=False
    )
    object = Column(verbose_name=u'Объект')

    class Meta(EbsadminTableReport.Meta):
        model = Comment
        configurable = True
        available_fields = ('id', 'comment', 'object',
                            'created', 'due_date', 'done',)

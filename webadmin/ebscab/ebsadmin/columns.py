# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from django_tables2.columns import Column, LinkColumn, TemplateColumn
from django_tables2.utils import A, AttributeDict


def showconfirmcolumn(href='{{record.get_remove_url}}', message=_(u'Удалить?'),
                      verbose_name=' ', icon_type='icon-remove'):
    return TemplateColumn(
        '<a href="%s" class="show-confirm" title="%s" data-clickmessage="%s">'
        '<i class="%s"></i></a>' % (href, message, message, icon_type),
        verbose_name=verbose_name,
        orderable=False
    )


def modallinkcolumn(url_name='', modal_title='', modal_id=''):
    return LinkColumn(
        url_name,
        get_params={
            'id': A('pk')
        },
        attrs={
            'a': {
                'rel': 'alert3',
                'class': 'general-modal-dialog',
                'data-dlgtitle': modal_title,
                'data-dlgid': modal_id
            }
        }
    )


class FormatBlankColumn(Column):

    def render(self, value):
        return "" if value is None else value


class FormatBooleanHTMLColumn(TemplateColumn):

    def render(self, value):
        return "" if value else value


class FormatFloatColumn(Column):

    def render(self, value):
        return "%.2f" % float(value) if value else ''


class FormatDateTimeColumn(Column):

    def render(self, value):
        try:
            return value.strftime("%d.%m.%Y %H:%M:%S") if value else ''
        except:
            return value


class FormatBlankSpeedColumn(LinkColumn):

    def render(self, value):
        return value if value else ''


class YesNoColumn(Column):

    def render(self, value):
        return mark_safe(
            '<img src="%sicons/16/%s.png" />' %
            (settings.STATIC_URL, 'accept' and True or 'cross'))


class RadioColumn(Column):

    def render(self, value, bound_column):
        default = {
            'type': 'radio',
            'name': bound_column.name,
            'value': value
        }
        general = self.attrs.get('input')
        specific = self.attrs.get('td__input')
        attrs = AttributeDict(
            default, **(specific or general or {}))
        return mark_safe(u'<input %s/>' % attrs.as_html())

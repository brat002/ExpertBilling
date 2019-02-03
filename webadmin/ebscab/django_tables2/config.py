# -*- coding: utf-8 -*-

from django.core.paginator import EmptyPage, PageNotAnInteger

from ebsadmin.forms import TableColumnsForm, TablePerPageForm
from ebsadmin.models import TableSettings


class RequestConfig(object):
    """
    A configurator that uses request data to setup a table.

    :type  paginate: `dict` or `bool`
    :param paginate: indicates whether to paginate, and if so, what default
                     values to use. If the value evaluates to `False`,
                     pagination will be disabled. A `dict` can be used to
                     specify default values for the call to
                     `~.tables.Table.paginate` (e.g. to define a default
                     *per_page* value).

                     A special *silent* item can be used to enable automatic
                     handling of pagination exceptions using the following
                     algorithm:

                     - If `~django.core.paginator.PageNotAnInteger`` is raised,
                       show the first page.
                     - If `~django.core.paginator.EmptyPage` is raised, show
                       the last page.

    """

    def __init__(self, request, paginate=True):
        self.request = request
        self.paginate = paginate

    def configure(self, table):
        """
        Configure a table using information from the request.
        """
        if table.Meta.__dict__.get("configurable"):
            try:
                ts = TableSettings.objects.get(
                    name=table.name, user=self.request.user)
            except:
                af = table.Meta.__dict__.get('available_fields')
                ts = TableSettings.objects.create(
                    name=table.name,
                    value={
                        'fields': af if af else table.base_columns.keys()
                    },
                    per_page=50,
                    user=self.request.user
                )

            bc = table.base_columns
            table.sequence = ts.value.get('fields')
            for key in table.base_columns:
                column = table.base_columns.get(key)
                if key not in ts.value.get('fields'):
                    column.visible = False

            selected_columns = ts.value.get('fields')
            z = [x for x in table.base_columns if x not in selected_columns]

            table.columns_form = TableColumnsForm(
                initial={'columns': selected_columns, 'table_name': table.name})
            table.columns_form.fields['columns'].choices = [
                (x, table.base_columns.get(x).verbose_name or x)
                for x in tuple(selected_columns) + tuple(z) if bc.get(x)
            ]

            table.per_page_form = TablePerPageForm(
                per_page_id='id_per_page%s' % table.name,
                initial={
                    'per_page': ts.per_page
                }
            )

        order_by = self.request.GET.getlist(table.prefixed_order_by_field)
        if order_by:
            table.order_by = order_by
        if self.paginate:
            self.paginate = {}
            if table.Meta.__dict__.get("configurable"):
                self.paginate['per_page'] = ts.per_page
            if hasattr(self.paginate, "items"):
                kwargs = dict(self.paginate)
            else:
                kwargs = {}
            # extract some options from the request
            for arg in ("page", "per_page"):
                name = getattr(table, u"prefixed_%s_field" % arg)
                try:
                    kwargs[arg] = int(self.request.GET[name])
                except (ValueError, KeyError):
                    pass

            silent = kwargs.pop('silent', True)
            if not silent:
                table.paginate(**kwargs)
            else:
                try:
                    table.paginate(**kwargs)
                except PageNotAnInteger:
                    table.page = table.paginator.page(1)
                except EmptyPage:
                    table.page = table.paginator.page(
                        table.paginator.num_pages)

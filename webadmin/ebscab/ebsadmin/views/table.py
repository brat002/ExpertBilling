# -*- coding: utf-8 -*-

from billservice.utils import systemuser_required
from ebscab.utils.decorators import ajax_request
from object_log.models import LogItem

import ebsadmin.tables
from ebsadmin.forms import TableColumnsForm
from ebsadmin.models import TableSettings


log = LogItem.objects.log_action


@ajax_request
@systemuser_required
def table_settings(request):
    table_name = request.POST.get("table_name")
    per_page = request.POST.get("per_page") or 25
    table = getattr(ebsadmin.tables, table_name)
    form = TableColumnsForm(request.POST)
    form.fields['columns'].choices = [(x, x) for x in table.base_columns]
    if form.is_valid():
        try:
            ts = TableSettings.objects.get(name=table_name, user=request.user)
            ts.value = {'fields': form.cleaned_data.get('columns', [])}
            ts.per_page = per_page if per_page not in ['undefined', ''] else 25
            ts.save()
        except Exception, e:
            ts = TableSettings.objects.create(
                name=table_name,
                value={
                    'fields': form.cleaned_data.get('columns', [])
                },
                per_page=per_page,
                user=request.user)
            ts.save()

    return {
        "status": True
    }

# -*- coding: utf-8 -*-


from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import IpInUseLogForm
from billservice.helpers import systemuser_required
from billservice.models import IPInUse, SubAccount
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import render_to

from ebsadmin.tables import IPInUseTable


@systemuser_required
@render_to('ebsadmin/ipinuse_list.html')
def ipinusereport(request):
    if not (request.user.account.has_perm('billservice.view_ipinuse')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    if request.method == 'GET' and request.GET:
        data = request.GET
        form = IpInUseLogForm(data)
        if form.is_valid():
            account = form.cleaned_data.get('account')
            subaccount = form.cleaned_data.get('subaccount')
            types = form.cleaned_data.get('types')
            ip = form.cleaned_data.get('ip')
            ippool = form.cleaned_data.get('ippool')

            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            res = IPInUse.objects.select_related().all()
            if account:
                subaccs = SubAccount.objects.filter(account__id__in=account)
                t = [x.vpn_ipinuse_id for x in subaccs] + \
                    [x.ipn_ipinuse_id for x in subaccs]
                for subacc in subaccs:
                    res = res.filter(Q(activesession__ipinuse__isnull=False) |
                                     Q(activesession__subaccount=subacc))
                res = res.filter(id__in=t)

            if ip:
                res = res.filter(ip=ip)
            if types:
                if 'static' in types:
                    res = res.filter(dynamic=False)
                elif 'dynamic' in types:
                    res = res.filter(dynamic=True)

            if start_date:
                res = res.filter(datetime__gte=start_date)
            if end_date:
                res = res.filter(datetime__lte=end_date)

            if ippool:
                res = res.filter(pool__in=ippool)

            table = IPInUseTable(res)
            table_to_report = RequestConfig(
                request,
                paginate=(False if request.GET.get('paginate') == 'False'
                          else True))
            table_to_report = table_to_report.configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)

            return {
                'table': table,
                'form': form,
                'resultTab': True
            }

        else:
            return {
                'status': False,
                'form': form
            }
    else:
        form = IpInUseLogForm()
        return {
            'form': form
        }

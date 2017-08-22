# -*- coding: utf-8 -*-

from django.contrib import messages
from django.http import HttpResponseRedirect

from billservice.forms import (
    AccountPrepaysRadiusTraficForm,
    AccountPrepaysRadiusTraficSearchForm
)
from billservice.helpers import systemuser_required
from billservice.models import AccountPrepaysRadiusTrafic
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import render_to, ajax_request
from object_log.models import LogItem

from ebsadmin.tables import AccountPrepaysRadiusTraficTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/accountprepaysradiustraffic/list.html')
def accountprepaysradiustraffic(request):
    if not request.user.account.has_perm(
            'billservice.view_accountprepaysradiustraffic'):
        messages.error(request,
                       u'У вас нет прав на доступ в этот раздел.',
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    if request.method == 'GET' and request.GET:
        data = request.GET
        form = AccountPrepaysRadiusTraficSearchForm(data)
        if form.is_valid():
            account = form.cleaned_data.get('account')
            current = form.cleaned_data.get('current')
            tariff = form.cleaned_data.get('tariff')
            date_start = form.cleaned_data.get('date_start')
            date_end = form.cleaned_data.get('date_end')
            res = (AccountPrepaysRadiusTrafic.objects
                   .all()
                   .order_by('account_tarif__account', 'current'))
            if account:
                res = res.filter(account_tarif__account__id__in=account)

            if tariff:
                res = res.filter(account_tarif__tarif__in=tariff)

            if current:
                res = res.filter(current=current)

            if date_start:
                res = res.filter(datetime__gte=date_start)

            if date_end:
                res = res.filter(datetime__lte=date_end)

            table = AccountPrepaysRadiusTraficTable(res)
            table_to_report = RequestConfig(
                request,
                paginate=(False if request.GET.get('paginate') == 'False'
                          else True))
            table_to_report = table_to_report.configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)

            return {
                "table": table,
                'form': form,
                'resultTab': True
            }

        else:
            return {
                'status': False,
                'form': form
            }
    else:
        form = AccountPrepaysRadiusTraficSearchForm()
        return {
            'form': form
        }


@systemuser_required
@render_to('ebsadmin/accountprepaysradiustraffic/edit.html')
def accountprepaysradiustraffic_edit(request):
    id = request.POST.get("id")
    item = None
    if request.method == 'POST':
        if id:
            model = AccountPrepaysRadiusTrafic.objects.get(id=id)
            form = AccountPrepaysRadiusTraficForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'billservice.change_accountprepaysradiustraffic')):
                messages.error(request,
                               (u'У вас нет прав на редактирование '
                                u'предоплаченного RADIUS трафика'),
                               extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = AccountPrepaysRadiusTraficForm(request.POST)
        if not (request.user.account.has_perm(
                'billservice.add_accountprepaysradiustraffic')):
            messages.error(request,
                           (u'У вас нет прав на добавление RADIUS '
                            u'предоплаченного трафика.'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect(request.path)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            return {
                'form': form,
                'status': True
            }
        else:
            return {
                'form': form,
                'status': False
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm('billservice.view_accountprepaysradiustraffic')):
            messages.error(request,
                           u'У вас нет прав на доступ в этот раздел.',
                           extra_tags='alert-danger')
            return {
                'status': False
            }

        if id:
            item = AccountPrepaysRadiusTrafic.objects.get(id=id)
            form = AccountPrepaysRadiusTraficForm(instance=item)
        else:
            form = AccountPrepaysRadiusTraficForm()

    return {
        'form': form,
        'status': False
    }


@ajax_request
@systemuser_required
def accountprepaysradiustraffic_delete(request):
    if not (request.user.account.has_perm(
            'billservice.delete_accountprepaysradiustrafic')):
        return {
            'status': False,
            'message': (u'У вас нет прав на удаление предоплаченного NetFlow '
                        u'трафика')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = AccountPrepaysRadiusTrafic.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": u"Указанная запись не найдена %s" % str(e)
            }

        log('DELETE', request.user, item)

        item.delete()
        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "message": "AccountPrepaysRadiusTrafic not found"
        }

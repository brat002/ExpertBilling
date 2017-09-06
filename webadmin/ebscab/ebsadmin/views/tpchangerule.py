# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import TPChangeRuleForm, TPChangeMultipleRuleForm
from billservice.utils import systemuser_required
from billservice.models import TPChangeRule
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import render_to, ajax_request
from object_log.models import LogItem

from ebsadmin.tables import TPChangeRuleTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/common/list.html')
def tpchangerule(request):
    if not (request.user.account.has_perm('billservice.view_tpchangerule')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    items = TPChangeRule.objects.all()
    table = TPChangeRuleTable(items)
    table_to_report = RequestConfig(
        request,
        paginate=False if request.GET.get('paginate') == 'False' else True)
    table_to_report = table_to_report.configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)

    return {
        "list_url": reverse('tpchangerule'),
        "list_header": _(u'Правила смены тарифных планов'),
        "add_btn_url": reverse('tpchangerule_edit'),
        "table": table
    }


@systemuser_required
@render_to('ebsadmin/tpchangerule/edit.html')
def tpchangerule_edit(request):
    id = request.POST.get("id")
    item = None
    if request.method == 'POST':
        if id:
            model = TPChangeRule.objects.get(id=id)
            form = TPChangeRuleForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'billservice.change_tpchangerule')):
                messages.error(
                    request,
                    _(u'У вас нет прав на редактирование правил смены '
                        u'тарифных планов'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = TPChangeMultipleRuleForm(request.POST)
            if not (request.user.account.has_perm(
                    'billservice.add_tpchangerule')):
                messages.error(
                    request,
                    _(u'У вас нет прав на редактирование правил смены '
                        u'тарифных планов'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        if form.is_valid():
            if id:
                model = form.save(commit=False)
                model.save()
            else:
                from_tariff = form.cleaned_data.get("from_tariff")
                cost = form.cleaned_data.get("cost")
                disabled = form.cleaned_data.get("disabled")
                on_next_sp = form.cleaned_data.get("on_next_sp")
                settlement_period = form.cleaned_data.get("settlement_period")
                ballance_min = form.cleaned_data.get("ballance_min")
                mirror = form.cleaned_data.get("mirror")

                for tariff in form.cleaned_data.get("to_tariffs"):
                    tp = TPChangeRule.objects.filter(
                        from_tariff=from_tariff, to_tariff=tariff)
                    if not tp:
                        model = TPChangeRule(
                            from_tariff=from_tariff,
                            to_tariff=tariff,
                            cost=cost,
                            disabled=disabled,
                            on_next_sp=on_next_sp,
                            settlement_period=settlement_period,
                            ballance_min=ballance_min)
                        model.save()
                    else:
                        tp.update(cost=cost,
                                  disabled=disabled,
                                  on_next_sp=on_next_sp,
                                  settlement_period=settlement_period,
                                  ballance_min=ballance_min)

                    log('CREATE', request.user, model)
                    tp = TPChangeRule.objects.filter(
                        from_tariff=tariff, to_tariff=from_tariff)
                    if not tp and mirror:
                        model = TPChangeRule(
                            from_tariff=tariff,
                            to_tariff=from_tariff,
                            cost=cost,
                            disabled=disabled,
                            on_next_sp=on_next_sp,
                            settlement_period=settlement_period,
                            ballance_min=ballance_min)
                        model.save()
                    elif mirror:
                        tp.update(cost=cost,
                                  disabled=disabled,
                                  on_next_sp=on_next_sp,
                                  settlement_period=settlement_period,
                                  ballance_min=ballance_min)
                    log('CREATE', request.user, model)

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            return HttpResponseRedirect(reverse("tpchangerule"))
        else:
            print form._errors
            return {
                'form': form,
                'status': False
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm(
                'billservice.view_tpchangerule')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        if id:
            item = TPChangeRule.objects.get(id=id)
            form = TPChangeRuleForm(instance=item)
        else:
            form = TPChangeMultipleRuleForm()

    return {
        'form': form,
        'status': False,
        'item': item
    }


@ajax_request
@systemuser_required
def tpchangerule_delete(request):
    if not (request.user.account.has_perm('billservice.delete_tpchangerule')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление правил смены '
                         u'тарифных планов')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = TPChangeRule.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанное правило не найдено %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "message": "TPChangeRule not found"
        }

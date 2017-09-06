# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import ContractTemplateForm
from billservice.utils import systemuser_required
from billservice.models import ContractTemplate
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import render_to, ajax_request
from object_log.models import LogItem

from ebsadmin.tables import ContractTemplateTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/contracttemplate/list.html')
def contracttemplate(request):
    if not (request.user.account.has_perm('billservice.view_group')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    res = ContractTemplate.objects.all()
    table = ContractTemplateTable(res)
    table_to_report = RequestConfig(
        request,
        paginate=False if request.GET.get('paginate') == 'False' else True)
    table_to_report = table_to_report.configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)

    return {
        "table": table
    }


@systemuser_required
@render_to('ebsadmin/contracttemplate/edit.html')
def contracttemplate_edit(request):
    id = request.POST.get("id")
    item = None
    if request.method == 'POST':
        model = None
        if id:
            model = ContractTemplate.objects.get(id=id)
            form = ContractTemplateForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'billservice.change_tariff')):
                messages.error(request,
                               _(u'У вас нет прав на редактирование тарифного '
                                 u'плана'),
                               extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        else:
            form = ContractTemplateForm(request.POST)
        if not (request.user.account.has_perm('billservice.add_tariff')):
            messages.error(request,
                           _(u'У вас нет прав на создание тарифного плана'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect(request.path)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            form.save_m2m()
            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(request,
                             _(u'Шаблон номера договора успешно создан.'),
                             extra_tags='alert-success')
            return HttpResponseRedirect(reverse("contracttemplate"))
        else:
            messages.error(
                request,
                _(u'При сохранении шаблона номера договора возникли ошибки.'),
                extra_tags='alert-danger')
            return {
                'form': form,
                'status': False,
                'item': model
            }

    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm('billservice.view_tariff')):
            messages.error(
                request,
                _(u'У вас нет прав на доступ на просмотр тарифных планов.'),
                extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        if id:
            item = ContractTemplate.objects.get(id=id)
            form = ContractTemplateForm(instance=item)
        else:
            form = ContractTemplateForm()

    return {
        'form': form,
        'status': False,
        'item': item
    }


@ajax_request
@systemuser_required
def contracttemplate_delete(request):
    if not (request.user.account.has_perm('billservice.delete_tariff')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление тарифных планов')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = ContractTemplate.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанный шаблона номера договора "
                             u"не найден %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request,
                         _(u'Шаблон номера договора успешно удалён.'),
                         extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(
            request,
            _(u'При удалении шаблона номера договора возникли ошибки.'),
            extra_tags='alert-danger')
        return {
            "status": False,
            "message": "ContractTemplate not found"
        }

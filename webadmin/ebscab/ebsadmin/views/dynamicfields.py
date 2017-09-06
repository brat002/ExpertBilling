# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import DynamicSchemaFieldForm
from billservice.utils import systemuser_required
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from dynamicmodel.models import DynamicSchemaField
from ebscab.utils.decorators import render_to, ajax_request
from object_log.models import LogItem

from ebsadmin.tables import DynamicSchemaFieldTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/dynamicschemafield/list.html')
def dynamicschemafield(request):
    if not (request.user.account.has_perm('dynamicmodel.change_dynamicschemafield')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    res = DynamicSchemaField.objects.all()
    table = DynamicSchemaFieldTable(res)
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
@render_to('ebsadmin/dynamicschemafield/edit.html')
def dynamicschemafield_edit(request):
    id = request.POST.get("id")
    item = None
    if request.method == 'POST':
        if id:
            model = DynamicSchemaField.objects.get(id=id)
            form = DynamicSchemaFieldForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'dynamicmodel.change_dynamicschemafield')):
                messages.error(request,
                               _(u'У вас нет прав на редактирование '
                                 u'дополнительного поля'),
                               extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = DynamicSchemaFieldForm(request.POST)
            if not (request.user.account.has_perm(
                    'dynamicmodel.change_dynamicschemafield')):
                messages.error(
                    request,
                    _(u'У вас нет прав на создание дополнительного поля'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(request,
                             _(u'Дополнительное поле успешно сохранёно.'),
                             extra_tags='alert-success')
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(request,
                           _(u'При сохранении поля возникли ошибки.'),
                           extra_tags='alert-danger')
            return {
                'form': form,
                'status': False
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm(
                'dynamicmodel.change_dynamicschemafield')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return {}
        if id:
            item = DynamicSchemaField.objects.get(id=id)
            form = DynamicSchemaFieldForm(instance=item)
        else:
            form = DynamicSchemaFieldForm()

    return {
        'form': form,
        'status': False
    }


@ajax_request
@systemuser_required
def dynamicschemafield_delete(request):
    if not (request.user.account.has_perm(
            'dynamicmodel.change_dynamicschemafield')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление дополнительных полей')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = DynamicSchemaField.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанное поле не найдено %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request,
                         _(u'Поле успешно удалёно.'),
                         extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(request,
                       _(u'При удалении поля возникли ошибки.'),
                       extra_tags='alert-danger')
        return {
            "status": False,
            "message": "dynamic field not found"
        }

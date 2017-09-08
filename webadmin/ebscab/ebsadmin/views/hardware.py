# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import HardwareForm
from billservice.utils import systemuser_required
from billservice.models import Hardware
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.utils.decorators import render_to, ajax_request
from object_log.models import LogItem

from ebsadmin.tables import HardwareTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/common/list.html')
def hardware(request):
    if not (request.user.account.has_perm('billservice.view_hardware')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    res = Hardware.objects.all()
    table = HardwareTable(res)
    table_to_report = RequestConfig(
        request,
        paginate=False if request.GET.get('paginate') == 'False' else True)
    table_to_report = table_to_report.configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)

    return {
        "list_url": reverse('hardware'),
        "list_header": _(u'Устройства'),
        "add_btn_url": reverse('hardware_edit'),
        "table": table
    }


@systemuser_required
@render_to('ebsadmin/common/edit_form.html')
def hardware_edit(request):
    id = request.POST.get("id")
    item = None

    if request.method == 'POST':
        if id:
            model = Hardware.objects.get(id=id)
            form = HardwareForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'billservice.change_hardware')):
                messages.error(
                    request,
                    _(u'У вас нет прав на редактирование оборудования'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = HardwareForm(request.POST)
            if not (request.user.account.has_perm('billservice.add_hardware')):
                messages.error(request,
                               _(u'У вас нет прав на создание оборудования'),
                               extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            return HttpResponseRedirect(reverse("hardware"))
        else:
            return {
                'form': form,
                'status': False,
                'list_url': reverse('hardware'),
                'list_label': _(u'Устройства'),
                'form_action_url': reverse('hardware_edit'),
                'form_legend': _(u'Параметры устройства'),
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm('billservice.view_hardware')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        if id:
            item = Hardware.objects.get(id=id)
            form = HardwareForm(instance=item)
        else:
            form = HardwareForm()

    return {
        'form': form,
        'status': False,
        'item': item,
        'list_url': reverse('hardware'),
        'list_label': _(u'Устройства'),
        'form_action_url': reverse('hardware_edit'),
        'form_legend': _(u'Параметры устройства'),
    }


@ajax_request
@systemuser_required
def hardware_delete(request):
    if not (request.user.account.has_perm('billservice.delete_hardware')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление оборудования')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = Hardware.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанное оборудование не найдено %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "message": "Hardware not found"
        }

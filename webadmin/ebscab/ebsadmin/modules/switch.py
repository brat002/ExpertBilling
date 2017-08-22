# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import SwitchForm
from billservice.helpers import systemuser_required
from billservice.models import Switch
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import render_to, ajax_request
from object_log.models import LogItem

from ebsadmin.tables import SwitchTable, SwitchPortsTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/common/list.html')
def switch(request):
    if not (request.user.account.has_perm('billservice.view_switch')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    res = Switch.objects.all()
    table = SwitchTable(res)
    table_to_report = RequestConfig(
        request,
        paginate=False if request.GET.get('paginate') == 'False' else True)
    table_to_report = table_to_report.configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)

    return {
        "list_url": reverse('switch'),
        "list_header": _(u'Коммутаторы'),
        "add_btn_url": reverse('switch_edit'),
        "table": table
    }


@systemuser_required
@render_to('ebsadmin/switch/edit.html')
def switch_edit(request):
    id = request.POST.get("id")
    item = None
    if request.method == 'POST':
        if id:
            model = Switch.objects.get(id=id)
            form = SwitchForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'billservice.change_switch')):
                messages.error(
                    request,
                    _(u'У вас нет прав на редактирование коммутатора'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = SwitchForm(request.POST)
            if not (request.user.account.has_perm('billservice.add_switch')):
                messages.error(request,
                               _(u'У вас нет прав на создание коммутатора'),
                               extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            return HttpResponseRedirect(reverse("switch"))
        else:
            return {
                'form': form,
                'status': False
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm('billservice.view_switch')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        if id:

            item = Switch.objects.get(id=id)

            form = SwitchForm(instance=item)
            ports = []
            broken_ports = item.broken_ports.split(',')
            uplink_ports = item.uplink_ports.split(',')
            protected_ports = item.protected_ports.split(',')
            monitored_ports = item.monitored_ports.split(',')
            disabled_ports = item.disabled_ports.split(',')
            for x in xrange(1, item.ports_count + 1):
                ports.append({
                    'port': x, 'broken_port': str(x) in broken_ports,
                    'uplink_port': str(x) in uplink_ports,
                    'protected_port': str(x) in protected_ports,
                    'monitored_port': str(x) in monitored_ports,
                    'disabled_port': str(x) in disabled_ports,
                })
            ports_table = SwitchPortsTable(ports)
            table_to_report = RequestConfig(request, paginate=False)
            table_to_report = table_to_report.configure(ports_table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)
        else:
            form = SwitchForm()
            ports_table = None

    return {
        'form': form,
        'ports_table': ports_table,
        'status': False,
        'item': item
    }


@ajax_request
@systemuser_required
def switch_port_status(request):
    if not (request.user.account.has_perm('billservice.change_switch')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на редактирование коммутатора')
        }

    switch_id = int(request.POST.get('switch_id', 0))
    port = int(request.POST.get('port', 0))
    port_type = request.POST.get('port_type')
    port_state = request.POST.get('port_state') and 'checked' or False
    if switch_id and port and port_type:
        try:
            item = Switch.objects.get(id=switch_id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанный коммутатор не найден %s") % str(e)
            }

        if port_type == 'broken_port':
            broken_ports = item.broken_ports.split(',')
            if port_state and port not in broken_ports:
                broken_ports.append(port)
            elif not port_state and port in broken_ports:
                broken_ports.remove(port)
            item.broken_ports = ','.join([str(x) for x in broken_ports])
            item.save()

        if port_type == 'uplink_port':
            uplink_ports = item.uplink_ports.split(',')
            if port_state and port not in uplink_ports:
                uplink_ports.append(port)
            elif not port_state and port in uplink_ports:
                uplink_ports.remove(port)
            item.uplink_ports = ','.join([str(x) for x in uplink_ports])
            item.save()

        if port_type == 'protected_port':
            protected_ports = item.protected_ports.split(',')
            if port_state and port not in protected_ports:
                protected_ports.append(port)
            elif not port_state and port in protected_ports:
                protected_ports.remove(port)
            item.protected_ports = ','.join([str(x) for x in protected_ports])
            item.save()

        if port_type == 'monitored_port':
            monitored_ports = item.monitored_ports.split(',')
            if port_state and port not in monitored_ports:
                monitored_ports.append(port)
            elif not port_state and port in monitored_ports:
                monitored_ports.remove(port)
            item.monitored_ports = ','.join([str(x) for x in monitored_ports])
            item.save()

        if port_type == 'disabled_port':
            disabled_ports = item.disabled_ports.split(',')
            if port_state and port not in disabled_ports:
                disabled_ports.append(port)
            elif not port_state and port in disabled_ports:
                disabled_ports.remove(port)
            item.disabled_ports = ','.join([str(x) for x in disabled_ports])
            item.save()

        log('EDIT', request.user, item)

        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "message": "Switch not found"
        }


@ajax_request
@systemuser_required
def switch_delete(request):
    if not (request.user.account.has_perm('billservice.delete_switch')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление коммутатора')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = Switch.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанный коммутатор не найден %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "message": "Switch not found"
        }

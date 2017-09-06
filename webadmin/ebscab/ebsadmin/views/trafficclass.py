# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import F
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from IPy import IP

from billservice.utils import systemuser_required
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.utils.decorators import render_to, ajax_request
from nas.forms import TrafficClassForm, TrafficNodeForm
from nas.models import TrafficClass, TrafficNode
from object_log.models import LogItem

from ebsadmin.forms import TrafficNodesUploadForm
from ebsadmin.tables import TrafficClassTable, TrafficNodeTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/trafficclass/list.html')
def trafficclass(request):
    if not (request.user.account.has_perm('nas.view_trafficclass')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    res = TrafficClass.objects.all()
    table = TrafficClassTable(res)
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
@render_to('ebsadmin/trafficclass/upload.html')
def trafficclass_upload(request):
    table = None
    if request.POST:
        form = TrafficNodesUploadForm(request.POST, request.FILES)
        if form.is_valid():
            nodes_file = form.cleaned_data.get('nodes_file')
            networks = form.cleaned_data.get('networks')
            traffic_class = form.cleaned_data.get('traffic_class')
            res = []
            bulk = []
            for line in nodes_file:
                line = line.strip()
                if not line:
                    continue

                try:
                    IP(line)
                except Exception, e:
                    messages.error(request,
                                   u'Неправильная сеть %s' % line,
                                   extra_tags='alert-danger')
                    continue

                for network in networks.split('\n'):
                    network = network.strip()
                    if not network:
                        continue

                    try:
                        IP(network)
                    except Exception, e:
                        messages.error(request,
                                       u'Неправильная сеть %s' % network,
                                       extra_tags='alert-danger')
                        continue
                    bulk.append(TrafficNode(traffic_class=traffic_class,
                                            dst_ip=line,
                                            src_ip=network))
            TrafficNode.objects.bulk_create(bulk)
            return HttpResponseRedirect(
                "%s?id=%s" % (reverse('trafficnode_list'), traffic_class.id))
        else:
            print form._errors
    else:
        traffic_class = request.GET.get('traffic_class')
        if traffic_class:
            form = TrafficNodesUploadForm(
                initial={
                    'traffic_class': TrafficClass.objects.get(id=traffic_class)
                }
            )
        else:
            form = TrafficNodesUploadForm()

    return {
        "form": form,
        'table': table
    }


@ajax_request
@systemuser_required
def trafficclass_weight(request):
    if not (request.user.account.has_perm('nas.change_trafficclass')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на изменение классов')
        }
    ids = request.POST.getlist("id")
    k = 1
    if ids:
        TrafficClass.objects.all().update(weight=F('weight') + 1000)
    for i in ids:
        item = TrafficClass.objects.get(id=i)
        item.weight = k
        item.save()

        if id:
            log('EDIT', request.user, item)
        else:
            log('CREATE', request.user, item)
        k += 1
    return {
        'status': True
    }


@systemuser_required
@render_to('ebsadmin/trafficnode_list.html')
def trafficnode_list(request):
    if not (request.user.account.has_perm('nas.view_trafficnode')):
        messages.error(
            request,
            _(u'У вас нет прав на доступ в этот раздел.'),
            extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    id = request.GET.get("id")
    res = TrafficNode.objects.filter(traffic_class__id=id)
    table = TrafficNodeTable(res)
    table_to_report = RequestConfig(
        request,
        paginate=True if not request.GET.get('paginate') == 'False' else False)
    table_to_report = table_to_report.configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    return {
        "table": table,
        'item': TrafficClass.objects.get(id=id)
    }


@systemuser_required
@render_to('ebsadmin/trafficclass/edit.html')
def trafficclass_edit(request):
    id = request.GET.get("id")
    item = None
    model = None
    if request.method == 'POST':
        if id:
            model = TrafficClass.objects.get(id=id)
            form = TrafficClassForm(request.POST, instance=model)
            if not (request.user.account.has_perm('nas.change_trafficclass')):
                messages.error(request,
                               _(u'У вас нет прав на редактирование классов трафика'),
                               extra_tags='alert-danger')
                return {}
        else:
            form = TrafficClassForm(request.POST)
            if not (request.user.account.has_perm('nas.add_trafficclass')):
                messages.error(request,
                               _(u'У вас нет прав на создание классов трафика'),
                               extra_tags='alert-danger')
                return {}

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
        if not (request.user.account.has_perm('nas.view_trafficclass')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return {}

        if id:
            item = TrafficClass.objects.get(id=id)
            form = TrafficClassForm(instance=item)
        else:
            form = TrafficClassForm()

    return {
        'form': form,
        'status': False,
        'item': item
    }


@systemuser_required
@render_to('ebsadmin/trafficnode_edit.html')
def trafficnode(request):
    traffic_class = request.GET.get("traffic_class")
    id = request.GET.get("id")
    accountaddonservice = None
    item = None
    if request.method == 'POST':
        if id:
            model = TrafficNode.objects.get(id=id)
            form = TrafficNodeForm(request.POST, instance=model)
            if not (request.user.account.has_perm('nas.change_trafficnode')):
                messages.error(
                    request,
                    _(u'У вас нет прав на изменение составляющих '
                        u'класса трафика'),
                    extra_tags='alert-danger')
                return {}
        else:
            form = TrafficNodeForm(request.POST)
            if not (request.user.account.has_perm('nas.add_trafficnode')):
                messages.error(
                    request,
                    _(u'У вас нет прав на создание составляющих '
                        u'класса трафика'),
                    extra_tags='alert-danger')
                return {}

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
        traffic_class_id = request.GET.get("traffic_class")
        if not (request.user.account.has_perm('nas.view_trafficnode')):
            messages.error(
                request,
                _(u'У вас нет прав на доступ в этот раздел.'),
                extra_tags='alert-danger')
            return {}

        if id:
            item = TrafficNode.objects.get(id=id)
            form = TrafficNodeForm(instance=item)
        elif traffic_class_id:
            form = TrafficNodeForm(
                initial={
                    'traffic_class': (TrafficClass.objects
                                      .get(id=traffic_class_id))
                }
            )

    return {
        'form': form,
        'status': False,
        'item': item
    }


@ajax_request
@systemuser_required
def trafficnode_delete(request):
    if not (request.user.is_staff == True and
            request.user.account.has_perm('nas.delete_trafficnode')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление направлений')
        }
    id = request.GET.getlist('d')
    if id:
        try:
            items = TrafficNode.objects.filter(id__in=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанное направление не найдено %s") % str(e)
            }
        for item in items:
            log('DELETE', request.user, item)
            item.delete()
        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "message": "TrafficNode not found"
        }


@ajax_request
@systemuser_required
def trafficclass_delete(request):
    if not (request.user.is_staff == True and
            request.user.account.has_perm('billservice.delete_trafficclass')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление классов трафика')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = TrafficClass.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанный класс не найден %s") % str(e)
            }

        log('DELETE', request.user, item)

        item.delete()
        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "message": "TrafficClass not found"
        }

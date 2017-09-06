# -*- coding: utf-8 -*-


from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import RadiusAttrsForm
from billservice.utils import systemuser_required
from billservice.models import RadiusAttrs, Tariff
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import render_to, ajax_request
from nas.models import Nas
from object_log.models import LogItem

from ebsadmin.tables import RadiusAttrTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/radiusattr/list.html')
def radiusattr(request):
    if not (request.user.account.has_perm('billservice.view_radiusattrs')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    nas_id = request.GET.get("nas")
    tarif_id = request.GET.get("tarif")
    item = None
    tariff = None
    nas = None
    if nas_id:
        nas = Nas.objects.get(id=nas_id)
        res = RadiusAttrs.objects.filter(nas__id=nas_id)
    elif tarif_id:
        tariff = Tariff.objects.get(id=tarif_id)
        res = RadiusAttrs.objects.filter(tarif__id=tarif_id)
    else:
        res = RadiusAttrs.objects.all()
    table = RadiusAttrTable(res)
    table_to_report = RequestConfig(
        request,
        paginate=False if request.GET.get('paginate') == 'False' else True)
    table_to_report = table_to_report.configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)

    return {
        "table": table,
        'nas': nas,
        'tariff': tariff,
        'model_name': (nas.__class__.__name__ if nas else
                       tariff.__class__.__name__ if tariff else '')
    }


@systemuser_required
@render_to('ebsadmin/radiusattr/edit.html')
def radiusattr_edit(request):
    account = None
    nas_id = request.GET.get("nas")
    tarif_id = request.GET.get("tarif")
    id = request.POST.get("id")
    tariff = None
    nas = None
    if nas_id:
        nas = Nas.objects.get(id=nas_id)
    elif tarif_id:
        tariff = Tariff.objects.get(id=tarif_id)

    if request.method == 'POST':
        if id:
            model = RadiusAttrs.objects.get(id=id)
            form = RadiusAttrsForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'billservice.change_radiusattrs')):
                messages.error(
                    request,
                    _(u'У вас нет прав на редактирование радиус атрибутов'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            if not (request.user.account.has_perm(
                    'billservice.add_radiusattrs')):
                messages.error(
                    request,
                    _(u'У вас нет прав на создание радиус атрибутов'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

            form = RadiusAttrsForm(request.POST)

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
                'status': False,
                'nas': nas,
                'tariff': tariff
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm('billservice.view_radiusattrs')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return {}
        if id:
            item = RadiusAttrs.objects.get(id=id)
            form = RadiusAttrsForm(instance=item)
        elif nas_id:
            form = RadiusAttrsForm(initial={'nas': nas})
        elif tarif_id:
            form = RadiusAttrsForm(initial={'tarif': tariff, })

    return {
        'form': form,
        'status': False,
        'nas': nas,
        'tariff': tariff
    }


@ajax_request
@systemuser_required
def radiusattr_delete(request):
    if not (request.user.account.has_perm('billservice.delete_radiusattrs')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление радиус атрибутов')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = RadiusAttrs.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанный атрибут найден %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "message": "RadiusAttrs not found"
        }

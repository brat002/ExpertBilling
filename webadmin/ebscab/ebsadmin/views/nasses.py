# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.utils import systemuser_required
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.utils.decorators import render_to, ajax_request
from ebscab.utils.ssh import ssh_client
from nas.forms import NasForm
from nas.models import actions
from nas.models import Nas
from object_log.models import LogItem

from ebsadmin.tables import NasTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/nas/list.html')
def nas(request):
    if not (request.user.account.has_perm('nas.view_nas')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    res = Nas.objects.all()
    table = NasTable(res)
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
@render_to('ebsadmin/nas/edit.html')
def nas_edit(request):
    id = request.POST.get("id")
    item = None
    if request.method == 'POST':
        fill = request.POST.get("fill", False)
        if id:
            if not (request.user.account.has_perm('nas.change_nas')):
                messages.error(
                    request,
                    _(u'У вас нет прав на редактирование серверов доступа'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        else:
            if not (request.user.account.has_perm('nas.add_nas')):
                messages.error(
                    request,
                    _(u'У вас нет прав на создание серверов доступа'),
                    extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        if fill:
            if id:
                item = Nas.objects.get(id=id)
                form = NasForm(
                    initial=actions.get(request.POST.get("type", ''), {}),
                    instance=item)
            else:
                form = NasForm(
                    initial=actions.get(request.POST.get("type", ''), {}))
            return {
                'form': form,
                'status': False,
                'item': item
            }

        if id:
            item = Nas.objects.get(id=id)
            form = NasForm(request.POST, instance=item)
        else:
            form = NasForm(request.POST)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(
                request,
                _(u'Сервер доступа успешно сохранён.'),
                extra_tags='alert-success')
            return HttpResponseRedirect(reverse("nas"))
        else:
            messages.error(
                request,
                _(u'При сохранении сервера доступа возникли ошибки.'),
                extra_tags='alert-danger')
            return {
                'form': form,
                'status': False
            }
    else:
        if not (request.user.account.has_perm('nas.view_nas')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        id = request.GET.get("id")
        fill = request.GET.get("fill", False)
        nas_type = request.GET.get("nas_type", '')
        if id:
            item = Nas.objects.get(id=id)
            form = NasForm(initial=actions.get(nas_type, {}), instance=item)
        else:
            form = NasForm(initial=actions.get(nas_type, {}))

    return {
        'form': form,
        'item': item
    }


@ajax_request
@systemuser_required
def nas_delete(request):
    if not (request.user.account.has_perm('nas.delete_nas')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление серверов доступа')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = Nas.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанный сервер доступа найден %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        messages.success(request,
                         _(u'Сервер доступа успешно удалён.'),
                         extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(request,
                       _(u'При удалении сервера доступа возникли ошибки.'),
                       extra_tags='alert-danger')
        return {
            "status": False,
            "message": "Nas not found"
        }


@systemuser_required
@ajax_request
def testCredentials(request):
    if not (request.user.account.has_perm('billservice.testcredentials')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на тестирование подключения')
        }
    host, login, password = (request.POST.get('host'),
                             request.POST.get('login'),
                             request.POST.get('password'))
    try:
        a = ssh_client(host, login, password, '')
    except Exception, e:
        return {
            'status': False,
            'message': str(e)
        }
    return {
        'status': True
    }

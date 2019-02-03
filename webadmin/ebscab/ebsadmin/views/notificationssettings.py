# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import NotificationsSettingsForm
from billservice.utils import systemuser_required
from billservice.models import NotificationsSettings
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.utils.decorators import render_to, ajax_request
from object_log.models import LogItem

from ebsadmin.tables import NotificationsSettingsTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/notificationssettings_list.html')
def notificationssettings(request):
    if not (request.user.account.has_perm('billservice.view_notificationssettings')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    items = NotificationsSettings.objects.all()
    table = NotificationsSettingsTable(items)
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
@render_to('ebsadmin/common/edit_form.html')
def notificationssettings_edit(request):
    id = request.POST.get("id")
    item = None
    if request.method == 'POST':
        if id:
            model = NotificationsSettings.objects.get(id=id)
            form = NotificationsSettingsForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'billservice.change_notificationssettings')):
                messages.error(
                    request,
                    _(u'У вас нет прав на редактирование нотификаций'),
                    extra_tags='alert-danger')

                return HttpResponseRedirect(request.path)
        else:

            if not (request.user.account.has_perm(
                    'billservice.add_notificationssettings')):
                messages.error(request,
                               _(u'У вас нет прав на создание нотификаций'),
                               extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

            form = NotificationsSettingsForm(request.POST)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            form.save_m2m()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            return HttpResponseRedirect(reverse("notificationssettings"))
        else:
            return {
                'form': form,
                'status': False,
                'list_url': reverse('notificationssettings'),
                'list_label': _(u'Уведомления'),
                'form_action_url': reverse('notificationssettings_edit'),
                'form_legend': _(u'Параметры группы доступа'),
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm(
                'billservice.view_notificationssettings')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        if id:

            item = NotificationsSettings.objects.get(id=id)

            form = NotificationsSettingsForm(instance=item)

        else:
            form = NotificationsSettingsForm()

    return {
        'form': form,
        'status': False,
        'item': item,
        'list_url': reverse('notificationssettings'),
        'list_label': _(u'Уведомления'),
        'form_action_url': reverse('notificationssettings_edit'),
        'form_legend': _(u'Параметры уведомлений'),
    }


@ajax_request
@systemuser_required
def notificationssettings_delete(request):
    if not (request.user.account.has_perm(
            'billservice.delete_notificationssettings')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление групп доступа')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = NotificationsSettings.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанный способ уведомлений не найден %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "message": _(u'Notificationssettings not found')
        }

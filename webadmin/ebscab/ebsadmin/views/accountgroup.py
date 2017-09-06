# -*- coding: utf-8 -*-

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import AccountGroupForm
from billservice.utils import systemuser_required
from billservice.models import AccountGroup
from django_tables2.config import RequestConfig
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.utils.decorators import render_to, ajax_request
from object_log.models import LogItem

from ebsadmin.tables import AccountGroupTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/accountgroup/list.html')
def accountgroup(request):
    if not request.user.account.has_perm('billservice.view_accountgroup'):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')
    res = AccountGroup.objects.all()
    table = AccountGroupTable(res)
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
@render_to('ebsadmin/accountgroup/edit.html')
def accountgroup_edit(request):
    id = request.POST.get("id")
    item = None
    if request.method == 'POST':
        if id:
            model = AccountGroup.objects.get(id=id)
            form = AccountGroupForm(request.POST, instance=model)
            if not (request.user.account.has_perm(
                    'billservice.change_accountgroup')):
                messages.error(request,
                               _(u'Ошибка при сохранении группы.'),
                               extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = AccountGroupForm(request.POST)
            if not (request.user.account.has_perm(
                    'billservice.add_accountgroup')):
                messages.error(
                    request,
                    _(u'У вас нет прав на добавление групп абонентов'),
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
                             _(u'Группа успешно сохранена.'),
                             extra_tags='alert-success')
            return {
                'form': form,
                'status': True
            }
        else:
            messages.error(request,
                           _(u'Ошибка при сохранении группы.'),
                           extra_tags='alert-danger')
            return {
                'form': form,
                'status': False,
                'item': model
            }
    else:
        id = request.GET.get("id")
        if not request.user.account.has_perm('billservice.view_accountgroup'):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return {
                'status': False
            }

        if id:
            item = AccountGroup.objects.get(id=id)
            form = AccountGroupForm(instance=item)
        else:
            form = AccountGroupForm()

    return {
        'form': form,
        'status': False,
        'item': item
    }


@ajax_request
@systemuser_required
def accountgroup_delete(request):
    if not (request.user.account.has_perm('billservice.delete_accountgroup')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление групп пользователей')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = AccountGroup.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанная группа не найдена %s") % str(e)
            }

        log('DELETE', request.user, item)

        item.delete()
        messages.success(request,
                         _(u'Группа аккаунтов успешно удалена.'),
                         extra_tags='alert-success')
        return {
            "status": True
        }
    else:
        messages.error(request,
                       _(u'Ошибка при удалении группы.'),
                       extra_tags='alert-danger')
        return {
            "status": False,
            "message": _(u'AccountGroup not found')
        }

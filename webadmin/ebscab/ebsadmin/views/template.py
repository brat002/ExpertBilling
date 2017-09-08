# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import connection
from django.http import HttpResponseRedirect
from django.template import Template as DjangoTemplate
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from billservice.forms import TemplateForm, TemplateSelectForm
from billservice.helpers import systemuser_required
from billservice.models import Account, Organization, Template, Transaction
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import ajax_request, render_to
from object_log.models import LogItem

from ebsadmin.lib import instance_dict
from ebsadmin.tables import TemplateTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/common/list.html')
def template(request):
    if not (request.user.account.has_perm('billservice.view_template')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    res = Template.objects.all()
    table = TemplateTable(res)
    table_to_report = RequestConfig(
        request,
        paginate=(True if not request.GET.get('paginate') == 'False'
                  else False))
    table_to_report = table_to_report.configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    return {
        'list_url': reverse('template'),
        'list_header': _(u'Шаблоны документов'),
        'add_btn_url': reverse('template_edit'),
        'table': table
    }


@systemuser_required
@render_to('ebsadmin/template/select_window.html')
def templateselect(request):
    if not (request.user.account.has_perm('billservice.view_template')):
        messages.error(request,
                       _(u'У вас нет прав на просмотр списка шаблонов'),
                       extra_tags='alert-danger')
        return {}

    types = request.GET.getlist('type')
    form = TemplateSelectForm()
    form.fields['template'].queryset = \
        Template.objects.filter(type__id__in=types)
    return {
        'form': form
    }


@systemuser_required
@render_to('ebsadmin/template/edit.html')
def template_edit(request):
    id = request.GET.get("id")
    item = None
    if id:
        item = Template.objects.get(id=id)

    if request.method == 'POST':
        if item:
            form = TemplateForm(request.POST, instance=item)
        else:
            form = TemplateForm(request.POST)
        if id:
            if not (request.user.account.has_perm(
                    'billservice.change_template')):
                messages.error(request,
                               _(u'У вас нет прав на редактирование '
                                 u'шаблонов документов'),
                               extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        else:
            if not (request.user.account.has_perm('billservice.add_template')):
                messages.error(request,
                               _(u'У вас нет прав на создание шаблонов '
                                 u'документов'),
                               extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)

            return HttpResponseRedirect(reverse("template"))
        else:
            return {
                'form': form,
                'template': item
            }
    else:
        if not (request.user.account.has_perm('billservice.view_template')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        if item:
            form = TemplateForm(instance=item)
        else:
            form = TemplateForm()

    return {
        'form': form,
        'template': item
    }


@ajax_request
@systemuser_required
def template_delete(request):
    if not (request.user.account.has_perm('billservice.delete_template')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление шаблонов')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = Template.objects.get(id=id)
        except Exception, e:
            return {
                'status': False,
                'message': _(u"Указанный шаблон не найден %s") % str(e)
            }

        log('DELETE', request.user, item)

        item.delete()
        return {
            'status': True
        }
    else:
        return {
            'status': False,
            'message': 'Template not found'
        }


@ajax_request
@systemuser_required
def templates(request):
    if not (request.user.account.has_perm('billservice.template_view')):
        return {
            'status': True,
            'records': [],
            'totalCount': 0
        }

    fields = request.POST.get('fields', [])
    id = request.POST.get('id', None)
    type_id = request.POST.get('type_id', None)
    if id and id != 'None':
        items = Template.objects.filter(id=id)
        if not items:
            return {
                'status': False,
                'message': 'Template item with id=%s not found' % id
            }
        if len(items) > 1:
            return {
                'status': False,
                'message': 'Returned >1 items with id=%s' % id
            }
    elif type_id:
        items = Template.objects.filter(type__id=type_id)
    else:
        items = Template.objects.all()

    res = []
    for item in items:
        res.append(instance_dict(item, fields=fields, normal_fields=False))

    return {
        "records": res,
        'status': True,
        'totalCount': len(res)
    }


@ajax_request
@systemuser_required
def templates_save(request):
    id = request.POST.get('id')
    if id:
        if not (request.user.account.has_perm('billservice.change_template')):
            return {
                'status': False,
                'message': _(u"У вас нет прав на изменение шаблона")
            }
        item = Template.objects.get(id=id)
        form = TemplateForm(request.POST, instance=item)
    else:
        if not (request.user.account.has_perm('billservice.add_template')):
            return {
                'status': False,
                'message': _(u"У вас нет прав на добавление шаблона")
            }
        form = TemplateForm(request.POST)

    if form.is_valid():
        try:
            model = form.save(commit=False)
            model.save()
            res = {"status": True, 'id': model.id}

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
        except Exception, e:
            res = {
                "status": False,
                "message": str(e)
            }
    else:
        res = {
            "status": False,
            "errors": form._errors
        }

    return res


@ajax_request
@systemuser_required
def templaterender(request):
    if not request.user.account.has_perm('billservice.documentrender'):
        return {
            'status': False,
            'message': _(u'У вас нет прав на рендеринг документов')
        }

    form = TemplateForm(request.POST)
    if form.is_valid():
        templatetype = form.cleaned_data.get('type')
        t = DjangoTemplate(
            mark_safe(unicode(unicode(form.cleaned_data.get('body')))))
        data = ''

        cur = connection.cursor()
        if templatetype.id == 1:
            account = Account.objects.all()[0]
            c = {
                'account': account,
                'connection': cur
            }

        if templatetype.id == 2:
            account = Account.objects.all()[0]
            operator = Organization.objects.all()[0]
            c = {
                'account': account,
                'operator': operator,
                'connection': cur
            }

        if templatetype.id == 5:
            transaction = Transaction.objects.all()[0]
            operator = Organization.objects.all()[0]
            c = {
                'transaction': transaction,
                'operator': operator,
                'connection': cur
            }

        try:
            data = t.render(c)
        except Exception, e:
            data = u"Error %s" % str(e)

        res = {
            'success': True,
            'body': data.encode("utf-8", 'replace')
        }
    else:
        res = {
            "success": False,
            "errors": form._errors
        }

    return res

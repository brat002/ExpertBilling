# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.helpers import systemuser_required
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.billservice.forms import DealerForm, BankDataForm, DealerSelectForm
from ebscab.billservice.models import Dealer
from ebscab.lib.decorators import render_to, ajax_request
from object_log.models import LogItem

from ebsadmin.tables import DealerTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/dealer/list.html')
def dealer(request):
    if not (request.user.account.has_perm('billservice.view_dealer')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    res = Dealer.objects.all()
    table = DealerTable(res)

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
@render_to('ebsadmin/dealer/edit.html')
def dealer_edit(request):
    id = request.POST.get("id")
    item = None
    if request.method == 'POST':
        id = request.POST.get("dealer-id")
        if id:
            if not (request.user.account.has_perm('billservice.change_dealer')):
                messages.error(request,
                               _(u'У вас нет прав на редактирование дилеров'),
                               extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
            item = Dealer.objects.get(id=id)
            form = DealerForm(request.POST, instance=item, prefix='dealer')
            bank_form = BankDataForm(
                request.POST, instance=item.bank, prefix='bank')
        else:
            form = DealerForm(request.POST, prefix='dealer')
            bank_form = BankDataForm(request.POST, prefix='bank')

            if not (request.user.account.has_perm('billservice.add_dealer')):
                messages.error(request,
                               _(u'У вас нет прав на создание дилеров'),
                               extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)

        if form.is_valid() and bank_form.is_valid():
            model = form.save(commit=False)
            bank_model = bank_form.save(commit=False)
            bank_model.save()
            model.bank = bank_model
            model.save()
            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            return HttpResponseRedirect(reverse("dealer"))
        else:
            print form._errors
            return {
                'form': form,
                'status': False,
                'item': item,
                'bank_form': bank_form
            }
    else:
        id = request.GET.get("id")
        if not (request.user.account.has_perm('billservice.view_dealer')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        if id:
            item = Dealer.objects.get(id=id)
            form = DealerForm(instance=item, prefix='dealer')
            bank_form = BankDataForm(instance=item.bank, prefix='bank')
        else:
            form = DealerForm(prefix='dealer')
            bank_form = BankDataForm(prefix='bank')

    return {
        'form': form,
        'bank_form': bank_form,
        'item': item
    }


@systemuser_required
@render_to('ebsadmin/dealer/select_window.html')
def dealer_select(request):
    if not (request.user.account.has_perm('billservice.view_dealer')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return {}

    form = DealerSelectForm()
    return {
        'form': form
    }


@ajax_request
@systemuser_required
def dealer_delete(request):
    if not (request.user.is_staff == True and request.user.account.has_perm('nas.delete_nas')):
        return {
            'status': False,
            'message': _(u'У вас нет прав на удаление серверов доступа')
        }
    id = int(request.POST.get('id', 0)) or int(request.GET.get('id', 0))
    if id:
        try:
            item = Dealer.objects.get(id=id)
        except Exception, e:
            return {
                "status": False,
                "message": _(u"Указанный сервер доступа найден %s") % str(e)
            }
        log('DELETE', request.user, item)
        item.delete()
        return {
            "status": True
        }
    else:
        return {
            "status": False,
            "message": "Nas not found"
        }

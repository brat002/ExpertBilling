# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import SubAccountForm
from billservice.utils import systemuser_required
from billservice.models import Account, AccountAddonService, SubAccount
from django_tables2.config import RequestConfig as DTRequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import ajax_request, render_to
from object_log.models import LogItem

from ebsadmin.tables import AccountAddonServiceTable
from ebsadmin.views.utils import subaccount_ipn_delete


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/subaccount_edit.html')
def subaccountedit(request):
    id = request.GET.get("id")
    account_id = request.GET.get("account_id")
    ipn_ipinuse = None
    vpn_ipinuse = None
    subaccount = None
    table = None
    action_log_table = None
    if id:
        if not (request.user.account.has_perm(
                'billservice.change_subaccount')):
            messages.error(request,
                           _(u'У вас нет прав на редактирование субаккаунтов'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect(request.path)
        subaccount = SubAccount.objects.get(id=id)
        res = AccountAddonService.objects.filter(subaccount=subaccount)
        table = AccountAddonServiceTable(res)
        table_to_report = DTRequestConfig(request, paginate=False)
        table_to_report = table_to_report.configure(table)
        if table_to_report:
            return create_report_http_response(table_to_report, request)

        res = []
        prev = None
    else:
        if not (request.user.account.has_perm('billservice.add_subaccount')):
            messages.error(request,
                           _(u'У вас нет прав на создание аккаунтов'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect(request.path)
    if account_id:
        account = Account.objects.get(id=account_id)
    elif subaccount:
        account = subaccount.account
    else:
        account = None

    if request.method == 'POST':
        if subaccount and request.POST:
            form = SubAccountForm(request.POST, instance=subaccount)
        else:
            form = SubAccountForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            ipn_mac_address = form.cleaned_data.get("ipn_mac_address")
            vpn_ip_address = form.cleaned_data.get("vpn_ip_address")
            ipn_ip_address = form.cleaned_data.get("ipn_ip_address")
            ipv4_vpn_pool = form.cleaned_data.get("ipv4_vpn_pool")
            ipv4_ipn_pool = form.cleaned_data.get("ipv4_ipn_pool")
            ipv6_vpn_pool = form.cleaned_data.get("ipv6_vpn_pool")
            vpn_ipv6_ip_address = form.cleaned_data.get("vpn_ipv6_ip_address")

            model = form.save(commit=False)
            model.save()

            if id:
                log('EDIT', request.user, model)
            else:
                log('CREATE', request.user, model)
            messages.success(request,
                             _(u'Субаккаунт сохранён.'),
                             extra_tags='alert-success')
            return HttpResponseRedirect(
                "%s?id=%s" % (reverse("subaccount"), model.id))

        else:
            if form._errors:
                for k, v in form._errors.items():
                    if str(k) == '__all__':
                        k = ''
                    messages.error(request,
                                   '%s %s' % (k, ','.join(v)),
                                   extra_tags='alert-danger')
            return {
                'subaccount': subaccount,
                'account': account,
                'action_log_table': action_log_table,
                'accountaddonservice_table': table,
                'form': form
            }
    else:
        if not (request.user.account.has_perm('billservice.view_subaccount')):
            messages.error(request,
                           _(u'У вас нет прав на доступ в этот раздел.'),
                           extra_tags='alert-danger')
            return HttpResponseRedirect('/ebsadmin/')
        if subaccount:

            form = SubAccountForm(instance=subaccount)
        else:
            form = SubAccountForm(initial={'account': account, })
        return {
            'subaccount': subaccount,
            'account': account,
            'action_log_table': action_log_table,
            'accountaddonservice_table': table,
            'form': form
        }


@ajax_request
@systemuser_required
def subaccount_delete(request):
    if not (request.user.account.has_perm('billservice.delete_subaccount')):
        return {
            'status': True,
            'message': _(u'У вас нет прав на удаление субаккаунта')
        }
    id = request.POST.get('id') or request.GET.get('id')
    if id:
        # TODO: СДелать удаление субаккаунта с сервера доступа, если он там был
        item = SubAccount.objects.get(id=id)
        if item.vpn_ipinuse:
            log('DELETE', request.user, item.vpn_ipinuse)
            item.vpn_ipinuse.delete()

        if item.ipn_ipinuse:
            log('DELETE', request.user, item.ipn_ipinuse)
            item.ipn_ipinuse.delete()

        if item.vpn_ipv6_ipinuse:
            log('DELETE', request.user, item.vpn_ipv6_ipinuse)
            item.vpn_ipv6_ipinuse.delete()

        log('DELETE', request.user, item)

        if item.ipn_added:
            subaccount_ipn_delete(item.account, item, item.nas, 'IPN')

        item.delete()

        messages.success(request,
                         _(u'Субаккаунт удалён.'),
                         extra_tags='alert-success')
        return {
            'status': True
        }
    else:
        return {
            'status': False,
            'message': 'SubAccount not found'
        }

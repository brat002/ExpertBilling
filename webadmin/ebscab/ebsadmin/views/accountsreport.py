# -*- coding: utf-8 -*-

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import SearchAccountForm
from billservice.utils import systemuser_required
from billservice.models import Account
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import render_to

from ebsadmin.tables import AccountsReportTable


@systemuser_required
@render_to('ebsadmin/accounts_list.html')
def accountsreport(request):
    if not (request.user.account.has_perm('billservice.view_account')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    if request.method == 'GET':
        data = request.GET or request.POST
        if not data:
            form = SearchAccountForm()
            return {
                'form': form
            }

        form = SearchAccountForm(data)
        if form.is_valid():
            date_start, date_end = None, None
            account = (form.cleaned_data.get('account') +
                       form.cleaned_data.get('fullname') +
                       form.cleaned_data.get('contactperson') +
                       form.cleaned_data.get('username') +
                       form.cleaned_data.get('contract'))  # - concatenate tuples
            account_text = request.GET.get('account_text')
            username_text = request.GET.get('username_text')
            contract_text = request.GET.get('contract_text')
            fullname_text = request.GET.get('fullname_text')
            contactperson_text = request.GET.get('contactperson_text')
            id = form.cleaned_data.get('id')
            passport = form.cleaned_data.get('passport')
            created = form.cleaned_data.get('created')
            tariff = form.cleaned_data.get('tariff')
            street = form.cleaned_data.get('street')
            room = form.cleaned_data.get('room')
            city = form.cleaned_data.get('city')
            row = form.cleaned_data.get('row')
            house = form.cleaned_data.get('house')
            house_bulk = form.cleaned_data.get('house_bulk')
            ballance = form.cleaned_data.get('ballance')
            vpn_ip_address = form.cleaned_data.get('vpn_ip_address')
            ipn_ip_address = form.cleaned_data.get('ipn_ip_address')
            ipn_mac_address = form.cleaned_data.get('ipn_mac_address')
            elevator_direction = form.cleaned_data.get('elevator_direction')
            nas = form.cleaned_data.get('nas')
            deleted = form.cleaned_data.get('deleted')
            ipn_status = form.cleaned_data.get('ipn_status')
            organization = form.cleaned_data.get('organization')
            phone = form.cleaned_data.get('phone')
            suppagreement = form.cleaned_data.get('suppagreement')
            addonservice = form.cleaned_data.get('addonservice')
            credit = form.cleaned_data.get('credit')
            status = int(form.cleaned_data.get('status', 0)or 0)

            if type(created) == tuple:
                date_start, date_end = created

            systemuser = form.cleaned_data.get('systemuser')

            if deleted:
                res = Account.objects.deleted_set()
            else:
                res = Account.objects.all()

            if id:
                res = res.filter(id=id)
            if room:
                res = res.filter(room__icontains=room)

            if account:
                res = res.filter(id__in=account)

            if account_text:
                res = res.filter(username__icontains=account_text)

            if username_text:
                res = res.filter(username__icontains=username_text)

            if contract_text:
                res = res.filter(contract__icontains=contract_text)

            if fullname_text:
                res = res.filter(fullname__icontains=fullname_text)

            if contactperson_text:
                res = res.filter(contactperson__icontains=contactperson_text)
            if systemuser:
                res = res.filter(systemuser=systemuser)

            if suppagreement:
                res = res.filter(
                    accountsuppagreement__suppagreement=suppagreement)

            if addonservice:
                res = res.filter(accountaddonservice__service=addonservice)
            if date_start:
                res = res.filter(created__gte=date_start)
            if date_end:
                res = res.filter(created__lte=date_end)

            if not (date_start and date_end) and created:
                res = res.filter(created=created)
            if tariff:
                res = res.extra(
                    where=['''\
billservice_account.id in (
    SELECT account_id
    FROM billservice_accounttarif
    WHERE id in (
        SELECT max(id)
        FROM billservice_accounttarif
        GROUP BY account_id
        HAVING account_id IN (SELECT id FROM billservice_account)
        AND MAX(datetime) <= now())
    AND tarif_id in %s
)'''],
                    params=[tuple(['%s' % x.id for x in tariff])])

            if city:
                res = res.filter(city=city)
            if street:
                res = res.filter(street__icontains=street)

            if house:
                res = res.filter(house__icontains=house)

            if row:
                res = res.filter(row=row)

            if elevator_direction:
                res = res.filter(elevator_direction=elevator_direction)

            if phone:
                res = res.filter(Q(phone_h__contains=phone) |
                                 Q(phone_m__contains=phone))

            if status:
                res = res.filter(status=status)

            if passport:
                res = res.filter(passport__icontains=passport)

            if vpn_ip_address:
                res = res.filter(subaccounts__vpn_ip_address=vpn_ip_address)

            if ipn_ip_address:
                res = res.filter(subaccounts__ipn_ip_address=ipn_ip_address)

            if ipn_mac_address:
                res = res.filter(
                    subaccounts__ipn_mac_address__icontains=ipn_mac_address)

            if nas:
                res = res.filter(subaccounts__nas__in=nas)

            if organization:
                res = res.filter(Q(organization__in=organization))

            if ipn_status and 'undefined' not in ipn_status:
                res = res.filter(
                    subaccounts__ipn_added='added' in ipn_status,
                    subaccounts__ipn_enabled='enabled')

            if type(ballance) == tuple:
                cond, value = ballance
                if cond == ">":
                    res = res.filter(ballance__gte=value)
                elif cond == "<":
                    res = res.filter(ballance__lte=value)
            elif ballance:
                res = res.filter(ballance=ballance)

            if type(credit) == tuple:
                cond, value = credit
                if cond == ">":
                    res = res.filter(credit__gte=value)
                elif cond == "<":
                    res = res.filter(credit__lte=value)
            elif credit:
                res = res.filter(credit=credit)

            res = res.distinct()
            table = AccountsReportTable(res)
            table_to_report = RequestConfig(
                request,
                paginate=(False if request.GET.get('paginate') == 'False'
                          else True))
            table_to_report = table_to_report.configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)

            return {
                'table': table,
                'form': form,
                'resultTab': True
            }

        else:
            return {
                'status': False,
                'form': form
            }
    else:
        form = SearchAccountForm()
        return {
            'form': form
        }

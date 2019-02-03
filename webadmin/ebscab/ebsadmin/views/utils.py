# -*- coding: utf-8 -*-

import json
from operator import __not__

import psycopg2
import psycopg2.extras
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from billservice.models import AddonService, PeriodicalService, TransactionType
from tasks import subass_delete, subass_recreate


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def gettransactiontypes(current=[]):
    res = []
    for t in TransactionType.objects.all():
        d = []
        if t.internal_name == 'PS_AT_START':
            pstypes = PeriodicalService.objects.filter(cash_method='AT_START')
            d = []
            for pstype in pstypes:
                key = 'PS_AT_START___%s' % pstype.id
                d.append({
                    'title': pstype.name,
                    'key': key,
                    'select': True if key in current else False
                })
        if t.internal_name == 'PS_AT_END':
            pstypes = PeriodicalService.objects.filter(cash_method='AT_END')
            d = []
            for pstype in pstypes:
                key = 'PS_AT_END___%s' % pstype.id
                d.append({
                    'title': pstype.name,
                    'key': key,
                    'select': True if key in current else False
                })

        if t.internal_name == 'PS_GRADUAL':
            pstypes = PeriodicalService.objects.filter(cash_method='GRADUAL')
            d = []
            for pstype in pstypes:
                key = 'PS_GRADUAL___%s' % pstype.id
                d.append({
                    'title': pstype.name,
                    'key': key,
                    'select': True if key in current else False
                })

        if t.internal_name == 'ADDONSERVICE_PERIODICAL_GRADUAL':
            pstypes = AddonService.objects.filter(sp_type='GRADUAL')
            d = []
            for pstype in pstypes:
                key = 'ADDONSERVICE_PERIODICAL_GRADUAL___%s' % pstype.id
                d.append({
                    'title': pstype.name,
                    'key': key,
                    'select': True if key in current else False
                })

        if t.internal_name == 'ADDONSERVICE_PERIODICAL_AT_START':
            pstypes = AddonService.objects.filter(sp_type='AT_START')
            d = []
            for pstype in pstypes:
                key = 'ADDONSERVICE_PERIODICAL_AT_START___%s' % pstype.id
                d.append({
                    'title': pstype.name,
                    'key': key,
                    'select': True if key in current else False
                })
        if t.internal_name == 'ADDONSERVICE_PERIODICAL_AT_END':
            pstypes = AddonService.objects.filter(sp_type='AT_END')
            d = []
            for pstype in pstypes:
                key = 'ADDONSERVICE_PERIODICAL_AT_END___%s' % pstype.id
                d.append({
                    'title': pstype.name,
                    'key': key,
                    'select': True if key in current else False
                })
        if t.internal_name == 'ADDONSERVICE_ONETIME':
            pstypes = AddonService.objects.filter(service_type='onetime')
            d = []
            for pstype in pstypes:
                key = 'ADDONSERVICE_ONETIME___%s' % pstype.id
                d.append({
                    'title': pstype.name,
                    'key': key,
                    'select': True if key in current else False
                })

        res.append({
            'title': t.name,
            'key': t.internal_name,
            'children': d,
            'isFolder': True if d else False,
            'select': True if t.internal_name in current else False
        })

    res = {
        'title': u'Все',
        'key': 'all',
        'children': res,
        'isFolder': True,
        'select': True
    }
    res = json.dumps(res, ensure_ascii=False)
    return res


def get_account_data(account):
    tariff = account.get_account_tariff()
    accounttarif = account.get_accounttariff()
    return {
        'account_id': account.id,
        'ballance': account.ballance,
        'credit': account.credit,
        'datetime': account.created,
        'tarif_id': tariff.id if tariff else '',
        'access_parameters_id': (tariff.access_parameters.id
                                 if tariff and tariff.access_parameters
                                 else ''),
        'time_access_service_id': (tariff.time_access_service.id
                                   if tariff and tariff.time_access_service
                                   else ''),
        'traffic_transmit_service_id': (tariff.traffic_transmit_service.id
                                        if (tariff and
                                            tariff.traffic_transmit_service)
                                        else ''),
        'cost': tariff.cost if tariff else '',
        'reset_tarif_cost': tariff.reset_tarif_cost if tariff else '',
        'settlement_period_id': (tariff.settlement_period.id
                                 if tariff and tariff.settlement_period
                                 else ''),
        'tarif_active': tariff.active if tariff else '',
        'acctf_id': accounttarif.id if accounttarif else '',
        'account_created': account.created,
        'disabled_by_limit': account.disabled_by_limit,
        'balance_blocked': account.balance_blocked,
        'allow_express_pay': account.allow_expresscards,
        'account_status': account.status,
        'username': account.username,
        'password': account.password,
        'require_tarif_cost': tariff.require_tarif_cost,
        'radius_traffic_transmit_service_id': (
            tariff.radius_traffic_transmit_service.id
            if tariff and tariff.radius_traffic_transmit_service
            else '')

    }


def get_subaccount_data(subaccount):
    return {
        'id': subaccount.id,
        'account_id': subaccount.account.id,
        'username': subaccount.username,
        'password': subaccount.password,
        'vpn_ip_address': subaccount.vpn_ip_address,
        'ipn_ip_address': subaccount.ipn_ip_address,
        'ipn_mac_address': subaccount.ipn_mac_address,
        'nas_id': subaccount.nas.id if subaccount.nas else '',
        'ipn_added': subaccount.ipn_added,
        'ipn_enabled': subaccount.ipn_enabled,
        'need_resync': subaccount.need_resync,
        'speed': subaccount.speed,
        'switch_id': subaccount.switch.id if subaccount.switch else '',
        'switch_port': subaccount.switch_port,
        'allow_dhcp': subaccount.allow_dhcp,
        'allow_dhcp_with_null': subaccount.allow_dhcp_with_null,
        'allow_dhcp_with_minus': subaccount.allow_dhcp_with_minus,
        'allow_dhcp_with_block': subaccount.allow_dhcp_with_block,
        'allow_vpn_with_null': subaccount.allow_dhcp_with_null,
        'allow_vpn_with_minus': subaccount.allow_vpn_with_minus,
        'allow_vpn_with_block': subaccount.allow_vpn_with_block,
        'associate_pptp_ipn_ip': subaccount.associate_pptp_ipn_ip,
        'associate_pppoe_ipn_mac': subaccount.associate_pppoe_ipn_mac,
        'ipn_speed': subaccount.ipn_speed,
        'vpn_speed': subaccount.vpn_speed,
        'allow_addonservice': subaccount.allow_addonservice,
        'allow_ipn_with_null': subaccount.allow_ipn_with_null,
        'allow_ipn_with_minus': subaccount.allow_ipn_with_minus,
        'allow_ipn_with_block': subaccount.allow_ipn_with_block,
        'vlan': subaccount.vlan,
        'vpn_ipv6_ip_address': subaccount.vpn_ipv6_ip_address,
        'ipv4_ipn_pool_id': subaccount.ipv4_ipn_pool_id,
        'ipv4_vpn_pool_id': subaccount.ipv4_vpn_pool_id,
    }


def get_nas_data(nas):
    if not nas:
        return {}
    return {
        'id': nas.id,
        'type': nas.type,
        'name': nas.name,
        'ipaddress': nas.ipaddress,
        'secret': nas.secret,
        'login': nas.login,
        'password': nas.password,
        'user_add_action': nas.user_add_action,
        'user_enable_action': nas.user_enable_action,
        'user_disable_action': nas.user_disable_action,
        'user_delete_action': nas.user_delete_action,
        'vpn_speed_action': nas.vpn_speed_action,
        'ipn_speed_action': nas.ipn_speed_action,
        'reset_action': nas.reset_action,
        'speed_vendor_1': nas.speed_vendor_1,
        'speed_vendor_2': nas.speed_vendor_2,
        'speed_attr_id1': nas.speed_attr_id1,
        'speed_attr_id2': nas.speed_attr_id2,
        'speed_value1': nas.speed_value1,
        'speed_value2': nas.speed_value2,
        'identify': nas.identify,
        'subacc_add_action': nas.subacc_add_action,
        'subacc_enable_action': nas.subacc_enable_action,
        'subacc_disable_action': nas.subacc_disable_action,
        'subacc_del_action': nas.subacc_delete_action,
        'subacc_ipn_speed_action': nas.subacc_ipn_speed_action,
        'acct_interim_interval': nas.acct_interim_interval,
    }


def subaccount_ipn_recreate(account, subaccount, nas, access_type):
    subass_recreate.delay(
        get_account_data(account),
        get_subaccount_data(subaccount),
        nas,
        access_type)


def subaccount_ipn_delete(account, subaccount, nas, access_type):
    subass_delete.delay(
        get_account_data(account),
        get_subaccount_data(subaccount),
        get_nas_data(nas),
        access_type)


class DBWrap:

    def __init__(self, dsn):
        self.connection = None
        self._cur = None
        self.dsn = dsn

    @property
    def cursor(self):
        if self.connection is None:
            self.connection = psycopg2.connect(self.dsn)
            # set autocommit transations
            self.connection.set_isolation_level(0)
            self._cur = self.connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor)
        elif not self._cur:
            self._cur = self.connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor)
        return self._cur


class ExtDirectStore(object):
    """
    Implement the server-side needed to load an Ext.data.DirectStore
    """

    def __init__(self, model, extras=[], root='records', total='total',
                 start='start', limit='limit', sort='sort', dir='dir',
                 groupby='groupby', groupdir='groupdir'):
        self.model = model
        self.root = root
        self.total = total
        self.extras = extras

        # paramNames
        self.start = start
        self.limit = limit
        self.sort = sort
        self.dir = dir
        self.groupby = groupby
        self.groupdir = groupdir

    def query(self, qs=None, **kw):
        paginate = False
        total = None
        order = False
        groupby = None
        if kw.has_key(self.groupby):
            groupby = kw.pop(self.groupby)
            groupdir = kw.pop(self.groupdir)

        if kw.has_key(self.start) and kw.has_key(self.limit) and \
                kw.get(self.limit) != -1:
            start = kw.pop(self.start)
            limit = kw.pop(self.limit)
            paginate = True

        if kw.has_key(self.sort) and kw.has_key(self.dir):
            sort = kw.pop(self.sort)
            dir = kw.pop(self.dir)
            order = True

            if dir == 'DESC':
                sort = '-' + sort

        if qs is not None:
            # Don't use queryset = qs or self.model.objects
            # because qs could be empty list (evaluate to False)
            # but it's actually an empty queryset that must have precedence
            queryset = qs
        else:
            queryset = self.model.objects

        queryset = queryset.filter(**kw)

        if groupby:
            queryset = queryset.order_by(
                "-%s" % groupby if groupdir == 'asc' else groupby)
        if order:
            queryset = queryset.order_by(sort)

        if not paginate:
            objects = queryset
            total = queryset.count()
        else:
            paginator = Paginator(queryset, limit)
            total = paginator.count

            try:
                page = paginator.page(int(start / limit) + 1)
            except (EmptyPage, InvalidPage), e:
                print e
                # out of range, deliver last page of results.
                page = paginator.page(paginator.num_pages)

            objects = page.object_list

        return objects, total

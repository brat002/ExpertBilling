# -*- coding: utf-8 -*-

import IPy

from billservice.helpers import systemuser_required
from billservice.models import IPInUse, IPPool, SubAccount
from ebscab.lib.decorators import ajax_request


@ajax_request
@systemuser_required
def getipfrompool(request):
    if not (request.user.account.has_perm('billservice.view_ippool')):
        return {
            'status': True,
            'records': [],
            'totalCount': 0
        }

    default_ip = '0.0.0.0'
    if default_ip:
        default_ip = IPy.IP(default_ip).int()
    pool_id = request.POST.get("pool_id")
    limit = int(request.POST.get("limit", 500))
    start = int(request.POST.get("start", 0))
    term = request.POST.get("term", '')
    if not pool_id:
        return {'records': [], 'status': False}
    pool = IPPool.objects.get(id=pool_id)
    ipinuse = IPInUse.objects.filter(pool=pool, disabled__isnull=True)

    accounts_ip = SubAccount.objects.values_list(
        'ipn_ip_address', 'vpn_ip_address', 'vpn_ipv6_ip_address')
    if term:
        ipinuse = ipinuse.filter(ip__contains=term)

    ipversion = 4 if pool.type < 2 else 6
    accounts_used_ip = []
    for accip in accounts_ip:
        if accip[0]:
            accounts_used_ip.append(IPy.IP(accip[0]).int())
        if accip[1]:
            accounts_used_ip.append(IPy.IP(accip[1]).int())
        if accip[2]:
            accounts_used_ip.append(IPy.IP(accip[2]).int())

    start_pool_ip = IPy.IP(pool.start_ip).int()
    end_pool_ip = IPy.IP(pool.end_ip).int()

    ipinuse_list = [IPy.IP(x.ip).int() for x in ipinuse]
    ipinuse_list += accounts_used_ip

    find = False
    res = []
    x = start_pool_ip
    i = 0
    while x <= end_pool_ip:
        if x not in ipinuse_list and x != default_ip:
            if not term or term and \
                    str(IPy.IP(x, ipversion=ipversion)).rfind(term) != -1:
                res.append(str(IPy.IP(x, ipversion=ipversion)))
            if len(res) == limit:
                break
            i += 1
        x += 1
    return {
        'totalCount': str(len(res)),
        'records': res,
        'status': True
    }


@ajax_request
@systemuser_required
def getipfrompool2(request):
    if not (request.user.account.has_perm('billservice.view_ippool')):
        return {
            'status': True,
            'records': [],
            'totalCount': 0
        }

    default_ip = '0.0.0.0'
    if default_ip:
        default_ip = IPy.IP(default_ip).int()
    pool_id = request.POST.get("pool_id") or request.GET.get("pool_id")
    limit = int(request.POST.get("limit", 500))
    start = int(request.POST.get("start", 0))
    if not pool_id:
        return {
            'records': [],
            'status': False
        }
    pool = IPPool.objects.get(id=pool_id)
    ipinuse = IPInUse.objects.filter(pool=pool, disabled__isnull=True)
    accounts_ip = SubAccount.objects.values_list(
        'ipn_ip_address', 'vpn_ip_address')
    ipversion = 4 if pool.type < 2 else 6
    accounts_used_ip = []
    for accip in accounts_ip:
        accounts_used_ip.append(IPy.IP(accip[0]).int())
        accounts_used_ip.append(IPy.IP(accip[1]).int())

    start_pool_ip = IPy.IP(pool.start_ip).int()
    end_pool_ip = IPy.IP(pool.end_ip).int()

    ipinuse_list = [IPy.IP(x.ip).int() for x in ipinuse]
    ipinuse_list += accounts_used_ip

    find = False
    res = []
    x = start_pool_ip
    i = 0
    while x <= end_pool_ip:
        if x not in ipinuse_list and x != default_ip:
            res.append(str(IPy.IP(x, ipversion=ipversion)))
            i += 1
        x += 1
    return [res[start:start + limit]]

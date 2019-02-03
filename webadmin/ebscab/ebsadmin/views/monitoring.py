# -*- coding: utf-8 -*-

from django.db.models import Sum

from billservice.utils import systemuser_required
from ebscab.utils.decorators import render_to, ajax_request
from object_log.models import LogItem
from radius.models import RadiusStat


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/monitoring.html')
def index(request):
    # radiusstat nasses
    nasses = (RadiusStat.objects
              .all()
              .values('nas', 'nas__name')
              .order_by('nas__name')
              .distinct())
    radiusstat_nasses = []
    for item in nasses:
        radiusstat_nasses.append((item.get('nas'), item.get('nas__name')))

    return {
        'radiusstat_nasses': radiusstat_nasses
    }


@systemuser_required
@ajax_request
def radiusstat(request):
    nas = request.GET.get('nas')
    if not nas:
        items = (RadiusStat.objects
                 .all()
                 .values('datetime')
                 .order_by('-datetime')
                 .annotate(active=Sum('active')))[:2000]
    else:
        items = (RadiusStat.objects
                 .filter(nas__id=nas)
                 .values('datetime')
                 .order_by('-datetime')
                 .annotate(active=Sum('active')))[:2000]

    items = sorted(items, key=lambda x: x.get('datetime'))
    res = []

    for item in items:
        res.append({
            "date": item.get('datetime').strftime('%Y/%m/%d %H:%M'),
            "active": item.get('active')
        })
    return {
        "records": res,
        'status': True,
        'totalCount': len(res)
    }

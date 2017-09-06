# -*- coding: utf-8 -*-

from django.db import connection

from billservice.utils import systemuser_required
from ebscab.lib.decorators import ajax_request
from object_log.models import LogItem

from ebsadmin.views.utils import dictfetchall


log = LogItem.objects.log_action


@ajax_request
@systemuser_required
def sql(request):
    if not (request.user.account.has_perm('billservice.rawsqlexecution')):
        return {
            'status': False,
            'records': [],
            'totalCount': 0
        }

    s = request.POST.get('sql', '')
    if not s:
        return {
            'status': False,
            'message': 'SQL not defined'
        }

    cur = connection.cursor()
    try:
        log('RAWSQL',
            request.user,
            request.user.account,
            data={'sql': unicode(s, errors="ignore")})
    except:
        pass

    try:
        cur.execute(s)
        res = dictfetchall(cur)
    except Exception, e:
        return {
            'status': False,
            'message': str(e)
        }

    return {
        "records": res,
        'status': True,
        'totalCount': len(res)
    }

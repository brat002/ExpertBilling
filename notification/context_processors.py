# -*- coding: utf-8 -*-
import datetime
from django.core.cache import cache
from django.conf import settings

def notices(request):
    if request.session.has_key('user'):
        user = request.session['user']
        cache_user = cache.get(user.id)
        if type(cache_user) == u'NoneType':
            if int(cache_user['count']) > settings.ACTIVATION_COUNT and not bool(cache_user['blocked']):
                cache.delete(user.id)
                cache.set(user.id, {'count':int(cache_user['count']),'last_date':cache_user['last_date'],'blocked':True,}, 86400*365)
            if int(cache_user['count']) > settings.ACTIVATION_COUNT and bool(cache_user['blocked']):
                time = datetime.datetime.now() - cache_user['last_date']
                if time.seconds > settings.BLOCKED_TIME:
                    cache.delete(user.id)
                    cache.set(user.id, {'count':0,'last_date':cache_user['last_date'],'blocked':False,}, 86400*365)
            return {
                    'user': user,
                    'status': bool(cache_user['blocked']),
                    }
        return {
                'user': user,
                }
    else:
        return HttpResponseRedirect('/login/')
        #return {
        #        'user': None,
        #        'status': True,
        #        }
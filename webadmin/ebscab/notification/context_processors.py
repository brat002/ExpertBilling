# -*- coding: utf-8 -*-
import datetime
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponseRedirect
from billservice.models import Operator
from django.contrib.auth.models import AnonymousUser


def footer(request):
    operator = Operator.objects.all()[:1]
    return {
            'operator':operator,
            }

def notices(request):
    if request.user and not isinstance(request.user, AnonymousUser):
        user = request.user
        cache_user = cache.get(str(user.id))
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

def setCurrency(request):
    return {
            'CURRENCY':settings.CURRENCY,
            }

def auth(request):
    """
    Returns context variables required by apps that use Django's authentication
    system.

    If there is no 'user' attribute in the request, uses AnonymousUser (from
    django.contrib.auth).
    """
    if hasattr(request, 'user'):
        user = request.user
    else:
        user = AnonymousUser()
    return {
        'user': user,
        'perms': PermWrapper(user),
    }


class PermLookupDict(object):
    def __init__(self, user, module_name):
        self.user, self.module_name = user, module_name

    def __repr__(self):
        return str(self.user.get_all_permissions())

    def __getitem__(self, perm_name):
        return self.user.has_perm("%s.%s" % (self.module_name, perm_name))

    def __nonzero__(self):
        return self.user.has_module_perms(self.module_name)

class PermWrapper(object):
    def __init__(self, user):
        self.user = user

    def __getitem__(self, module_name):
        return PermLookupDict(self.user, module_name)

    def __iter__(self):
        # I am large, I contain multitudes.
        raise TypeError("PermWrapper is not iterable.")

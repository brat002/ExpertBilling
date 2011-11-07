# -*- coding: utf-8 -*-
import datetime
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponseRedirect
from billservice.models import Operator 



def footer(request):
    operator = Operator.objects.all()[:1]
    return {
            'operator':operator,
            }

def notices(request):

        return {

                }

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
        from django.contrib.auth.models import AnonymousUser
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
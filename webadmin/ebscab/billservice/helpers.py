from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from billservice.models import SystemUser

def systemuser_required(func):

    def wrapper(request, *args, **kw):
        user=request.user  
        
        if not user.id:
            return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.get_full_path()),)
        else:
            if not isinstance(user.account, SystemUser):
                return HttpResponseRedirect(reverse('billservice_index'))

            return func(request, *args, **kw)
    return wrapper


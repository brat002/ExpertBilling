from django.http import HttpResponseRedirect
from django.utils.http import urlquote
from helpdesk.settings import LOGIN_URL

redirect_field_name = 'next'

def login_required(function):
    def wrap(request, *args, **kwargs):
            #this check the session if userid key exist, if not it will redirect to login page
            if not request.user.is_authenticated():
                path = urlquote(request.get_full_path())
                login_list = LOGIN_URL, redirect_field_name, path
                return HttpResponseRedirect('%s?%s=%s' % login_list)
            return function(request, *args, **kwargs)
    return wrap

#-*-coding=utf-8-*-
from django.http import Http404, HttpResponseRedirect, HttpResponse 
from billservice.models import SystemUser
from billservice import authenticate, log_in, log_out

from helpdesk.models import Ticket
from helpdesk.forms import LoginForm 
from lib.decorators import render_to

@render_to('helpdesk/login.html')
def _login(request):
    form = LoginForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            try:
                user = SystemUser.objects.get(username=form.cleaned_data['username'])
                if user.password == form.cleaned_data['password']:
                    user = authenticate(username=user.username, password=form.cleaned_data['password'])
                    log_in(request, user)
                    return HttpResponseRedirect('/helpdesk/')
                else:
                    form = LoginForm(initial={'username': form.cleaned_data['username']})
                    return {
                            'form':form,
                            }
            except :
                form = LoginForm(initial={'username': form.cleaned_data['username']})
                return {
                        'form':form,
                        }
    else:
        form = LoginForm(initial={'username': request.POST.get('username', None)})
        return {

                'form':form,
                }
        
@render_to('helpdesk/index.html')
def index(request):
    return {
            'index':'index',
            }




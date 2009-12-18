
#-*-coding:utf-8-*-

from django.http import Http404, HttpResponseRedirect, HttpResponse 
from billservice.models import SystemUser
from billservice import authenticate, log_in, log_out

from helpdesk.models import Ticket
from helpdesk.forms import LoginForm 
from lib.decorators import render_to
from billservice.models import SystemGroup, SystemUser
from django.contrib.contenttypes.models import ContentType

@render_to('helpdesk/manage_ticket.html')
def manage_tickets(request):
    system_group = SystemGroup.objects.all()
    return {"departaments":system_group}

@render_to('helpdesk/index_tickets.html')
def index_tickets(reuqest):
    system_group = SystemGroup.objects.all()
    return {"departaments":system_group}

def update_owner_ticket(request):
    id_ticket = request.GET.get('id',None)
    object = request.GET.get('object',None)
    object_id = request.GET.get('object_id',None)
    print id_ticket
    try:
        ticket = Ticket.objects.get(id = int(id_ticket))
    except:
        raise Http404
    
    if object=='departament':
         ctype = ContentType.objects.get_for_model(SystemGroup)
    elif object=='user':
         ctype = ContentType.objects.get_for_model(SystemUser)
    ticket.content_type = ctype
    ticket.object_id = object_id
    ticket.save()
    return HttpResponse(True, mimetype="text/plain")



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


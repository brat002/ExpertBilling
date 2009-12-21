
#-*-coding:utf-8-*-
from datetime import datetime
from django.http import Http404, HttpResponseRedirect, HttpResponse 
from billservice.models import SystemUser, SystemGroup, Account
from billservice import authenticate, log_in, log_out

from helpdesk.models import Ticket
from helpdesk.forms import LoginForm, TicketForm 
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

def ajax_update_owner_ticket(request):
    id_ticket = request.GET.get('id',None)
    object = request.GET.get('object',None)
    object_id = request.GET.get('object_id',None)
    try:
        ticket = Ticket.objects.get(id = int(id_ticket))
    except:
        raise Http404
    if object == 'departament':
         ctype = ContentType.objects.get_for_model(SystemGroup)
    elif object == 'user':
         ctype = ContentType.objects.get_for_model(SystemUser)
    ticket.content_type = ctype
    ticket.object_id = object_id
    ticket.save()
    return HttpResponse(True, mimetype="text/plain")

@render_to('helpdesk/ajax_load_table_tickets.html')
def ajax_load_table_tickets(request):
    object = request.GET.get('object',None)
    object_id = request.GET.get('object_id',None)
    if object ==  'departament':
        try:
            object = SystemGroup.objects.get(id=int(object_id))
        except SystemGroup.DoesNotExist:
            raise Http404
    if object ==  'user':
        try:
            object = SystemUser.objects.get(id=int(object_id))
        except SystemUser.DoesNotExist:
            raise Http404
            
       
    return {"object":object}


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

@render_to('helpdesk/ticket_add.html')
def ticket_add(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            account = Account.objects.get(id=form.cleaned_data['user'])
            ticket = Ticket(
                            account = account,
                            email = form.cleaned_data['email'],
                            source = form.cleaned_data['source'],
                            subject = form.cleaned_data['subject'],
                            body = form.cleaned_data['text'],    
                            status = form.cleaned_data['status'],
                            type = form.cleaned_data['type'],
                            additional_status = form.cleaned_data['additional_status'], 
                            priority = form.cleaned_data['priority'],
                            created = datetime.now(),
                            last_update = datetime.now(),
                            assign_date = datetime.now(),
                            )
            if form.cleaned_data['assigned_to']:
                assigned_to = form.cleaned_data['assigned_to'].split('_')
                assigned_to_content_type = ContentType.objects.get(model=assigned_to[0])
                ticket.content_type = assigned_to_content_type
                ticket.object_id = assigned_to[1]   
            ticket.save() 
            return {
                    'form':form,
                    'ok_message':u'Все Работает',
                    }
        else:
            return {
                    'form':form,
                    'error_message':u'Проверьте поля формы',
                    }
    else:
        return {
                'form':TicketForm(),
                }

@render_to('helpdesk/ticket_edit.html')
def ticket_edit(request, ticket_id):
    addon_text = ''
    try:
        ticket = Ticket.objects.get(id = ticket_id)
    except:
        raise Http404
    if request.method == 'POST':
        ticket.account = ticket.account,
        ticket.email = form.cleaned_data['email'],
        ticket.source = form.cleaned_data['source'],
        ticket.subject = form.cleaned_data['subject'],
        ticket.body = form.cleaned_data['text'],    
        ticket.status = form.cleaned_data['status'],
        ticket.type = form.cleaned_data['type'],
        ticket.additional_status = form.cleaned_data['additional_status'], 
        ticket.priority = form.cleaned_data['priority'],
        ticket.created = ticket.created
        ticket.last_update = datetime.now(),
        if form.cleaned_data['assigned_to']:
            assigned_to = form.cleaned_data['assigned_to'].split('_')
            assigned_to_content_type = ContentType.objects.get(model=assigned_to[0])
            ticket.content_type = assigned_to_content_type
            ticket.object_id = assigned_to[1]
        if ticket.save():
            addon_text = u'Тикет сохранен'
        else:
            addon_text = u'Ошибка при сожранении'
    user = u'%s_%s' % (ticket.content_type,ticket.object_id)
    data = {
            'user':user,
            'account':ticket.account,
            'email':ticket.email,
            'source':ticket.source,
            'subject':ticket.subject,
            'body':ticket.text,    
            'status':ticket.status,
            'type':ticket.type,
            'additional_status':ticket.additional_status, 
            'priority':ticket.priority,
           } 
    form = TicketForm(data)
    return {
            'form':form,
            'addon_text':addon_text,
            }
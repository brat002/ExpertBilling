
#-*-coding:utf-8-*-
from datetime import datetime

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.contenttypes.models import ContentType
 
from billservice.models import SystemUser, SystemGroup, Account, AccountTarif, TPChangeRule, AccountAddonService
from billservice import authenticate, log_in, log_out
from billservice.models import SystemGroup, SystemUser
from billservice.forms import ChangeTariffForm

from helpdesk.models import Ticket, Comment, TicketHistrory, NEW, TicketHistrory, Note, UserAttention, CLOSED, RESOLVED
from helpdesk.decorators import login_required
from helpdesk.forms import LoginForm, TicketForm, TicketEditForm, CommentForm, UserFilter, ChangeAccountStatusForm, ChangeAccountPasswordForm, ChangeUserInformation 
from lib.decorators import render_to, ajax_request
from django.utils import simplejson
from billservice.utility import settlement_period_info

@login_required
@render_to('helpdesk/manage_ticket.html')
def manage_tickets(request):
    system_group = SystemGroup.objects.all()
    return {"departaments":system_group}

@login_required
@render_to('helpdesk/index_tickets.html')
def index_tickets(reuqest):
    system_group = SystemGroup.objects.all()
    return {"departaments":system_group}

   
def ajax_archived_tickets(request):
    if request.method=="POST":
        ticket_id = int(request.POST['ticket_id'])
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            if ticket.status == CLOSED or ticket.status == RESOLVED:
                ticket.archived = True
                ticket.save()
        except Ticket.DoesNotExist:
            pass
        return HttpResponse(True, mimetype="text/plain")
    
def ajax_update_owner_ticket(request):
    id_ticket = request.GET.get('id',None)
    object = request.GET.get('object',None)
    object_id = request.GET.get('object_id',None)
    try:
        ticket = Ticket.objects.get(id = int(id_ticket))
    except Ticket.DoesNotExist:
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
    object_name = request.GET.get('object',None)
    object_id = request.GET.get('object_id',None)
    count = request.GET.get('count',10)
    order_by = request.GET.get('order_by','id')
    order_by_reverse = request.GET.get('order_by_reverse',False)
    if object_name ==  'departament':
        try:
            object = SystemGroup.objects.get(id=int(object_id))
        except SystemGroup.DoesNotExist:
            raise Http404
    if object_name ==  'user':
        try:
            object = SystemUser.objects.get(id=int(object_id))
        except SystemUser.DoesNotExist:
            raise Http404
    return { "order_by":order_by,"order_by_reverse":order_by_reverse, "count":count, "object":object, 'object_name':object_name}

def ajax_deleted_tickets(request):
    """
    Только для админа {ДОДЕЛАТЬ}
    """
    if request.method == "POST":
        ids_tickets = request.POST['ids_tickets']
        ids_tickets = simplejson.loads(ids_tickets)
        tickets = Ticket.objects.filter(id__in=ids_tickets).delete()
        return HttpResponse(True, mimetype="text/plain")
    
@render_to('helpdesk/login.html')
def _login(request):
    form = LoginForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            try:
                user = SystemUser.objects.get(username=form.cleaned_data['username'])
                if user.text_password == form.cleaned_data['password']:
                    user = authenticate(username=user.username, password=form.cleaned_data['password'])
                    log_in(request, user)
                    return HttpResponseRedirect('/helpdesk/tickets/')
                else:
                    form = LoginForm(initial={'username': form.cleaned_data['username']})
                    return {
                            'form':form,
                            }
            except:
                form = LoginForm(initial={'username': form.cleaned_data['username']})
                return {
                        'form':form,
                        }
    else:
        form = LoginForm(initial={'username': request.POST.get('username', None)})
        return {
                'form':form,
                }
        
def login_out(request):
    log_out(request)
    return HttpResponseRedirect('/helpdesk/')

@login_required        
@render_to('helpdesk/index.html')
def index(request):
    return {
            'index':'index',
            }

@login_required
@render_to('helpdesk/system_user_settings.html')
def system_user_settings(request, system_user_id):
    try:
        system_user = SystemUser.objects.get(id = system_user_id)
    except:
        raise Http404
    if request.method == 'POST':
        form = ChangeUserInformation(request.POST)
        if form.is_valid():
            system_user.text_password = form.cleaned_data['password']
            system_user.email = form.cleaned_data['email']
            system_user.save()
    else:
        data = {
                'email':system_user.email,
                'password':system_user.text_password,
                }
        form = ChangeUserInformation(initial=data)
    return {
            'form':form,
            }

@login_required
@render_to('helpdesk/user_info.html')
def user_info(request, user_id):
    try:
        account = Account.objects.get(id = user_id)
    except Account.DoesNotExist:
        raise Http404
    status_form = ChangeAccountStatusForm(initial={'status': account.status,}) 
    password_form = ChangeAccountPasswordForm(initial={'password': account.password,})
    try:
        ballance = account.ballance - account.credit
        ballance = u'%.2f' % ballance
    except:
        ballance = 0
    account_tariff_id =  AccountTarif.objects.filter(account = account, datetime__lt=datetime.now()).order_by('-datetime')[:1]
    account_tariff = account_tariff_id[0]
    tariffs = TPChangeRule.objects.filter(ballance_min__lte=account.ballance, from_tariff = account_tariff.tarif)
    #kwargs = {'':True,}
    tariff_form = ChangeTariffForm(account, account_tariff, with_date = True)  
    return {
            'account':account,
            'status_form':status_form,
            'password_form':password_form,
            'ballance':ballance,
            'tariff_form':tariff_form,
            'tariff':account_tariff,
            'tariff_objects':tariffs,
            }     

@login_required
@render_to('helpdesk/filter_form.html')
def filter_form(request):
    if request.method == 'GET':
        from lib.paginator import SimplePaginator
        form = UserFilter(request.GET)
        qs = {}
        if form.is_valid():
            data = form.__dict__['data']
            form_keys = form.cleaned_data.keys()
            keys = data.keys() 
            for key in keys:
                if key in form_keys and data[key] != '':
                    qs[str(key)] = data[key]
        users = Account.objects.filter(**qs).order_by('id')
        order_field = request.GET.get('field', 'id') 
        way = request.GET.get('way', 'esc')     
        if way == 'esc':
            users = users.order_by(order_field)
        else:
            users = users.order_by('-%s' %order_field)
        filter_form = UserFilter(initial = qs)
        paginator = SimplePaginator(request, users, 2, 'page')
    return {
            'filter_form':UserFilter(initial = qs),
            'users':paginator.get_page_items(),
            'paginator': paginator,
            'order_field':order_field,
            'way':way,
            }

@render_to('helpdesk/get_users.html')
def get_users(request):
    if request.method == 'GET':
        from lib.paginator import SimplePaginator
        form = UserFilter(request.GET)
        qs = {}
        if form.is_valid():
            data = form.__dict__['data']
            keys = data.keys() 
            for key in keys:
                if data[key] != '':
                    qs[str(key)] = data[key]
        users = Account.objects.filter(**qs).order_by('id')
        paginator = SimplePaginator(request, users, 2, 'page')     
    return {
            'users':paginator.get_page_items(),
            'paginator': paginator,
            }

@login_required
@render_to('helpdesk/ticket_add.html')
def ticket_add(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            account = Account.objects.get(username=form.cleaned_data['user'])
            ticket = Ticket(
                            account = account,
                            email = form.cleaned_data['email'],
                            source = form.cleaned_data['source'],
                            subject = form.cleaned_data['subject'],
                            body = form.cleaned_data['text'],    
                            status = NEW,
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
            if request.POST.has_key('save_ticket'):
                return HttpResponseRedirect('/helpdesk%s' % ticket.get_absolute_url()) 
            elif request.POST.has_key('save_tickets'):
                return HttpResponseRedirect('/helpdesk/tickets/')
            else:
                raise Http404
        else:
            return {
                    'form':form,
                    'error_message':u'Проверьте поля формы',
                    }
    else:
        return {
                'form':TicketForm(),
                }

@login_required
@render_to('helpdesk/ticket_show_comments.html')
def ticket_show_comments(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id = ticket_id)
    except Ticket.DoesNotExist:
        raise Http404
    notes = Note.objects.filter(ticket = ticket)
    return {
            'notes':notes,
            }
    
    
@login_required
@render_to('helpdesk/ticket_edit.html')
def ticket_edit(request, ticket_id):
    addon_text = ''
    try:
        ticket = Ticket.objects.get(id = ticket_id)
    except Ticket.DoesNotExist:
        raise Http404
    if request.user ==  ticket.assigned_to:
        if request.method == 'POST':
            form = TicketEditForm(request.POST)
            if form.is_valid():  
                ticket.status = form.cleaned_data['status']
                ticket.additional_status = form.cleaned_data['additional_status'] 
                ticket.last_update = datetime.now()
                if form.cleaned_data['assigned_to']:
                    model_name, user_id = form.cleaned_data['assigned_to'].split('_')
                    ticket.content_type = ContentType.objects.get(model=model_name) 
                    ticket.object_id = user_id
                    ticket.assign_date = datetime.now()
                ticket.save()
        disabled = False
    else:
        disabled = True
    data = {}
    if ticket.content_type: 
        user = u'%s_%s' % (ticket.content_type.model,ticket.object_id)
        data['assigned_to'] = user
    data['status'] = ticket.status[0]
    data['additional_status'] = ticket.additional_status[0] 
    comments = Comment.objects.filter(ticket = ticket)
    history_items = TicketHistrory.objects.filter(ticket = ticket)
    try:
        open_date = history_items.filter(action__contains = u'на Открыт').order_by('-created')[0]
        
    except IndexError:
        open_date = None  
    try:
        close_date = history_items.filter(action__contains = u'на Закрыт').order_by('-created')[0]
    except IndexError:
        close_date = None
    form = TicketEditForm(data)
    request.session['current_ticket'] = ticket.id
    request.session['current_account'] = ticket.account.id 
    return {
            'disabled':disabled,
            'form':form,
            'addon_text':addon_text,
            'comment_form':CommentForm(initial = {'text':u'Введите комментарий',}),
            'ticket':ticket,
            'comments':comments,
            'history_items':history_items,
            'ticket':ticket,
            'open_date':open_date,
            'close_date':close_date,
            }

@login_required
def comment_add(request, ticket_id):
    print request.FILES
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = Ticket.objects.get(id=ticket_id)
            content_type = ContentType.objects.get(model='systemuser')
            comment = Comment(
                              ticket = ticket,
                              content_type = content_type,
                              object_id = request.user.id,
                              body = form.cleaned_data['text'],
                              time = form.cleaned_data['time'],
                              created = datetime.now(),
                              )
            if form.cleaned_data['file']:
                comment.file.save(request.FILES['file'].name, request.FILES['file'])
            comment.save()  
            history_item = TicketHistrory(
                                          ticket = ticket,
                                          user = request.user,
                                          action = u'Добавлен комментарий',
                                          created = datetime.now(), 
                                          )
            history_item.save()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
@render_to('helpdesk/ticket_new.html')
def tickets_new(request):
    new_status = u'%s' %NEW
    tickets = Ticket.objects.filter(status=new_status, content_type__isnull = True).order_by('-created')
    return {
            'tickets':tickets,
            }
    
@login_required
@render_to('helpdesk/tickets_attention.html')
def tickets_attention(request):
    tickets = UserAttention.objects.filter(user = request.user).order_by('-created')
    return {
            'tickets':tickets,
            }

@login_required    
@ajax_request
def change_password(request, user_id):
    if request.method == 'POST':
        password = request.POST.get('new_password', '')
        try:
            account = Account.objects.get(id = int(user_id))
            change = True
        except Account.DoesNotExist:
            change = False
            message = u'Пользователя нет в базе!'
        if change:
            account.password = password
            account.save()
            message = u'Пароль изменен'
    return {
            'message':message,
            }

import random
import string
def _gen_password(length=8, chars=string.letters + string.digits):
    return ''.join([random.choice(chars) for i in range(length)])


@login_required    
@ajax_request
def gen_password(request):
    return {
            'password':_gen_password(),
            'message':u'Новый пароль сгенирирован',
            } 

@login_required    
@ajax_request
def change_status(request, user_id):
    if request.method == 'POST':
        status = request.POST.get('new_status', '')
        try:
            account = Account.objects.get(id = user_id)
            change = True
        except Account.DoesNotExist:
            change = False
            message = u'Пользователя нет в базе!!!!'
        if change:
            account.status = status
            account.save()
            message = u'Статус изменент'
    return {
            'message':message,
            }

@login_required    
@ajax_request
def ticket_accept(request):
    if request.method == 'POST':
        try:
            ticket_id = request.POST.get('ticket_id')
            ticket = Ticket.objects.get(id = ticket_id) 
        except Ticket.DoesNotExist:
            raise Http404
        ticket.content_type = ContentType.objects.get(model='systemuser') 
        ticket.object_id = request.user.id
        ticket.assign_date = datetime.now()
        ticket.save()
        return {
                'message':u'тикет принят',
                }

@login_required    
@ajax_request
def change_tariff(request, user_id):
    """
        settlement_period_info
        1 - дата начала действия тарифа
    """
    from datetime import datetime
    if request.method == 'POST':
        try:
            account = Account.objects.get(id = user_id)
        except Account.DoesNotExist:
            return {
                    'error_message':u'Пользователь не найден в базе',
                    }
        account_tariff_id =  AccountTarif.objects.filter(account = account, datetime__lt=datetime.now()).order_by('-datetime')[:1]
        account_tariff = account_tariff_id[0]  
        kwargs = {'with_date':True,}
        form = ChangeTariffForm(account, account_tariff, request.POST, **kwargs) 
        if form.is_valid():      
            rule = TPChangeRule.objects.get(id=form.cleaned_data['tariff_id'])
            tariff = AccountTarif.objects.create(
                                                    account = account,
                                                    tarif = rule.to_tariff,
                                                    datetime = form.cleaned_data['from_date'],  
                                                )
            return {
                     'ok_message':u'Тариф изменен',   
                    }
        else:
            return {
                    'error_message':u'Проверьте тариф',
                    }
    else:
        return {
                'error_message':u'Проверьте тариф',
                }
        
@login_required
def ticket_detail(request):
    if request.session.has_key('current_ticket'):
        return HttpResponseRedirect('/helpdesk/ticket/edit/%s/' % request.session['current_ticket'])
    raise Http404

@login_required
@render_to('helpdesk/tickets_history.html')
def tickets_history(request):
    tickets = Ticket.objects.all().order_by('-created')
    if request.session.has_key('current_ticket'):
        tickets = tickets.exclude(id = request.session['current_ticket'])
    return {
            'tickets':tickets,
            }

@login_required    
def ticket_user_info(request):
    if request.session.has_key('current_account'):
        return HttpResponseRedirect('/helpdesk/user/%s/' % request.session['current_account'])
    raise Http404
    


@render_to('helpdesk/report.html')
def report(request):
    return {
            
            }














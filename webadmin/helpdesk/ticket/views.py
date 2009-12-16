#-*-coding:utf-8-*-

from lib.decorators import render_to
from account.models import Departament
from ticket.models import Ticket
from django.contrib.auth.models import User
from django.http import HttpResponse
from pyorbited.simple import Client

@render_to('ticket/manage_ticket.html')
def manage_tickets(request):
    departaments = Departament.objects.all()
    tickets = Ticket.objects.filter(departament = None, owner = None)
    if request.method == 'POST':
        tickets = eval(request.POST.get('tickets',None))
        for new_ticket in tickets:
            ticket = Ticket.objects.get(id = new_ticket['id'])
            if new_ticket['object']=='departament':
                object = Departament.objects.get(id=new_ticket['object_id'])
                ticket.departament = object
                ticket.owner=None
            elif new_ticket['object']=='owner':
                object = User.objects.get(id=new_ticket['object_id'])
                ticket.owner = object
                ticket.departament=None
            ticket.save()
    return {"departaments":departaments, 'tickets':tickets}

@render_to('ticket/index_tickets.html')
def index_tickets(reuqest):
    departaments = Departament.objects.all()
    
    return {"departaments":departaments}
orbit = Client()

def test(request):    
    orbit.event(["/chat"], 'joined')
    return HttpResponse('ok')

def update_owner_ticket(request):
    new_ticket = eval(request.GET['ticket'])
    print new_ticket['id']
    ticket = Ticket.objects.get(id = int(new_ticket['id']))
    if new_ticket['object']=='departament':
         object = Departament.objects.get(id=new_ticket['object_id'])
         ticket.departament = object
         ticket.owner=None
    elif new_ticket['object']=='owner':
         object = User.objects.get(id=new_ticket['object_id'])
         ticket.owner = object
         ticket.departament=None
    ticket.save()
    return HttpResponse(True, mimetype="text/plain")
from django.contrib import admin
from ticket.models import Ticket, Type

admin.site.register(Ticket)
admin.site.register(Type)
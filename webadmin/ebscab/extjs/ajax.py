
#-*-coding:utf-8-*-
from datetime import datetime

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.contenttypes.models import ContentType
 
from billservice.models import SystemUser, SystemGroup, Account, AccountTarif, TPChangeRule, AccountAddonService
from billservice import authenticate, log_in, log_out
from billservice.models import SystemGroup, SystemUser
from billservice.forms import ChangeTariffForm

#from helpdesk.models import Ticket, Comment, TicketHistrory, NEW, TicketHistrory, Note, UserAttention, CLOSED, RESOLVED
#from helpdesk.decorators import login_required
#from helpdesk.forms import LoginForm, TicketForm, TicketEditForm, CommentForm, UserFilter, ChangeAccountStatusForm, ChangeAccountPasswordForm, ChangeUserInformation 
from lib.decorators import render_to, ajax_request
from django.utils import simplejson
from billservice.utility import settlement_period_info


def get_model_description(model, user):
    # check access rules
    return {}

@ajax_request
def ajax(request):
    if request.method == 'GET':
        return {"Test":"Ok"}
    # TODO: Return window content here


"""
#@login_required
#@render_to('helpdesk/ajax_load_table_tickets.html')
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

"""
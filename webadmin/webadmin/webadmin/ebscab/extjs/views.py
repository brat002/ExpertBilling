
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


@render_to('ext_base.html')
def index(request):
    return {}

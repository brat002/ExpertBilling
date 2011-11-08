#-*-coding:utf-8-*-


#from helpdesk.models import Ticket, Comment, TicketHistrory, NEW, TicketHistrory, Note, UserAttention, CLOSED, RESOLVED
#from helpdesk.decorators import login_required
#from helpdesk.forms import LoginForm, TicketForm, TicketEditForm, CommentForm, UserFilter, ChangeAccountStatusForm, ChangeAccountPasswordForm, ChangeUserInformation 
from lib.decorators import render_to, ajax_request



@render_to('ext_base.html')
def index(request):
    return {}

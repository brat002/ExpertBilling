from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from helpdesk.models import Queue, Ticket, FollowUp, PreSetReply, KBCategory
from helpdesk.models import EscalationExclusion, EmailTemplate, KBItem
from helpdesk.models import TicketChange, Attachment, IgnoreEmail
from django.utils.translation import ugettext as _

class QueueAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'email_address')
    fields = ('title', 'slug', 'email_address','allow_public_submission','escalate_days','new_ticket_cc','updated_ticket_cc',)
    

class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'assigned_to', 'submitter_email',)
    date_hierarchy = 'created'
    list_filter = ('assigned_to', 'status', )

class IgnoreEmailAdmin(admin.ModelAdmin):
    exclude = ('keep_in_mailbox',)

    
class TicketChangeInline(admin.StackedInline):
    model = TicketChange

class AttachmentInline(admin.StackedInline):
    model = Attachment

class FollowUpAdmin(admin.ModelAdmin):
    inlines = [TicketChangeInline, AttachmentInline]

class KBItemAdmin(admin.ModelAdmin):
    list_display = ('category', 'title', 'last_updated',)
    list_display_links = ('title',)


class HelpDeskAdminSite(AdminSite):
    def __init__(self, *args, **kwargs):
        super(HelpDeskAdminSite, self).__init__(*args, **kwargs)
        self.root_path = '/helpdesk/admin'
        self.app_name = 'helpdesk'
    
    def index(self, request, extra_context=None):
        extra_context = {'title':u""}
        return super(HelpDeskAdminSite, self).index(request, extra_context)

site = HelpDeskAdminSite()

site.register(Ticket, TicketAdmin)
site.register(Queue, QueueAdmin)
site.register(FollowUp, FollowUpAdmin)
site.register(PreSetReply)
site.register(EscalationExclusion)
site.register(EmailTemplate)
site.register(KBCategory)
site.register(KBItem, KBItemAdmin)
#site.register(IgnoreEmail,IgnoreEmailAdmin)

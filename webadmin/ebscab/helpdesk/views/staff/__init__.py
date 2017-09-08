# -*- coding: utf-8 -*-

from helpdesk.views.staff.dashboard import dashboard
from helpdesk.views.staff.email import (
    email_ignore,
    email_ignore_add,
    email_ignore_del
)
from helpdesk.views.staff.followup import followup_edit
from helpdesk.views.staff.queue import queueselect, rss_list
from helpdesk.views.staff.reply import raw_details
from helpdesk.views.staff.report import report_index, run_report
from helpdesk.views.staff.search import delete_saved_query, save_query
from helpdesk.views.staff.ticket import (
    create_ticket,
    delete_ticket,
    edit_ticket,
    hold_ticket,
    mass_update,
    ticket_assign,
    ticket_info,
    ticket_list,
    tickets,
    unhold_ticket,
    update_ticket,
    view_ticket
)
from helpdesk.views.staff.ticket_cc import (
    ticket_cc,
    ticket_cc_add,
    ticket_cc_del
)
from helpdesk.views.staff.user_settings import user_settings

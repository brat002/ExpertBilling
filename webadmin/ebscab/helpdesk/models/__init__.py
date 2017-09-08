# -*- coding: utf-8 -*-

from helpdesk.models.attachment import Attachment
from helpdesk.models.email import EmailTemplate, IgnoreEmail
from helpdesk.models.escalation_exclusion import EscalationExclusion
from helpdesk.models.followup import FollowUp, FollowUpManager
from helpdesk.models.knowledge_base import KBCategory, KBItem
from helpdesk.models.queue import Queue
from helpdesk.models.reply import PreSetReply
from helpdesk.models.search import SavedSearch
from helpdesk.models.ticket import (
    prio,
    source_types,
    Ticket,
    TicketCC,
    TicketChange
)
from helpdesk.models.user_settings import UserSettings

# -*- coding: utf-8 -*-

from django.db import connection
from django.shortcuts import render

from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response

from helpdesk.utils import query_to_dict, staff_member_required
from helpdesk.models import Ticket
from helpdesk.tables import UnassignedTicketTable, UnpagedTicketTable


@staff_member_required
def dashboard(request):
    """
    A quick summary overview for users: A list of their own tickets, a table
    showing ticket counts by queue/status, and a list of unassigned tickets
    with options for them to 'Take' ownership of said tickets.
    """

    tickets = (Ticket.objects
               .filter(assigned_to=request.user.account)
               .exclude(status=Ticket.CLOSED_STATUS))

    ticket_table = UnpagedTicketTable(tickets)
    table_to_report = RequestConfig(
        request, paginate=False).configure(ticket_table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)

    unassigned_tickets = (Ticket.objects
                          .filter(assigned_to__isnull=True)
                          .exclude(status=Ticket.CLOSED_STATUS))

    unassigned_ticket_table = UnassignedTicketTable(unassigned_tickets)
    table_to_report = RequestConfig(request, paginate=False)
    table_to_report = table_to_report.configure(unassigned_ticket_table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    # The following query builds a grid of queues & ticket statuses,
    # to be displayed to the user. EG:
    #          Open  Resolved
    # Queue 1    10     4
    # Queue 2     4    12

    cursor = connection.cursor()
    cursor.execute("""
SELECT  q.id as queue,
        q.title AS name,
        COUNT(CASE t.status WHEN '1' THEN t.id WHEN '2' THEN t.id END) AS open,
        COUNT(CASE t.status WHEN '3' THEN t.id END) AS resolved
FROM  helpdesk_ticket t, helpdesk_queue q
WHERE q.id =  t.queue_id
GROUP BY queue, name
ORDER BY q.id;
    """)
    dash_tickets = query_to_dict(cursor.fetchall(), cursor.description)

    return render(request,
                  'helpdesk/dashboard.html',
                  {
                      'user_tickets': tickets,
                      'unassigned_tickets': unassigned_tickets,
                      'dash_tickets': dash_tickets,
                      'ticket_table': ticket_table,
                      'unassigned_ticket_table': unassigned_ticket_table
                  })

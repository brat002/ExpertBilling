# -*- coding: utf-8 -*-

from django.db import connection
from django.shortcuts import render
from django.utils.translation import ugettext as _

from helpdesk.utils import (
    bar_chart,
    line_chart,
    query_to_dict,
    staff_member_required
)
from helpdesk.models import Queue, Ticket


@staff_member_required
def report_index(request):
    number_tickets = Ticket.objects.all().count()
    return render(request,
                  'helpdesk/report_index.html',
                  {'number_tickets': number_tickets})


@staff_member_required
def run_report(request, report):
    priority_sql = []
    priority_columns = []
    for p in Ticket.PRIORITY_CHOICES:
        priority_sql.append(
            "COUNT(CASE t.priority WHEN '%s' THEN t.id END) AS \"%s\"" %
            (p[0], p[1]._proxy____cast()))
        priority_columns.append("%s" % p[1]._proxy____cast())
    priority_sql = ", ".join(priority_sql)

    status_sql = []
    status_columns = []
    for s in Ticket.STATUS_CHOICES:
        status_sql.append(
            "COUNT(CASE t.status WHEN '%s' THEN t.id END) AS \"%s\"" %
            (s[0], s[1]._proxy____cast()))
        status_columns.append("%s" % s[1]._proxy____cast())
    status_sql = ", ".join(status_sql)

    queue_sql = []
    queue_columns = []
    for q in Queue.objects.all():
        queue_sql.append(
            "COUNT(CASE t.queue_id WHEN '%s' THEN t.id END) AS \"%s\"" %
            (q.id, q.title))
        queue_columns.append(q.title)
    queue_sql = ", ".join(queue_sql)

    month_sql = []
    months = (
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec',
    )
    month_columns = []

    first_ticket = Ticket.objects.all().order_by('created')[0]
    first_month = first_ticket.created.month
    first_year = first_ticket.created.year

    last_ticket = Ticket.objects.all().order_by('-created')[0]
    last_month = last_ticket.created.month
    last_year = last_ticket.created.year

    periods = []
    year, month = first_year, first_month
    working = True

    while working:
        temp = (year, month)
        month += 1
        if month > 12:
            year += 1
            month = 1
        if (year > last_year) or (month > last_month and year >= last_year):
            working = False
        periods.append((temp, (year, month)))

    for (low_bound, upper_bound) in periods:
        low_sqlmonth = '%s-%02i-01' % (low_bound[0], low_bound[1])
        upper_sqlmonth = '%s-%02i-01' % (upper_bound[0], upper_bound[1])
        desc = '%s %s' % (months[low_bound[1] - 1], low_bound[0])
        month_sql.append("""
          COUNT(
             CASE 1 = 1
             WHEN (date(t.created) >= date('%s')
                  AND date(t.created) < date('%s')) THEN t.id END) AS "%s"
             """ % (low_sqlmonth, upper_sqlmonth, desc))
        month_columns.append(desc)

    month_sql = ", ".join(month_sql)
    queue_base_sql = """
            SELECT      q.title as queue, %s
                FROM    helpdesk_ticket t,
                        helpdesk_queue q
                WHERE   q.id =  t.queue_id
                GROUP BY queue
                ORDER BY queue;
                """
    user_base_sql = """
            SELECT      u.username as username, %s
                FROM    helpdesk_ticket t,
                        auth_user u
                WHERE   u.id =  t.assigned_to_id
                GROUP BY u.username
                ORDER BY u.username;
                """

    if report == 'userpriority':
        sql = user_base_sql % priority_sql
        columns = ['username'] + priority_columns
        title = _(u'User by priority')

    elif report == 'userqueue':
        sql = user_base_sql % queue_sql
        columns = ['username'] + queue_columns
        title = _(u'User by queue')

    elif report == 'userstatus':
        sql = user_base_sql % status_sql
        columns = ['username'] + status_columns
        title = _(u'User by status')

    elif report == 'usermonth':
        sql = user_base_sql % month_sql
        columns = ['username'] + month_columns
        title = _(u'User by month')

    elif report == 'queuepriority':
        sql = queue_base_sql % priority_sql
        columns = ['queue'] + priority_columns
        title = _(u'Queue by priority')

    elif report == 'queuestatus':
        sql = queue_base_sql % status_sql
        columns = ['queue'] + status_columns
        title = _(u'Queue by status')

    elif report == 'queuemonth':
        sql = queue_base_sql % month_sql
        columns = ['queue'] + month_columns
        title = _(u'Queue by month')

    cursor = connection.cursor()
    cursor.execute(sql)
    report_output = query_to_dict(cursor.fetchall(), cursor.description)

    data = []

    for record in report_output:
        line = []
        for c in columns:
            c = c.encode('utf-8')
            line.append(record[c])
        data.append(line)

    if report in ('queuemonth', 'usermonth'):
        chart_url = line_chart([columns] + data)
    elif report in ('queuestatus', 'queuepriority', 'userstatus',
                    'userpriority'):
        chart_url = bar_chart([columns] + data)
    else:
        chart_url = ''

    return render(request,
                  'helpdesk/report_output.html',
                  {
                      'headings': columns,
                      'data': data,
                      'chart': chart_url,
                      'title': title
                  })

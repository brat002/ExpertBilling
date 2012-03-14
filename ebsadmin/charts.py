from chartit import DataPool, Chart
from billservice.models import BalanceHistory
from django.shortcuts import render_to_response

def rainfall_pivot_chart_view(request):
    #Step 1: Create a PivotDataPool with the data we want to retrieve.
    ds = DataPool(
           series=
            [{'options': {
                'source': BalanceHistory.objects.filter(account__id=10)},
              'terms': [
                'balance',
                'datetime', 
                ]}])

    cht = Chart(
            datasource = ds, 
            series_options = 
              [{'options':{
                  'type': 'line',
                  'xAxis': 0,
                  'yAxis': 0,
                  'zIndex': 1},
                'terms':{
                  'datetime': [
                    'balance']}},
               ],
            chart_options = 
              {'title': {
                   'text': 'Weather Data by Month (on different axes)'},
               'xAxis': {
                    'type': 'datetime' ,
                    'title': {
                       'text': 'Month number'}}})
    #end_code
    #data = BalanceHistory.objects.filter(account__id__in=[11,10,12,13,14,15,16,17,18]).order_by("datetime")
    res = []
    total = []
    for i in xrange(10, 50):
        items = BalanceHistory.objects.filter(account__id=i).order_by("datetime")
        if not items: continue
        res.append((items[0].account.username, [(x.datetime, x.balance) for x in items]))
        
    return render_to_response('chartit.html', {'chart_list': [cht], 'res':res})


def session_count_chart_view(request):
    from django.db import connection
    cur = connection.cursor()
    cur.execute("select date_trunc('hours', date_start), count(*) FROM radius_activesession WHERE date_start between now() - interval '2 day' and now() GROUP BY date_trunc('hours', date_start) ORDER BY date_trunc('hours', date_start)  ASC")
    res = cur.fetchall()
   # res = []

        
    return render_to_response('sessionschart.html', {'res':res})

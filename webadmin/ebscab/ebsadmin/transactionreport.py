#-*-coding:utf-8-*-
from billservice.forms import TransactionReportForm
from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from billservice.models import Transaction, TransactionType, PeriodicalServiceHistory, PeriodicalService, TotalTransactionReport as TransactionReport, OneTimeServiceHistory, SubAccount, AccountTarif
from views import instance_dict
import billservice.models as bsmodels
from lib import QuerySetSequence, ExtDirectStore,IableSequence
import time
from django.core import serializers
from django.forms import model_to_dict
from django.db import connection
from django.db.models import Sum
import psycopg2.extras
import psycopg2
from django.conf import settings
# Очень важный момент, возврат результата из базы в виде словаря а не списка.
from psycopg2.extras import RealDictCursor 
from psycopg2 import IntegrityError, InternalError
try:
    import json
    json.loads("{}")
except:
    import simplejson as json

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

import django_tables2 as tables
from django_tables2.config import RequestConfig
from billservice.forms import SearchAccountForm
from billservice.models import Account
from django_tables2.utils import A
    
class FormatBlankColumn(tables.Column):
    def render(self, value):
        return "" if value is None else value

class FormatFloatColumn(tables.Column):
    def render(self, value):
        return "%.2f" % float(value)
    
class FormatDateTimeColumn(tables.Column):
    def render(self, value):
        return value.strftime("%d.%m.%Y %H:%M:%S") if value else ''
        
LEADING_PAGE_RANGE_DISPLAYED = TRAILING_PAGE_RANGE_DISPLAYED = 8
LEADING_PAGE_RANGE = TRAILING_PAGE_RANGE = 8
NUM_PAGES_OUTSIDE_RANGE = 10
ADJACENT_PAGES = 8


def digg_paginator( current, cnt):
        in_leading_range = in_trailing_range = False
        pages_outside_leading_range = pages_outside_trailing_range = range(0)
 
        if (cnt <= LEADING_PAGE_RANGE_DISPLAYED):
            in_leading_range = in_trailing_range = True
            page_numbers = [n for n in range(1, cnt + 1) if n > 0 and n <= cnt]           
        elif (current <= LEADING_PAGE_RANGE):
            in_leading_range = True
            page_numbers = [n for n in range(1, LEADING_PAGE_RANGE_DISPLAYED + 1) if n > 0 and n <= cnt]
            pages_outside_leading_range = [n + cnt for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
        elif (current > cnt - TRAILING_PAGE_RANGE):
            in_trailing_range = True
            page_numbers = [n for n in range(cnt - TRAILING_PAGE_RANGE_DISPLAYED + 1, cnt + 1) if n > 0 and n <= cnt]
            pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
        else: 
            page_numbers = [n for n in range(current - ADJACENT_PAGES, current + ADJACENT_PAGES + 1) if n > 0 and n <= cnt]
            pages_outside_leading_range = [n + cnt for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
            pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
        return {
            "page_numbers": page_numbers,
            "pages_outside_trailing_range": pages_outside_trailing_range,
            "pages_outside_leading_range": pages_outside_leading_range
            

        }
        
class DBWrap:
    def __init__(self, dsn):
        self.connection = None
        self._cur = None
        self.dsn = dsn

    @property
    def cursor(self):
        if self.connection is None:
            self.connection = psycopg2.connect(self.dsn)
            # set autocmmit transations
            self.connection.set_isolation_level(0)
            self._cur = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        elif not self._cur:
            self._cur = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return self._cur

dsn = 'host=%s port=%s dbname=%s user=%s password=%s' % (
settings.DATABASE_HOST,
settings.DATABASE_PORT,
settings.DATABASE_NAME,
settings.DATABASE_USER,
settings.DATABASE_PASSWORD
)

db = DBWrap(dsn)

TRANSACTION_MODELS = {"PS_GRADUAL":'PeriodicalServiceHistory',
                        "PS_AT_END":'PeriodicalServiceHistory',
                        "PS_AT_START":'PeriodicalServiceHistory',
                        "TIME_ACCESS": "TimeTransaction",
                        "NETFLOW_BILL":'TrafficTransaction',
                        "END_PS_MONEY_RESET":'Transaction',
                        "MANUAL_TRANSACTION":'Transaction',
                        "ACTIVATION_CARD":'Transaction',
                        "ONETIME_SERVICE":'OneTimeServiceHistory',
                        "OSMP_BILL":'Transaction',
                        "ADDONSERVICE_WYTE_PAY":'AddonServiceTransaction',
                        "ADDONSERVICE_PERIODICAL_GRADUAL":'AddonServiceTransaction',
                        "ADDONSERVICE_PERIODICAL_AT_START":'AddonServiceTransaction',
                        "ADDONSERVICE_PERIODICAL_AT_END":'AddonServiceTransaction',
                        "ADDONSERVICE_ONETIME":'AddonServiceTransaction',
                        "PAY_CARD":'Transaction',
                        "CASSA_TRANSACTION":'Transaction',
                        "PAYMENTGATEWAY_BILL":'Transaction',
                        "BELARUSBANK_PAYMENT_IMPORT":'Transaction',
                        "WEBMONEY_PAYMENT_IMPORT":'Transaction',
                        "EASYPAY_PAYMENT_IMPORT":'Transaction',
                        "PRIORBANK_PAYMENT_IMPORT":'Transaction',
                        "BELPOST_PAYMENT_IMPORT":'Transaction',
                        "ERIP_PAYMENT_IMPORT":'Transaction',
                        "SHTRAF_PAYMENT":'Transaction',
                        "QUICKPAY_BILL":'Transaction',
                        "OSMP_CUSTOM_BILL":'Transaction',
                        "USERBLOCK_PAYMENT":'Transaction',
                        "MONEY_TRANSFER_TO":'Transaction',
                        "MONEY_TRANSFER_FROM":'Transaction',

                      }

#print bsmodels.__dict__
@ajax_request
@login_required
def transactionreport(request):

    data = json.loads(request.POST.get('data','{}'))
    form = TransactionReportForm(data)
    if form.is_valid():
        #items = PeriodicalServiceHistory.objects.all()[0:200]
        account = form.cleaned_data.get('account')
        date_start = form.cleaned_data.get('start_date')
        date_end = form.cleaned_data.get('end_date')
        systemusers = form.cleaned_data.get('systemuser')
        tariffs = form.cleaned_data.get('tarif')
        extra={}
        if data.get('limit',100)=='all':
            l=-1
        else:
            l=int(data.get('limit',100))
            extra={'start':int(data.get('start',0)), 'limit':l}
            
        if data.get('sort',''):
            extra['sort'] = data.get('sort','')
            extra['dir'] = data.get('dir','asc')
        if data.get('groupBy',''):
            extra['groupby'] = data.get('groupBy','')
            extra['groupdir'] = data.get('groupDir','asc')
            
        res=[]
        resitems = []
        TYPES={}
        TRTYPES={}
        LTYPES=[]
        for x in form.cleaned_data.get('transactiontype', ''):
            key=TRANSACTION_MODELS.get(x)
            model = bsmodels.__dict__.get(key)
            if key not in TYPES:
                TYPES[key]=[]
            if key not in TRTYPES:
                TRTYPES[key]=[]
            TYPES[key].append(model)
            TRTYPES[key].append(TransactionType.objects.get(internal_name=x))
            LTYPES.append(x)
                
        #print TYPES
        #print ','.join(["'%s'" % x for x in LTYPES])
        items = TransactionReport.objects.filter(created__gte=date_start, created__lte=date_end).order_by('-created')
        if account:
            items = items.filter(account=account)

        
        if systemusers:
            items = items.filter(systemuser__in=systemusers)
        if tariffs:
            items = items.filter(tariff__in=tariffs)
        
        if form.cleaned_data.get('transactiontype'):
            #print form.cleaned_data.get('transactiontype')
            items = items.filter(type__in=LTYPES)
        
        if form.cleaned_data.get('addonservice'):
            items = items.filter(service_id__in=[x.id for x in form.cleaned_data.get('addonservice')], type__in=['ADDONSERVICE_WYTE_PAY','ADDONSERVICE_PERIODICAL_GRADUAL','ADDONSERVICE_PERIODICAL_AT_START','ADDONSERVICE_PERIODICAL_AT_END','ADDONSERVICE_ONETIME'])
            
        if form.cleaned_data.get('periodicalservice'):
            items = items.filter(service_id__in=[x.id for x in form.cleaned_data.get('periodicalservice')], type__in=['PS_GRADUAL','PS_AT_END','PS_AT_START'])
            
        
        ds = ExtDirectStore(TransactionReport)
        items, totalcount = ds.query(items, **extra)
        res = tuple(items.values('id', 'service_name', 'table', 'created','tariff__name','summ','account__username', 'account__fullname', 'type', 'systemuser_id','bill','description','end_promise', 'promise_expired')) 
        #print items.query
        t=[{'name': 'id', 'sortable':True,'type':'integer'},
           {'name': 'service_name', 'sortable':True,'type':'string'},
           {'name': 'created', 'sortable':True,'type':'date'},
           {'name': 'tariff__name', 'sortable':True,'type':'string'},
           {'name': 'summ', 'sortable':True,'type':'float'},
           {'name': 'account', 'sortable':True,'type':'string'},
           {'name': 'type', 'sortable':True,'type':'string'},
           {'name': 'type__name', 'sortable':True,'type':'string'},
           {'name': 'systemuser', 'sortable':True,'type':'string'},
           {'name': 'bill', 'sortable':True,'type':'string'},
           {'name': 'descrition', 'sortable':True,'type':'string'},
           {'name': 'end_promise',  'sortable':True,'type':'date'},
           {'name': 'promise_expired', 'sortable':True,'type':'boolean'},]
        
        return {"records": res,  'status':True, 'totalCount':len(res), 'metaData':{'root': 'records',
                                             'totalProperty':'total', 
                                             
                                             'fields':t
                                             },
                "sortInfo":{
                "field": "created",
                "direction": "ASC",
                
               },
                                 
                }        

    else:

        return {'status':False, 'errors':form._errors}
        
    
@login_required
@render_to('djtables.html')
def transactionreport2(request):
    import django_tables2 as tables
    from django_tables2.config import RequestConfig
    from billservice.forms import TransactionReportForm, TransactionModelForm
    from billservice.models import TotalTransactionReport
    
    class FormatBlankColumn(tables.Column):
        def render(self, value):
            return "" if value is None else value

    class FormatFloatColumn(tables.Column):
        def render(self, value):
            return "%.2f" % float(value) if value else value
        
    class FormatDateTimeColumn(tables.Column):
        def render(self, value):
            return value.strftime("%d.%m.%Y %H:%M:%S") if value else ''
        
    class TotalTransactionReportTable(tables.Table):
        tariff__name = FormatBlankColumn()
        id = FormatBlankColumn()
        account = FormatBlankColumn()
        bill = FormatBlankColumn()
        description = FormatBlankColumn()
        service = FormatBlankColumn()
        type = FormatBlankColumn()

        summ = FormatFloatColumn()
        created = FormatDateTimeColumn()
        end_promise = FormatDateTimeColumn()
        promise_expired = FormatBlankColumn()
        class Meta:
            #attrs = {'class': 'table table-striped table-bordered table-condensed'}
            attrs = {'class': 'paleblue'}
            
            sequence = ("id", "account",  "type", "summ", "bill", "description", "end_promise", "promise_expired",  "service", "created")
            #model = TotalTransactionReport
            exclude = ( 'table', 'service_id','tariff__name', "tariff", "systemuser")

    if request.GET:
        data = request.GET
        print 1
        #pageitems = 100
        form = TransactionReportForm(data)
        if form.is_valid():
            #items = PeriodicalServiceHistory.objects.all()[0:200]
            page = int(request.GET.get("page", 1))
           
            if "all" in request.GET:
                per_page=10000000000000000
            else:
                 per_page = int(request.GET.get("per_page", 25))
            pageitems = per_page
            sort = request.GET.get("sort", '-created')
            account = form.cleaned_data.get('account')
            date_start = form.cleaned_data.get('start_date')
            date_end = form.cleaned_data.get('end_date')
            systemusers = form.cleaned_data.get('systemuser')
            promise = form.cleaned_data.get('promise')
            promise_expired = form.cleaned_data.get('promise_expired')
            accounts_str = ''
            if account:
                accounts_str = " and account_id in (%s)" %  ','.join(['%s' % x.id for x in account])
            systemusers_str = ''
            if systemusers:
                systemusers_str = " and systemuser_id in (%s)" %  ','.join(['%s' % x.id for x in systemusers])
            res=[]
            resitems = []
            TYPES={}
            TRTYPES={}
            LTYPES=[]
            cnt =0
            LIMIT = "LIMIT %s OFFSET %s" % (pageitems, (page-1)*pageitems, )
            for x in form.cleaned_data.get('transactiontype', 1):
                key=TRANSACTION_MODELS.get(x, "Transaction")
                model = bsmodels.__dict__.get(key)
                if key not in TYPES:
                    TYPES[key]=[]
                TYPES[key].append(x)
            transactiontypes = {}
            for tr in TransactionType.objects.all():
                transactiontypes[tr.internal_name] = tr.name
            cur = connection.cursor()
            
            summ = 0
            for x in TYPES:
                trtypes = TYPES.get(x)
                if trtypes:
                    type_id = " and type_id in (%s)" %  ','.join(["'%s'" % t for t in trtypes])
                else:
                    type_id = ""

                
                if x=="PeriodicalServiceHistory":
                    print type_id
                    pservices = {}
                    for pservice in PeriodicalService.objects.all():
                        pservices[pservice.id] = pservice.name
                    
                    cur.execute("SELECT count(*) as cnt FROM billservice_periodicalservicehistory WHERE True %s and created  between %%s and %%s %s;" % (accounts_str, type_id), (date_start, date_end, ))
                    cnt +=  dictfetchall(cur)[0]['cnt']
                    cur.execute("SELECT sum((-1)*summ) as summ FROM billservice_periodicalservicehistory WHERE True %s and created  between %%s and %%s %s;" % (accounts_str, type_id), (date_start, date_end, ))
                    result = cur.fetchone()
                    print "result", result
                    if result[0]:
                        summ +=  0 if not result[0] else result[0]     
                    cur.execute("SELECT id, service_id, (-1)*summ as summ, (SELECT username FROM billservice_account WHERE id=psh.account_id) as account, type_id as type, created FROM billservice_periodicalservicehistory as psh WHERE True %s and created  between %%s and %%s %s %s;" % (accounts_str, type_id, LIMIT), (date_start, date_end, ))
                    #print cur.query
                    items = []
                    res+=dictfetchall(cur)
                    for r in res:
                        r['service'] = pservices.get(r['service_id'], "")
                        items.append(r)
                    res = items
                if x=="OneTimeServiceHistory":
                    print type_id
                    pservices = {}
                    for pservice in OneTimeServiceHistory.objects.all():
                        pservices[pservice.id] = pservice.name
                    
                    cur.execute("SELECT count(*) as cnt FROM billservice_onetimeservicehistory WHERE True %s and created  between %%s and %%s %s;" % (accounts_str, type_id), (date_start, date_end, ))
                    cnt +=  dictfetchall(cur)[0]['cnt']
                    cur.execute("SELECT sum((-1)*summ) as summ FROM billservice_onetimeservicehistory WHERE True %s and created  between %%s and %%s %s;" % (accounts_str, type_id), (date_start, date_end, ))
                    result = cur.fetchone()
                    print "result", result
                    if result[0]:
                        summ +=  0 if not result[0] else result[0]     
                    cur.execute("SELECT id, service_id, (-1)*summ as summ, (SELECT username FROM billservice_account WHERE id=psh.account_id) as account, type_id as type, created FROM billservice_onetimeservicehistory as psh WHERE True %s and created  between %%s and %%s %s %s;" % (accounts_str, type_id, LIMIT), (date_start, date_end, ))
                    #print cur.query
                    items = []
                    res+=dictfetchall(cur)
                    for r in res:
                        r['service'] = pservices.get(r['service_id'], "")
                        items.append(r)
                    res = items
                if x=="AddonServiceTransaction":
                    print type_id
                    
                    cur.execute("SELECT count(*) as cnt FROM billservice_addonservicetransaction WHERE True %s and created  between %%s and %%s %s;" % (accounts_str, type_id), (date_start, date_end, ))
                    cnt +=  dictfetchall(cur)[0]['cnt']
                    cur.execute("SELECT sum((-1)*summ) as summ FROM billservice_addonservicetransaction WHERE True %s and created  between %%s and %%s %s;" % (accounts_str, type_id), (date_start, date_end, ))
                    summ +=  dictfetchall(cur)[0]['summ']
                    cur.execute("SELECT id, service_id, (-1)*summ as summ, (SELECT username FROM billservice_account WHERE id=psh.account_id) as account, type_id as type, created FROM billservice_addonservicetransaction as psh WHERE True %s and created  between %%s and %%s %s %s;" % (accounts_str, type_id, LIMIT), (date_start, date_end, ))
                    items = dictfetchall(cur)
                    r = []
                    for item in items:
                        item["type"] = transactiontypes.get(item["type"])
                        r.append(item)
                    res+=r
                if x=="TrafficTransaction":
                    print type_id
                    
                    cur.execute("SELECT count(*) as cnt FROM billservice_traffictransaction WHERE True %s and created  between %%s and %%s ;" % (accounts_str,), (date_start, date_end, ))
                    cnt +=  dictfetchall(cur)[0]['cnt']
                    cur.execute("SELECT sum((-1)*summ) as summ FROM billservice_traffictransaction WHERE True %s and created  between %%s and %%s ;" % (accounts_str, ), (date_start, date_end, ))
                    summ +=  dictfetchall(cur)[0]['summ'] or 0
                    cur.execute("SELECT id, (-1)*summ as summ, (SELECT username FROM billservice_account WHERE id=psh.account_id) as account, 'NETFLOW_BILL' as type, created FROM billservice_traffictransaction as psh WHERE True %s and created  between %%s and %%s %s;" % (accounts_str,  LIMIT), (date_start, date_end, ))
                    items = dictfetchall(cur)
                    r = []
                    for item in items:
                        item["type"] = transactiontypes.get(item["type"])
                        r.append(item)
                    res+=r
                if x=="Transaction":
                    promise_str = ""
                    if promise:
                        promise_str = " and promise = True "
                    promise_expired_str = ""
                    if promise_expired:
                        promise_expired_str = "and promise_expired is not NULL"
                        
                    cur.execute("SELECT count(*) as cnt FROM billservice_transaction WHERE True %s %s %s %s and created  between %%s and %%s %s;" % (promise_expired_str, promise_str, systemusers_str, accounts_str, type_id), (date_start, date_end, ))
                    cnt += dictfetchall(cur)[0]['cnt']
                    print cur.query
                    cur.execute("SELECT sum((-1)*summ) as summ FROM billservice_transaction WHERE True %s %s %s %s and created  between %%s and %%s %s;" % (promise_expired_str, promise_str, systemusers_str, accounts_str, type_id), (date_start, date_end, ))
                    summ += dictfetchall(cur)[0]['summ'] or 0
                    cur.execute("SELECT id, '' as service_id, (-1)*summ as summ, (SELECT username FROM billservice_account WHERE id=trs.account_id) as account, bill, description, end_promise, type_id as type, created FROM billservice_transaction as trs WHERE True %s %s %s %s and created  between %%s and %%s %s %s;" % (promise_expired_str, promise_str, accounts_str, systemusers_str, type_id, LIMIT), (date_start, date_end, ))
                    items = dictfetchall(cur)
                    print cur.query
                    r = []
                    for item in items:
                        item["type"] = transactiontypes.get(item["type"])
                        r.append(item)
                    res+=r
            items = []
            summOnThePage = 0
            for item in res:
                summOnThePage +=item['summ']

                    #print res
            pg = digg_paginator(page, int(cnt/pageitems)+1)
            


            tf = TransactionReportForm(request.GET)   
            table = TotalTransactionReportTable(res)
            RequestConfig(request, paginate = False).configure(table)

            
            table.data.list+=([{"type": u"На странице", "summ":summOnThePage}])
            table.data.list+=([{"type": u"Всего", "summ":summ}])
            #===================================================================
            #for kq in connection.queries:
            #    print kq
            return {"table": table,  'form':tf, "totalSumm": summ, "cnt":cnt, "pages_range": pg['pages_outside_trailing_range']+ ['...']+pg['page_numbers']+ ['...']+ pg['pages_outside_leading_range']}   
    
        else:
    
            return {'status':False, 'errors':form._errors}
    else:
        form = TransactionReportForm(request.GET)
        return { 'form':form}   
    
        
@login_required
@render_to('ebsadmin/account_edit.html')
def accountsreport(request):

    

        
    class TotalTransactionReportTable(tables.Table):
        row_number = tables.Column(verbose_name="#")
        id = FormatBlankColumn()
        username = tables.LinkColumn('account_detail', args=[A('pk')])
        contract = FormatBlankColumn()
        fullname = FormatBlankColumn()
        
        ballance = FormatFloatColumn()
        credit = FormatFloatColumn()
        created = FormatDateTimeColumn()

        def render_row_number(self):
            value = getattr(self, '_counter', 0)
            self._counter = value + 1
            return '%d' % value
        
        class Meta:
            #attrs = {'class': 'table table-striped table-bordered table-condensed'}
            attrs = {'class': 'paleblue'}

    if request.GET:
        data = request.GET

        #pageitems = 100
        form = SearchAccountForm(data)
        if form.is_valid():
            date_start, date_end = None, None
            account = form.cleaned_data.get('account')+form.cleaned_data.get('fullname')+form.cleaned_data.get('contactperson')+form.cleaned_data.get('username')
            id = form.cleaned_data.get('id')
            passport = form.cleaned_data.get('passport')
            created = form.cleaned_data.get('created')
            tariff = form.cleaned_data.get('tariff')
            street = form.cleaned_data.get('street')
            room = form.cleaned_data.get('room')
            row = form.cleaned_data.get('row')
            house = form.cleaned_data.get('house')
            house_bulk = form.cleaned_data.get('house_bulk')
            ballance = form.cleaned_data.get('ballance')
            ballance_exp = form.cleaned_data.get('ballance_exp')
            vpn_ip_address = form.cleaned_data.get('vpn_ip_address')
            ipn_ip_address = form.cleaned_data.get('ipn_ip_address')
            ipn_mac_address = form.cleaned_data.get('ipn_mac_address')
            nas = form.cleaned_data.get('nas')

            credit = form.cleaned_data.get('credit')
            credit_exp = form.cleaned_data.get('credit_exp')
                        
            status = int(form.cleaned_data.get('status', 0))
            
            if type(created)==tuple:
                date_start, date_end = created
            systemusers = form.cleaned_data.get('systemuser')

            
            res = Account.objects.all()
            if id:
                res = Account.objects.filter(id=id)
            if room:
                res = Account.objects.filter(room__icontains=room)

                
            if account:
                res = Account.objects.filter(id__in=account)
            if date_start:
                res = res.filter(created__gte=date_start)
            if date_end:
                res = res.filter(created__lte=date_end)
                
            if not (date_start and date_end) and created:
                res = res.filter(created=created)
            if tariff:
                res = res.extra(where=['billservice_account.id in (SELECT account_id FROM billservice_accounttarif WHERE tarif_id in (%s))'], params=[ ','.join(['%s' % x.id for x in tariff]) ])
            
            if street:
                res = res.filter(street__name__icontains=street)

            if house:
                res = res.filter(house__name__icontains=house)

            if row:
                res = Account.objects.filter(row=row)
                
            if status:
                res = res.filter(status=status)

            if passport:
                res = res.filter(passport__icontains=passport)
                
            if vpn_ip_address:
                res = res.filter(subaccounts__vpn_ip_address__icontains=vpn_ip_address)

            if ipn_ip_address:
                res = res.filter(subaccounts__ipn_ip_address__icontains=ipn_ip_address)

            if ipn_mac_address:
                res = res.filter(subaccounts__ipn_mac_address__icontains=ipn_mac_address)

            if nas:
                res = res.filter(subaccounts__nas__in=nas)
                                 
            if ballance_exp:
                if ballance_exp=='>':
                    res = res.filter(ballance__gte=ballance)
                elif ballance_exp=='<':
                    res = res.filter(ballance__lte=ballance)
                else:
                    res = res.filter(ballance=ballance)
                    
            if credit_exp:
                if credit_exp=='>':
                    res = res.filter(credit__gte=credit)
                elif credit_exp=='<':
                    res = res.filter(credit__lte=credit)
                else:
                    res = res.filter(credit=credit)
                    
            table = TotalTransactionReportTable(res)
            RequestConfig(request, paginate = True).configure(table)

            #===================================================================
            #for kq in connection.queries:
            #    print kq
            return {"table": table,  'form':form}   
    
        else:
            return {'status':False, 'form':form}
    else:
        form = SearchAccountForm()
        return { 'form':form}   
    
@login_required
@render_to('ebsadmin/account_edit.html')
def accountedit(request, account_id):
    from billservice.forms import AccountForm
    from billservice.models import Account
    
    class SubAccountsTable(tables.Table):
        row_number = tables.Column(verbose_name="#")
        id = FormatBlankColumn()
        username = tables.LinkColumn('subaccount_detail', args=[A('pk')])
        password = FormatBlankColumn()
        nas = FormatBlankColumn()
        
        ipv4_vpn_ip_address = FormatBlankColumn()
        ipv4_ipn_ip_address = FormatBlankColumn()
        ipn_mac_address = FormatBlankColumn()
        
        

        def render_row_number(self):
            value = getattr(self, '_counter', 0)
            self._counter = value + 1
            return '%d' % value
        
        class Meta:
            #attrs = {'class': 'table table-striped table-bordered table-condensed'}
            attrs = {'class': 'paleblue'}

    class AccountTarifTable(tables.Table):
        row_number = tables.Column(verbose_name="#")
        id = FormatBlankColumn()
        tarif = tables.LinkColumn('subaccount_detail', args=[A('pk')])
        datetime = FormatBlankColumn()

        
        

        def render_row_number(self):
            value = getattr(self, '_counter', 0)
            self._counter = value + 1
            return '%d' % value
        
        class Meta:
            #attrs = {'class': 'table table-striped table-bordered table-condensed'}
            attrs = {'class': 'paleblue'}

    account = Account.objects.get(id=account_id)

    res = SubAccount.objects.filter(account=account)
    table = SubAccountsTable(res)
    RequestConfig(request, paginate = True).configure(table)

    res = AccountTarif.objects.filter(account=account)
    accounttarif_table = AccountTarifTable(res)
    RequestConfig(request, paginate = True).configure(table)

            
    if request.GET:
        data = request.GET

        form = AccountForm(data)
        if form.is_valid():



            #===================================================================
            #for kq in connection.queries:
            #    print kq
            return {"table": table,  'form':form}   
    
        else:
    
            return {'status':False, 'errors':form._errors}
    else:
        
        form = AccountForm(instance=account)
        return {"table": table, "accounttarif_table": accounttarif_table,  'form':form} 
    
@login_required
@render_to('ebsadmin/account_edit.html')
def subaccountedit(request, subaccount_id):
    from billservice.forms import SubAccountForm, AccountAddonService
    from billservice.models import SubAccount
    
    class AccountAddonServiceTable(tables.Table):
        row_number = tables.Column(verbose_name="#")
        id = FormatBlankColumn()
        service = tables.LinkColumn('subaccount_detail', args=[A('pk')])
        activated = FormatBlankColumn()
        deactivated = FormatBlankColumn()
        temporary_blocked = FormatBlankColumn()
        
        

        def render_row_number(self):
            value = getattr(self, '_counter', 0)
            self._counter = value + 1
            return '%d' % value
        
        class Meta:
            #attrs = {'class': 'table table-striped table-bordered table-condensed'}
            attrs = {'class': 'paleblue'}

            
    subaccount = SubAccount.objects.get(id=subaccount_id)

    res = AccountAddonService.objects.filter(subaccount=subaccount)
    table = AccountAddonServiceTable(res)
    RequestConfig(request, paginate = True).configure(table)

            
    if request.GET:
        data = request.GET

        form = SubAccountForm(data)
        if form.is_valid():



            #===================================================================
            #for kq in connection.queries:
            #    print kq
            return {"table": table,  'form':form}   
    
        else:
    
            return {'status':False, 'errors':form._errors}
    else:
        
        form = SubAccountForm(instance=subaccount)
        return {"table": table, 'form':form} 
    
    
@login_required
@render_to('ebsadmin/account_edit.html')
def activesessionreport(request):
    from radius.forms import SessionFilterForm
    from radius.models import ActiveSession
    #{% elif record.session_status == 'NACK' %}important{% elif record.session_status == 'ACTIVE' %}label-success
    class ActiveSessionTable(tables.Table):
        session_status = tables.TemplateColumn("<span class='label {% if record.session_status == 'ACK' %}info{% endif %}'>{{ record.session_status }}</span>")

        
        class Meta:
            #attrs = {'class': 'table table-striped table-bordered table-condensed'}
            model = ActiveSession
            attrs = {'class': 'paleblue'}


    res = ActiveSession.objects.all()
    table = ActiveSessionTable(res)
    RequestConfig(request, paginate = True).configure(table)

            
    if request.GET:
        data = request.GET

        form = SessionFilterForm()
        if form.is_valid():



            #===================================================================
            #for kq in connection.queries:
            #    print kq
            return {"table": table,  'form':form}   
    
        else:
    
            return {"table": table,  'form':form}
    else:
        
        form = SessionFilterForm()
        return {"table": table, 'form':form} 
    
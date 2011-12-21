#-*-coding:utf-8-*-
from billservice.forms import TransactionReportForm
from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from billservice.models import Transaction,PeriodicalServiceHistory, TotalTransactionReport as TransactionReport
from views import instance_dict
import billservice.models as bsmodels
from lib import QuerySetSequence, ExtDirectStore,IableSequence
import time
from django.core import serializers
from django.forms import model_to_dict
from django.db import connection
import psycopg2.extras
import psycopg2
from django.conf import settings
# Очень важный момент, возврат результата из базы в виде словаря а не списка.
from psycopg2.extras import RealDictCursor 
from psycopg2 import IntegrityError, InternalError




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
                        "TIME_ACCESS"
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

    
    form = TransactionReportForm(request.POST)
    if form.is_valid():
        #items = PeriodicalServiceHistory.objects.all()[0:200]
        account = form.cleaned_data.get('account')
        date_start = form.cleaned_data.get('start_date')
        date_end = form.cleaned_data.get('end_date')
        systemusers = form.cleaned_data.get('systemuser')
        tariffs = form.cleaned_data.get('tarif')
        extra={'start':int(request.POST.get('start',0)), 'limit':int(request.POST.get('limit',100))}
        if request.POST.get('sort',''):
            extra['sort'] = request.POST.get('sort','')
            extra['dir'] = request.POST.get('dir','asc')
        if request.POST.get('groupBy',''):
            extra['groupby'] = request.POST.get('groupBy','')
            extra['groupdir'] = request.POST.get('groupDir','asc')
            
        res=[]
        resitems = []
        TYPES={}
        TRTYPES={}
        LTYPES=[]
        for x in form.cleaned_data.get('transactiontype'):
            key=TRANSACTION_MODELS.get(x.internal_name)
            model = bsmodels.__dict__.get(key)
            if key not in TYPES:
                TYPES[key]=[]
            if key not in TRTYPES:
                TRTYPES[key]=[]
            TYPES[key].append(model)
            TRTYPES[key].append(x)
            LTYPES.append(x.internal_name)
                
        #print TYPES
        print ','.join(["'%s'" % x for x in LTYPES])
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
        res = tuple(items.values('id', 'service_name','created','tariff__name','summ','account','type','type__name','systemuser','bill','descrition','end_promise', 'promise_expired')) 
        #=======================================================================
        # count_sql = """
        #        SELECT count(*) as cnt 
        #        FROM billservice_totaltransactionreport as ttr 
        #        WHERE ttr.created between '%s' and '%s' and ttr.type in (%s) %%s
        #        """% (date_start, date_end, ','.join(["'%s'" % x for x in LTYPES]))
        #   
        # sql = """
        #        SELECT ttr.id, ttr.service,ttr.created,(SELECT name FROM billservice_tariff WHERE id=ttr.tariff) as tarif,ttr.summ,ttr.account,ttr.systemuser,ttr.bill,ttr.descrition,ttr.end_promise, ttr.promise_expired,  
        #        (SELECT name FROM billservice_transactiontype WHERE internal_name=ttr.type) as type 
        #        FROM billservice_totaltransactionreport as ttr 
        #        WHERE ttr.created between '%s' and '%s' and ttr.type in (%s) %%s ORDER BY ttr.created DESC LIMIT %s OFFSET %s
        #        """% (date_start, date_end, ','.join(["'%s'" % x for x in LTYPES]),extra.get('limit',0),extra.get('start',0))        
        # if tariffs:
        #    app=" and ttr.tariff in (%s)" % ','.join([str(x.id) for x in tariffs])
        # else:
        #    app=''
        # sql=sql % app
        # count_sql=count_sql % app
        # db.cursor.execute(sql)
        # res = db.cursor.fetchall()
        # 
        # db.cursor.execute(count_sql)        
        # totalcount = db.cursor.fetchone()['cnt']    
        #=======================================================================
        
        """
        if 'Transaction' in TYPES:
            model = bsmodels.__dict__.get('Transaction')
            items = model.objects.filter(created__gte=date_start, created__lte=date_end).order_by('-created')#.values('id','account','summ')
            items=items.filter(type__in=TRTYPES.get('Transaction'))
            
            if account:
                items = items.filter(account=account)

            
            if systemusers:
                items = items.filter(systemuser__in=systemusers)
            if tariffs:
                items = items.filter(accounttarif__tarif__in=tariffs)
                
            res.append(items)
            #for item in items:
                #print instance_dict(acc).keys()
            #    res.append(instance_dict(item,normal_fields=True))
                #res.append(item)
        if 'PeriodicalServiceHistory' in TYPES:
            
            model = bsmodels.__dict__.get('PeriodicalServiceHistory')
            items = model.objects.filter(created__gte=date_start, created__lte=date_end).order_by('-created')#.values('id','account','summ')
            items=items.filter(type__in=TRTYPES.get('PeriodicalServiceHistory'))
            
            if account:
                items = items.filter(account=account)
                

            if tariffs:
                items = items.filter(accounttarif__tarif__in=tariffs)
                
            periodicalservice = form.cleaned_data.get('periodicalservice')
            if periodicalservice:
                items = items.filter(service__in=periodicalservice)
            
            
            res.append(items)
            """
#===============================================================================
#            if account:
# 
#                #cursor=db.cursor()
#                db.cursor.execute("""
#                SELECT psh.id, (SELECT name FROM billservice_periodicalservice WHERE id=psh.service_id) as name, psh.created, (SELECT name FROM billservice_tariff WHERE id=(SELECT tarif_id FROM billservice_accounttarif where id=psh.accounttarif_id) as tarif, psh.summ, (SELECT username FROM billservice_account WHERE id=psh.account_id) as username,  
#                (SELECT name FROM billservice_transactiontype WHERE internal_name=psh.type_id) as type 
#                FROM billservice_periodicalservicehistory as psh 
#                WHERE psh.created between %s and %s and psh.account_id=%s and type_id in %s::array ORDER BY psh.created DESC
#                """, (date_start, date_end, account.id, ','.join([x.internal_name for x in TRTYPES.get('PeriodicalServiceHistory')])))
#            else:
#                #cursor=connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
#                #cursor = db.cursor()
#                db.cursor.execute("""
#                SELECT psh.id, (SELECT name FROM billservice_periodicalservice WHERE id=psh.service_id) as name, psh.created, (SELECT name FROM billservice_tariff WHERE id=(SELECT tarif_id FROM billservice_accounttarif where id=psh.accounttarif_id)) as tarif, psh.summ, (SELECT username FROM billservice_account WHERE id=psh.account_id) as username,  
#                (SELECT name FROM billservice_transactiontype WHERE internal_name=psh.type_id) as type 
#                FROM billservice_periodicalservicehistory as psh 
#                WHERE psh.created between %s and %s and type_id in (%s) ORDER BY psh.created DESC
#                """, (date_start, date_end,','.join([x.internal_name for x in TRTYPES.get('PeriodicalServiceHistory')])))
#        
#            res = db.cursor.fetchall()
#===============================================================================

            #print res[0]
            #items=items.values('id','account__username', 'summ')
            #print res
        """
        if 'AddonServiceHistory' in TYPES:
            model = bsmodels.__dict__.get('AddonServiceHistory')
            items = model.objects.filter(created__gte=date_start, created__lte=date_end).order_by('-created')#.values('id','account','summ')
            items=items.filter(type__in=TRTYPES.get('AddonServiceHistory'))
            
            if account:
                items = items.filter(account=account)
                

            if tariffs:
                items = items.filter(accounttarif__tarif__in=tariffs)
                
            periodicalservice = form.cleaned_data.get('AddonServiceHistory')
            if periodicalservice:
                items = items.filter(periodicalservice__in=periodicalservice)
            res.append(items)
            
        qs = QuerySetSequence(*res)#.order_by('-created')
        #items = ExtDirectStore(None)
        items = qs.filter(**extra)
        
        res=[]
        for item in items:
            #print instance_dict(acc).keys()
            res.append(instance_dict(item, normal_fields=True))
            
            
        #print item._meta.get_all_field_names()
        """
        print len(res)
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
        
        return {"records": res,  'total':totalcount, 'metaData':{'root': 'records',
                                             'totalProperty':'total', 
                                             
                                             'fields':t
                                             },
                "sortInfo":{
                "field": "created",
                "direction": "ASC",
                
               },
                                 
                }        


        #print transaction_type

        if self.transactions_types.get(transaction_type, None) in ["billservice_transaction",None]:
            sql = """SELECT transaction.*, transactiontype.name as transaction_type_name, tariff.name as tariff_name, (SELECT username FROM billservice_account WHERE id=transaction.account_id) as username, (SELECT fullname FROM billservice_account WHERE id=transaction.account_id) as fullname, (SELECT username FROM billservice_systemuser WHERE id=transaction.systemuser_id) as systemuser
                                            FROM billservice_transaction as transaction
                                            JOIN billservice_transactiontype as transactiontype ON transactiontype.internal_name = transaction.type_id
                                            LEFT JOIN billservice_tariff as tariff ON tariff.id = transaction.tarif_id   
                                            WHERE transaction.created between '%s' and '%s' %%s and transaction.type_id='%s' ORDER BY transaction.created DESC""" %  (start_date, end_date,transaction_type)
    
            if account_id:
                sql = sql % " and transaction.account_id=%s %%s" % account_id
            else:
                sql = sql % " %s"
    
            systemuser_id = self.comboBox_cashier.itemData(self.comboBox_cashier.currentIndex()).toInt()[0]
            #print sql
            if systemuser_id!=0:
                sql = sql % " and transaction.systemuser_id=%s " % systemuser_id
            else:
                sql = sql % " "
    
            items = self.connection.sql(sql)
            self.connection.commit()
            self.tableWidget.setRowCount(len(items))
            i=0
            
        if self.transactions_types.get(transaction_type)=="billservice_periodicalservicehistory":
            services = self.connection.get_models("billservice_periodicalservice")
            s = {}
            for x in services:
                s[x.id] = x.name
    
            tariffs = self.connection.get_models("billservice_tariff")
            t = {}
            for x in tariffs:
                t[x.id] = x.name
                               
            sql = """
            SELECT psh.id, psh.service_id, psh.datetime, psh.accounttarif_id, (SELECT tarif_id FROM billservice_accounttarif WHERE id=psh.accounttarif_id) as tarif_id, psh.summ, (SELECT username FROM billservice_account WHERE id=psh.account_id) as username, (SELECT fullname FROM billservice_account WHERE id=psh.account_id) as fullname, psh.type_id 
            FROM billservice_periodicalservicehistory as psh 
            WHERE psh.datetime between '%s' and '%s' %%s and type_id='%s' ORDER BY psh.datetime DESC
            """ % (start_date, end_date,transaction_type)
            
            if account_id:
                sql = sql % " and psh.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            items = self.connection.sql(sql)
            self.connection.commit()
            
            
        if self.transactions_types.get(transaction_type)=="billservice_onetimeservicehistory":
            services = self.connection.get_models("billservice_onetimeservice")
            s = {}
            for x in services:
                s[x.id] = x.name
    
            tariffs = self.connection.get_models("billservice_tariff")
            t = {}
            for x in tariffs:
                t[x.id] = x.name
                               
            sql = """
            SELECT osh.id, osh.onetimeservice_id, osh.datetime, osh.accounttarif_id, (SELECT tarif_id FROM billservice_accounttarif WHERE id=osh.accounttarif_id) as tarif_id, osh.summ, (SELECT username FROM billservice_account WHERE id=osh.account_id) as username, (SELECT fullname FROM billservice_account WHERE id=osh.account_id) as fullname 
            FROM billservice_onetimeservicehistory as osh 
            WHERE osh.datetime between '%s' and '%s' %%s ORDER BY osh.datetime DESC
            """ % (start_date, end_date,)
            
            if account_id:
                sql = sql % " and osh.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            items = self.connection.sql(sql)
            self.connection.commit()
            
                        
        if self.transactions_types.get(transaction_type)=="billservice_traffictransaction":
            tariffs = self.connection.get_models("billservice_tariff")
            t = {}
            for x in tariffs:
                t[x.id] = x.name
                               
            sql = """
            SELECT tr.id, tr.datetime, tr.accounttarif_id, (SELECT tarif_id FROM billservice_accounttarif WHERE id=tr.accounttarif_id) as tarif_id, tr.summ, (SELECT username FROM billservice_account WHERE id=tr.account_id) as username , (SELECT fullname FROM billservice_account WHERE id=tr.account_id) as fullname
            FROM billservice_traffictransaction as tr 
            WHERE tr.datetime between '%s' and '%s' %%s ORDER BY tr.datetime DESC
            """ % (start_date, end_date,)
            
            if account_id:
                sql = sql % " and tr.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            items = self.connection.sql(sql)
            self.connection.commit()
            self.tableWidget.setRowCount(len(items))
            i=0
            
            
        if self.transactions_types.get(transaction_type)=="billservice_timetransaction":
            #print 111
            tariffs = self.connection.get_models("billservice_tariff")
            t = {}
            for x in tariffs:
                t[x.id] = x.name
                               
            sql = """
            SELECT tr.id, tr.datetime, tr.accounttarif_id, (SELECT tarif_id FROM billservice_accounttarif WHERE id=tr.accounttarif_id) as tarif_id, tr.summ, (SELECT username FROM billservice_account WHERE id=tr.account_id) as username, (SELECT fullname FROM billservice_account WHERE id=tr.account_id) as fullname
            FROM billservice_timetransaction as tr 
            WHERE tr.datetime between '%s' and '%s' %%s ORDER BY tr.datetime DESC
            """ % (start_date, end_date,)
            
            if account_id:
                sql = sql % " and tr.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            items = self.connection.sql(sql)
            self.connection.commit()
                                
        self.tableWidget.setColumnHidden(0, False)
        
        if self.transactions_types.get(transaction_type)=="billservice_addonservicetransaction":
            #print 111
            tr_types = self.connection.get_models("billservice_transactiontype")
            t = {}
            for x in tr_types:
                t[x.internal_name] = x.name
    
            sql = """
            select addst.id, (SELECT name FROM billservice_addonservice WHERE id=addst.service_id) as service_name, addst.summ, addst.created, addst.type_id, (SELECT username FROM billservice_account WHERE id=addst.account_id) as username, (SELECT fullname FROM billservice_account WHERE id=addst.account_id) as fullname
            FROM billservice_addonservicetransaction as addst
            WHERE addst.created>='%s' and addst.created<='%s' %%s ORDER BY created ASC
            """ % (start_date, end_date,)
            
            if account_id:
                sql = sql % " and addst.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            items = self.connection.sql(sql)
            self.connection.commit()
                                 
        self.tableWidget.setColumnHidden(0, False)
    
        if self.transactions_types.get(transaction_type)=="qiwi_invoice":
            #print 111
            #tr_types = self.connection.get_models("billservice_transactiontype")
            #t = {}
            #for x in tr_types:
            #    t[x.internal_name] = x.name
                               
            #print (start_date, end_date,)
            [u'#', u'Аккаунт', u"ФИО",  u"№ инвойса", u'Создан', u"Автозачисление", u'Оплачен', u"Сумма"]
            sql = """
            SELECT qi.id as id, (SELECT username FROM billservice_account WHERE id=qi.account_id) as username,(SELECT fullname FROM billservice_account WHERE id=qi.account_id) as fullname,qi,created as created, qi.autoaccept, qi.date_accepted, qi.summ
            FROM qiwi_invoice as qi
            WHERE qi.created>='%s' and qi.created<='%s' %%s ORDER BY created ASC
            """ % (start_date, end_date,)
            
            if account_id:
                sql = sql % " and qi.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            items = self.connection.sql(sql)
            self.connection.commit()
            self.tableWidget.setRowCount(len(items))
            

        if self.transactions_types.get(transaction_type)=="totaltransactions":
            
            sql = """
            SELECT qi.id as id, (SELECT username FROM billservice_account WHERE id=qi.account_id) as username,(SELECT fullname FROM billservice_account WHERE id=qi.account_id) as fullname,qi,created as created, qi.autoaccept, qi.date_accepted, qi.summ, get_tarif_name(qi.account_id, qi.date_accepted) as tarif_name
            FROM qiwi_invoice as qi
            WHERE qi.date_accepted is not Null and qi.created>='%s' and qi.created<='%s' %%s ORDER BY created ASC
            """ % (start_date, end_date,)
            
            if account_id:
                sql = sql % " and qi.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            qiwi_items = self.connection.sql(sql)
    
   
                
            sql = """
            select addst.id, (SELECT name FROM billservice_addonservice WHERE id=addst.service_id) as service_name, addst.summ, addst.created, addst.type_id, (SELECT username FROM billservice_account WHERE id=addst.account_id) as username, (SELECT fullname FROM billservice_account WHERE id=addst.account_id) as fullname, get_tarif_name(addst.account_id,addst.created) as tarif_name
            FROM billservice_addonservicetransaction as addst
            WHERE addst.created>='%s' and addst.created<='%s' %%s ORDER BY created ASC
            """ % (start_date, end_date,)
            
            if account_id:
                sql = sql % " and addst.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            addonservice_items = self.connection.sql(sql)
            
            ##
            
    
                               
            sql = """
            SELECT tr.id, tr.datetime, tr.accounttarif_id, (SELECT tarif_id FROM billservice_accounttarif WHERE id=tr.accounttarif_id) as tarif_id, tr.summ, (SELECT username FROM billservice_account WHERE id=tr.account_id) as username, (SELECT fullname FROM billservice_account WHERE id=tr.account_id) as fullname
            FROM billservice_timetransaction as tr 
            WHERE tr.datetime between '%s' and '%s' %%s ORDER BY tr.datetime DESC
            """ % (start_date, end_date,)
            
            if account_id:
                sql = sql % " and tr.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            timetransaction_items = self.connection.sql(sql)
            
            ##
            
                               
            sql = """
            SELECT tr.id, tr.datetime, tr.accounttarif_id, (SELECT tarif_id FROM billservice_accounttarif WHERE id=tr.accounttarif_id) as tarif_id, tr.summ, (SELECT username FROM billservice_account WHERE id=tr.account_id) as username , (SELECT fullname FROM billservice_account WHERE id=tr.account_id) as fullname, tr.radiustraffictransmitservice_id
            FROM billservice_traffictransaction as tr 
            WHERE tr.datetime between '%s' and '%s' %%s ORDER BY tr.datetime DESC
            """ % (start_date, end_date,)
            
            if account_id:
                sql = sql % " and tr.account_id=%s " % account_id
            else:
                sql = sql % " "  
        
            traffictransaction_items = self.connection.sql(sql)
            return {}
    else:
        print "form not valid"
        print [form._errors.get(x) for x in form._errors][0][0]
            
        return {'success':False, 'msg':form._errors}
        
    
        
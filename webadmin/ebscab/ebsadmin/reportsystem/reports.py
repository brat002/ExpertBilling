#-*- coding: utf-8 -*-


from ebsadmin.reportsystem.forms import AccountBallanceForm, CachierReportForm, ReportForm

from ebscab.lib.decorators import render_to, ajax_request
from billservice.helpers import systemuser_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from billservice.models import Account, AccountAddonService, Transaction, TotalTransactionReport, Tariff
from django_tables2_reports.tables import TableReport
import django_tables2 as django_tables
from django.db.models import Sum
#from ebsadmin.tables import AccountsCashierReportTable, CashierReportTable
import datetime
from ebsadmin.tables import FormatFloatColumn

class FormatFloatColumn(django_tables.Column):
    def render(self, value):
        return "%.2f" % float(value) if value else ''
    
@systemuser_required
@render_to("reportsystem/generic.html")
def render_report(request, slug):
    class AccountTransactionsSumm(TableReport):
        username = django_tables.Column()
        summ = FormatFloatColumn()
        class Meta:
            attrs = {'class': 'table table-striped table-bordered table-condensed"'}
    name = rep.get(slug)[1]
    if request.GET and request.method=='GET':
        form = AccountBallanceForm(request.GET)
        if form.is_valid():
            date_start = form.cleaned_data.get('date_start')
            date_end = form.cleaned_data.get('date_end')
            accounts = form.cleaned_data.get('accounts')
            res = Account.objects.all()
            if accounts:
                res = res.filter(id__in=[a.id for a in accounts])
            res =res.extra(
                select={
                    'summ': "SELECT sum(summ) FROM billservice_transaction WHERE account_id=billservice_account.id and created between '%s' and '%s' " % (date_start, date_end)
                },
                where=["(SELECT sum(summ) FROM billservice_transaction WHERE account_id=billservice_account.id and created between '%s' and '%s' )<>0" % (date_start, date_end)]
            )
            table = AccountTransactionsSumm(res)
            table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)
            #print res[0].SUMM
            return {'form': form, 'table': table, 'name': name, 'slug': slug}
            
    form = AccountBallanceForm()
    return {'form': form, 'name': name, 'slug': slug}

@systemuser_required
@render_to("reportsystem/generic.html")
def accountaddonservicereport(request, slug):
    class AccountAddonServiceReport(TableReport):
        class Meta:
            model = AccountAddonService
            attrs = {'class': 'table table-striped table-bordered table-condensed"'}
            
    name = rep.get(slug)[1]
    if request.GET and request.method=='GET':
        form = AccountBallanceForm(request.GET)
        if form.is_valid():
            date_start = form.cleaned_data.get('date_start')
            date_end = form.cleaned_data.get('date_end')
            accounts = form.cleaned_data.get('accounts')
            
            res = AccountAddonService.objects.all()
            if date_start:
                res = res.filter(activated__gte=date_start)
                
            if date_end:
                res = res.filter(deactivated__lte=date_end)
                
            if accounts:
                res = res.filter(account__in=accounts)
            table = AccountAddonServiceReport(res)
            table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)
            #print res[0].SUMM
            return {'form': form, 'table': table, 'name': name, 'slug': slug}
        else:
            return {'form': form, 'name': name, 'slug': slug}
    form = AccountBallanceForm()
    return {'form': form, 'name': name, 'slug': slug}

@systemuser_required
@render_to("reportsystem/generic.html")
def cashierdailyreport(request, slug):

            
    name = rep.get(slug)[1]
    if request.GET and request.method=='GET':
        form = CachierReportForm(request.GET)
        if form.is_valid():
            class TypeTransactionsSumm(TableReport):
                type__name = django_tables.Column(verbose_name=u'Тип операции')
                summ = FormatFloatColumn()
                
                def __init__(self, form, *args, **kwargs):
                    super(TypeTransactionsSumm, self).__init__(form, *args, **kwargs)
                    self.footer_data = self.TableDataClass(data=[pp.aggregate(summ=Sum('summ'))], table=self)
                    self.footer = django_tables.rows.BoundRows(self.footer_data, self)    
                class Meta:
                    attrs = {'class': 'table table-striped table-bordered table-condensed"'}
                    annotations = ('summ', )
                    
            date_start = form.cleaned_data.get('date_start')
            date_end = form.cleaned_data.get('date_end')
            systemuser = form.cleaned_data.get('systemuser')
            res = Transaction.objects.all()
            if date_start:
                res = res.filter(created__gte=date_start)
            if date_end:
                res = res.filter(created__lte=date_end+datetime.timedelta(days=1))
            
            
            if systemuser:
                res = res.filter(systemuser=systemuser)
                
            pp = res
            res = res.values('type__name').annotate(summ=Sum('summ')).order_by()
            


            table = TypeTransactionsSumm(res)
            table_to_report = RequestConfig(request, paginate=False).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)

            return {'form': form, 'table': table, 'name': name, 'slug': slug}
        else:
            return {'form': form, 'name': name, 'slug': slug}
    form = CachierReportForm()
    return {'form': form, 'name': name, 'slug': slug}

@systemuser_required
@render_to("reportsystem/generic.html")
def totaltransactionreport(request, slug):

            
    name = rep.get(slug)[1]
    if request.GET and request.method=='GET':
        form = ReportForm(request.GET)
        if form.is_valid():
            class TotalTransactionsSumm(TableReport):
                type__name = django_tables.Column(verbose_name=u'Тип операции')
                summ = FormatFloatColumn()
                
                def __init__(self, form, *args, **kwargs):
                    super(TotalTransactionsSumm, self).__init__(form, *args, **kwargs)
                    self.footer_data = self.TableDataClass(data=[pp.aggregate(summ=Sum('summ'))], table=self)
                    self.footer = django_tables.rows.BoundRows(self.footer_data, self)    
                class Meta:
                    attrs = {'class': 'table table-striped table-bordered table-condensed"'}
                    annotations = ('summ', )

            date_start = form.cleaned_data.get('date_start')
            date_end = form.cleaned_data.get('date_end')
            transactiontype = form.cleaned_data.get('transactiontype')


            res = TotalTransactionReport.objects.all()
            if date_start:
                res = res.filter(created__gte=date_start)
            if date_end:
                res = res.filter(created__lte=date_end+datetime.timedelta(days=1))
            if transactiontype:
                res = res.filter(type__in=[x.internal_name for x in transactiontype])
            pp = res


            res = res.values('type__name').annotate(summ=Sum('summ')).order_by()


            table = TotalTransactionsSumm(res)
            table_to_report = RequestConfig(request, paginate=False).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)

            return {'form': form,  'table': table, 'name': name, 'slug': slug}
        else:
            return {'form': form, 'name': name, 'slug': slug}
    form = ReportForm()
    return {'form': form, 'name': name, 'slug': slug}


@systemuser_required
@render_to("reportsystem/generic.html")
def accountperiodreport(request, slug):

            
    name = rep.get(slug)[1]
    if request.GET and request.method=='GET':
        form = AccountBallanceForm(request.GET)
        if form.is_valid():
            class AccountPeriodReportTable(TableReport):
                username = django_tables.Column(verbose_name=u'Логин')
                fullname = django_tables.Column(verbose_name=u'ФИО')
                #ballance = FormatFloatColumn(verbose_name=u'Текущий баланс')
                balance_start = FormatFloatColumn(verbose_name=u'Начальный баланс')
                periodic_summ = FormatFloatColumn(verbose_name=u'Списания по период. услугам')
                addonservice_summ = FormatFloatColumn(verbose_name=u'Списания под подкл. услугам')
                traffictransaction_summ = FormatFloatColumn(verbose_name=u'Списания за трафик')
                timetransaction_summ = FormatFloatColumn(verbose_name=u'Списания за время')
                transaction_summ_pos = FormatFloatColumn(verbose_name=u'Пополнений баланса')
                transaction_summ_neg = FormatFloatColumn(verbose_name=u'Вычеты и баланса')
                balance_end = FormatFloatColumn(verbose_name=u'Конечный баланс')
                #summ = FormatFloatColumn()
                
                #===============================================================
                # def __init__(self, form, *args, **kwargs):
                #    super(TotalTransactionsSumm, self).__init__(form, *args, **kwargs)
                #    self.footer_data = self.TableDataClass(data=[pp.aggregate(summ=Sum('summ'))], table=self)
                #    self.footer = django_tables.rows.BoundRows(self.footer_data, self)    
                class Meta:
                    attrs = {'class': 'table table-bordered table-condensed"'}
                    configurable = True
                    #annotations = ('summ', )
                def __init__(self, *args, **argv):
                    super(AccountPeriodReportTable, self).__init__(*args, **argv)
                    self.name = self.__class__.__name__

            date_start = form.cleaned_data.get('date_start')
            date_end = form.cleaned_data.get('date_end')
            accounts = form.cleaned_data.get('accounts')
            #transactiontype = form.cleaned_data.get('transactiontype')

            res = Account.objects.all()
            if accounts:
                res = Account.objects.filter(id__in =accounts)
            res = res.extra(select={'balance_start':
                                             '''SELECT balance as balance_start FROM billservice_balancehistory 
                                             WHERE   account_id=billservice_account.id and datetime<='%(START_DATE)s' ORDER BY datetime DESC limit 1
                                             '''

 
                                              % {
                                                 'START_DATE': date_start
                                                 },
                                            'balance_end':
                                             '''SELECT balance as balance_start FROM billservice_balancehistory 
                                             WHERE   account_id=billservice_account.id and datetime<='%(END_DATE)s' ORDER BY datetime DESC limit 1'''

 
                                              % {
                                                 'END_DATE': date_end
                                                 },
                                            'periodic_summ':
                                             '''SELECT sum(summ) FROM billservice_periodicalservicehistory 
                                             WHERE   account_id = billservice_account.id and created between '%(START_DATE)s' and '%(END_DATE)s' '''

 
                                              % {
                                                 'START_DATE': date_start,
                                                 'END_DATE': date_end
                                                 },
                                            'addonservice_summ':
                                             '''SELECT sum(summ) FROM billservice_addonservicetransaction 
                                             WHERE   account_id = billservice_account.id and created between '%(START_DATE)s' and '%(END_DATE)s' '''

 
                                              % {
                                                 'START_DATE': date_start,
                                                 'END_DATE': date_end
                                                 },
                                            'traffictransaction_summ':
                                             '''SELECT sum(summ) FROM billservice_traffictransaction 
                                             WHERE   account_id = billservice_account.id and created between '%(START_DATE)s' and '%(END_DATE)s'  '''

 
                                              % {
                                                 'START_DATE': date_start,
                                                 'END_DATE': date_end
                                                 },
                                            'timetransaction_summ':
                                             '''SELECT sum(summ) FROM billservice_timetransaction 
                                             WHERE   account_id = billservice_account.id and created between '%(START_DATE)s' and '%(END_DATE)s'  '''

 
                                              % {
                                                 'START_DATE': date_start,
                                                 'END_DATE': date_end
                                                 },
                                            'transaction_summ_neg':
                                             '''SELECT sum(summ) FROM billservice_transaction 
                                             WHERE   account_id = billservice_account.id and summ<0 and created between '%(START_DATE)s' and '%(END_DATE)s'  '''

 
                                              % {
                                                 'START_DATE': date_start,
                                                 'END_DATE': date_end
                                                 },
                                            'transaction_summ_pos':
                                             '''SELECT sum(summ) FROM billservice_transaction 
                                             WHERE   account_id = billservice_account.id and summ>0 and created between '%(START_DATE)s' and '%(END_DATE)s'  '''

 
                                              % {
                                                 'START_DATE': date_start,
                                                 'END_DATE': date_end
                                                 },
                                              })
            
            pp = res


            #res = res.values('type__name').annotate(summ=Sum('summ')).order_by()


            table = AccountPeriodReportTable(res)
            table_to_report = RequestConfig(request, paginate=False).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)

            return {'form': form,  'table': table, 'name': name, 'slug': slug}
        else:
            return {'form': form, 'name': name, 'slug': slug}
    form = AccountBallanceForm()
    return {'form': form, 'name': name, 'slug': slug}

def A():

            
    name = rep.get(slug)[1]
    if request.GET and request.method=='GET':
        form = AccountBallanceForm(request.GET)
        if form.is_valid():
            class TariffStatReportTable(TableReport):
                name = django_tables.Column()
                
                accounts_count = django_tables.Column()
                
                #summ = FormatFloatColumn()
                
                #===============================================================
                # def __init__(self, form, *args, **kwargs):
                #    super(TotalTransactionsSumm, self).__init__(form, *args, **kwargs)
                #    self.footer_data = self.TableDataClass(data=[pp.aggregate(summ=Sum('summ'))], table=self)
                #    self.footer = django_tables.rows.BoundRows(self.footer_data, self)    
                class Meta:
                    attrs = {'class': 'table table-striped table-bordered table-condensed"'}
                    #annotations = ('summ', )
                #===============================================================
                pass

            date_start = form.cleaned_data.get('date_start')
            date_end = form.cleaned_data.get('date_end')

            #transactiontype = form.cleaned_data.get('transactiontype')
            from django.db import connection
            cursor = connection.cursor()
            res = Tariff.objects.all()
            now = datetime.datetime.now()
            now_day = datetime.datetime(now.year, now.month, now.day())
            for item in res:
                
                cursor.execute('''SELECT count(*) FROM billservice_accounttarif 
                                     WHERE tarif_id=%s AND  id in 
                                     (SELECT max(id) FROM billservice_accounttarif WHERE  datetime<now() GROUP BY account_id HAVING max(datetime)<now())'''
                , (item.id, ))
                accounts_count = cursor.fetchone()[0] 
                cursor.execute('''SELECT count(*) FROM billservice_accounttarif as at
                                             WHERE at.tarif_id=%s AND  date_trunc(datetime, 'hours')=%s
                                             
                                             ''', (item.id, now_day))
                account_now = cursor.fetchone()[0]
            
                cursor.execute('''SELECT count(*) FROM billservice_accounttarif as at
                                             WHERE at.prev_tarif_id=%s AND  date_trunc(datetime, 'hours')=%s
                                             
                                             ''', (item.id, now_day))
                account_leave_now = cursor.fetchone()[0]
                
                cursor.execute('SELECT account_id FROM billservice_account WHERE tariff_id=%s', (item.id, ))
                
            pp = res


            #res = res.values('type__name').annotate(summ=Sum('summ')).order_by()


            table = AccountPeriodReportTable(res)
            table_to_report = RequestConfig(request, paginate=False).configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)

            return {'form': form,  'table': table, 'name': name, 'slug': slug}
        else:
            return {'form': form, 'name': name, 'slug': slug}
    form = AccountBallanceForm()
    return {'form': form, 'name': name, 'slug': slug}

rep = {
       'blabla': (render_report, u'Отчёт по сумме платежей за период'),
       'accountaddonservicereport': (accountaddonservicereport, u'Отчёт по подключенным подключаемым услугам'),
       'cashierdailyreport': (cashierdailyreport, u'Отчёт по платежам за период'),
       'totaltransactionreport': (totaltransactionreport, u'Отчёт по сумме списаний за период'),
       'accountperiodreport': (accountperiodreport, u'Отчёт за период')
       
       
       }


# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from object_log.models import LogItem
from django.db.models import Sum

from ebsadmin.tables import CardTable, SaleCardTable, SaleCardsTable
from ebsadmin.randgen import GenPasswd2
from billservice.forms import CardForm, CardGenerationForm, CardSearchForm, CardBatchChangeForm, SaleCardForm
from billservice.models import Card, Dealer, SaleCard, DealerPay
import string
import random
import datetime

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/card_list.html')
def card(request):
    

    if request.GET: 
        res = Card.objects.all()
        form = CardSearchForm(request.GET)
        date_start, date_end = None, None
        ac_date_start, ac_date_end = None, None
        s_date_start, s_date_end = None, None
        if form.is_valid():
            created = form.cleaned_data.get("created")
            
            id = form.cleaned_data.get("id")
            card_type = form.cleaned_data.get("card_type")
            series = form.cleaned_data.get("series")
            login = form.cleaned_data.get("login")
            pin = form.cleaned_data.get("pin")
            nominal = form.cleaned_data.get("nominal")
            tariff = form.cleaned_data.get("tariff")
            template = form.cleaned_data.get("template")
            nas = form.cleaned_data.get("nas")
            ippool = form.cleaned_data.get("ippool")
            sold = form.cleaned_data.get("sold")
            not_sold = form.cleaned_data.get("not_sold")
            activated = form.cleaned_data.get("activated")
            activated_by = form.cleaned_data.get("activated_by")
            dealer = form.cleaned_data.get("dealer")
    
            print 1
            if type(created)==tuple:
                date_start, date_end = created
                print 2
            if date_start:
                res = res.filter(created__gte=date_start, created__lte=date_end)
                print 3
            elif created:
                res = res.filter(created=created)
                print 4
            print created, "s", series
            if id:
                res = res.filter(id=id)
                print 5
            if card_type:
                res = res.filter(type=card_type)
                print 6
            if series:
                res = res.filter(series=series)
                print 7
            if tariff:
                res = res.filter(tarif=tariff)
                print 7

            if login:
                res = res.filter(login=login)
                print 7
            if pin:
                res = res.filter(pin=pin)
                print 7
            if template:
                res = res.filter(template=template)
                print 7
            if nas:
                res = res.filter(nas=nas)
                print 7
            if ippool:
                res = res.filter(ippool=ippool)
                print 7
            if type(activated)==tuple:
                ac_date_start, ac_date_end = activated
                print 2
            if ac_date_start:
                res = res.filter(activated__gte=ac_date_start, activated__lte=ac_date_end)
            elif activated:
                res = res.filter(activated=activated)
                print 4
            if activated_by:
                res = res.filter(activated_by__in=activated_by)
            
            if dealer:
                res = res.filter(salecard__dealer=dealer)
                
            if not_sold==True:
                res = res.filter(salecard__isnull=True)
            elif sold:
                if type(sold)==tuple:
                    s_date_start, s_date_end = sold
                    print 2
                if s_date_start:
                    res = res.filter(salecard__created__gte=s_date_start, salecard__created__lte=s_date_end)
                elif sold:
                    res = res.filter(salecard__created=sold)
                    print 4
            print "nominal", nominal
            if type(nominal)==tuple:
                cond, value = nominal
                if cond==">":
                    res = res.filter(nominal__gte=value)
                elif cond=="<":
                    res = res.filter(nominal__lte=value)
            elif nominal:
                res = res.filter(nominal=nominal)
    
        table = CardTable(res)
        table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
        if table_to_report:
            return create_report_http_response(table_to_report, request)
            
    else:
        form = CardSearchForm()
        table = CardTable([])
    
    return {"table": table, 'form':form} 
    
@login_required
@render_to('ebsadmin/card_edit.html')
def card_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 

        if id:
            model = Card.objects.get(id=id)
            form = CardForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_card')):
                return {'status':False, 'message': u'У вас нет прав на редактирование карт'}
        else:
            form = CardForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_card')):
            return {'status':False, 'message': u'У вас нет прав на добавление карт'}


        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return HttpResponseRedirect(reverse("hardware")) 
        else:

            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.card_view')):
                return {'status':True}

            item = Card.objects.get(id=id)
            
            form = CardForm(instance=item)
        else:
            form = CardForm()

    return { 'form':form, 'status': False} 



@login_required
@render_to('ebsadmin/salecard_edit.html')
def salecard_edit(request):
    id = request.POST.get("id")

    item = None
    ids = request.GET.getlist('d')
    print request.POST
    if request.method == 'POST': 

        if id:
            model = SaleCard.objects.get(id=id)
            form = SaleCardForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_salecard')):
                return {'status':False, 'message': u'У вас нет прав на редактирование карт'}
        else:
            form = SaleCardForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_salecard')):
            return {'status':False, 'message': u'У вас нет прав на добавление карт'}

        
        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            cards = form.cleaned_data.get("cards")
            for c in cards:
                c.salecard = model
                c.save()
            if form.cleaned_data.get('prepayment_sum')>0:
                m = DealerPay()
                m.salecard = model
                m.pay = form.cleaned_data.get('prepayment_sum')
                m.created = model.created
                m.save()
                

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return HttpResponseRedirect(reverse("card")) 
        else:
            print form._errors
            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.salecard_view')):
                return {'status':True}

            item = SaleCard.objects.get(id=id)
            dealer = item.dealer
            form = SaleCardForm(instance=item)
            res = Card.objects.filter(salecard=item)
            cards_sum = res.aggregate(total_sum=Sum('nominal')).get("total_sum")
        else:
            d = request.GET.getlist('d')
            dealer_id = request.GET.get('dealer')
            dealer = None
            if dealer_id:
                dealer = Dealer.objects.get(id=dealer_id)
            form = SaleCardForm(initial={'cards': d, 'dealer':dealer, 'paydeffer': dealer.paydeffer, 'prepayment': dealer.prepayment, })
            res = Card.objects.filter(id__in=ids)
            cards_sum = Card.objects.filter(id__in=ids).aggregate(total_sum=Sum('nominal')).get("total_sum")
            
        table = SaleCardsTable(res)
        
        table_to_report = RequestConfig(request, paginate=False).configure(table)
        if table_to_report:
            return create_report_http_response(table_to_report, request)
            
        
    return { 'form':form, 'table': table, 'status': False, 'dealer':dealer, 'cards_sum': cards_sum} 

@login_required
@render_to('ebsadmin/card_generate.html')
def card_generate(request):
    id = request.GET.get("id")
    item = None
    model = None
    if request.method == 'POST': 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.edit_card')):
            return {'status':False, 'message': u'У вас нет прав на редактирование карт'}
        form = CardGenerationForm(request.POST)
        print request.POST
        if form.is_valid():
            card_type = int(form.cleaned_data.get("card_type"))
            print "card_type", card_type, type(card_type)
            pin_mask = ''
            if form.cleaned_data.get("pin_letters")==True:
                pin_mask+=string.letters
            if form.cleaned_data.get("pin_numbers")==True:
                pin_mask+=string.digits
            login_mask = ''
            if form.cleaned_data.get("login_letters")==True:
                login_mask+=string.letters
            if form.cleaned_data.get("login_numbers")==True:
                login_mask+=string.digits
                
            dnow = datetime.datetime.now()
            if card_type in [1,2,3]:
                tarif = form.cleaned_data.get("tariff")
                
            template= form.cleaned_data.get("template")
            
            if card_type in [2,]:
                nas = form.cleaned_data.get("nas")
                
            pool=None
            if card_type in [1,2]:
                pool = form.cleaned_data.get("pool")
             
                
            cards_count=form.cleaned_data.get("count")
            series=form.cleaned_data.get("series")
            nominal=form.cleaned_data.get("nominal")
            template=form.cleaned_data.get("template")
            
            date_start=form.cleaned_data.get("date_start")
            date_end=form.cleaned_data.get("date_end")
            
            pin_length_from=form.cleaned_data.get("pin_length_from")
            pin_length_to=form.cleaned_data.get("pin_length_to")
            
            login_length_from=form.cleaned_data.get("login_length_from")
            login_length_to=form.cleaned_data.get("login_length_to")
            
            #print date_start, date_end
            i=0
            bad=0
            """
            типы карт
            0 - экспресс оплата
            1 - хотспот
            2- vpn доступ 
            """
            while i<cards_count:
                if bad>=100:
                    return {'form':form,  'status': False, 'message': u"Было сгенерировано только %s карт.\nРасширьте условия генерации для уменьшения количества дублирующихся логинов." % i} 
                model = Card()
    
                model.series = series
                model.pin = GenPasswd2(length=random.randint(pin_length_from,pin_length_to), chars=pin_mask)
                model.type = 0
                if card_type==2:
                    model.login =GenPasswd2(length=random.randint(login_length_from, login_length_to),chars=login_mask)
                    model.tarif = tarif
                    model.ippool = pool
                    model.nas = nas
                    model.type = 2
                if card_type==1:
                    model.login = GenPasswd2(length=random.randint(login_length_from, login_length_to),chars=login_mask)
                    model.tarif = tarif
                    model.type = 1
                    model.ippool = pool or None
                if card_type==2:
                    model.login = GenPasswd2(length=random.randint(login_length_from, login_length_to),chars=login_mask)
                    model.tarif = tarif
                    model.type = 3
                    
                model.nominal = nominal
                model.start_date = date_start
                model.end_date = date_end
                model.template = template
                
                model.created = dnow
                try:
                    print model.pin
                    print model.login
                    model.save()
                    i+=1
                except Exception, e:
                    print repr(e)
                    bad+=1

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False} 
    else:
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_card')):
            return {'status':True}
        now = datetime.datetime.now()
        card_type = request.GET.get("card_type")
        form = CardGenerationForm(initial={'card_type':card_type, 'count':100, 'nominal':0, "date_start":now, 'date_end':now+datetime.timedelta(days=365), 'login_length_from':6, 'login_length_to':6, 'pin_length_from':6, 'pin_length_to':6, 'login_letters':True, 'login_numbers':True, 'pin_letters':True, 'pin_numbers':True,})
   
    return { 'form':form, 'status': False} 

@login_required
@render_to('ebsadmin/card_update.html')
def card_update(request):
    item = None
    model = None
    ids = request.GET.getlist('d')
    print 1
    if request.method == 'POST': 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_card')):
            return {'status':False, 'message': u'У вас нет прав на добавление карт'}
        form = CardBatchChangeForm(request.POST)
        print request.POST
        if form.is_valid():
            card_type = int(form.cleaned_data.get("card_type"))
            print "card_type", card_type, type(card_type)
            pin_mask = ''
            if form.cleaned_data.get("pin_letters")==True:
                pin_mask+=string.letters
            if form.cleaned_data.get("pin_numbers")==True:
                pin_mask+=string.digits
            login_mask = ''
            if form.cleaned_data.get("login_letters")==True:
                login_mask+=string.letters
            if form.cleaned_data.get("login_numbers")==True:
                login_mask+=string.digits
                

            tarif = form.cleaned_data.get("tariff")
                
            template= form.cleaned_data.get("template")
            
            nas = form.cleaned_data.get("nas")
                
            pool=None
            pool = form.cleaned_data.get("pool")
             

            series=form.cleaned_data.get("series")
            change_pin=form.cleaned_data.get("change_pin")
            change_login=form.cleaned_data.get("change_login")
            nominal=form.cleaned_data.get("nominal")
            template=form.cleaned_data.get("template")
            
            
            date_start=form.cleaned_data.get("date_start")
            date_end=form.cleaned_data.get("date_end")
            
            pin_length_from=form.cleaned_data.get("pin_length_from")
            pin_length_to=form.cleaned_data.get("pin_length_to")
            
            login_length_from=form.cleaned_data.get("login_length_from")
            login_length_to=form.cleaned_data.get("login_length_to")
            
            #print date_start, date_end
            i=0
            bad=0
            """
            типы карт
            0 - экспресс оплата
            1 - хотспот
            2- vpn доступ 
            """
            ids = form.cleaned_data.get("cards", '').split(",")
            for id in ids:

                model = Card.objects.get(id=id)
                if series:
                    model.series = series
                if change_pin:
                    model.pin = GenPasswd2(length=random.randint(pin_length_from,pin_length_to), chars=pin_mask)
                if int(card_type)>-1:
                    model.type = card_type
                if change_login:
                    model.login =GenPasswd2(length=random.randint(login_length_from, login_length_to),chars=login_mask)
                if tarif:
                    model.tarif = tarif
                    
                if pool:
                    model.pool = pool
                if nas:
                    model.nas = nas
                if nominal:
                    model.nominal = nominal
                if template:
                    model.template = template
                   
                if date_start:
                    model.start_date = date_start
                    
                if date_end:
                    model.end_date = date_end
                    

                try:
                    model.save()
                    i+=1
                except Exception, e:
                    print repr(e)

                log('EDIT', request.user, model)
            return {'form':form,  'status': True} 
        else:
            print form._errors
            return {'form':form,  'status': False} 
    else:
        print 2
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.edit_card')):
            return {'status':True}
        print 3
        card_type = request.GET.get("card_type")
        print ids
        print 
        form = CardBatchChangeForm(initial={'cards': ','.join(ids), 'card_type':card_type,  'login_length_from':6, 'login_length_to':6, 'pin_length_from':6, 'pin_length_to':6, 'login_letters':True, 'login_numbers':True, 'pin_letters':True, 'pin_numbers':True,})
        print 4
    return { 'form':form, 'status': False} 

@ajax_request
@login_required
def card_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_card')):
        return {'status':False, 'message': u'У вас нет прав на удаление карточек'}
    id = request.GET.getlist('d')
    if id:
        try:
            items = Card.objects.filter(id__in=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная карта не найдена %s" % str(e)}
        for item in items:
            log('DELETE', request.user, item)
            item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "Card not found"} 
    
@ajax_request
@login_required
def card_manage(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.edit_card')):
        return {'status':False, 'message': u'У вас нет прав на редактирование карточек'}
    id = request.GET.getlist('d')
    action = request.GET.get('action')
    if id:
        try:
            items = Card.objects.filter(id__in=id)
        except Exception, e:
            return {"status": False, "message": u"Указанная карта не найдена %s" % str(e)}
        for item in items:
            if action == 'enable':
                log('EDIT', request.user, item)
                item.disabled=False
                item.save()
            elif action == 'disable':
                log('EDIT', request.user, item)
                item.disabled=True
                item.save()
        return {"status": True}
    else:
        return {"status": False, "message": "Card not found"}
    
@login_required
@render_to('ebsadmin/salecard_list.html')
def salecard(request):
    res = SaleCard.objects.all()
    table = SaleCardTable(res)
    table_to_report = RequestConfig(request, paginate=True if not request.GET.get('paginate')=='False' else False).configure(table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
            
    return {"table": table}
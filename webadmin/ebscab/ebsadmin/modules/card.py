# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2.config import RequestConfig
from object_log.models import LogItem

from ebsadmin.tables import CardTable
from ebsadmin.randgen import GenPasswd2
from billservice.forms import CardForm, CardGenerationForm, CardSearchForm
from billservice.models import Card
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
            activated = form.cleaned_data.get("activated")
            activated_by = form.cleaned_data.get("activated_by")
    
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
        RequestConfig(request, paginate = False).configure(table)
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
@render_to('ebsadmin/card_generate.html')
def card_generate(request):
    id = request.GET.get("id")
    item = None
    model = None
    if request.method == 'POST': 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_card')):
            return {'status':False, 'message': u'У вас нет прав на добавление карт'}
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
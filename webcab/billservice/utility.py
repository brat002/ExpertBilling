# -*- coding:utf-8 -*-
from dateutil.relativedelta import relativedelta
import datetime
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django import template
from django.conf import settings
from billservice.forms import LoginForm
from dateutil.relativedelta import relativedelta

import calendar


def in_period(time_start, length, repeat_after, now=None):

    if not now:
        now=datetime.datetime.now()
    #time_start=time_start.replace(tzinfo='UTC')
    if repeat_after=='DAY':
        delta_days=now - time_start

        #Когда будет начало в текущем периоде.
        nums,ost= divmod(delta_days.days*86400+delta_days.seconds, 86400)
        tnc=now-datetime.timedelta(seconds=ost)
        #Когда это закончится
        tkc=tnc+datetime.timedelta(seconds=length)
        if now>=tnc and now<=tkc:
            return True
        return False
    elif repeat_after=='WEEK':
        delta_days = now - time_start

        #Когда будет начало в текущем периоде.
        nums,ost = divmod(delta_days.days*86400+delta_days.seconds, 86400*7)
        tnc=time_start+relativedelta(weeks=nums)
        tkc=tnc+datetime.timedelta(seconds=length)

        #print tnc, tkc
        if now>=tnc and now<=tkc:
            #print "WEEK TRUE"
            return True
        return False
    elif repeat_after=='MONTH':
        #Февраль!
        rdelta = relativedelta(now, time_start)
        tnc=time_start+relativedelta(months=rdelta.months, years = rdelta.years)
        n_days=calendar.mdays[tnc.month]
        tkc=tnc+relativedelta(months=1)
        days=calendar.mdays[tkc.month]
        if time_start.day>tkc.day and days>=tkc.day:
            tkc=tkc.replace(day=days)
        if now>=tnc and now<=tkc:
            return True
        return False
    elif repeat_after=='YEAR':
        #Февраль!
        rdelta = relativedelta(now, time_start)
        tnc=time_start+relativedelta(years = rdelta.years)
        tkc=tnc+datetime.timedelta(seconds=length)
        if now>=tnc and now<=tkc:
            return True
        return False
    elif repeat_after=='DONT_REPEAT':
        delta_days=now - time_start

        tkc=time_start+datetime.timedelta(seconds=length)
        if now>=time_start and now<=tkc:
            return True
        return False
def settlement_period_info(time_start, repeat_after='', repeat_after_seconds=0,  now=None, prev = False):
    """
        Функция возвращает дату начала и дату конца текущего периода
        @param time_start: время начала расчётного периода
        @param repeat_after: период повторения в константах
        @param repeat_after_seconds: период повторения в секундах
        @param now: текущая дата
        @param prev: получить данные о прошлом расчётном периоде     
    """

    #print time_start, repeat_after, repeat_after_seconds,  now

    if not now:
        now=datetime.datetime.now()
    #time_start=time_start.replace(tzinfo='UTC')
    #print "repeat_after_seconds=",repeat_after_seconds
    if repeat_after_seconds>0:
        #print 1
        delta_days = (now - time_start) if not prev else (now-datetime.timedelta(seconds=repeat_after_seconds) - time_start)
        length=repeat_after_seconds
        if repeat_after!='DONT_REPEAT':
            #Когда будет начало в текущем периоде.
            nums,ost= divmod(delta_days.days*86400+delta_days.seconds, length)
            tnc=now-datetime.timedelta(seconds=ost)
            #Когда это закончится
            tkc=tnc+datetime.timedelta(seconds=length)
            return (tnc, tkc, length)
        else:
            return (time_start,time_start+datetime.timedelta(seconds=repeat_after_seconds), repeat_after_seconds)
    elif repeat_after=='DAY':
        delta_days = (now - time_start) if not prev else (now-datetime.timedelta(seconds=86400) - time_start)
        length=86400
        #Когда будет начало в текущем периоде.
        nums,ost= divmod(delta_days.days*86400+delta_days.seconds, length)
        tnc=now-datetime.timedelta(seconds=ost)
        #Когда это закончится
        tkc=tnc+datetime.timedelta(seconds=length)
        return (tnc, tkc, length)

    elif repeat_after=='WEEK':
        delta_days = (now - time_start) if not prev else (now-datetime.timedelta(seconds=604800) - time_start)
        length=604800
        #Когда будет начало в текущем периоде.
        nums,ost= divmod(delta_days.days*86400+delta_days.seconds, length)
        tnc=time_start+relativedelta(weeks=nums)
        tkc=tnc+relativedelta(weeks=1)
        return (tnc, tkc, length)
    
    elif repeat_after=='MONTH':
        rdelta = relativedelta(now, time_start) if not prev else relativedelta(now-relativedelta(months=1),time_start)
        tnc=time_start+relativedelta(months=rdelta.months, years = rdelta.years)
        
        n_days=calendar.mdays[tnc.month]
        tkc=tnc+relativedelta(months=1)
        days=calendar.mdays[tkc.month]
        if time_start.day>tkc.day and days>=tkc.day:
            tkc=tkc.replace(day=days)
        #Если начало - конец месяца, то во всех следующих месяцах выбираем максимальный день месяца
        #if tnc.day>tkc.day and days>tkc.day:
        #    
        #    tkc=tnc.replace(month=tnc.month+1)
        delta=tkc-tnc

        return (tnc, tkc, delta.days*86400+delta.seconds)
    elif repeat_after=='YEAR':
        #Февраль!
        #To-DO: Добавить проверку на prev 
        tnc=time_start+relativedelta(years=relativedelta(now, time_start).years)

        tkc=tnc+relativedelta(years=1)
        delta=tkc-tnc
        return (tnc, tkc, delta.days*86400+delta.seconds)
        
def is_login_user(request):         
   form = LoginForm()
   context = {
               'MEDIA_URL':settings.MEDIA_URL,
               'form':form,
               }
   return render_to_response('registration/login.html',
                              context,
                              context_instance=RequestContext(request))
   
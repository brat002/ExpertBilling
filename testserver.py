#-*-coding:utf-8 -*-

import datetime
import datetime, calendar
from dateutil.relativedelta import relativedelta
dateDelim = "."
strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"

def settlement_period_info(time_start, repeat_after='', repeat_after_seconds=0,  now=None, prev = False):
        """
        Функция возвращает дату начала и дату конца текущегопериода
        """
        
        #print time_start, repeat_after, repeat_after_seconds,  now
        
        if not now:
            now=datetime.datetime.now()
        #time_start=time_start.replace(tzinfo='UTC')
        #print "repeat_after_seconds=",repeat_after_seconds
        if repeat_after_seconds>0:
            #print 1
            if prev==False:
                delta_days=now - time_start
            else:
                delta_days=now-datetime.timedelta(seconds=repeat_after_seconds) - time_start
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
            if prev==False:
                delta_days=now - time_start
            else:
                delta_days=now-datetime.timedelta(seconds=86400) - time_start
            length=86400
            #Когда будет начало в текущем периоде.
            nums,ost= divmod(delta_days.days*86400+delta_days.seconds, length)
            tnc=now-datetime.timedelta(seconds=ost)
            #Когда это закончится
            tkc=tnc+datetime.timedelta(seconds=length)
            return (tnc, tkc, length)

        elif repeat_after=='WEEK':
            if prev==False:
                delta_days=now - time_start
            else:
                delta_days=now-datetime.timedelta(seconds=604800) - time_start
            length=604800
            #Когда будет начало в текущем периоде.
            nums,ost= divmod(delta_days.days*86400+delta_days.seconds, length)
            tnc=start+relativedelta(weeks=nums)
            tkc=tnc+relativedelta(weeks=1)

            return (tnc, tkc, length)
        elif repeat_after=='MONTH':
            if prev==False:
                months=relativedelta(now,time_start).months
            else:
                months=relativedelta(now-relativedelta(months=1),time_start).months
                
            tnc=time_start+relativedelta(months=months)
            tkc=tnc+relativedelta(months=1)
            delta=tkc-tnc

            return (tnc, tkc, delta.days*86400)
        elif repeat_after=='YEAR':
            #Февраль!
            #To-DO: Добавить проверку на prev 
            tnc=start+relativedelta(years=relativedelta(now, time_start).years)

            tkc=tnc+relativedelta(years=1)
            delta=tkc-tnc
            return (tnc, tkc, delta.seconds)
    
start=datetime.datetime(year=2008, month=1, day=1)    
now = datetime.datetime(year=2012, month=2, day=9)

n,c,s = settlement_period_info(time_start=start, repeat_after='WEEK', now=now)

print n.strftime(strftimeFormat), c.strftime(strftimeFormat)

#print start+relativedelta(years=relativedelta(now, start).years)








#-*- coding=utf-8 -*-
import datetime

def convert_values(value):
    if str(value).endswith('k'):
        return str(int(str(value)[0:-1])*1000)
    elif str(value).endswith('M'):
        return str(int(str(value)[0:-1])*1000*1000)
    else:
        return str(value)
                
def get_decimals_speeds(params):
    #print "before", params
    i = 0
    for param in params:
        #values = map(convert_values, str(params[param]).split('/'))
        values = map(convert_values, str(param).split('/'))
        #print values
        params[i] ='/'.join(values)
        i += 1
    #print 'after', params
    return params

def split_speed(speed):
    return speed.split("/")

def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).
    """

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(int(el))
    return result

def check_speed(speed):
    speed = flatten(map(split_speed,get_decimals_speeds(speed)))
    return speed[0]>speed[9] and speed[1]>speed[10] and \
    speed[2]>speed[0] and speed[3]>speed[1] and \
    speed[4]>speed[9] and speed[5]>speed[10] and speed[4]<speed[2] and speed[5]<speed[3] and speed[4]<speed[0] and speed[5]<speed[1]



from utilites import in_period
from utilites import in_period_info

data = []
#1 Каждый день
data.append((datetime.datetime(2008, 01, 01, 0,0,0), 86400, 'DAY',  [[datetime.datetime(2009, 01, 01, 2,0,1), True],
                                                                               [datetime.datetime(2009, 12, 31, 0,0,1), True],
                                                                               [datetime.datetime(2009, 02, 28, 0,0,1), True],
                                                                               [datetime.datetime(2012, 02, 29, 0,0,1), True],
                                                                               ]))
#2 Каждый понедельник
data.append((datetime.datetime(2008, 01, 07, 0,0,0), 86400, 'WEEK', [[datetime.datetime(2009, 02, 01, 10,0,12), False],
                                                                               [datetime.datetime(2009, 02, 02, 0,0,1), True],
                                                                               [datetime.datetime(2012, 02, 27, 0,0,1), True],
                                                                               [datetime.datetime(2009, 03, 16, 0,0,1), True],
                                                                               ]))
#3 Первое число каждого месяца
data.append((datetime.datetime(2008, 01, 01, 0,0,1), 86400, 'MONTH', [[datetime.datetime(2010, 01, 01, 0,0,1), True],
                                                                               [datetime.datetime(2009, 01, 02, 0,0,2), False],
                                                                               [datetime.datetime(2012, 02, 27, 0,0,1), False],
                                                                               [datetime.datetime(2009, 03, 16, 0,0,1), False],
                                                                               ]))

#4 Каждый новый год
data.append((datetime.datetime(2008, 12, 31, 0,0,0), 86400*2, 'YEAR', [[datetime.datetime(2009, 01, 01, 0,0,1), True],
                                                                               [datetime.datetime(2010, 12, 31, 01,01,01), True],
                                                                               [datetime.datetime(2010, 12, 28, 01,01,01), False],
                                                                               ]))


#print in_period_info(start, 86400,'YEAR',now)

print "========testing in_period================="
for d in data:
    for n in d[3]:
        print in_period(d[0], d[1], d[2], n[0])==n[1]

print "testing in_period_info"
from utilites import settlement_period_info
for d in data:
    for n in d[3]:
        print in_period_info(d[0], d[1], d[2], n[0])



print "testing settlement periods"
data=[]
# date repeat_after repeat_after_seconds
 
data.append((datetime.datetime(2008, 01, 01, 0,0,1), 'DAY', 0))        
data.append((datetime.datetime(2008, 01, 01, 0,0,1), 'WEEK', 0))
data.append((datetime.datetime(2008, 01, 01, 0,0,1), 'MONTH', 0))
data.append((datetime.datetime(2008, 01, 01, 0,0,1), 'YEAR', 0))
data.append((datetime.datetime(2008, 01, 01, 0,0,1), '', 2592000))
data.append((datetime.datetime(2008, 01, 01, 0,0,1), 'DONT_REPEAT', 2592000))

data.append((datetime.datetime(2008, 01, 29, 0,0,1), 'DAY', 0))        
data.append((datetime.datetime(2008, 01, 29, 0,0,1), 'WEEK', 0))
data.append((datetime.datetime(2008, 01, 29, 0,0,1), 'MONTH', 0))
data.append((datetime.datetime(2008, 01, 29, 0,0,1), 'YEAR', 0))
data.append((datetime.datetime(2008, 01, 29, 0,0,1), '', 2592000))
data.append((datetime.datetime(2008, 01, 29, 0,0,1), 'DONT_REPEAT', 2592000))

now_dates = []
now_dates.append(datetime.datetime(2008, 12, 31, 0,0,1))
now_dates.append(datetime.datetime(2009, 12, 31, 0,0,1))
now_dates.append(datetime.datetime(2009, 1, 1, 0,0,1))
now_dates.append(datetime.datetime(2008, 10, 26, 3,0,0))
now_dates.append(datetime.datetime(2012, 02, 29, 0,0,1))

for n in now_dates:
    for d in data:
        print "======="
        print "for date", n
        print "check", d[0], d[1], d[2]
        print settlement_period_info(d[0], d[1], d[2], n)
        print "======="
        raw_input()
        




 
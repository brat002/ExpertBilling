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
        
        
"sp"
'6;"+Месяц";"2008-12-05 15:30:53.502";0;"MONTH";TRUE'
'7;"Месяц";"2009-01-01 00:00:00";0;"MONTH";FALSE'
'11;"+Месяц 30 дней";"2009-02-23 13:08:00.006";0;"MONTH";TRUE'
'12;"Месяц 30 дней";"2009-01-01 00:00:00";2592000;"''";FALSE'



"""cacheAT"""
"""
tarif{ba.id, ba.ballance,ba.credit,act.datetime,bt.id,bt.access_parameters_id,bt.time_access_service_id,bt.traffic_transmit_service_id,bt.cost,bt.reset_tarif_cost,bt.settlement_period_id,bt.active,act.id,FALSE,ba.created,ba.disabled_by_limit,ba.balance_blocked,ba.nas_id,ba.vpn_ip_address,ba.ipn_ip_address,ba.ipn_mac_address,ba.assign_ipn_ip_from_dhcp,ba.ipn_status,ba.ipn_speed,ba.vpn_speed,ba.ipn_added,bt.ps_null_ballance_checkout,bt.deleted,bt.allow_express_pay,ba.status,ba.allow_vpn_null, ba.allow_vpn_block, ba.username, ba.password}
"""
{17: [(181, 4018.3580645000002, 0.0, datetime.datetime(2009, 2, 18, 13, 12, 46, 187000), 17, 24, None, 7, 20000.0, True, 7, True, 196, False, datetime.datetime(2008, 12, 5, 15, 59, 59, 318000), False, True, 3, '192.168.11.100', '10.10.1.2', u'', False, False, u'', u'', False, False, False, False, True, False, False, u'user', u'2'), 
      (182, -1131.7142858, 0.0,datetime.datetime(2009, 2, 18, 13, 11, 53, 873000), 17, 24, None, 7, 20000.0, True, 7, True, 195, False, datetime.datetime(2009, 2, 5, 10, 32, 47, 792000), False, True, 3, '0.0.0.0', '10.10.1.3', u'', False, False, u'', u'', True, False, False, False, True, False, False, u'maun', u'5FTkT6zn'), 
      (184, -20003.714285714301, 0.0, datetime.datetime(2009, 2, 18, 13, 13, 46, 819000), 17, 24, None, 7, 20000.0, True, 7, True, 197, False, datetime.datetime(2009, 2, 6, 13, 31, 18, 156000), False, True, 3, '0.0.0.0', '10.10.10.10', u'', False, False, u'', u'', False, False, False, False, True, False, False, u'eiboassaur', u'3MYRhkUK')], 
22: [(183, -9107.1428571413799, 0.0, datetime.datetime(2009, 2, 5, 13, 33, 3, 125000), 22, 29, None, None, 0.0, False, None, True, 193, False, datetime.datetime(2009, 2, 5, 13, 33, 3), False, False, 3, '192.123.12.21', '0.0.0.0', u'', False, False, u'', u'', False, False, False, False, True, False, False, u'duloasis', u'mypGguNi')], 
23: [(187, 0.0, 0.0, datetime.datetime(2009, 2, 18, 14, 35, 4, 612961), 23, 30, None, None, 0.0, False, 6, True,200, False, datetime.datetime(2009, 2, 18, 14, 36, 43, 920000), False, False, 3, '192.168.100.4', '0.0.0.0', u'', False, False, u'', u'', False, False, False, False, True, False, False, u'test4', u'1avNywPT'), 
     (185, -1.0, 0.0, datetime.datetime(2009, 2, 18, 14, 26, 37, 220000), 23, 30, None, None, 0.0, False, 6, True, 198, False, datetime.datetime(2009, 2, 18, 14, 26, 37, 111000), False, False, 3, '192.168.100.1', '0.0.0.0', u'', False, False, u'', u'', False, False, False, False, True, False, False, u'test1', u'test1')], 
24: [(188, -10.0, 0.0, datetime.datetime(2009, 2, 18, 14, 40, 49, 238691), 24, 31, None, None, 10.0, False, 6, True, 201, False, datetime.datetime(2009, 2, 18, 14, 42, 28, 446000), False, True, 3, '192.168.100.5', '0.0.0.0', u'', False, False, u'', u'', False, False, False, False, True, False, False, u'test_5', u'pFkBCag5')], 
25: [(189, -10.0, 0.0, datetime.datetime(2009, 2, 18, 15, 44, 37, 244005), 25, 32, None, None, 10.0, True, 6, True, 202, False, datetime.datetime(2009, 2, 18, 15, 46, 16, 253000), False, True, 3, '192.168.100.6', '0.0.0.0',u'', False, False, u'', u'', False, False, False, False, True, False, False, u'test6', u'test6')], 
26: [(190, 5.0, 0.0,datetime.datetime(2009, 2, 21, 12, 57, 38, 872729), 26, 33, None, None, 0.0, False, None, True, 203, False, datetime.datetime(2009, 2, 21, 12, 59, 22, 871000), False, False, 3, '192.168.11.202', '0.0.0.0', u'', False, False, u'', u'', False, False, False, False, True, False, False, u'testdn', u'testdn')]}

"""cachePerTarif
tarif_id, settlement_period_id
"""
[(20, 7), (18, None), (19, None), (21, None), (22, None)]

"""cachePerSetp"""
"""tarif_id{ b.id, b.name, b.cost, b.cash_method, c.name, c.time_start, c.length, c.length_in, c.autostart, b.tarif_id, b.condition, b.created}
b - periodical_service
c - settlement_period
"""
{18: [(5, u'1200 \u0440\u0443\u0431\u043b\u0435\u0439 \u0432 \u043c\u0435\u0441\u044f\u0446', 1200.0, u'GRADUAL', u'+\u041c\u0435\u0441\u044f\u0446', datetime.datetime(2008, 12, 5, 15, 30, 53, 502000), 0, u'MONTH', True, 18, 0, None), (13,u'1', 1.0, u'GRADUAL', u'+\u041c\u0435\u0441\u044f\u0446', datetime.datetime(2008, 12, 5, 15, 30, 53, 502000), 0, u'MONTH', True, 18, 0, datetime.datetime(2009, 2, 16, 16, 28, 3, 861320)), (14, u'2', 2.0, u'GRADUAL', u'+\u041c\u0435\u0441\u044f\u0446', datetime.datetime(2008, 12, 5, 15, 30, 53, 502000), 0, u'MONTH', True, 18, 0, None)], 19: [(6, u'1500 \u0440\u0443\u0431\u043b\u0435\u0439 \u0432 \u043c\u0435\u0441\u044f\u0446', 1500.0, u'GRADUAL', u'\u041c\u0435\u0441\u044f\u0446', datetime.datetime(2008, 12, 1, 0, 0, 0, 994000), 0, u'MONTH', False, 19, 0, None)], 20: [(7, u'\u0410\u0431\u043e\u043d\u0435\u043d\u0442\u0441\u043a\u043e\u0435 \u043e\u0431\u0441\u043b\u0443\u0436\u0438\u0432\u0430\u043d\u0438\u0435', 100.0, u'GRADUAL', u'+\u041c\u0435\u0441\u044f\u0446', datetime.datetime(2008, 12, 5, 15, 30, 53, 502000), 0, u'MONTH', True, 20, 0, None), (11, u'\u041f\u043b\u0430\u0442\u0430 \u0437\u0430 \u043f\u0440\u043e\u0441\u0442\u043e\u0439',2.0, u'GRADUAL', u'\u0421\u0443\u0442\u043a\u0438', datetime.datetime(2008, 12, 1, 0, 0), 0, u'DAY', False, 20, 2, None)], 21: [(8, u'Unlim 256', 42000.0, u'GRADUAL', u'+\u041c\u0435\u0441\u044f\u0446', datetime.datetime(2008, 12, 5, 15, 30, 53, 502000), 0, u'MONTH', True, 21, 0, None)], 22: [(9, u'Unlim', 20000.0, u'GRADUAL', u'+\u041c\u0435\u0441\u044f\u0446', datetime.datetime(2008, 12, 5, 15, 30, 53, 502000), 0, u'MONTH', True, 22, 0, None)]}

"""cacheSuspP"""
"account_id{account_id, susp_per}"
{189: [(2, 189)]}

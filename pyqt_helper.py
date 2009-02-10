#-*- coding=utf-8 -*-

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




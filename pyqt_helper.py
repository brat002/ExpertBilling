#-*- coding=utf-8 -*-

a=1800

def prntime(s):

    m,s=divmod(s,60)
    h,m=divmod(m,60)
    if h==0 and m==0:
        return u"%sс" % s
    elif h==0 and m!=0:
        return u"%sм %sс" % (m,s,)
    else:
        return u"%sч %sм %sс" % (h,m,s)
    
    
print prntime(a)
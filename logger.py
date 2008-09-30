import sys
#print 123

class Log:
    """file like for writes with auto flush after each write
    to ensure that everything is logged, even during an
    unexpected exit."""
    def __init__(self, f):
        self.f = f
    def write(self, s):
        self.f.write(s)
        self.f.flush()




#sys.stderr=sys.stdout=Log(open('/opt/www/vhosts/drugme.ru/www/drugme/rpclog.txt','a+'))

def redirect_std(module, redirect=True):
    if redirect==True:
        f=open("./log/%s.log" % module,"a+")
        handle=Log(f)
        
        sys.stdout=handle
        sys.stderr=handle
    
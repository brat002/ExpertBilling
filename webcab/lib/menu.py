from django.core.urlresolvers import reverse

class ReversrConf(object):
    def __init__(self, view_name, args, kwargs):
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs

def get_reverse_conf(view_name, *args, **kwargs):
    return ReversrConf(view_name, args, kwargs)

class Menu(object):
    """
    Common menu generator
    """
    def __init__(self, current_view_name=None):
        self.items = []
        self.current_view_name = current_view_name

    def flatten_attrs(self, attrs):
        if attrs:
            return " ".join([u'%s=%s' % (name, value) for name,value in attrs.items()])
        return u''
                    
    def add(self, reverse_conf, verbose_name, attrs=None):
        """
        @param revers_conf string Name of a view
        @param verbose_name unicode/proxystring Displayed link
        @attrs dict Optional html attributes will be applied to the `a` tag 
        """
        if isinstance(reverse_conf, basestring):
            reverse_conf = get_reverse_conf(reverse_conf)
        
        self.items.append({
            'name': reverse_conf.view_name, # url name from urls.py
            'verbose_name': verbose_name,
            'url': reverse_conf.view_name.startswith("/") \
                   and reverse_conf.view_name \
                   or reverse(reverse_conf.view_name, \
                              args=reverse_conf.args, kwargs=reverse_conf.kwargs),
            'is_current': self.check_current(reverse_conf),
            'attrs': self.flatten_attrs(attrs)
        })
        
    def check_current(self, reverse_conf):
        if callable(self.current_view_name):
            return self.current_view_name(reverse_conf)
        else:
            return reverse_conf.view_name == self.current_view_name 
    
    def __iter__(self):
        return iter(self.items)

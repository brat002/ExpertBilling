class CharField(object):
    def __init__(self, length=255):
        self.value=''

class IntegerField(object):
    def __init__(self):
        self.value=''

class FloatField(object):
    def __init__(self):
        self.value=''
        
class BaseModel(object):
    def __init__(self):
        self.id=0
        
        
class TrafficClass(BaseModel):
    def __init__(self):
        super(TrafficClass, self).__init__()
        name = ''
        weight = 0
        color = '#FFFFFF'
        store    = False
        passthrough = False
        
class TrafficNode(BaseModel):
    def __init__(self):
        super(TrafficNode, self).__init__()
        self.clas = TrafficClass()
        name = ''
        direction = ''
        protocol = ''
        src_ip  = '0.0.0.0/0'
        src_port  = 0
        dst_ip = '0.0.0.0/0'
        dst_mask='0.0.0.0'
        dst_port  = 0
        next_hop = '0.0.0.0'
        
class Nas(BaseModel):
    def __init__(self):
        super(Nas, self).__init__()

        type = 'mikrotik3'
        name = ''
        ipaddress = ''
        secret = models.CharField(verbose_name=u'Секретная фраза', help_text=u"Смотрите вывод команды /radius print", max_length=255)
        login = models.CharField(verbose_name=u'Имя для доступа к серверу по SSH', max_length=255, blank=True, default='admin')
        password = models.CharField(verbose_name=u'Пароль для доступа к серверу по SSH', max_length=255, blank=True, default='')
        #description = models.TextField(verbose_name=u'Описание', blank=True, default='')
        allow_pptp = models.BooleanField(verbose_name=u'Разрешить серверу работать с PPTP', default=True)
        allow_pppoe = models.BooleanField(verbose_name=u'Разрешить серверу работать с PPPOE', default=True)
        allow_ipn = models.BooleanField(verbose_name=u'Сервер поддерживает IPN', help_text=u"IPN - технология, которая позволяет предоставлять доступ в интернет без установления VPN соединения с сервером доступа", default=True)
        user_add_action = models.TextField(verbose_name=u'Действие при создании пользователя',blank=True, null=True)
        user_enable_action = models.TextField(verbose_name=u'Действие при разрешении работы пользователя',blank=True, null=True)
        user_disable_action = models.TextField(verbose_name=u'Действие при запрещении работы пользователя',blank=True, null=True)
        user_delete_action = models.TextField(verbose_name=u'Действие при удалении пользователя',blank=True, null=True)
        vpn_speed_action = models.TextField(max_length=255, blank=True, default="")
        ipn_speed_action = models.TextField(max_length=255, blank=True, default="")
        reset_action = models.TextField(max_length=255, blank=True, default="")
        confstring = models.TextField(verbose_name="Конфигурация по запросу", blank=True, default='')
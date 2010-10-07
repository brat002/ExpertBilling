#-*-coding=utf-8-*-

from django.db import models
   
   
class DealerTarif(models.Model):
    cost = models.DecimalField(decimal_places=2, max_digits=32)#Стоимость тарифного плана на месяц
    allowed_hotspots = models.IntegerField()# 0 -unlimited
    cards_in_month = models.IntegerField()# Суммируем карты доступа и пополнения баланса
    card_expiration_period = models.PositiveInteger() # Число дней в течении которых активированные карты можно использовать
    
class Dealer(models.Model):
    name = models.CharField(max_length=32)
    tarif = models.ForeignKey(DealerTarif)
    password = models.CharField(max_length=32)
    address = models.CharField(max_length=32)
    phone = models.CharField(max_length=32)
    currency = models.CharField(max_length=32)
    wmz = models.CharField(max_length=255)# Номер WMZ кошелька
    yandex_money = models.CharField(max_length=255)# Номер YandexMoney кошелька
    allow_activate_unsold_cards = models.BooleanField(default=True)
    
class HotSpot(models.Model):
    """
    Хотспот абонента
    """
    
    NAS_TYPES=(
    ("MikroTik", "MikroTik"),
    )
    dealer = models.ForeignKey(Dealer)
    name = models.CharField(max_length=32, blank=False)
    location = models.CharField(max_length=32, default='', blank=True)#Физический адрес                  
    type = models.CharField(max_length=32, choices=NAS_TYPES)#MikroTik/DD-WRT. Пока только MikroTik
    ip = models.CharField(max_length=32, blank=False) #Может быть как IP так и доменным именем
    identify = models.CharField(max_length=32, blank=False) #Radius параметр. Генерируем сами и идендифицируем хотспот абонента по этому идентификатору 
    secret = models.CharField(max_length=32, blank=False)#Radius параметр 
    comment = models.TextField()#Описание
    active = models.BooleanField(default = True)
    
    
    
   
class Profile(models.Model):
    """Cпособ тарификации услуги. 
    """

    dealer = models.ForeignKey(Dealer)
    #В пределах одного профиля может быть указан или лимитированный объём услуги 
    time_limit = models.IntegerField()
    time_limit_units = models.CharField(max_length=32)#s/m/h
    traffic_limit_in = models.IntegerField()
    traffic_limit_out = models.IntegerField()
    traffic_limit_total = models.IntegerField()
    traffic_limit_units = models.IntegerField()#kb/mb/gb
    #;
    defspeed = models.CharField(max_length=32) #применимо только, если сервер доступа MikroTik. Формат rx/tx (вх/исх)
    created = models.DateTimeField()
    allowed_hotspots = models.ManyToManyField(HotSpot) # Хотспоты дилера, на которых разрешено активировать карточки для пополнения этого профиля

class RadiusAttr(models.Model):
    """
    Дополнительные RADIUS атрибуты, которые можно назначить тарифному плану
    """
    vendor_id = models.IntegerField()
    attr_id = models.IntegerField()
    value_type = models.CharField(max_length=32)#ip, int, string
    value = models.CharField(max_length=1024)
    profile = models.ForeignKey(Profile)

    
class CardUser(models.Model):
    """
    Нужно реализовать механизм генерации карт.
    В параметрах генерации - длина логина, составь логина(буквы-цифры), длина пина, став пина(буквы-цифры) 
    Если карты ещё не активированы и не проданы - даём возможность удалять их из системы
    """
    dealer = models.ForeignKey(Dealer)
    series = models.IntegerField(max_length=32)#Нужно сделать автоинкремент в пределах одного дилера
    card_id = models.IntegerField()#Нужно сделать автоинкремент в пределах одного дилера
    login = models.CharField(max_length=32)
    pin = models.CharField(max_length=32) #(пароль)
    profile = models.ForeignKey(Profile, blank=True)
    """
    Каждый раз при получении Accounting Alive пакета обновляем эти поля соответствующими значениями из атрибутов сессии.
    rest_of_traffic_in
    rest_of_traffic_out
    rest_of_traffic_total
    """
    rest_of_traffic_in = models.IntegerField()# в байтах
    rest_of_traffic_out = models.IntegerField()# в байтах    
    rest_of_traffic_total = models.IntegerField()# в байтах
    rest_of_time = models.IntegerField()# в секундах
    activated_on_hotspot = models.ForeignKey(HotSpot)
    created = models.DateTimeField()
    activation_date = models.DateTimeField()
    active = models.BooleanField(default = True)
    
class CardTemplate(models.Model):
    """
    Шаблон для шаблонизатора, который будет рисовать карточки для их последующей распечатки
    """
    body = models.TextField()
    
    

class RadiusSession(models.Model):
    """
    Сессии абонентов
    """
    dealer = models.ForeignKey(Dealer)
    hotspot = models.ForeignKey(HotSpot)
    username = models.CharField(max_length=32)
    card = models.ForeignKey(CardUser)
    bytes_in = models.IntegerField()
    bytes_out = models.IntegerField()
    session_time = models.IntegerField()
    rest_of_time = models.IntegerField()
    rest_of_traffic_in = models.IntegerField()
    rest_of_traffic_out = models.IntegerField()
    rest_of_traffic_total = models.IntegerField()

    
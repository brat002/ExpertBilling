#-*-coding=utf-8-*-

from django.db import models
from ebscab.billservice.models import Account

from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

'''
    Источник тикета
'''
WEBCAB = 1
ICQ = 2
PHONE = 3
EMAIL = 4

SOURCE_TYPES = (
                (WEBCAB,u"Веб-кабинет"),
                (ICQ,u"ICQ"),
                (PHONE,u"Телефон"),
                (EMAIL,u"Электронная почта"),
                )

'''
    Cтатус тикета
'''
NEW = 1
OPENED = 2
HOLD = 3
CLOSED = 4
RESOLVED = 5
REOPENED = 6
INVALID = 7

TICKET_STATUS = (
                (NEW, u"Новый",), # - Тикет ни на кого не назначен
                (OPENED, u"Открыт",), # - Тикет назначен, идёт работа
                (HOLD, u"Удержание",),# - Тикет назначен, идёт работа, тикет невозможно переназначить без смены статуса
                (CLOSED, u"Закрыт",), # - Тикет закрыт - может быть архивирован
                (RESOLVED, u"Решён",), # - Тикет закрыт - может быть архивирован                
                (REOPENED, u"Переоткрыт",), # - Тикет закрыт - может быть архивирован                
                (INVALID, u"Отклонён",),# - Тикет отклонён - может быть архивирован
                )

'''
   Тип тикета 
'''

PASSWORD_REQUEST = 1 
ACCOUNT_INFO_REQUEST = 2
NEW_CLIENT = 3
BILLING_PROBLEM = 4
NETWORK_PROBLEM = 5
OTHER = 6

TICKET_TYPE = (
                (PASSWORD_REQUEST, u"Запрос на смену парля",),
                (ACCOUNT_INFO_REQUEST, u"Запрос на смену информации о абоненте",),
                (NEW_CLIENT, u"Подключение нового абонента",),
                (BILLING_PROBLEM, u"Ошибка в расчётах",),
                (NETWORK_PROBLEM, u"Проблема сети",),
                (OTHER, u"Другое",),
                )

'''
    Дополнительный тип тикета
'''
USER_ERROR = 1 
SYSTEM_ERROR = 2
NETWORK_HARDWARE_ERROR = 3
VIRUSES = 4
DECEPTION = 5
OTHER = 6

TICKET_ADDITIONAL_TYPE=(
                (USER_ERROR, u"Ошибка пользователя",),
                (SYSTEM_ERROR, u"Ошибка системы",),
                (NETWORK_HARDWARE_ERROR, u"Сбой оборудования",),
                (VIRUSES, u"Вирусы",),
                (DECEPTION, u"Попытка обмана",),
                (OTHER, u"Другое",),
                )



class Ticket(models.Model):
    account = models.ForeignKey(Account, blank=True, null = True) # Пользователь, владелец тикета
    email = models.EmailField(blank=True, default="")
    source = models.CharField(max_length=32, choices=SOURCE_TYPES) # Способ получения тикета
    subject = models.CharField(max_length=1024) # Тема тикета
    body = models.TextField() # Содержание тикета
    
    content_type = models.ForeignKey(ContentType, editable=False, null=True, blank=True)
    object_id = models.PositiveIntegerField(editable=False, null=True, blank=True)
    assigned_to = generic.GenericForeignKey('content_type', 'object_id')    

    assign_date = models.DateTimeField() # Дата открытия(назначения) тикета
    status = models.CharField(max_length=32, choices = TICKET_STATUS)
    type = models.CharField(max_length=32, choices = TICKET_TYPE)
    additional_status = models.CharField(max_length=32, choices = TICKET_ADDITIONAL_TYPE)
    priority = models.PositiveIntegerField()# от 0 до 4. 0 - критический, 1 - немедленно, 2-высокий, 3 - средний, 4-низкий
    created = models.DateTimeField() # Дата создания тикета
    last_update = models.DateTimeField()# - Дата последнего изменения
    archived = models.BooleanField(blank=True, default=False)
    
    
class Comment(models.Model):
    ticket = models.ForeignKey(Ticket)
    account = models.ForeignKey(Account, blank=True, default = True)# Поле исключает поле systemuser
    systemuser = models.ForeignKey(User, blank=True, default = True)# Поле исключает поле account
    body = models.TextField()
    time = models.IntegerField()#потраченное время. Поле видно только пользователю хелпдеска

    created = models.DateTimeField()
    

class Attachment(models.Model):
    """
    Аттачмент может быть как у тикета, так и у комментария к тикету
    """
    file = models.FileField(upload_to = '/uploads/')
    content_type = models.ForeignKey(ContentType, editable=False, null=True, blank=True)
    object_id = models.PositiveIntegerField(editable=False, null=True, blank=True)
    owner = generic.GenericForeignKey('content_type', 'object_id')
        
    
class Note(models.Model):
    """
    Скрытый комментарий, который видят только пользователя HelpDesk-а
    """
    ticket = models.ForeignKey(Ticket)
    user = models.ForeignKey(User)
    body = models.TextField()
    date = models.DateTimeField()
    

class TicketHistoryTemplate(models.Model):
    """
    Шаблоны сообщений для TicketHistory. Для каждого типа действия должен быть создан свой шаблон.
    """
    internal_name = models.CharField(max_length=256, unique=True)
    template = models.TextField()


class TicketHistrory(models.Model):
    """
    История действий над тикетом.
    """
    ticket = models.ForeignKey(Ticket)
    user = models.ForeignKey(User)
    action = models.TextField()
    created = models.DateTimeField()
    
    
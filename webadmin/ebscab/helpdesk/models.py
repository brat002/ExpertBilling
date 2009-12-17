#-*-coding=utf-8-*-

from django.db import models
from ebscab.billservice.models import Account

from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
SOURCE_TYPES=(
        (u"WEBCAB",u"Веб-кабинет"),
        (u"ICQ",u"ICQ"),
        (u"PHONE",u"Телефон"),
        (u"EMAIL",u"Электронная почта"),
        )

SESSION_STATUS=(
                (u"ACTIVE", u"Активна",),
                (u"NACK", u"Не сброшена",),
                (u"ACK", u"Cброшена",),
                )


TICKET_STATUS=(
                (u"NEW", u"Новый",), # - Тикет ни на кого не назначен
                (u"OPENED", u"Открыт",), # - Тикет назначен, идёт работа
                (u"HOLD", u"Удержание",),# - Тикет назначен, идёт работа, тикет невозможно переназначить без смены статуса
                (u"CLOSED", u"Закрыт",), # - Тикет закрыт - может быть архивирован
                (u"RESOLVED", u"Решён",), # - Тикет закрыт - может быть архивирован                
                (u"REOPENED", u"Переоткрыт",), # - Тикет закрыт - может быть архивирован                
                (u"INVALID", u"Отклонён",),# - Тикет отклонён - может быть архивирован
                )

TICKET_TYPE=(
                (u"PASSWORD_REQUEST", u"Запрос на смену парля",),
                (u"ACCOUNT_INFO_REQUEST", u"Запрос на смену информации о абоненте",),
                (u"NEW_CLIENT", u"Подключение нового абонента",),
                (u"BILLING_PROBLEM", u"Ошибка в расчётах",),
                (u"NETWORK_PROBLEM", u"Проблема сети",),
                (u"OTHER", u"Другое",),
                )

TICKET_ADDITIONAL_TYPE=(
                (u"USER_ERROR", u"Ошибка пользователя",),
                (u"SYSTEM_ERROR", u"Ошибка системы",),
                (u"NETWORK_HARDWARE_ERROR", u"Сбой оборудования",),
                (u"VIRUSES", u"Вирусы",),
                (u"DECEPTION", u"Попытка обмана",),
                (u"OTHER", u"Другое",),
                )



class Ticket(models.Model):
    account = models.ForeignKey(Account, blank=True, null = True) # Пользователь, владелец тикета
    email = models.EmailField(blank=True, default="")
    source = models.CharField(max_length=32, choices=SOURCE_TYPES) # Способ получения тикета
    subject = models.CharField(max_length=1024) # Тема тикета
    body = models.TextField() # Содержание тикета
    
    content_type = models.ForeignKey(ContentType, editable=False, null=True, blank=True, verbose_name=_(u'Content type'))
    object_id = models.PositiveIntegerField(editable=False, null=True, blank=True, verbose_name=_(u'Object Id'))
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
    file = models.FileField()
    content_type = models.ForeignKey(ContentType, editable=False, null=True, blank=True, verbose_name=_(u'Content type'))
    object_id = models.PositiveIntegerField(editable=False, null=True, blank=True, verbose_name=_(u'Object Id'))
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
    
    
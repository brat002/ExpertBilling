#-*-coding=utf-8-*-
from datetime import datetime

from django.db import models


from billservice.models import SystemUser, SystemGroup
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from billservice.models import Account
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

"""
Цвет статуса у тикета
"""
COLOR_TICKETS = (
                 (NEW,u"#4bd42f",),       # - Тикет ни на кого не назначен
                 (OPENED, u"#a2b247",), # - Тикет назначен, идёт работа
                 (HOLD, u"#fea019",),# - Тикет назначен, идёт работа, тикет невозможно переназначить без смены статуса
                 (CLOSED, u"#adadad",), # - Тикет закрыт - может быть архивирован
                 (RESOLVED, u"#9E7FB0",), # - Тикет закрыт - может быть архивирован                
                 (REOPENED, u"#d5bb75",), # - Тикет закрыт - может быть архивирован                
                 (INVALID, u"#e0584f",),# - Тикет отклонён - может быть архивирован
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
                (PASSWORD_REQUEST, u"Запрос на смену пароля",),
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

'''
    Приоритет
    от 0 до 4. 0 - критический, 1 - немедленно, 2-высокий, 3 - средний, 4-низкий
'''

Critical = 0
Immediately = 1
High = 2
Average = 3
Low = 4


PRIORITY_TYPES = (
                  (Critical,u'критический'),
                  (Immediately,u'немедленно'),
                  (High,u'высокий'),
                  (Average,u'средний'),
                  (Low,u'низкий'),
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

    assign_date = models.DateTimeField(blank=True, default=False) # Дата открытия(назначения) тикета
    status = models.CharField(max_length=32, choices = TICKET_STATUS)
    type = models.CharField(max_length=32, choices = TICKET_TYPE)
    additional_status = models.CharField(max_length=32, choices = TICKET_ADDITIONAL_TYPE)
    priority = models.PositiveIntegerField(choices = PRIORITY_TYPES)# от 0 до 4. 0 - критический, 1 - немедленно, 2-высокий, 3 - средний, 4-низкий
    created = models.DateTimeField(blank=True, default=False) # Дата создания тикета
    last_update = models.DateTimeField(blank=True, default=False)# - Дата последнего изменения
    archived = models.BooleanField(blank=True, default=False)
    
    def get_absolute_url(self):
        return '/ticket/edit/%s/' %self.id
    
    def get_edit_url(self):
        return '/helpdesk/ticket/edit/%s/' %self.id
    
    def get_conten_type_label(self):
        return self.content_type.model
    
    def get_user_url(self):
        return u'/helpdesk/user/%s/' %self.account.id
    
    def get_status(self):
        return dict(TICKET_STATUS)[int(self.status)]
    
    def get_status_color(self):
        return dict(COLOR_TICKETS)[int(self.status)]
    
    def get_source(self):
        return dict(SOURCE_TYPES)[int(self.source)]
    
    def get_type(self):
        return dict(TICKET_TYPE)[int(self.type)]
    
class Comment(models.Model):
    ticket = models.ForeignKey(Ticket)
    content_type = models.ForeignKey(ContentType, editable=False, null=True, blank=True)
    object_id = models.PositiveIntegerField(editable=False, null=True, blank=True)
    user = generic.GenericForeignKey('content_type', 'object_id')
    body = models.TextField()
    time = models.IntegerField(null=True, blank=True)#потраченное время. Поле видно только пользователю хелпдеска
    created = models.DateTimeField()
    file = models.FileField(upload_to = 'uploads/', null=True, blank=True)
    
    def get_user_link(self):
       model = self.content_type.model_class()
       user = model.objects.get(id = self.object_id)
       return user.get_absolute_url()
   
    def get_user(self):
       model = self.content_type.model_class()
       user = model.objects.get(id = self.object_id)
       return user.username  
    

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
    history = models.ForeignKey('TicketHistrory')
    user = models.ForeignKey(SystemUser)
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
    user = models.ForeignKey(SystemUser)
    action = models.TextField()
    created = models.DateTimeField()


class UserAttention(models.Model):
    user = models.ForeignKey(SystemUser)
    ticket = models.ForeignKey(Ticket)
    created = models.DateTimeField()


def get_ticket_status(status_nom):
    for status in TICKET_STATUS:
        if status[0] == status_nom:
            return status[1]
    return False

def get_ticket_additional_status(additional_status_nom):
    for additional_status in TICKET_ADDITIONAL_TYPE:
        if additional_status[0] == additional_status_nom:
            return additional_status[1]
    return False   

def add_history_item(instance, **kwargs):
    from lib.threadlocals import get_request
    request = get_request() # достаем request
    if request.method == 'POST': 
        data = instance.__dict__
        user = request.user
        history_item = TicketHistrory() 
        try: 
            old_ticket = Ticket.objects.get(id=data['id']) # проверка на существование тикета, если он есть, то заполняем action 
            create_history = True     
        except:
            create_history = False    
        if create_history:
            new_status = data['status']
            if int(old_ticket.status) != int(new_status[0]): # проверка основного статуса тикета
                new_status = get_ticket_status(int(new_status[0]))  
                history_item.action += u'Изменен статус с %s на %s <br>' %(get_ticket_status(int(old_ticket.status)), new_status) # добавление истории
            new_additional_status = data['additional_status']
            if int(old_ticket.additional_status) != int(new_additional_status[0]): # проверка дополнительного статуса
                new_additional_status = get_ticket_additional_status(int(new_additional_status[0])) 
                history_item.action += u'Изменен дополнительный статус с %s на %s <br>' %(get_ticket_additional_status(int(old_ticket.additional_status)), new_additional_status) # добавление истории
            if request.POST.get('reasign_option') == u'1': # если переназначен пользователь    
                if old_ticket.content_type.id != data['content_type_id'] or old_ticket.object_id != data['object_id']: # проверка на необходимость изменения пользователя
                    model_class = ContentType.objects.get(id = data['content_type_id']).model_class()
                    obj = model_class.objects.get(id=data['object_id'])
                    history_item.action += u'Переведен на %s <br>' %obj
            send_users = request.POST.getlist('send')
            if send_users: # нужно ли уведомить пользователей
                send_users = request.POST.getlist('send') # достаем список пользователей для уведомления
                history_item.action += u'Уведомлены: <br>'
                for send_user in send_users:
                    try:
                        user = SystemUser.objects.get(id = send_user)
                        history_item.action += u'%s <br>' %user
                        attention = UserAttention(
                                                   user = user,
                                                   ticket = old_ticket,
                                                   created = datetime.now(),
                                                  )
                        attention.save()
                    except:
                        pass
            if request.POST.get('hide_comment'): # Проверка на добавление заметки
                history_item.action += u'Добавлена заметка<br>'
                node_add = True
            else:
                node_add = False
            if history_item.action != '': # если были проведены изменения стикетом, то сохраняем их
                history_item.ticket = old_ticket 
                history_item.user = request.user
                history_item.created = datetime.now()
                history_item.save()
                if node_add: # добавление скрытого комментария
                    node = Note(
                                ticket = old_ticket,
                                history = history_item,
                                user = request.user,
                                body = request.POST.get('hide_comment',''),
                                date = datetime.now(),  
                                )
                    node.save()     

def is_new_ticket(instance, created, **kwargs):
    if created:
        from lib.threadlocals import get_request
        data = instance.__dict__
        request = get_request()
        body = u'Открыт<br>'
        if request.POST.get('hide_comment'):
            node_add = True
            body += u'Добавлена заметка<br>'
        else:
            node_add = False
        if data['content_type_id'] and data['object_id']: 
            model_class = ContentType.objects.get(id = data['content_type_id']).model_class()
            obj = model_class.objects.get(id=data['object_id'])
            body += u'Назначен на %s <br>' %obj         
        history_item = TicketHistrory(
                                      ticket = instance,
                                      user = request.user,
                                      action = body,
                                      created = datetime.now(),
                                      )
        history_item.save()
        if node_add:
            node = Note(
                        ticket = instance,
                        history = history_item,
                        user = request.user,
                        body = request.POST.get('hide_comment',''),
                        date = datetime.now(),  
                        )
            node.save()


models.signals.pre_save.connect(add_history_item, sender=Ticket)
models.signals.post_save.connect(is_new_ticket, sender=Ticket)
 
 
 
 
 
 
    

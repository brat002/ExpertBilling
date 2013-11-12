#-*-coding: utf-8 -*-
from sys import modules

from django.db import models

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import transaction
from django.db.utils import DatabaseError
from django.template.loader import get_template
from django.template import Context
from django.utils import simplejson

from ebsadmin.lib import instance_dict
import ipaddr
import datetime
from decimal import Decimal

def default(obj):
    '''Convert object to JSON encodable type.'''
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')
    else:
        if type(obj)==ipaddr.IPv4Network or  type(obj)==ipaddr.IPAddress:
            return str(obj)
        return simplejson.JSONEncoder().default(obj)
        
def compare(old, new):
    r = []
    for key in new:
        if new[key]!=old.get(key) and not (new[key]  in [None, ''] and old.get(key)  in [None, '']):
            r.append({'%s_old' % key: old.get(key), '%s_new' % key:new.get(key)})
    return r


class LogActionManager(models.Manager):
    _cache = {}
    _SYNCED = False
    _DELAYED = []

    def register(self, key, template, build_cache=None):
        if LogActionManager._SYNCED:
            return LogAction.objects._register(key, template, build_cache)
        else:
            self._DELAYED.append((key, template, build_cache))

    @transaction.commit_manually
    def _register(self, key, template, build_cache=None):
        """
        Registers and caches an LogAction type
        
        @param key : Key identifying log action
        @param template : template associated with key
        """
        try:
            try:
                action = self.get_from_cache(key)
                action.template = template
                action.save()
            except LogAction.DoesNotExist:
                action, new = LogAction.objects.get_or_create(name=key, \
                template=template)
                self._cache.setdefault(self.db, {})[key] = action
                action.save()
            action.build_cache = build_cache
            return action
        except:
            transaction.rollback()
        finally:
            transaction.commit()

    def _register_delayed(sender, **kwargs):
        """
        Register all permissions that were delayed waiting for database tables to
        be created.
        
        Don't call this from outside code.
        """
        try:
            for args in LogActionManager._DELAYED:
                LogAction.objects._register(*args)
            models.signals.post_syncdb.disconnect(LogActionManager._register_delayed)
            LogActionManager._SYNCED = True
        except DatabaseError:
            # still waiting for models in other apps to be created
            pass

    # connect signal for delayed registration.  Filter by this module so that
    # it is only called once
    models.signals.post_syncdb.connect(_register_delayed, \
                                       sender=modules['object_log.models'])

    def get_from_cache(self, key):
        """
        Attempts to retrieve the LogAction from cache, if it fails, loads
        the action into the cache.
        
        @param key : key passed to LogAction.objects.get
        """
        try:
            action = self._cache[self.db][key]
        except KeyError:
            action = LogAction.objects.get(name=key)
            self._cache.setdefault(self.db, {})[key]=action

            # update build_cache function if needed
            for key_, template, build_cache in LogActionManager._DELAYED:
                if key == key_:
                    action.build_cache = build_cache

        return action


class LogAction(models.Model):
    """
    Type of action of log entry (for example: addition, deletion)

    @param name           string  verb (for example: add)
    """
    
    name = models.CharField(max_length=128, unique=True, primary_key=True)
    template = models.CharField(max_length=128)
    objects = LogActionManager()
    
    def __unicode__(self):
        return u'%s' % self.name
    

class LogItemManager(models.Manager):

    def log_action(self, key, user, object1, object2=None, object3=None, data=None):
        """
        Creates new log entry

        @param user             Profile
        @param affected_object  any model
        @param key              string (LogAction.name)
        """
        # Want to use unicode?
        # Add this at import section of the file
        #from django.utils.encoding import smart_unicode
        # Uncomment below:
        #key = smart_unicode(key)
        action = LogAction.objects.get_from_cache(key)
        entry = self.model(action=action, user=user, object1=object1)
        
        if object2 is not None:
            entry.object2 = object2
        
        if object3 is not None:
            entry.object3 = object3
        
        # build cached data and or arbitrary data.
        if action.build_cache is not None:
            entry.data = action.build_cache(user, object1, object2, object3, data)
        elif data is not None:
            entry.data = data

        entry.save(force_insert=True)
        return entry


class LogItem(models.Model):
    """
    Single entry in log
    """
    action = models.ForeignKey(LogAction, verbose_name=u'Действие', related_name="entries")
    #action = models.CharField(max_length=128)
    timestamp = models.DateTimeField(verbose_name=u'Дата', auto_now_add=True, )
    user = models.ForeignKey(User, verbose_name=u'Пользователь', related_name='log_items')
    
    object_type1 = models.ForeignKey(ContentType, \
    verbose_name=u'Тип объекта', related_name='log_items1', null=True)
    object_id1 = models.PositiveIntegerField(null=True)
    object1 = GenericForeignKey("object_type1", "object_id1")
    
    #object_type2 = models.ForeignKey(ContentType, \
    #related_name='log_items2', null=True)
    #object_id2 = models.PositiveIntegerField(null=True)
    #object2 = GenericForeignKey("object_type2", "object_id2")
    
    #object_type3 = models.ForeignKey(ContentType, \
    #related_name='log_items3', null=True)
    #object_id3 = models.PositiveIntegerField(null=True)
    #object3 = GenericForeignKey("object_type3", "object_id3")

    serialized_data = models.TextField(null=True, verbose_name=u'Дамп',)
    changed_data = models.TextField(null=True, verbose_name=u'Изменённые поля',)

    objects = LogItemManager()
    _data = None

    class Meta:
        ordering = ("timestamp", )

    @property
    def data(self):
        if self._data is None and not self.serialized_data is None:
            self._data = simplejson.loads(self.serialized_data)
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.serialized_data = None

    @property
    def template(self):
        """
        retrieves template for this log item
        """
        action = LogAction.objects.get_from_cache(self.action_id)
        return get_template(action.template)

    def save(self, *args, **kwargs):
        
        
        sd = {}
        try:
            content_type = ContentType.objects.get_for_model(self.object1)
            log = LogItem.objects.filter(object_type1=content_type, object_id1=self.object1.pk).order_by('-id').select_related('user').distinct()[0]
            if log:
                sd = simplejson.loads(log.serialized_data)

        except:
            pass
            
        if self._data is not None and self.serialized_data is None:
            self.serialized_data = simplejson.dumps(self._data, ensure_ascii=False, default=default)
            self.changed_data = simplejson.dumps(compare(sd.get('object1_str',{}), self._data.get('object1_str',{})), ensure_ascii=False, default=default)
        super(LogItem, self).save(*args, **kwargs)

    def render(self, **context):
        """
        render this LogItem

        @param context: extra kwargs to add to the context when rendering
        """
        context['log_item'] = self
        action = LogAction.objects.get_from_cache(self.action_id)
        template = get_template(action.template)
        return template.render(Context(context))

    def __repr__(self):
        return 'time: %s user: %s object_type1: %s'%(self.timestamp, self.user, self.object_type1)
    
    def __unicode__(self):
        """
        Renders single line log entry to a string, 
        containing information like:
        - date and extensive time
        - user who performed an action
        - action itself
        - object affected by the action
        """
        return u"%s" % self.render()


def build_default_cache(user, obj1, obj2, obj3, data):
    """ build cache for default log types """
    return {'object1_str':instance_dict(obj1), 'data':data}


#Most common log types, registered by default for convenience
def create_defaults():
    LogAction.objects.register('EDIT', 'object_log/edit.html', build_default_cache)
    LogAction.objects.register('CREATE', 'object_log/add.html', build_default_cache)
    LogAction.objects.register('DELETE', 'object_log/delete.html', build_default_cache)
    LogAction.objects.register('RAWSQL','object_log/rawsql.html', build_default_cache)
create_defaults()

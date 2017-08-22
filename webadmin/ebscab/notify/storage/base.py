# -*- coding: utf-8 -*-

'''
Base temporary notification storage.

This is not a complete class, to be usable it should be subclassed and the
two methods ``_get`` and ``_store`` overridden.
'''

from django.utils.encoding import force_unicode, StrAndUnicode


class Notification(StrAndUnicode):

    def __init__(self, message, tags='', extras=None):
        self.message = force_unicode(message)
        self.tags = tags
        self.extras = extras or {}

    def __unicode__(self):
        return force_unicode(self.message)


class BaseStorage(object):

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self._new_data = []
        self.used = False
        self.added_new = False
        super(BaseStorage, self).__init__(*args, **kwargs)

    def __len__(self):
        return len(self._data) + len(self._new_data)

    def __iter__(self):
        self.used = True
        if self._new_data:
            self._data.extend(self._new_data)
            self._new_data = []
        return iter(self._data)

    def __contains__(self, item):
        return item in self._data or item in self._new_data

    @property
    def _data(self):
        if not hasattr(self, '_loaded_data'):
            self._loaded_data = self._get() or []
        return self._loaded_data

    def _get(self):
        raise NotImplementedError()

    def _store(self, data, response):
        raise NotImplementedError()

    def update(self, response):
        if self.used:
            self._store(self._new_data, response)
        elif self.added_new:
            self._store(self._data + self._new_data, response)

    def add(self, message, tags='', **extras):
        if not message:
            return
        self.added_new = True
        notification = Notification(message, tags, extras)
        self._new_data.append(notification)

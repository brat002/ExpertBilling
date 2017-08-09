# -*- coding: utf-8 -*-

'''
Cookie based temporary notification storage.
'''

import pickle
from hashlib import sha1

from django.conf import settings

from notify.storage.base import BaseStorage


class CookieStorage(BaseStorage):
    cookie_name = 'notifications'

    def _get(self):
        data = self.request.COOKIES.get(self.cookie_name)
        return self._decode(data)

    def _store(self, data, response):
        if data:
            response.set_cookie(self.cookie_name, self._encode(data))
        else:
            response.delete_cookie(self.cookie_name)

    def _hash(self, value):
        return sha1(value + settings.SECRET_KEY).hexdigest()

    def _encode(self, data):
        value = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        return '%s$%s' % (self._hash(value), value)

    def _decode(self, data):
        if not data:
            return None
        bits = data.split('$', 1)
        if len(bits) == 2:
            hash, value = bits
            if hash == self._hash(value):
                try:
                    # If we get here (and the pickle works), everything is
                    # good. In any other case, drop back and return None.
                    return pickle.loads(value)
                except:
                    pass
        # Mark the data as used (so it gets removed) since something was wrong
        # with the data.
        self.used = True
        return None

'''
Session based temporary notification storage.
'''

from notify.storage.base import BaseStorage


class SessionStorage(BaseStorage):
    session_key = '_notifications'

    def __init__(self, request, *args, **kwargs):
        assert hasattr(request, 'session'), "The session-based temporary "\
            "notification storage requires session middleware to be installed."
        super(SessionStorage, self).__init__(request, *args, **kwargs)

    def _get(self):
        return self.request.session.get(self.session_key, [])

    def _store(self, data, response):
        if data:
            self.request.session[self.session_key] = data
        else:
            self.request.session.pop(self.session_key, None)

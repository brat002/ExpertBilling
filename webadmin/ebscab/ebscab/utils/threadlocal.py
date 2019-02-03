# -*- coding: utf-8 -*-

from threading import local


_thread_local = local()


def get_request():
    return getattr(_thread_local, 'request', None)


class ThreadLocalsMiddleware(object):
    """Middleware that saves request in thread local starage"""

    def process_request(self, request):
        _thread_local.request = request

'''
Middleware which handles temporary notifications.
'''

from notify.storage import Storage


class NotificationsMiddleware(object):
    def process_request(self, request):
        request.notifications = Storage(request)

    def process_response(self, request, response):
        # A higher middleware layer may return a request which does not contain
        # notifications storage, so make no assumption that it will be there.
        if hasattr(request, 'notifications'):
            request.notifications.update(response)
        return response

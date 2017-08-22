# -*- coding: utf-8 -*-

import unittest

from django import http

from notify.middleware import NotificationsMiddleware


class MiddlewareTest(unittest.TestCase):

    def setUp(self):
        self.middleware = NotificationsMiddleware()

    def test_response_without_notifications(self):
        """
        A higher middleware layer may return a request directly before
        notifications get applied, so the response middleware is tolerant of
        notifications not existing on request.
        """
        request = http.HttpRequest()
        response = http.HttpResponse()
        self.middleware.process_response(request, response)

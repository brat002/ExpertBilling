# -*- coding: utf-8 -*-

from notify.storage.cookie import CookieStorage
from notify.tests.base import BaseTest


class CookieTest(BaseTest):
    storage_class = CookieStorage

    def check_store(self, storage, response):
        # Get a list of cookies, excluding ones with a max-age of 0 (because
        # they have been marked for deletion).
        cookie = response.cookies.get(storage.cookie_name)
        if not cookie:
            return 0
        data = storage._decode(cookie.value)
        if not data:
            return 0
        return len(data)

    def test_get(self):
        pass

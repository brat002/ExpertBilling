from notify.tests.base import BaseTest
from notify.storage.session import SessionStorage


class SessionTest(BaseTest):
    storage_class = SessionStorage

    def get_request(self):
        self.session = {}
        request = super(SessionTest, self).get_request()
        request.session = self.session
        return request

    def check_store(self, storage, response):
        data = self.session.get(storage.session_key, [])
        return len(data)

    def test_get(self):
        pass

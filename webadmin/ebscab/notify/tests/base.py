# -*- coding: utf-8 -*-

import unittest

from django import http

from notify.storage import get_storage, Storage
from notify.storage.base import Notification


class BaseTest(unittest.TestCase):
    storage_class = Storage

    def get_request(self):
        return http.HttpRequest()

    def get_response(self):
        return http.HttpResponse()

    def get_storage(self, data=None):
        storage = self.storage_class(self.get_request())
        storage._loaded_data = data or []
        return storage

    def test_add(self):
        storage = self.get_storage()
        self.assertFalse(storage.added_new)
        storage.add('Test message 1')
        self.assert_(storage.added_new)
        storage.add('Test message 2', 'tag')
        self.assertEqual(len(storage), 2)

    def test_no_update(self):
        storage = self.get_storage()
        response = self.get_response()
        storage.update(response)
        storing = self.check_store(storage, response)
        self.assertEqual(storing, 0)

    def test_add_update(self):
        storage = self.get_storage()
        response = self.get_response()

        storage.add('Test message 1')
        storage.add('Test message 1', 'tag')
        storage.update(response)

        storing = self.check_store(storage, response)
        self.assertEqual(storing, 2)

    def test_existing_add_read_update(self):
        storage = self.get_existing_storage()
        response = self.get_response()

        storage.add('Test message 3')
        data = list(storage)   # Simulates a read
        storage.update(response)

        storing = self.check_store(storage, response)
        self.assertEqual(storing, 0)

    def test_existing_read_add_update(self):
        storage = self.get_existing_storage()
        response = self.get_response()

        data = list(storage)   # Simulates a read
        storage.add('Test message 3')
        storage.update(response)

        storing = self.check_store(storage, response)
        self.assertEqual(storing, 1)

    def check_store(self, storage, response):
        """
        Returns the number of messages being stored after a
        ``storage.update()`` call
        """
        raise NotImplementedError('This method must be set by a subclass.')

    def test_get(self):
        raise NotImplementedError('This method must be set by a subclass.')

    def get_existing_storage(self):
        storage = self.get_storage([Notification('Test message 1'),
                                    Notification('Test message 2', 'tag')])
        return storage

    def test_existing_read(self):
        """
        Test that reading the existing
        """
        storage = self.get_existing_storage()
        self.assertFalse(storage.used)
        # After iterating the storage engine directly, the used flag is set.
        data = list(storage)
        self.assert_(storage.used)
        # The data does not disappear because it has been iterated.
        self.assertEqual(data, list(storage))

    def test_existing_add(self):
        storage = self.get_existing_storage()
        self.assertFalse(storage.added_new)
        storage.add('Test message 3')
        self.assert_(storage.added_new)

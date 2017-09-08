# -*- coding: utf-8 -*-

from django.db import models


class SoftDeleteManager(models.Manager):
    """Use this manager to get objects that have a deleted field"""

    def get_queryset(self):
        return (super(SoftDeleteManager, self)
                .get_queryset()
                .filter(deleted=False))

    def all_with_deleted(self):
        return super(SoftDeleteManager, self).get_queryset()

    def deleted_set(self):
        return (super(SoftDeleteManager, self)
                .get_queryset()
                .filter(deleted=True))


class SoftDeletedDateManager(models.Manager):
    ''' Use this manager to get objects that have a deleted field '''

    def get_queryset(self):
        return (super(SoftDeletedDateManager, self)
                .get_queryset()
                .filter(deleted__isnull=True))

    def all_with_deleted(self):
        return super(SoftDeletedDateManager, self).get_queryset()

    def deleted_set(self):
        return (super(SoftDeletedDateManager, self)
                .get_queryset()
                .filter(deleted__isnull=False))

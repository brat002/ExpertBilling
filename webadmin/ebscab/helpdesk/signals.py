# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models

from helpdesk.models import UserSettings


def create_usersettings(sender, created_models=[], instance=None,
                        created=False, **kwargs):
    """
    Helper function to create UserSettings instances as
    required, eg when we first create the UserSettings database
    table via 'migrate' or when we save a new user.

    If we end up with users with no UserSettings, then we get horrible
    'DoesNotExist: UserSettings matching query does not exist.' errors.
    """
    if sender == User and created:
        # This is a new user, so lets create their settings entry.
        s, created = UserSettings.objects.get_or_create(user=instance)
        s.save()
    elif UserSettings in created_models:
        # We just created the UserSettings model, lets create a UserSettings
        # entry for each existing user. This will only happen once (at install
        # time, or at upgrade) when the UserSettings model doesn't already
        # exist.
        for u in User.objects.all():
            try:
                s = UserSettings.objects.get(user=u)
            except UserSettings.DoesNotExist:
                s = UserSettings(user=u)
                s.save()

models.signals.post_migrate.connect(create_usersettings)
models.signals.post_save.connect(create_usersettings, sender=User)

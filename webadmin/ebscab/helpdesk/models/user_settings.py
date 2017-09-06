# -*- coding: utf-8 -*-

import cPickle

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from helpdesk.utils import b64decode, b64encode


class UserSettings(models.Model):
    """
    A bunch of user-specific settings that we want to be able to define, such
    as notification preferences and other things that should probably be
    configurable.

    We should always refer to user.usersettings.settings['setting_name'].
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    settings_pickled = models.TextField(
        _('Settings Dictionary'),
        help_text=_('This is a base64-encoded representation of a pickled '
                    'Python dictionary. Do not change this field via '
                    'the admin.'),
        blank=True,
        null=True
    )

    def _set_settings(self, data):
        # data should always be a Python dictionary.
        self.settings_pickled = b64encode(cPickle.dumps(data))

    def _get_settings(self):
        # return a python dictionary representing the pickled data.
        try:
            return cPickle.loads(b64decode(str(self.settings_pickled)))
        except cPickle.UnpicklingError:
            return {}

    settings = property(_get_settings, _set_settings)

    def __unicode__(self):
        return u'Preferences for %s' % self.user

    class Meta:
        verbose_name = _(u'User Settings')
        verbose_name_plural = _(u'User Settings')

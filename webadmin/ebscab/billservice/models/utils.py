# -*- coding: utf-8 -*-

import re
from functools import partial

from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_phone(value):
    if value and not re.match(r'''\+\d{1,25}$''', value):
        raise ValidationError(_(u'Некорректный формат номера. Используйте '
                                u'международный формат +71923453333'))


get_model = partial(apps.get_model, 'billservice')

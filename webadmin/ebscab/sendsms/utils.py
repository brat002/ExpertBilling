# -*- coding: utf-8 -*-

from importlib import import_module

from django.conf import settings


def load_object(import_path):
    """
    Shamelessly stolen from https://github.com/ojii/django-load

    Loads an object from an 'import_path', like in MIDDLEWARE_CLASSES and the
    likes.

    Import paths should be: "mypackage.mymodule.MyObject". It then imports the
    module up until the last dot and tries to get the attribute after that dot
    from the imported module.

    If the import path does not contain any dots, a TypeError is raised.

    If the module cannot be imported, an ImportError is raised.

    If the attribute does not exist in the module, a AttributeError is raised.
    """
    if '.' not in import_path:
        raise TypeError(
            "'import_path' argument to 'load_object' must "
            "contain at least one dot."
        )
    module_name, object_name = import_path.rsplit('.', 1)
    module = import_module(module_name)
    return getattr(module, object_name)


def get_backend_choices(currency=None):
    """
    Get active backends modules. Backend list can be filtered by supporting given currency.
    """
    backends_names = getattr(settings, 'SENDSMS_BACKENDS', [])
    return backends_names


def get_backend_settings(backend):
    """
    Returns backend settings. If it does not exist it fails back to empty dict().
    """
    backends_settings = getattr(settings, 'SENDSMS_BACKENDS_SETTINGS', {})
    try:
        return backends_settings[backend]
    except KeyError:
        return {}

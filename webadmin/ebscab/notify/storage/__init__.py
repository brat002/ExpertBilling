from django.conf import settings
from notify.storage.base import BaseStorage


def get_storage(import_name):
    bits = import_name.split('.')
    if len(bits) < 2:
        raise TypeError('No class name specified.')
    module_name = '.'.join(bits[:-1])
    class_name = bits[-1]
    try:
        module = __import__('notify.storage.%s' % module_name,
                            globals(), locals(), [class_name])
        storage_class = getattr(module, class_name)
    except (AttributeError, ImportError):
        module = __import__(module_name, globals(), locals(), [class_name])
        storage_class = getattr(module, class_name)
    if not issubclass(storage_class, BaseStorage):
        raise TypeError('Not a notification storage class.')
    return storage_class


Storage = get_storage(getattr(settings, 'NOTIFICATIONS_STORAGE',
                              'session.SessionStorage'))

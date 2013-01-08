from django.contrib.auth import models as auth_models
import django.db.models.signals
from django.db import connection

# Related ticket http://code.djangoproject.com/ticket/4748
def alter_django_auth_permissions(sender, **kwargs):
    if not auth_models.Permission in kwargs['created_models']:
        return
    SIZE_NAME=128
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM auth_permission LIMIT 1")
    
    print 123
    for desc in cursor.description:
        # See http://www.python.org/dev/peps/pep-0249/
        name, type_code, display_size, internal_size, precision, scale, null_ok = desc
        if not name=='name':
            continue
        if internal_size<SIZE_NAME:
            logging.info('auth_permission: Column "name" gets altered. Old: %d new: %d' % (
                    internal_size, SIZE_NAME))
            cursor.execute('''ALTER TABLE auth_permission ALTER COLUMN "name" type VARCHAR(%s)''',
                           [SIZE_NAME])
        break
    else:
        raise Exception('table auth_permission has not column "name"')
django.db.models.signals.post_syncdb.connect(alter_django_auth_permissions)

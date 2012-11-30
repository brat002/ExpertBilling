import sys

sys.path.append('.')

#===============================================================================
# BROKER_HOST = "localhost"
# BROKER_PORT = 5672
# BROKER_USER = "celeryuser"
# BROKER_PASSWORD = "celery"
# BROKER_VHOST = "celeryvhost"
#===============================================================================

BROKER_URL = 'amqp://celeryuser:celery@localhost:5672/celeryvhost'

CELERY_RESULT_BACKEND = "amqp"

CELERY_IMPORTS = ("tasks",)
CELERY_RESULT_PERSISTENT = True

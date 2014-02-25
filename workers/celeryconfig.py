import sys
import os

sys.path.append('.')
import ConfigParser
config = ConfigParser.ConfigParser()
BILLING_PATH = '/opt/ebs/data/'
config.read(os.path.join(BILLING_PATH, "ebs_config.ini"))

BROKER_URL = config.get("db", "kombu_dsn")

#CELERY_RESULT_BACKEND = "database"
CELERY_RESULT_BACKEND = "db+postgresql://%s:%s@%s/%s" % (config.get("db", "username"),config.get("db", "password"),config.get("db", "host"),config.get("db", "name"),)

CELERY_IMPORTS = ("tasks", )
CELERY_RESULT_PERSISTENT = True
CELERY_ACCEPT_CONTENT = ['pickle', ]
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'


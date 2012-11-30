import sys
import os

sys.path.append('.')
import ConfigParser
config = ConfigParser.ConfigParser()
BILLING_PATH = '/opt/ebs/data/'
config.read(os.path.join(BILLING_PATH, "ebs_config.ini"))

BROKER_URL = config.get("db", "kombu_dsn")

CELERY_RESULT_BACKEND = "amqp"

CELERY_IMPORTS = ("tasks",)
CELERY_RESULT_PERSISTENT = True

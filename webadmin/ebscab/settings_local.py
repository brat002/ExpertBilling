import os, sys

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'ebs_1.2'             # Or path to database file if using sqlite3.
DATABASE_USER = 'mikrobill'             # Not used with sqlite3.
DATABASE_PASSWORD = '1234'         # Not used with sqlite3.
DATABASE_HOST = '10.10.1.1'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '5432'  

WEBCAB_LOG = os.path.abspath('./log/webcab_log')

MEDIA_ROOT = os.path.abspath('./media')

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.abspath('./templates'),
)
from distutils.core import setup
import py2exe

setup(windows=['mdi.py'], options={"py2exe" : {"includes" : ["sip", "PyQt4._qt", "psycopg2.tz"]}})


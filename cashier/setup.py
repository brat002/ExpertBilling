from distutils.core import setup
import py2exe
import glob

setup(windows=[{"script":'cassa.py',}], options={"py2exe" : {"includes" : ["sip","db","PyQt4.QtNetwork", "psycopg2.tz"]}})


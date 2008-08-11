#-*-encoding:utf-8-*-

from distutils.core import setup
import py2exe

setup(console=['server.py'], options={"py2exe":{"includes":["controllers"]}})

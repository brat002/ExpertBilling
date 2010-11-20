#-*-encoding:utf-8-*-

from distutils.core import setup
import py2exe
import glob

setup(console=['core.py'], \
     data_files = [(r'fonts', glob.glob(r'D:\projects\mikrobill\chartprovider\fonts\*.*')),\
                   (r'dicts', glob.glob(r'D:\projects\mikrobill\dicts\*'))])

from distutils.core import setup
import py2exe
import glob, sys, os
sys.path.append(os.path.abspath('../'))

setup(windows=[{"script":'cassa.py',"icon_resources": [(1, "cassa_icon.ico")]}], options={"py2exe" : {"dist_dir": "cassa", "includes" : ["pkg_resources", "Crypto", "rpc2", "sip","mako.cache","db","PyQt4.QtNetwork", "PyQt4.QtSql","psycopg2.tz",  "zope", 'pygments.*', 'pygments.lexers.*', 'pygments.formatters.*','pygments.filters.*', 'pygments.styles.*'], "packages": ["sqlite3",]}},
data_files = [(r'images', glob.glob(r'D:\projects\mikrobill\mdi\images\user*.*')),\
                    (r'templates', glob.glob(r'D:\projects\mikrobill\mdi\templates\*.*')),\
                    (r'templates\tmp', glob.glob(r'D:\projects\mikrobill\mdi\templates\tmp\*.*')),\
                    (r'.', glob.glob(r'D:\projects\mikrobill\mdi\cassa_style.qss')),\
                   ])




from distutils.core import setup
import py2exe
import glob

setup(windows=[{"script":'cassa.py',"icon_resources": [(1, "cassa_icon.ico")]}], options={"py2exe" : {"dist_dir": "cassa", "includes" : ["sip","mako.cache","db","PyQt4.QtNetwork", "PyQt4.QtSql","psycopg2.tz"], "packages": ["sqlite3",]}},
data_files = [(r'images', glob.glob(r'D:\projects\mikrobill\mdi\images\user*.*')),\
                    (r'templates', glob.glob(r'D:\projects\mikrobill\mdi\templates\*.*')),\
                    (r'templates\tmp', glob.glob(r'D:\projects\mikrobill\mdi\templates\tmp\*.*')),\
                    (r'.', glob.glob(r'D:\projects\mikrobill\mdi\cassa_style.qss')),\
                   ])




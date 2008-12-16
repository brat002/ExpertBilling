from distutils.core import setup
import py2exe
import glob

setup(windows=[{"script":'mdi.py',"icon_resources": [(0, "icon.ico")]}], options={"py2exe" : {"includes" : ["sip","mako.cache","db","PyQt4.QtNetwork", "PyQt4.QtSql","psycopg2.tz"], "packages": ["sqlite3",]}}, \
      data_files = [(r'images', glob.glob(r'D:\projects\mikrobill\mdi\images\*.*')),\
                    (r'templates', glob.glob(r'D:\projects\mikrobill\mdi\templates\*.*')),\
                    (r'templates\cards', glob.glob(r'D:\projects\mikrobill\mdi\templates\cards\*.*')),\
                    (r'.\reports\xml', glob.glob(r'D:\projects\mikrobill\mdi\reports\xml\*.*')), \
                    (r'.\reports\fonts', glob.glob(r'D:\projects\mikrobill\mdi\reports\fonts\*.*')), \
                    (r'.', glob.glob(r'D:\projects\mikrobill\mdi\style.qss')),\
                    (r'.', glob.glob(r'D:\projects\mikrobill\mdi\mdi.qrc')),\
                   ])


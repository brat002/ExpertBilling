from distutils.core import setup
import py2exe
import glob, sys, os
sys.path.append(os.path.abspath('../'))

setup(windows=[{"script":'ebsadmin.py',"icon_resources": [(1, "icon.ico")]}], options={"py2exe" : {"dist_dir": "EBSAdmin", "includes" : ["Crypto", "rpc2", "sip","mako.cache","db","PyQt4.QtNetwork", "PyQt4.QtSql", "psycopg2.tz", "twisted.web.resource",], "packages": ["win32com", "sqlite3",]}}, \
      data_files = [(r'images', glob.glob(r'D:\projects\mikrobill\mdi\images\*.*')),\
                    (r'templates', glob.glob(r'D:\projects\mikrobill\mdi\templates\*.*')),\
                    (r'templates\cards', glob.glob(r'D:\projects\mikrobill\mdi\templates\cards\*.*')),\
                    (r'.\reports\xml', glob.glob(r'D:\projects\mikrobill\mdi\reports\xml\*.*')), \
                    (r'.\reports\fonts', glob.glob(r'D:\projects\mikrobill\mdi\reports\fonts\*.*')), \
                    (r'.', glob.glob(r'D:\projects\mikrobill\mdi\style.qss')),\
                    (r'.', glob.glob(r'D:\projects\mikrobill\mdi\mdi.qrc')),\
                   ])

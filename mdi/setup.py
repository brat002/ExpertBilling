from distutils.core import setup
import py2exe
import glob

setup(windows=['mdi.py'], options={"py2exe" : {"includes" : ["sip", "PyQt4._qt","db", "psycopg2.tz"]}}, \
      data_files = [(r'images', glob.glob(r'D:\projects\mikrobill\mdi\images\*.*')),\
                    (r'.\reports\xml', glob.glob(r'D:\projects\mikrobill\mdi\reports\xml\*.*')), \
                    (r'.\reports\fonts', glob.glob(r'D:\projects\mikrobill\mdi\reports\fonts\*.*')), \
                    (r'.', glob.glob(r'D:\projects\mikrobill\mdi\style.qss')),\
                    (r'.', glob.glob(r'D:\projects\mikrobill\mdi\mdi.qrc')),\
                   ])


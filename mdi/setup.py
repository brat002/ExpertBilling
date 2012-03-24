from distutils.core import setup
import py2exe
import glob, sys, os
import datetime
import time
dt = datetime.datetime.now().strftime("%d/%m/%y %H:%M")
sys.path.append(os.path.abspath('../'))
f=open('version','w')
f.write(dt)
f.close()
dllList =('mfc90.dll','msvcp90.dll','qtnetwork.pyd','qtxmlpatterns4.dll','qtsvg4.dll','libpq.dll')
origIsSystemDLL = py2exe.build_exe.isSystemDLL
def isSystemDLL(pathname):
    if os.path.basename(pathname).lower() in dllList:
        return 0
    return origIsSystemDLL(pathname)
py2exe.build_exe.isSystemDLL = isSystemDLL 
excludes = ["Secur32.dll", "SHFOLDER.dll","MSVCP90.dll"]
setup(windows=[{"script":'ebsadmin.py',"icon_resources": [(1, "icon.ico")]}], options={"py2exe" : {"dist_dir": "EBSAdmin", "includes" : ["pkg_resources",  "Crypto", "sip","mako.cache","db","PyQt4.QtNetwork", "PyQt4.QtSql", "PyQt4.QtWebKit", "psycopg2.tz", "twisted.web.resource", 'pygments.*', 'pygments.lexers.*', 'pygments.formatters.*','pygments.filters.*', 'pygments.styles.*',], "packages": [ "sqlite3", "json",], "dll_excludes": excludes}}, \
      data_files = [(r'images', glob.glob(r'D:\projects\mikrobill\mdi\images\*.*')),\
                    (r'templates', glob.glob(r'D:\projects\mikrobill\mdi\templates\*.*')),\
                    (r'templates\cards', glob.glob(r'D:\projects\mikrobill\mdi\templates\cards\*.*')),\
                    (r'templates\tmp', glob.glob(r'D:\projects\mikrobill\mdi\templates\tmp\*.*')),\
                    (r'.\reports\xml', glob.glob(r'D:\projects\mikrobill\mdi\reports\xml\*.*')), \
                    (r'.\reports\fonts', glob.glob(r'D:\projects\mikrobill\mdi\reports\fonts\*.*')), \
                    (r'.\reports\images', glob.glob(r'D:\projects\mikrobill\mdi\reports\images\*.*')), \
                    (r'.\images\reports', glob.glob(r'D:\projects\mikrobill\mdi\images\reports\*.*')), \
                    (r'.\reports\genhtml', glob.glob(r'D:\projects\mikrobill\mdi\reports\genhtml\*.*')), \
                    (r'.\reports\genhtml\charts', glob.glob(r'D:\projects\mikrobill\mdi\reports\charts\*.*')), \
                    (r'.\reports\genhtml\imgcache', glob.glob(r'D:\projects\mikrobill\mdi\reports\charts\imgcache\*.*')), \
                    (r'.', glob.glob(r'D:\projects\mikrobill\mdi\version')), \
                    (r'.\skins', glob.glob(r'D:\projects\mikrobill\mdi\skins\*')),\
                    (r'.', glob.glob(r'D:\projects\mikrobill\mdi\mdi.qrc')),\
                    (r'.', glob.glob(r'D:\projects\mikrobill\mdi\ebsadmin.ini')),\
                   ])

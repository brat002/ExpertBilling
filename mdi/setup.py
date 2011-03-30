from distutils.core import setup
import py2exe
import glob, sys, os
sys.path.append(os.path.abspath('../'))

dllList =('mfc90.dll','msvcp90.dll','qtnetwork.pyd','qtxmlpatterns4.dll','qtsvg4.dll','libpq.dll')
origIsSystemDLL = py2exe.build_exe.isSystemDLL
def isSystemDLL(pathname):
    if os.path.basename(pathname).lower() in dllList:
        return 0
    return origIsSystemDLL(pathname)
py2exe.build_exe.isSystemDLL = isSystemDLL 
excludes = ["Secur32.dll", "SHFOLDER.dll","MSVCP90.dll"]
setup(windows=[{"script":'ebsadmin.py',"icon_resources": [(1, "icon.ico")]}], options={"py2exe" : {"dist_dir": "EBSAdmin", "includes" : ["pkg_resources", "Crypto", "rpc2", "sip","mako.cache","db","PyQt4.QtNetwork", "PyQt4.QtSql", "PyQt4.QtWebKit", "psycopg2.tz", "twisted.web.resource", 'pygments.*', 'pygments.lexers.*', 'pygments.formatters.*','pygments.filters.*', 'pygments.styles.*',], "packages": [ "sqlite3",], "dll_excludes": excludes}}, \
      data_files = [(r'images', glob.glob(r'D:\projects\mikrobill\mdi\images\*.*')),\
                    (r'templates', glob.glob(r'D:\projects\mikrobill\mdi\templates\*.*')),\
                    (r'templates\cards', glob.glob(r'D:\projects\mikrobill\mdi\templates\cards\*.*')),\
                    (r'.\reports\xml', glob.glob(r'D:\projects\mikrobill\mdi\reports\xml\*.*')), \
                    (r'.\reports\fonts', glob.glob(r'D:\projects\mikrobill\mdi\reports\fonts\*.*')), \
                    (r'.', glob.glob(r'D:\projects\mikrobill\mdi\style.qss')),\
                    (r'.', glob.glob(r'D:\projects\mikrobill\mdi\mdi.qrc')),\
                   ])

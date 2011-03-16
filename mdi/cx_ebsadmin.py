# -*- coding: utf-8 -*-
import cx_Freeze
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"
    
includes = [ "PyQt4.QtXml",
             "PyQt4.QtNetwork",
             "mx.DateTime",
             "pygments",
             "pygments.lexers",
             "pygments.styles",
             "pygments.lexers.templates",
             "pygments.lexers.parsers",
             "pygments.lexers.asm",
             "pygments.lexers.math",
             "pygments.lexers.special",
             "pygments.styles.default",
]
"""
PyQt4,PyQt4.QtNetwork,mx.DateTime,pygments,pygments.lexers,pygments.styles,pygments.lexers.templates,
pygments.lexers.parsers,pygments.lexers.asm,pygments.lexers.math,pygments.lexers.special,
pygments.styles.default

"""
packages = [ "pygments" , 
             "pygments.lexers", 
             "pygments.styles", 
]
excludes = []

executables = [
        cx_Freeze.Executable("ebsadmin.py", 
                             base = base,
                             
                             )
]

includeFiles = [
    ("images", "images"),
    ("templates", "templates"),
    ("style.qss", "style.qss"),    
    ("reports", "reports"),    
]

options = dict(
    include_files = includeFiles,
    includes = includes, 
    excludes = excludes,
    packages = packages)
    
cx_Freeze.setup(
        name = "ebsadmin",
        version = "1.4",
        description = "ExpertBilling administrator console",
        executables = executables,
        options = dict(build_exe = options)
)


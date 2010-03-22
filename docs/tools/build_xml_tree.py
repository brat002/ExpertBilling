# -*- coding=utf-8 -*-
# @author Dmitry Kosov
# $Id$
"""
Build xml tree from directory file structure
"""
import os
import sys
from xml.dom.minidom import Document

doc = Document()

DEPRECATED_NAMES = ('TODO','BUILD','wcab','webadmin','webcab','temp','tests','docs','docs_old','log','fonts','debian')
D_EXTENSIONS = ('.png','.gif','.jpg','.bmp','.ico','.gz','.zip','.tz','.rar')
MODULE_EXT = ('.py',)

def makenode(path):
    '''Creates a document node contains a source directory tree start from the path.'''
    node = doc.createElement('directory')
    node.setAttribute('name', os.path.basename(path))
    node.setAttribute('path', path)
    for f in os.listdir(path):
        elem = None
        if not f in DEPRECATED_NAMES and not f.startswith('.'):
            path_f = os.path.join(path, f)
            if os.path.isdir(path_f):
                elem = makenode(path_f)
            else:
                _name, ext = os.path.splitext(f)
                if not ext in D_EXTENSIONS:
                    elem = doc.createElement('file')
                    if ext in MODULE_EXT:
                        name = _name
                    else:
                        name = '%s%s' % (_name, ext)
                    elem.setAttribute('name', name)
                    elem.setAttribute('ext',ext)
                    elem.setAttribute('path', path)
            if elem:
                node.appendChild(elem)
    return node

if __name__ == '__main__':
    os.chdir('..')
    doc.appendChild(makenode('.'))

print doc.toprettyxml()


# -*- coding=utf-8 -*-
# @author Dmitry Kosov
# $Id$
"""
Parse xml tree and creates Sphinx doc tree in selected diectory
"""
import os
import sys
from optparse import OptionParser
from lxml import etree

# load current Sphinx configuration
from conf import master_doc, source_suffix

DOCROOT_TITLE = 'Developer documentation'

def usage():
    print "Usage: python xml2doc -s source.xml -d path/to/destination/directory"

def render(out):
    return "\n".join(out)

def index_c(name, sub_list):

    header_tmpl = ":mod:`%s` -- Untitled"
    if name == '.': # I'm too stupid to solve this another way'
        is_docroot = True
        name = DOCROOT_TITLE
        header_tmpl = '%s'
    else:
        is_docroot = False
    """Form content and toc for an index file"""

    out = []
    out.append(header_tmpl % name)
    out.append('='*len(out[0]))
    out.append("")
    out.append(".. toctree::")
    out.append("   :maxdepth: %d" % is_docroot and 2 or 1)
    out.append("")
    out.append(sub_list)
    return render(out)

def module_c(name):
    """Form content and toc for a module file"""
    out = []
    out.append(":mod:`%s` -- Untitled" % name)
    out.append('='*len(out[0]))
    out.append("")
    out.append(".. module:: %s" % name)
    out.append("   :platform: Unix, Windows")
    out.append("   :synopsis: None")
    out.append("")
    out.append(".. currentmodule:: %s" % name)
    return render(out)

class DocEntry(object):

    def __init__(self, xml_element):
        self.elem = xml_element
        self.name = xml_element.get('name')

    def __str__(self):
        return self.name

    def save(self):
        raise NonImplementedError

    def isdir(self):
        return False

    def get_toc(self):
        return None

def sname(name):
    return '%s%s'%(name,source_suffix)


class Directory(DocEntry):
    """Directory wrapper"""
    def get_children_nodes(self):
        return self.elem.getchildren()

    def children_list(self):
        return [x.get('name') for x in self.get_children_nodes()]

    def get_toc(self):
        return '%s/%s' % (self.name, master_doc)

    def save(self):
        if not os.path.exists(self.get_path()):
            # create directory
            os.mkdir(self.get_path())
            # create index file
        # create index file
        index_file_path = os.path.join(self.get_path(),sname(master_doc))
        if not os.path.exists(index_file_path):
            index_file = open(index_file_path,'a+')
            index_file.write(index_c(name=self.name,\
                                     sub_list="\n".join(['   %s' % entry_fabric(x).get_toc()\
                                                        for x in self.get_children_nodes()])))
            index_file.close()

    def isdir(self):
        return True

    def get_path(self):
        return os.path.abspath(self.elem.get('path'))

class Module(DocEntry):
    """File wrapper"""
    def get_toc(self):
        return self.name

    def save(self):
        if not os.path.exists(self.get_path()):
            module_file = open(self.get_path(),'a+')
            module_file.write(module_c(name=self.name))
            module_file.close()

    def get_path(self):
        return os.path.join(os.path.abspath(self.elem.get('path')), sname(self.name))

    def isdir(self):
        return False

def entry_fabric(xml_element):
    return xml_element.tag == 'directory'\
                           and Directory(xml_element)\
                            or Module(xml_element)

def parse(xml_element):
    entry = entry_fabric(xml_element)
    entry.save()
    if entry.isdir():
        for child in entry.get_children_nodes():
            parse(child)

def test_parse(xml_element):
    entry = entry_fabric(xml_element)
    print entry.get_path()
    if entry.isdir():
        for child in entry.get_children_nodes():
            test_parse(child)

parser = OptionParser()
parser.add_option("-s", "--source", dest="source_file",
                  help="source XML file")
parser.add_option("-d", "--destination", dest="docroot",
                  help="directory where the document structure will be created")


if __name__ == '__main__':
    # start processing
    source_file = None
    docroot = None
    (options, args) = parser.parse_args()
    if not options.source_file or not options.docroot:
        parser.print_help()
        sys.exit(2)
    source_file = options.source_file
    docroot = options.docroot
    print 'Source: ', source_file
    print 'Destination: ', docroot
    print 'Start processing...'
    tree_root = etree.parse(source_file).getroot()
    os.chdir(docroot)
    parse(tree_root)
    print 'Done. Documentation tree was built in %s' % docroot


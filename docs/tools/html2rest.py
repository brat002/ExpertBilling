# -*- coding=utf-8 -*-
import os
import shutil
import codecs
import re
import itertools

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import Comment, Tag, NavigableString
from pytils.translit import slugify, translify

from tgdocs.html2rst import html2text

j = os.path.join
se = os.path.splitext
ap = os.path.abspath

class Element(object):
    def __init__(self, id, heading, href):
        self.id = id
        self.tlevel = id[1:].split('.')
        self.heading = heading
        self.file = href
        self.name, self.ext = [translify(unicode(x)).lower() for x in se(href)]
        self.parent = None
        self.type = self.set_init_type()

    def set_init_type(self):
        if len(self.tlevel) == 1:
            return 'directory'
        elif len(self.tlevel) == 2:
            return 'page'
        else:
            return 'content'

    def __unicode__(self):
        return u'%s: %s' % ('.'.join(self.tlevel), self.heading)

    def __repr__(self):
        return self.__unicode__().encode('utf8')

    def get_parent(self, toc_tree, elem_type=None):
        for e in toc_tree:
            if self.tlevel[:-1] == e.tlevel:
                if elem_type:
                    if e.type == elem_type:
                        return e
                    else:
                        continue
                return e
        return None

    def get_branch(self,toc_tree):
        return [e for e in toc_tree if self.tlevel == e.tlevel[0:len(self.tlevel)]]

    def get_children(self, toc_tree):
        return [e for e in toc_tree if self.tlevel == e.tlevel[0:len(self.tlevel)] and self != e]


    def toc_repr(self):
        if self.type == 'directory':
            return (u'%s <%s/index>' % (self.heading, self.name))
        elif self.type == 'page':
            return (u'%s <%s>' % (self.heading, self.name))
        return None

    def filename(self):
        return '%s%s' % (self.name, self.ext)

    def get_content(self,directory):
        f = codecs.open(j(directory,self.filename()),'r','utf8')
        c = f.read()
        f.close()
        return c

def get_attr(attrs, name):
    return [x[1] for x in attrs if x[0] == name][0]

def parse(directory):
    f_index = codecs.open(j(directory,'index.html'),'r','utf8')
    bs = BeautifulSoup(f_index.read())
    f_index.close()
    toc = []
    for tag in bs.findAll(attrs={'class':'toc'}):
        href = get_attr(tag.findChild('a').attrs, 'href')
        id = get_attr(tag.findChild('span').attrs, 'id')
        heading = tag.findChild('span').contents[0]
        toc.append(Element(id=id, heading=heading, href=href))
    return toc

index_t = """
.. _%(path)s:

%(heading)s
%(heading_dec)s

.. toctree::
   :maxdepth: 2

%(toctree)s
"""

page_t = """
.. _%(path)s:

%(heading_dec)s
%(heading)s
%(heading_dec)s


%(text)s


%(chapters)s
"""

chapter_t = """
%(heading)s
%(heading_dec)s


%(text)s
"""

def get_path(elem, toc_tree, path=None):
    path = path or []
    if not elem:
        return '-'.join([x.name for x in path[::-1]])
    else:
        path.append(elem)
        return get_path(elem.get_parent(toc_tree), toc_tree, path)

def get_fs_path(elem, toc_tree, path=None):
    path = path or []
    parent = elem.get_parent(toc_tree, elem_type='directory')
    if parent:
        path.append(parent.name)
        return get_fs_path(parent, toc_tree, path)
    return '/'.join(path)

def heading_dec(heading):
    return '='*len(heading)

def get_toctree_l(elem, toc_tree):
    '''returns list of elements will be included to toctree'''
    ch = elem.get_children(toc_tree)
    return [e for e in ch if e.type in ('directory','page')]

def rename_bulk(source_dir, dest_dir):

    f_index = codecs.open(j(source_dir,'index.html'),'r','utf8')
    ibs = BeautifulSoup(f_index.read())
    f_index.close()

    relations = {}
    for f in os.listdir(source_dir):
        name, ext = os.path.splitext(f)
        if ext != '.html' and name != 'index':
            pass
        else:
            f_o = codecs.open(f,'r','utf8')
            bs = BeautifulSoup(f_o.read())
            f_o.close()
            title = slugify(translify(bs.find('title').contents[0]).lower())
            del bs
            new_filename = '%s%s' % (title, ext)
            relations[f] = new_filename
            shutil.copy(j(source_dir,f), j(dest_dir, new_filename))
    # ctreate new index
    for tag in ibs.findAll(attrs={'class':'toc'}):
        tag_a = tag.findChild('a')
        for i,a in enumerate(tag_a.attrs):
            if a[0] == 'href':
                h = a[1].encode('utf8')
                del tag_a.attrs[i]
                tag_a.attrs.insert(i,('href',relations[h]))

    ni = open(j(dest_dir, 'index.html'),'w')
    ni.write(ibs.renderContents())
    ni.close()


def parse_text(elem, directory):
    """transform html to reST"""
    # Crop content html from source file
    start = '<table width="100%" border="0" cellspacing="0" cellpadding="5"><tr valign="top"><td align="left">'
    stop = '<hr noshade="noshade" size="1" />'
    content = elem.get_content(directory)
    return html2text(((content.split(start)[1]).split(stop))[0])

def filename (elem, name=None):
    return '%s%s' % (name or elem.name, '.txt')

def build_toctree_str(elem_list):
    return ''.join(map(lambda x: '   %s <%s>\n' % (x.heading,x.name), elem_list))

def index(elem, toc_tree, directory_path):
    """Form index file with toctree for directory"""
    file_path = ap(j(directory_path,filename(elem, 'index')))
    f = codecs.open(file_path,'w','utf8')
    content = index_t % \
              {
                'path':get_path(elem,toc_tree),
                'heading':elem.heading,
                'heading_dec':heading_dec(elem.heading),
                'toctree': build_toctree_str(get_toctree_l(elem, toc_tree))
              }
    f.write(content)
    f.close()

def get_chapters_content(elem,toc_tree,source_dir):
    # get all chapters
    content = []
    for c in elem.get_children(toc_tree):
        context = {
            'heading': c.heading,
            'heading_dec': heading_dec(c.heading),
            'text': parse_text(c,source_dir)
        }
        content.append(chapter_t % context)
    return '\n\n'.join(content)

def page(elem,toc_tree,source_dir,directory_path):
    """Form page file"""
    file_path = ap(j(directory_path,filename(elem)))
    f = codecs.open(file_path,'w','utf8')
    context = {
        'path': get_path(elem, toc_tree),
        'heading':elem.heading,
        'heading_dec':heading_dec(elem.heading),
        'text': parse_text(elem,source_dir)
    }
    context['chapters'] = get_chapters_content(elem, toc_tree, source_dir)
    content = page_t % context
    f.write(content)
    f.close()
    print "Created page %s" % j(directory_path,filename(elem))

def doc_index(index_tuple, dest_dir):
    tmpl = """
User manual
===========

.. toctree::
   :maxdepth: 2

%s
    """
    fi = codecs.open(j(dest_dir, 'index.txt'),'w','utf8')
    fi.write(tmpl % '\n'.join(index_tuple))
    fi.close()

def process_files(toc_tree, source_dir, dest_dir):
    main_index = []
    for elem in toc_tree:
        if elem.type == 'directory':
            dir_name = j(dest_dir,elem.name)
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)
            index(elem,toc_tree,dir_name)
            main_index.append('%s <%s/index>' % (elem.heading, elem.name))
        if elem.type == 'page':
            dir_name = get_fs_path(elem,toc_tree)
            dir_path = j(dest_dir,dir_name)
            page(elem,toc_tree,source_dir,dir_path)
            if len(elem.tlevel) == 1:
                main_index.append('   %s <%s>' % (elem.heading, elem.name))
    doc_index(main_index, dest_dir)


def extract_images(text):
    re_obj = re.compile(r"image::[\s\t]+_images/([-\.\w]+)", re.M)
    return re_obj.findall(text)

def get_embed_images(rst_source_filepath):
    rstf = file(rst_source_filepath,'r')
    content = ''.join(rstf.readlines())
    rstf.close()
    return extract_images(content)

def copy_images(doc_dir, source_dir):
    for dirname, _, files in os.walk(doc_dir):
        images = list(itertools.chain(*[get_embed_images(ap(j(dirname,f))) for f in files]))
        if images:
            _images_path = ap(j(dirname,'_images'))
            if not os.path.exists(_images_path):
                os.mkdir(_images_path)
            for image_name in images:
                image_file = ap(j(source_dir,image_name))
                if os.path.exists(image_file):
                    print "copying file %s" % image_file
                    shutil.copyfile(image_file, j(_images_path,image_name))


if __name__ == '__main__':
    # buildtree
    SOURCE = './HTML_RENAMED'

    def run():
        toc_tree = parse(SOURCE)
        # rebuild types
        for e in toc_tree:
            if len(e.get_children(toc_tree)) != 0 and len(e.tlevel) == 1:
                e.type = 'directory'
            if len(e.tlevel) == 2 or (len(e.get_children(toc_tree)) == 0 and len(e.tlevel) == 1):
                e.type = 'page'
            if len(e.tlevel) > 2:
                e.type = 'content'
        process_files(toc_tree, './HTML_RENAMED','./user')
    #run()
    copy_images('./user','./HTML')


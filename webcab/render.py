# -*- coding=utf-8 -*-
import os, sys
import web
import config
# input_encoding and output_encoding is important for unicode
# template file.
# Reference:
# http://www.makotemplates.org/docs/documentation.html#unicode
template_path = os.path.join(os.path.dirname(__file__), config.TEMPLATE_DIR).replace('\\','/')
base = web.template.render(template_path + '/base/')
render = web.template.render(template_path,cache=config.CACHE)

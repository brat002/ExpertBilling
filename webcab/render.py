# -*- coding=utf-8 -*-
import os, sys
from web.template import render as _render
# input_encoding and output_encoding is important for unicode
# template file.
# Reference:
# http://www.makotemplates.org/docs/documentation.html#unicode
render = _render(os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),cache=False)

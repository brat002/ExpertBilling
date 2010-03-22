from path import path
import os
import codecs

from postprocess import correct_headings, fix_links

restdocs = path("rstdocs2")

import sys
sys.stderr = sys.stdout

def test_all():
    """Test the REST->HTML conversion of all the docs"""
    for f in restdocs.walkfiles("*.rst"):
        rst_txt = open(f, "r").read()
#        rst_txt = correct_headings(rst_txt)
#        rst_txt = fix_links(rst_txt)

        from docutils.core import publish_parts
        print "#"*80
        print f
        content = publish_parts(rst_txt, writer_name="html")["html_body"]
        print ""

if __name__ == "__main__": test_all()

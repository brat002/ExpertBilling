import html2rst
from path import path
import os
from shutil import copytree
import re
import codecs

restdocs = path("rstdocs2")

#pre blocks are now fixed in html2rst.py (I think)
##def rewrite_pre(rst_txt):
##    """Rewrite preformatted text blocks ("::" -> "::\\n") to display correctly"""
##    rst_txt = rst_txt.replace("image::", "{IMAGE}")
##    rst_txt = rst_txt.replace("::", "::\n")
##    rst_txt = rst_txt.replace("{IMAGE}", "image::")
##    return rst_txt

is_underline = lambda l: reduce(lambda a,b: [None, a][a==b], l) in ["-", "~"]

def correct_headings(rst_txt):
    """Fix the "Title underline too short." error"""
    out = []
    lines = rst_txt.split("\n")
    for (i, line) in enumerate(lines):
        if len(line) > 1 and is_underline(line):
            line = len(lines[i-1])*line[0]
        out.append(line)
    return "\n".join(out)

def fix_links(rst_txt):
    """Fix single word links, which can be written without `backticks`"""
    onewordlinks = re.findall("`[a-zA-Z0-9]+`_", rst_txt)
    for link in onewordlinks:
        rst_txt = rst_txt.replace(link, link.replace("`", ""))
    return rst_txt

##def fix_one(filename):
##    rst_txt = open(filename, "r").read()
##    rst_txt = correct_headings(rst_txt)
##    codecs.open(filename.replace(".rst", ".fix.rst"), mode="w", encoding="utf-8").write(rst_txt)

##if __name__ == "__main__": fix_one(r"C:\code\python\_tg\tgdocs\rstdocs2\gs\validation.rst")

if __name__ == "__main__":
    for f in restdocs.walkfiles("*.rst"):
        rst_txt = open(f, "r").read()
        print f,
        rst_txt = correct_headings(rst_txt)
        rst_txt = fix_links(rst_txt)

        try:
            #codecs.open(f, mode="w", encoding="utf-8").write(rst_txt)
            open(f, "w").write(rst_txt)
        except:
            raise
            #print "(did not write, unicode decode error)"
        print "!"


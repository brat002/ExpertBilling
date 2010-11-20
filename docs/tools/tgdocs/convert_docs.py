import html2rst
from path import path
import os
from shutil import copytree
import re
import codecs

src = path("htmldocs")
dest = path("rstdocs2")

copytree(src, dest)

for f in dest.walkfiles("*.html"):
    html_text = open(f, "r").read()

    #all
    html_text = html_text.replace("<code>", "<pre>") #html2rst handles <pre> better than <code>
    html_text = html_text.replace("</code>", "</pre>")
    html_text = html_text.replace("<br/>", "") #I don't think BRs are needed, and they mess up gs/usedatabase
    html_text = html_text.replace("<br />", "")

    html_text = html_text.replace("`view plain`_ | `print`_ | `?`_\n", "") #artifacts from the syntax highlighter
    html_text = html_text.replace(".. _view plain: #\n", "")

    #special case #1
    if "eajax" in f and "paper" in f:
        html_text = html_text.replace("<pre>", "``")
        html_text = html_text.replace("</pre>", "``")
        html_text = html_text.replace("""<div class="dp-highlighter">""", """<pre><![CDATA[<div class="dp-highlighter">""")
        html_text = html_text.replace("</textarea>", "</textarea>]]></pre>")

    #special case #2
    if "usedatabase" in f:
        html_text = html_text.replace("&gt;&gt;&gt;", ">>>")

    #special case #3
    if "decorator" in f or "scheduler" in f:
        html_text = html_text.replace("<pre>", "``")
        html_text = html_text.replace("</pre>", "``")

    #special case #4
    if "apacheintegration" in f:
        html_text = html_text.replace("      <pre> ", "<pre>\n")

    #special case #5
    if "deployaswindows" in f:
        html_text = html_text.replace("<pre>service.py", "<pre>\nservice.py")
        html_text = html_text.replace("""<pre class="wiki">""", """\n<pre>\n""")

    #do html -> rest conversion
    data = html2rst.html2text_file(html_text, None)
    data = data.replace("$${", "${")
    data = data.replace("&gt;", ">")
    data = data.replace("&lt;", "<")
    data = data.replace("&amp;", "&")

    rst_path = os.path.join(f.splitpath()[0], f.namebase+".rst")
    rst_path = rst_path.replace("tgdocs", "rstdocs2")
    print rst_path
    codecs.open(rst_path, mode="w", encoding="utf-8").write(data)
    f.remove()

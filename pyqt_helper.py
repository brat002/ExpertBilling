from mako.template import Template

templ = Template("""
% for a in b:
${a["id"]}, ${a["name"]}
% endfor

""")
b=[{'id':1, 'name':'lala'}, {'id':2, 'name':'nana'}]
print templ.render(b=b, z=[1,2,3])
# -*- coding: utf-8 -*-
#$Id: paginator.py 159 2008-07-02 11:53:51Z dmitry $

from django.core.paginator import Paginator


class SimplePaginator(object):
    """
    Usage:
    1) in view

    def my_view(request):
        from path.to.paginator import SimplePaginator
        ....
        qs = MyModel.objects.filter(...)
        # Create paginator object - push it into context
        paginator = SimplePaginator(request, qs, 25, 'page')
        # Get items for template - push it into context
        items = paginator.get_page_items()
        ...

    2) in template
    For showing pagination use
    {% include 'paginator.html' %}


    Paginator template example
    {% ifnotequal paginator.pages 1 %}
    <div id="pagination">
    <table width="70%">
    <tr>
    <td>
                {% if paginator.has_p %}
                    <a href="{{ paginator.p_link }}" title="Previous page">&#8592;</a>&nbsp;
                {% endif %}
                    Page {{ paginator.current }} from {{ paginator.pages }}&nbsp;
                {% if paginator.has_n %}
                    <a href="{{ paginator.n_link }}" title="Next page">&#8594;</a>&nbsp;
                {% endif %}
    </td><td align="right">
                {% for group in paginator.windowed_page_links %}
                {% for p in group %}
                {% if not p.current %}
                <a href="{{p.link}}">{{ p.page }}</a>&nbsp;
                {% else %}
                <span class="current">{{ p.page }}</span>&nbsp;
                {% endif %}
                {% endfor %}{% if not forloop.last %}...{% endif %}
                {% endfor %}
    </td>
    </tr>
    </table>
    </div>
    {% endifnotequal %}

    """

    link_template = u'%(get_string)s%(delimeter)spage=%(page_number)d'

    def __init__(self, request, qs, per_page, link_name='page'):
        _get = request.GET.copy()

        if request.GET.has_key(link_name):
            self.current_page = _get.get(link_name)
            _get.pop(link_name)
        else:
            self.current_page = 1

        if len(_get) > 0:
            self.get_string = u'?%s' % "&".join(
                (u"%s=%s" % (k, v) for k, v in _get.items()))
            self.delimeter = '&'
        else:
            self.get_string = ''
            self.delimeter = '?'

        paginator = Paginator(qs, per_page)
        self.page = paginator.page(self.current_page)

        self.pages = self.page.paginator.num_pages

    def __repr__(self):
        return u'Page %d for %d' % (self.current(), self.page.paginator.count)

    def get_page_items(self):
        return self.page.object_list

    def has_p(self):
        return self.page.has_previous()

    def has_n(self):
        return self.page.has_next()

    def current(self):
        return self.page.number

    def total(self):
        return self.page.paginator.count

    def render_page_link(self, page_number):
        return self.link_template % {
            'get_string': self.get_string,
            'page_number': page_number,
            'delimeter': self.delimeter}

    def n_link(self):
        if self.has_n():
            return self.render_page_link(self.page.next_page_number())
        else:
            return u""

    def p_link(self):
        if self.has_p():
            return self.render_page_link(self.page.previous_page_number())
        else:
            return u""

    def make_page_links(self, start, end):
        return [(p + 1,
                 self.render_page_link(p + 1),
                 (p + 1 == self.current()))
                for p in range(start, end)]

    def page_links(self):
        return self.make_page_links(0, self.pages)

    def windowed_page_links(self, window_size=10):
        links = []
        if self.pages <= 12:
            links = [self.page_links()]
        elif self.page.number - window_size / 2 <= 3:
            links = [self.make_page_links(0, window_size),
                     self.make_page_links(self.pages - 2, self.pages)]
        elif self.page.number + window_size / 2 > self.pages - 2:
            links = [
                self.make_page_links(0, 2),
                self.make_page_links(self.pages - window_size, self.pages)
            ]
        else:
            links = [
                self.make_page_links(0, 2),
                self.make_page_links(self.page.number - window_size / 2 - 1,
                                     self.page.number + window_size / 2 - 1),
                self.make_page_links(self.pages - 2, self.pages)
            ]
        response = []
        for g in links:
            r = []
            for i in g:
                r.append({
                    'page': i[0],
                    'link': i[1],
                    'current': i[2]
                })
            response.append(r)
        return response

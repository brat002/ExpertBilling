from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.template import Library, Node, NodeList, Variable, TemplateSyntaxError
from django.utils.safestring import SafeUnicode

register = Library()

@register.filter()
def render_context(log_item, context):
    """
    helper tag needed for adding extra context when rendering a LogItem
    """

    return SafeUnicode(log_item.render(**context))


@register.filter()
def ct_for_id(id):
    """ returns a content type looked up by id """

    return ContentType.objects.get_for_id(id)


@register.simple_tag
def permalink(obj, display=None):
    """
    Return a link for an object if it as a get_absolute_url method.  Not all
    models will have this.  Models that do not have the method will be rendered
    as text
    """
    display = display if display else obj
    if hasattr(obj, 'get_absolute_url'):
        return u'<a href="%s">%s</a>' % (obj.get_absolute_url(), display)
    else:
        return obj


@register.tag
def contenttypelink(parser, token):
    """
    Return a link to an object using content types and a pk.  The model must
    have get_absolute_url() defined.  This tag is useful for rendering links to
    objects in a log entry, without having to query the object.
    """
    bits = token.contents.split()
    if len(bits) != 3:
        raise TemplateSyntaxError, "'content_type_link' tag takes two arguments: a content type id and pk"
    
    inner_nodelist = parser.parse(('endcontenttypelink',))
    parser.delete_first_token()

    return ContentTypeLinkNode(bits[1], bits[2], inner_nodelist)


LINK_FORMAT = '<a href="%s/object/%%s/%%s/">' % settings.SITE_ROOT
class ContentTypeLinkNode(Node):

    def __init__(self, content_type_id, pk, inner_nodelist):
        self.content_type_id = Variable(content_type_id)
        self.pk = Variable(pk)
        self.inner_nodelist = inner_nodelist

    def render(self, context):
        content_type_id = self.content_type_id.resolve(context)
        content_type = ContentType.objects.get_for_id(content_type_id)

        if hasattr(content_type.model_class(), 'get_absolute_url'):
            pk = self.pk.resolve(context)
            nodelist = NodeList()
            nodelist.append(LINK_FORMAT % (content_type.pk, pk))
            nodelist.append(self.inner_nodelist.render(context))
            nodelist.append('</a>')
            return nodelist.render(context)
        else:
            return self.inner_nodelist.render(context)

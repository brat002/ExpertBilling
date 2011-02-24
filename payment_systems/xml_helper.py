import re
import xml.sax.handler

def xml2obj(src):
    """
    A simple function to converts XML data into native Python object.
    """

    non_id_char = re.compile('[^_0-9a-zA-Z]')
    def _name_mangle(name):
        return non_id_char.sub('_', name)

    class DataNode(object):
        def __init__(self):
            self._attrs = {}    # XML attributes and child elements
            self.data = None    # child text data
        def __len__(self):
            # treat single element as a list of 1
            return 1
        def __getitem__(self, key):
            if isinstance(key, basestring):
                return self._attrs.get(key,None)
            else:
                return [self][key]
        def __contains__(self, name):
            return self._attrs.has_key(name)
        def __nonzero__(self):
            return bool(self._attrs or self.data)
        def __getattr__(self, name):
            if name.startswith('__'):
                # need to do this for Python special methods???
                raise AttributeError(name)
            return self._attrs.get(name,None)
        def _add_xml_attr(self, name, value):
            if name in self._attrs:
                # multiple attribute of the same name are represented by a list
                children = self._attrs[name]
                if not isinstance(children, list):
                    children = [children]
                    self._attrs[name] = children
                children.append(value)
            else:
                self._attrs[name] = value
        def __str__(self):
            return self.data or ''
        def __repr__(self):
            items = sorted(self._attrs.items())
            if self.data:
                items.append(('data', self.data))
            return u'{%s}' % ', '.join([u'%s:%s' % (k,repr(v)) for k,v in items])

    class TreeBuilder(xml.sax.handler.ContentHandler):
        def __init__(self):
            self.stack = []
            self.root = DataNode()
            self.current = self.root
            self.text_parts = []
        def startElement(self, name, attrs):
            self.stack.append((self.current, self.text_parts))
            self.current = DataNode()
            self.text_parts = []
            # xml attributes --> python attributes
            for k, v in attrs.items():
                self.current._add_xml_attr(_name_mangle(k), v)
        def endElement(self, name):
            text = ''.join(self.text_parts).strip()
            if text:
                self.current.data = text
            if self.current._attrs:
                obj = self.current
            else:
                # a text only node is simply represented by the string
                obj = text or ''
            self.current, self.text_parts = self.stack.pop()
            self.current._add_xml_attr(_name_mangle(name), obj)
        def characters(self, content):
            self.text_parts.append(content)

    builder = TreeBuilder()
    if isinstance(src,basestring):
        xml.sax.parseString(src, builder)
    else:
        xml.sax.parse(src, builder)
    return builder.root._attrs.values()[0]


#{'data': None, '_attrs': {u'account_list': {account:[{amount:u'1.00', bill_date:u'2011-02-23 18:14:06.0', comment:u'\u041f\u043e\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435 \u0441\u0447\u0451\u0442\u0430 brat002', direct:u'1', from:{prv:u'11468', trm_id:u'Diggit.ru'}, id:u'27409978', src:{amount_lk:u'1.00', card_pay:u'1'}, status:u'50', term_ransaction:u'10', to:{prv:u'7', trm_id:u'9514444003'}}, {amount:u'1.00', bill_date:u'2011-02-23 18:13:30.0', comment:u'\u041f\u043e\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435 \u0441\u0447\u0451\u0442\u0430 brat002', direct:u'1', from:{prv:u'11468', trm_id:u'Diggit.ru'}, id:u'27409884', src:{amount_lk:u'1.00', card_pay:u'1'}, status:u'50', term_ransaction:u'9', to:{prv:u'7', trm_id:u'9514444003'}}, {amount:u'1.00', bill_date:u'2011-02-23 18:10:54.0', comment:u'\u041f\u043e\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435 \u0441\u0447\u0451\u0442\u0430 brat002', direct:u'1', from:{prv:u'11468', trm_id:u'Diggit.ru'}, id:u'27409603', src:{amount_lk:u'1.00', card_pay:u'1'}, status:u'50', term_ransaction:u'5', to:{prv:u'7', trm_id:u'9514444003'}}, {amount:u'1.00', bill_date:u'2011-02-23 18:10:28.0', comment:u'\u041f\u043e\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435 \u0441\u0447\u0451\u0442\u0430 brat002', direct:u'1', from:{prv:u'11468', trm_id:u'Diggit.ru'}, id:u'27409561', src:{amount_lk:u'1.00', card_pay:u'1'}, status:u'50', term_ransaction:u'4', to:{prv:u'7', trm_id:u'9514444003'}}]}, u'result_code': {fatal:u'false', data:u'0'}}}


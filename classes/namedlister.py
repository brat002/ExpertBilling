from operator import itemgetter as _itemgetter, setitem as _setitem
from keyword import iskeyword as _iskeyword
import sys as _sys

def namedlist(typename, field_names, verbose=True, rename=False):

    # Parse and validate the field names.  Validation serves two purposes,
    # generating informative error messages and preventing template injection attacks.
    if isinstance(field_names, basestring):
        field_names = field_names.replace(',', ' ').split() # names separated by whitespace and/or commas
    field_names = tuple(map(str, field_names))
    if rename:
        names = list(field_names)
        seen = set()
        for i, name in enumerate(names):
            if not name or (not min(c.isalnum() or c=='_' for c in name)
                 or _iskeyword(name) or name[0].isdigit()
                 or name.startswith('_') or name in seen):
                    names[i] = '_%d' % (i+1)
            seen.add(name)
        field_names = tuple(names) 
    for name in (typename,) + field_names:
        if not min(c.isalnum() or c=='_' for c in name):
            raise ValueError('Type names and field names can only contain alphanumeric characters and underscores: %r' % name)
        if _iskeyword(name):
            raise ValueError('Type names and field names cannot be a keyword: %r' % name)
        if name[0].isdigit():
            raise ValueError('Type names and field names cannot start with a number: %r' % name)
    seen_names = set()
    for name in field_names:
        if name.startswith('_') and not rename:
            raise ValueError('Field names cannot start with an underscore: %r' % name)
        if name in seen_names:
            raise ValueError('Encountered duplicate field name: %r' % name)
        seen_names.add(name)

    # Create and fill-in the class template
    numfields = len(field_names)
    argtxt = repr(field_names).replace("'", "")[1:-1]   # tuple repr without parens or quotes
    defargtxt = ', '.join('%s=None' % name for name in field_names)
    reprtxt = ', '.join('%s=%%r' % name for name in field_names)
    dicttxt = ', '.join('%r: t[%d]' % (name, pos) for pos, name in enumerate(field_names))
    template = '''from operator import itemgetter, setitem\n
class %(typename)s(list):
    '%(typename)s(%(argtxt)s)' \n
    __slots__ = () \n
    _fields = %(field_names)r \n
    def __init__(self, empty=True, %(defargtxt)s):
        if empty:
            pass
        else:
            self.extend((%(argtxt)s)) \n                
    @classmethod
    def _make(cls, iterable):
        'Make a new %(typename)s object from a sequence or iterable'
        result = cls()
        result.extend(iterable)
        if len(result) < %(numfields)d:
            result.extend([None for i in xrange(%(numfields)d - len(result))])
        return result \n
    def __repr__(self):
        try:
            return '%(typename)s(%(reprtxt)s)' %% tuple(self) 
        except:
            return repr(tuple(self)) \n
    def _asdict(t):
        'Return a new dict which maps field names to their values'
        return {%(dicttxt)s} \n
    def _replace(self, **kwds):
        'Return a new %(typename)s object replacing specified fields with new values'
        result = self._make(map(kwds.pop, %(field_names)r, self))
        if kwds:
            raise ValueError('Got unexpected field names: %%r' %% kwds.keys())
        return result \n
    def __getnewargs__(self):
        return tuple(self) \n\n''' % locals()
    for i, name in enumerate(field_names):
        template += '    %s = property(itemgetter(%d), lambda self_, value_: setitem(self_, %d, value_))\n' % (name, i, i)
    if verbose:
        _sys.stdout.write(template)
        f = open(typename + '.py', 'wb')
        f.write(template)
        f.close()

    # Execute the template string in a temporary namespace
    namespace = dict(itemgetter=_itemgetter, setitem=_setitem)
    try:
        exec template in namespace
    except SyntaxError, e:
        raise SyntaxError(repr(e) + ':\n' + template)
    result = namespace[typename]

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple is created.  Bypass this step in enviroments where
    # sys._getframe is not defined (Jython for example).
    if hasattr(_sys, '_getframe') and _sys.platform != 'cli':
        result.__module__ = _sys._getframe(1).f_globals.get('__name__', '__main__')

    return result






if __name__ == '__main__':
    # verify that instances can be pickled
    namedlist(_sys.argv[1], reduce(str.__add__, _sys.argv[2:], ''), True)
    

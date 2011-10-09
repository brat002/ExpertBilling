
import re

VERSION = (0, 2, 1, "final")
PURSE_RE = re.compile(ur'^(?P<type>[ZREUYBGDC])(?P<number>\d{12})$')
WMID_RE = re.compile(ur'^\d{12}$')

def get_version():
    if VERSION[3] != "final":
        return "%s.%s.%s%s" % (VERSION[0], VERSION[1], VERSION[2], VERSION[3])
    else:
        return "%s.%s.%s" % (VERSION[0], VERSION[1], VERSION[2])

__version__ = get_version()

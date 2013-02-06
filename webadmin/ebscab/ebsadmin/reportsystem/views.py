
from reports import rep

def report(request, slug):
    return rep.get(slug)(request)
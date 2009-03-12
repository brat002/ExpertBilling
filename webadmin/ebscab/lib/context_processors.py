from django.contrib.sites.models import Site
def domain(request):
    return {
            'domain':Site.objects.get_current(),
            }
    
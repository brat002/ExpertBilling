from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from payments.w1ru import PaymentProcessor

class Command(BaseCommand):
    help = 'Display URL path for w1ru Online URL configuration'

    def handle(self, *args, **options):

        current_site = Site.objects.get_current()

        self.stdout.write('Login to w1ru configuration page and setup following links:\n\n')
        self.stdout.write(' * Postback URL: http://%s%s\n' % (
            current_site.domain,
            reverse('getpaid-w1ru-postback')

            )
        )


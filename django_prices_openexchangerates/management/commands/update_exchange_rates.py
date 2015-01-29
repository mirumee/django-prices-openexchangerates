from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from ...tasks import update_conversion_rates


class Command(BaseCommand):

    def handle(self, *args, **options):
        for conversion_rate in update_conversion_rates():
            self.stdout.write('%s' % (conversion_rate, ))

from django.core.management.base import BaseCommand, CommandError

from distribution.models import Component
from distribution.models import Distribution
from distribution.models import VENDORS

class Command(BaseCommand):
    args = '<vendor> <codename>'
    help = 'add a distribution'

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError("Please name vendor and codename")

        # handle vendor:
        vendor = args[0]
        for vendor_id, vendor_name in VENDORS:
            if vendor.lower() == vendor_name.lower():
                vendor = vendor_id

        # handle distro:
        codename = args[1]
        dist = Distribution.opjects.create(name=args[0], vendor=vendor_id)

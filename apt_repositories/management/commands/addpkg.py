import sys

from django.core.management.base import BaseCommand

from distribution.models import Component

from package.models import Package


class Command(BaseCommand):
    args = 'pkg [components...]'
    help = 'Add package with components'

    def err(self, msg):
        self.stderr.write("%s\n" % msg)

    def handle(self, *args, **options):
        if len(args) < 1:
            self.err("Package name is mandatory.")
            sys.exit(1)

        p = Package.objects.get_or_create(name=args[0])[0]
        comps = [Component.objects.get_or_create(name=comp)[0]
                 for comp in args[1:]]
        p.components.add(*comps)

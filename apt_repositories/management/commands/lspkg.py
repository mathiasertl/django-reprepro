from django.core.management.base import BaseCommand

from package.models import Package


class Command(BaseCommand):
    args = ''
    help = 'List all packages'

    def out(self, msg):
        self.stdout.write("%s\n" % msg)

    def err(self, msg):
        self.stderr.write("%s\n" % msg)

    def handle(self, *args, **options):
        for pkg in Package.objects.all():
            qs = pkg.components.order_by('name')
            comps = qs.values_list('name', flat=True)
            self.out('%s: %s' % (pkg.name, '|'.join(comps)))

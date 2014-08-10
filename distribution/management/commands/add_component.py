from django.core.management.base import BaseCommand, CommandError

from distribution.models import Component
from distribution.models import Distribution

class Command(BaseCommand):
    args = 'name'
    help = 'add a distribution'

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Please name a component name.")

        component, created = Component.objects.get_or_create(name=args[0])

        if not created:
            raise CommandError("Component already exists.")

        component.distribution_set.add(*Distribution.objects.all())

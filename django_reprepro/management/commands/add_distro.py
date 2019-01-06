# -*- coding: utf-8 -*-
#
# This file is part of django-reprepro (https://github.com/mathiasertl/django-reprepro).
#
# django-reprepro is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# django-reprepro is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with django-reprepro.  If
# not, see <http://www.gnu.org/licenses/>.

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from ...models import VENDORS
from ...models import Component
from ...models import Distribution


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
                break
        if vendor == args[0]:
            raise CommandError("Could not find vendor")

        # handle distro:
        codename = args[1]
        dist = Distribution.objects.create(name=codename, vendor=vendor_id)

        # get and add enabled components:
        components = Component.objects.filter(enabled=True)
        dist.components.add(*components)

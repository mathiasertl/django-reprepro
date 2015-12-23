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

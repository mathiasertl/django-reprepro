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

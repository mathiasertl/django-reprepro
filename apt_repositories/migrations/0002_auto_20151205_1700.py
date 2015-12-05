# -*- coding: utf-8 -*-
#
# This file is part of packagearchive (https://github.com/mathiasertl/packagearchive).
#
# packagearchive is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# packagearchive is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with packagearchive.
# If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from django.db import migrations


def migrate_data(apps, schema_editor):
    # import models
    new_comp = apps.get_model('apt_repositories', 'Component')
    old_comp = apps.get_model('distribution', 'Component')
    new_dist = apps.get_model('apt_repositories', 'Distribution')
    old_dist = apps.get_model('distribution', 'Distribution')
    new_pkg = apps.get_model('apt_repositories', 'Package')
    old_pkg = apps.get_model('package', 'Package')
    new_inc = apps.get_model('apt_repositories', 'IncomingDirectory')
    old_inc = apps.get_model('incoming', 'IncomingDirectory')

    # create components
    for old in old_comp.objects.all():
        new_comp.objects.create(name=old.name, enabled=old.enabled)

    # create dists
    for old in old_dist.objects.all():
        new = new_dist.objects.create(name=old.name, vendor=old.vendor)

        new_comps = new_comp.objects.filter(name__in=old.components.values_list('name', flat=True))
        new.components.add(*new_comps)

    # create packages
    for old in old_pkg.objects.all():
        new = new_pkg.objects.create(name=old.name, all_components=old.all_components,
                                     remove_on_update=old.remove_on_update)

        new_comps = new_comp.objects.filter(name__in=old.components.values_list('name', flat=True))
        new.components.add(*new_comps)

    for old in old_inc.objects.all():
        new_inc.objects.create(location=old.location, enabled=old.enabled)


class Migration(migrations.Migration):

    dependencies = [
        ('apt_repositories', '0001_initial'),
        ('distribution', '0001_initial'),
        ('package', '0001_initial'),
        ('incoming', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_data),
    ]

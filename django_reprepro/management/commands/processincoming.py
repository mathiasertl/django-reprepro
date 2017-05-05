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

from __future__ import unicode_literals

import os
import re
import time

from subprocess import Popen
from subprocess import PIPE

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from django_reprepro.models import Distribution
from django_reprepro.models import IncomingDirectory
from django_reprepro.models import Package
from django_reprepro.models import BinaryPackage
from django_reprepro.models import SourcePackage
from django_reprepro.util import ChangesFile

# NOTE 2016-01-15: We add --ignore=surprisingbinary because of automatically generated
#   -dbgsym packages, which are not included in the changes file. See
#   https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=808558 for more info. This is fixed
#   in reprepro 4.17.0.
BASE_ARGS = ['reprepro', '-b', '/var/www/apt.fsinf.at/', '--ignore=surprisingbinary']


class Command(BaseCommand):
    args = ''
    help = 'Process incoming files'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help="Don't really add any files.")
        parser.add_argument('--prerm', default='',
            help="Coma-seperated list of source packages to remove before "\
                    "adding them. Necessary for source packages that build"\
                    "several binary packages with new versions."
        )
        parser.add_argument('--norm', default=False, action='store_true',
                            help="Don't remove files after adding them to the repository.")

    def err(self, msg):
        self.stderr.write("%s\n" % msg)

    def rm(self, path):
        """Remove a file. Honours --dry, --norm and --verbose."""
        if self.norm:
            return
        if not self.dry:
            os.remove(path)

    def ex(self, *args):
        if self.verbose:
            print(' '.join(args))
        if not self.dry:
            p = Popen(args, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            return p.returncode, stdout, stderr
        else:
            return 0, '', ''

    def remove_src_package(self, pkg, dist):
        """Remove a source package from a distribution."""

        cmd = BASE_ARGS + ['removesrc', dist.name, pkg]
        return self.ex(*cmd)

    def include(self, dist, component, changesfile):
        """Add a .changes file to the repository."""

        cmd = BASE_ARGS + ['-C', component.name, 'include', dist.name, changesfile.path]
        return self.ex(*cmd)

    def includedeb(self, dist, component, changes, deb):
        path = os.path.join(os.path.dirname(changes.path), deb)
        cmd = BASE_ARGS + ['-C',  component.name, 'includedeb', dist.name, path]
        return self.ex(*cmd)

    def record_source_upload(self, package, changes, dist, components):
        version = changes['Version'].rsplit('-', 1)[0]
        p, created = SourcePackage.objects.get_or_create(package=package, dist=dist, defaults={
            'version': version,
        })
        if not created:
            p.version = version
            p.components.clear()
            p.timestamp = timezone.now()
            p.save()

        p.components.add(*components)
        return p

    def record_binary_upload(self, deb, package, dist, components):
        # parse name, version and arch from the filename
        match = re.match('(?P<name>.*)_(?P<version>.*)_(?P<arch>.*).deb', deb)
        name = match.group('name')
        version = match.group('version')
        arch = match.group('arch')

        p, created = BinaryPackage.objects.get_or_create(
            package=package, name=name, dist=dist, arch=arch, defaults={
                'version': version,
            })
        if not created:
            p.version = version
            p.components.clear()
            p.timestamp = timezone.now()
            p.save()

        p.components.add(*components)
        return p

    def handle_changesfile(self, changesfile, dist, arch):
        pkg = ChangesFile(changesfile)
        pkg.parse()

        srcpkg = pkg['Source']
        package = Package.objects.get_or_create(name=srcpkg)[0]
        package.last_seen = timezone.now()
        package.save()

        # get list of components
        if package.all_components:
            components = dist.components.filter(enabled=True)
        else:
            components = package.components.order_by('name').filter(distribution=dist)
            components.update(last_seen=timezone.now())
        if self.verbose:
            print('%s: %s' % (dist, ', '.join([c.name for c in components])))

        # see if all files exist. If not, try a few more times, we might be in
        # the middle of uploading a new package.
        for i in range(1, 5):
            if pkg.exists():
                break
            else:
                if self.verbose:
                    self.err('%s: Not all files exist, try again in 5s...'
                             % changesfile)
                time.sleep(5)

        # remove package if requested
        if srcpkg in self.prerm or package.remove_on_update:
            self.remove_src_package(pkg=srcpkg, dist=dist)

        totalcode = 0

        for component in components:
            if arch == 'amd64':
                code, stdout, stderr = self.include(dist, component, pkg)
                totalcode += code

                if code == 0:
                    self.record_source_upload(package, pkg, dist, components)
                    for deb in pkg.binary_packages:
                        self.record_binary_upload(deb, package, dist, components)
                else:
                    self.err('   ... RETURN CODE: %s' % code)
                    self.err('   ... STDOUT: %s' % stdout.decode('utf-8'))
                    self.err('   ... STDERR: %s' % stderr.decode('utf-8'))
            else:
                debs = [f for f in pkg.binary_packages if f.endswith('_%s.deb' % arch)]
                for deb in debs:
                    code, stdout, stderr = self.includedeb(dist, component, pkg, deb)
                    totalcode += code

                    if code == 0:
                        self.record_binary_upload(deb, package, dist, components)
                    else:
                        self.err('   ... RETURN CODE: %s' % code)
                        self.err('   ... STDOUT: %s' % stdout.decode('utf-8'))
                        self.err('   ... STDERR: %s' % stderr.decode('utf-8'))

        if totalcode == 0:
            # remove changes files and the files referenced:
            basedir = os.path.dirname(changesfile)
            for filename in pkg.files:
                self.rm(os.path.join(basedir, filename))

            self.rm(changesfile)

    def handle_directory(self, path):
        dist, arch = os.path.basename(path).split('-', 1)
        dist = Distribution.objects.get(name=dist)
        dist.last_seen = timezone.now()
        dist.save()

        for f in [f for f in os.listdir(path) if f.endswith('.changes')]:
            try:
                self.handle_changesfile(os.path.join(path, f), dist, arch)
            except RuntimeError as e:
                self.err(e)

    def handle_incoming(self, incoming):
        # A few safety checks:
        if not os.path.exists(incoming.location):
            self.err("%s: No such directory." % incoming.location)
            return
        if not os.path.isdir(incoming.location):
            self.err("%s: Not a directory." % incoming.location)
            return

        location = os.path.abspath(incoming.location)

        for dirname in sorted(os.listdir(location)):
            path = os.path.join(location, dirname)
            if not os.path.isdir(path) or '-' not in path:
                continue
            self.handle_directory(path)

    def handle(self, *args, **options):
        self.verbose = options['verbosity'] >= 2
        self.dry = options['dry_run']
        self.norm = options['norm']
        self.basedir = os.path.abspath(
            options.get('basedir', getattr(settings, 'APT_BASEDIR', '.')))
        self.prerm = options['prerm'].split(',')
        self.src_handled = {}

        directories = IncomingDirectory.objects.filter(enabled=True)

        for directory in directories.order_by('location'):
            self.handle_incoming(directory)

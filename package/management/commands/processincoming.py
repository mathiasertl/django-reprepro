import os
import sys

from optparse import make_option
from subprocess import Popen, PIPE

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from distribution.models import Distribution

from incoming.models import IncomingDirectory

from package.models import Package
from package.util import SourcePackage, BinaryPackage

BASE_ARGS = ['reprepro', '-b', '/var/www/apt.fsinf.at/', '--distdir=+b/dists/']


class Command(BaseCommand):
    args = ''
    help = 'Process incoming files'

    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
            action='store_true',
            default=False,
            help="Don't really add any files"
        ),
        make_option('--verbose',
            action='store_true',
            default=False,
            help="Don't really add any files"
        ),
    )

    def err(self, msg):
        self.stderr.write("%s\n" % msg)

    def handle_changesfile(self, changesfile, dist):
        pkg = BinaryPackage(changesfile)
        pkg.parse()

        args = BASE_ARGS + [
            '--outdir=+b/%s/' % dist,
            '--dbdir=+o/db/',
        ]

        srcpkg = pkg['Source']
        if srcpkg in self.src_handled[dist]:
            args += ['-T', 'deb']
        else:
            self.src_handled[dist][srcpkg] = Package.objects.get_or_create(
                name=srcpkg)[0]
        package = self.src_handled[dist][srcpkg]

        # get list of components
        if package.all_components:
            components = Component.objects.filter(distribution__name=dist)
        else:
            components = package.components.filter(distribution__name=dist)
        components = list(components.values_list('name', flat=True))
        if len(components) == 0:
            return  # no components found, exiting
        args += ['-C', '|'.join(components)]

        # add final include command:
        args += ['include', dist, changesfile]

        # actually execute:
        if self.verbose:
            print(' '.join(args))
        if not self.dry:
            p = Popen(args, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                self.err('   ... RETURN CODE: %s' % p.returncode)
                self.err('   ... STDOUT: %s' % stdout)
                self.err('   ... STDERR: %s' % stderr)

    def handle_directory(self, path):
        dist, arch = os.path.basename(path).split('-', 1)

        if dist not in self.src_handled:
            self.src_handled[dist] = {}

        for f in [f for f in os.listdir(path) if f.endswith('.changes')]:
            try:
                self.handle_changesfile(os.path.join(path, f), dist)
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
        self.verbose = options['verbose']
        self.dry = options['dry_run']
        self.basedir = os.path.abspath(
            options.get('basedir', getattr(settings, 'APT_BASEDIR', '.')))
        self.src_handled = {}

        directories = IncomingDirectory.objects.filter(enabled=True)

        for directory in directories.order_by('location'):
            self.handle_incoming(directory)

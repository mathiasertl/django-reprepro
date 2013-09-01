import os
import time

from optparse import make_option
from subprocess import Popen
from subprocess import PIPE

from django.conf import settings
from django.core.management.base import BaseCommand

from distribution.models import Component

from incoming.models import IncomingDirectory

from package.models import Package
from package.util import BinaryPackage

BASE_ARGS = ['reprepro', '-b', '/var/www/apt.fsinf.at/', ]


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
        make_option('--prerm',
            default='',
            help="Coma-seperated list of source packages to remove before "\
                    "adding them. Necessary for source packages that build"\
                    "several binary packages with new versions."
        ),
        make_option(
            '--norm', default=False, action='store_true',
            help="Don't remove files after adding them to the repository."
        ),
    )

    def err(self, msg):
        self.stderr.write("%s\n" % msg)

    def rm(self, path):
        """Remove a file. Honours --dry, --norm and --verbose."""
        if self.norm:
            return
        if self.verbose:
            print('rm %s' % path)
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

        cmd = BASE_ARGS + ['removesrc', dist, pkg]
        return self.ex(*cmd)

    def add_changesfile(self, cmd, dist, arch, component, changesfile):
        """Add a .changes file to the repository."""

        cmd = cmd + ['-C', component, 'include', dist, changesfile.path]
        return self.ex(*cmd)

    def includedeb(self, cmd, dist, component, changes, deb):
        path = os.path.join(os.path.dirname(changes.path), deb)
        cmd = cmd + ['-C',  component, 'includedeb', dist, path]
        return self.ex(*cmd)

    def handle_changesfile(self, changesfile, dist, arch):
        pkg = BinaryPackage(changesfile)
        pkg.parse()

        args = BASE_ARGS + [
            '--ignore=wrongsourceversion',
            '--ignore=wrongversion',
        ]

        srcpkg = pkg['Source']
        package = Package.objects.get_or_create(name=srcpkg)[0]

        # get list of components
        if package.all_components:
            components = Component.objects.filter(distribution__name=dist)
        else:
            components = package.components.filter(distribution__name=dist)
        components = list(components.values_list('name', flat=True))
        if len(components) == 0:
            base = os.path.basename(changesfile)
            self.err('%s: Not added because no components were found' % base)
            return  # no components found, not adding

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
                code, stdout, stderr = self.add_changesfile(
                     args, dist, arch, component, pkg)
                totalcode += code

                if code != 0:
                    self.err('   ... RETURN CODE: %s' % code)
                    self.err('   ... STDOUT: %s' % stdout)
                    self.err('   ... STDERR: %s' % stderr)
            else:
                debs = [f for f in pkg.files if f.endswith('%s.deb' % arch)]
                for deb in debs:
                    code, stdout, stderr = self.includedeb(args, dist, component, pkg, deb)
                    if code != 0:
                        self.err('   ... RETURN CODE: %s' % code)
                        self.err('   ... STDOUT: %s' % stdout)
                        self.err('   ... STDERR: %s' % stderr)

        if totalcode == 0:
            # remove changes files and the files referenced:
            basedir = os.path.dirname(changesfile)
            for filename in pkg.files:
                self.rm(os.path.join(basedir, filename))

            self.rm(changesfile)

    def handle_directory(self, path):
        dist, arch = os.path.basename(path).split('-', 1)

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
        self.verbose = options['verbose']
        self.dry = options['dry_run']
        self.norm = options['norm']
        self.basedir = os.path.abspath(
            options.get('basedir', getattr(settings, 'APT_BASEDIR', '.')))
        self.prerm = options['prerm'].split(',')
        self.src_handled = {}

        directories = IncomingDirectory.objects.filter(enabled=True)

        for directory in directories.order_by('location'):
            self.handle_incoming(directory)

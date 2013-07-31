import os
import sys
import time

from optparse import make_option
from subprocess import Popen, PIPE

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from distribution.models import Distribution, Component

from incoming.models import IncomingDirectory

from package.models import Package
from package.util import SourcePackage, BinaryPackage

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
    )

    def err(self, msg):
        self.stderr.write("%s\n" % msg)

    def remove_src_package(self, pkg, dist):
        #reprepro -b /var/www/apt.fsinf.at/ removesrc wheezy iptables-fsinf
        cmd = BASE_ARGS + ['removesrc', dist, pkg]

        if self.verbose or self.dry:
            print(' '.join(cmd))
        if not self.dry:
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()

    def add_changesfile(self, cmd, dist, component, changesfile):
        cmd = cmd + ['-C', component, 'include', dist, changesfile.path]

        # actually execute:
        if self.verbose:
            print(' '.join(cmd))
        if not self.dry:
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            return p.returncode, stdout, stderr
        else:
            return 0, '', ''  # return dummy values

    def handle_changesfile(self, changesfile, dist):
        pkg = BinaryPackage(changesfile)
        pkg.parse()

        args = BASE_ARGS + [
#            '--outdir=+b/dists/pool/%s/' % dist,
#            '--dbdir=+b/db/%s/' % dist,
            '--ignore=wrongsourceversion',
            '--ignore=wrongversion',
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
                    self.err('%s: Not all files exist, try again in 5 seconds...' % changesfile)
                time.sleep(5)

        # remove package if requested
        if srcpkg in self.prerm or package.remove_on_update:
            self.remove_src_package(pkg=srcpkg, dist=dist)

        totalcode = 0
        for component in components:
            code, stdout, stderr = self.add_changesfile(args, dist, component, pkg)
            totalcode += code

            if code != 0:
                self.err('   ... RETURN CODE: %s' % code)
                self.err('   ... STDOUT: %s' % stdout)
                self.err('   ... STDERR: %s' % stderr)

        if totalcode == 0 and not self.dry:
            # remove changes files and the files referenced:
            basedir = os.path.dirname(changesfile)
            for filename in pkg.get_files():
                fullpath = os.path.join(basedir, filename)
                if self.verbose:
                    print('rm %s' % fullpath)
                os.remove(fullpath)

            if self.verbose:
                print('rm %s' % changesfile)
            os.remove(changesfile)
        elif self.dry:
            basedir = os.path.dirname(changesfile)
            for filename in pkg.get_files():
                print('rm %s' % os.path.join(basedir, filename))
            print('rm %s' % changesfile)

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
        self.prerm = options['prerm'].split(',')
        self.src_handled = {}

        directories = IncomingDirectory.objects.filter(enabled=True)

        for directory in directories.order_by('location'):
            self.handle_incoming(directory)

import os
import subprocess
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from package.models import Package
from package.util import SourcePackage, BinaryPackage

BASE_ARGS = ['reprepro', '-b', '/var/www/apt.fsinf.at/', '--distdir=+b/dists/']

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

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
            self.src_handled[dist].append(srcpkg)

        #TODO: get real list of components
        components = ['all']
        args += ['-C', '|'.join(components)]

        # add final include command:
        args += ['include', dist, changesfile]

        # actually execute:
        print(' '.join(args))
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            print('   ... RETURN CODE: %s' % p.returncode)
            print('   ... STDOUT: %s' % stdout)
            print('   ... STDERR: %s' % stderr)


    def handle_directory(self, path):
        dist, arch = os.path.basename(path).split('-', 1)

        if dist not in self.src_handled:
            self.src_handled[dist] = []

        for f in [f for f in os.listdir(path) if f.endswith('.changes')]:
            try:
                self.handle_changesfile(os.path.join(path, f), dist)
            except RuntimeError as e:
                self.err(e)

    def handle(self, *args, **options):
        self.basedir = os.path.abspath(
            options.get('basedir', getattr(settings, 'APT_BASEDIR', '.')))
        self.srcdir = os.path.abspath(
            options.get('srcdir', getattr(settings, 'APT_SRCDIR', '.')))
        self.src_handled = {}

        for dirname in sorted(os.listdir(self.srcdir)):
            path = os.path.join(self.srcdir, dirname)
            if not os.path.isdir(path) or '-' not in path:
                continue

            self.handle_directory(path)


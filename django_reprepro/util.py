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
import gnupg


class Package(dict):
    _parsed = False
    _files = None

    def __init__(self, path):
        self.path = path

    @property
    def files(self):
        if not self._parsed:
            self.parse()

        if self._files is None:
            if 'Files' in self:
                raw = self.get('Files')
            else:
                raw = self.get([k for k in self.keys() if k.startswith('Checksums')][0])

            self._files = []
            for line in raw.split("\n"):
                self._files.append(line.split()[-1])

        return self._files

    def parse(self):
        self.data = gnupg.GPG().decrypt_file(open(self.path, 'rb'))
        if not self.data.valid:
            raise RuntimeError("%s: GPG signature not valid" % self.path)

        last_field = None
        for line in self.data.data.strip().split("\n"):
            if line.startswith(' '):
                # append to last line
                if self[last_field] == '':
                    self[last_field] = line[1:]
                else:
                    self[last_field] += "\n%s" % line[1:]
            else:
                field, value = line.split(':', 1)
                field = field.strip()
                value = value.strip()

                last_field = field
                self[field] = value
        self['Architecture'] = self['Architecture'].split()

        self._parsed=True

    def exists(self):
        """Check if all files referenced by this package exist."""
        basedir = os.path.dirname(self.path)

        for filename in self.files:
            path = os.path.join(basedir, filename)
            if not os.path.exists(path):
                return False

        return True


class SourcePackage(Package):
    pass


class BinaryPackage(Package):
    pass
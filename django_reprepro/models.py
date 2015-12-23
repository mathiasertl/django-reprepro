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

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from .constants import VENDOR_DEBIAN
from .constants import VENDOR_UBUNTU

VENDORS = (
    (VENDOR_DEBIAN, 'Debian'),
    (VENDOR_UBUNTU, 'Ubuntu'),
)


@python_2_unicode_compatible
class Component(models.Model):
    name = models.CharField(max_length=16, unique=True)
    enabled = models.BooleanField(default=True)
    last_seen = models.DateTimeField(null=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Distribution(models.Model):
    name = models.CharField(max_length=16, unique=True)
    vendor = models.SmallIntegerField(choices=VENDORS)
    last_seen = models.DateTimeField(null=True)

    components = models.ManyToManyField(Component)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Package(models.Model):
    name = models.CharField(max_length=64, unique=True)
    all_components = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True)

    components = models.ManyToManyField(Component)

    # Very useful if binary packages have individual changelogs where
    # the version is different from the source package version.
    remove_on_update = models.BooleanField(
        default=False,
        help_text="Remove package from index prior to adding a new version of the package."
    )

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class PackageUpload(models.Model):
    package = models.ForeignKey(Package)
    dist = models.ForeignKey(Distribution)
    components = models.ManyToManyField(Component)

    timestamp = models.DateTimeField(auto_now_add=True)
    version = models.CharField(max_length=32)
    arch = models.CharField(max_length=8)

    def __str__(self):
        return '%s_%s_%s' % (self.package.name, self.version, self.arch)


@python_2_unicode_compatible
class IncomingDirectory(models.Model):
    location = models.CharField(max_length=64)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.location

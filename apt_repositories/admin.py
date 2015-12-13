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

from django.contrib import admin

from .models import Component
from .models import Distribution
from .models import IncomingDirectory
from .models import Package

@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'last_seen', )
    list_filter = ('enabled', )
    ordering = ('name', )
    readonly_fields = ('last_seen', )


@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'last_seen', )
    list_filter= ('vendor', )
    ordering = ('name', )
    readonly_fields = ('last_seen', )


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'all_components', 'last_seen', )
    ordering = ('name', )
    readonly_fields = ('last_seen', )


@admin.register(IncomingDirectory)
class IncomingDirectoryAdmin(admin.ModelAdmin):
    list_display = ('location', 'enabled')

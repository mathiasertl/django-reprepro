from django.contrib import admin

from .models import Component
from .models import Distribution

admin.site.register(Component)
admin.site.register(Distribution)

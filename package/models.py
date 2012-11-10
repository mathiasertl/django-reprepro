from django.db import models

from distribution.models import Component


class Package(models.Model):
    name = models.CharField(max_length=64, unique=True)
    all_components = models.BooleanField(default=False)

    components = models.ManyToManyField(Component)
